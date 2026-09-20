"""Lightweight async LLM client built on httpx.

Supports two providers, chosen automatically:

* **OpenRouter** (``OPENROUTER_API_KEY``) — an OpenAI-compatible gateway that can
  route to many models. Preferred when its key is set.
* **Gemini** (``GEMINI_API_KEY``) — Google's Generative Language REST API.

When neither key is configured (or a call fails), every helper returns ``None``
so callers fall back to deterministic local behaviour and the interview flow keeps
working offline / in demos.

The module keeps the historical name ``gemini`` and its public surface
(``is_enabled`` / ``generate_text`` / ``generate_json``) so nothing else needs to
change when the provider switches.
"""

from __future__ import annotations

import json
import re
from typing import Any, Optional

import httpx

from app.core.config import settings

_TIMEOUT = httpx.Timeout(45.0, connect=10.0)

# ── Gemini ──
# Overridable via the GEMINI_MODEL env var so a Google model rename can be
# fixed from the dashboard without a code change / redeploy.
_GEMINI_MODEL = settings.GEMINI_MODEL
_GEMINI_BASE = "https://generativelanguage.googleapis.com/v1beta/models"

# ── OpenRouter (OpenAI-compatible) ──
_OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def _provider() -> Optional[str]:
    """Which backend to use, or ``None`` when no key is configured."""
    if settings.OPENROUTER_API_KEY:
        return "openrouter"
    if settings.GEMINI_API_KEY:
        return "gemini"
    return None


def is_enabled() -> bool:
    """True when some LLM provider is configured."""
    return _provider() is not None


def _strip_code_fences(text: str) -> str:
    """Models often wrap JSON in ```json ... ``` fences — remove them."""
    fenced = re.match(r"^```(?:json)?\s*(.*?)\s*```$", text.strip(), re.DOTALL)
    return fenced.group(1) if fenced else text.strip()


# ─── Gemini transport ────────────────────────────────────────────

def _gemini_extract(payload: dict) -> str:
    try:
        parts = (payload.get("candidates") or [])[0]["content"]["parts"]
        # Skip internal "thinking" parts (Gemini 2.5/3 emit these with
        # thought:true) — only real answer text has a usable value.
        return "".join(p.get("text", "") for p in parts if not p.get("thought")).strip()
    except (KeyError, IndexError, TypeError):
        return ""


async def _gemini_call(
    prompt: str, system: Optional[str], temperature: float, max_tokens: int, json_mode: bool
) -> Optional[str]:
    body: dict[str, Any] = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": temperature,
            # Current Flash models count internal "thinking" tokens against
            # maxOutputTokens, which can consume the whole budget and return
            # empty text. Give headroom AND disable thinking for these short,
            # non-reasoning calls so the model spends tokens on the answer.
            "maxOutputTokens": max(max_tokens, 512),
            "thinkingConfig": {"thinkingBudget": 0},
        },
    }
    if system:
        body["systemInstruction"] = {"parts": [{"text": system}]}
    if json_mode:
        body["generationConfig"]["responseMimeType"] = "application/json"

    url = f"{_GEMINI_BASE}/{_GEMINI_MODEL}:generateContent"
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        resp = await client.post(url, params={"key": settings.GEMINI_API_KEY}, json=body)
        # Older models reject thinkingConfig with a 400 — retry once without it.
        if resp.status_code == 400 and "thinkingConfig" in body["generationConfig"]:
            body["generationConfig"].pop("thinkingConfig", None)
            resp = await client.post(url, params={"key": settings.GEMINI_API_KEY}, json=body)
        resp.raise_for_status()
        return _gemini_extract(resp.json()) or None


# ─── OpenRouter transport ────────────────────────────────────────

def _openrouter_extract(payload: dict) -> str:
    try:
        return (payload["choices"][0]["message"]["content"] or "").strip()
    except (KeyError, IndexError, TypeError):
        return ""


async def _openrouter_call(
    prompt: str, system: Optional[str], temperature: float, max_tokens: int, json_mode: bool
) -> Optional[str]:
    messages: list[dict] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    body: dict[str, Any] = {
        "model": settings.OPENROUTER_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if json_mode:
        body["response_format"] = {"type": "json_object"}

    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        # Attribution headers for OpenRouter (optional, but good practice).
        "HTTP-Referer": (settings.CORS_ORIGINS[0] if settings.CORS_ORIGINS else "http://localhost:5173"),
        "X-Title": settings.APP_NAME,
    }
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        resp = await client.post(_OPENROUTER_URL, headers=headers, json=body)
        resp.raise_for_status()
        return _openrouter_extract(resp.json()) or None


# ─── Dispatch ────────────────────────────────────────────────────

async def _call(
    prompt: str, system: Optional[str], temperature: float, max_tokens: int, json_mode: bool
) -> Optional[str]:
    provider = _provider()
    if provider is None:
        return None
    try:
        if provider == "openrouter":
            return await _openrouter_call(prompt, system, temperature, max_tokens, json_mode)
        return await _gemini_call(prompt, system, temperature, max_tokens, json_mode)
    except Exception as exc:  # network, auth, quota — all non-fatal
        print(f"[WARN] LLM ({provider}) call failed: {exc}")
        return None


# ─── Public API ──────────────────────────────────────────────────

async def generate_text(
    prompt: str,
    *,
    system: Optional[str] = None,
    temperature: float = 0.7,
    max_output_tokens: int = 1024,
) -> Optional[str]:
    """Return generated text, or ``None`` when no provider is available/errored."""
    return await _call(prompt, system, temperature, max_output_tokens, json_mode=False)


async def generate_json(
    prompt: str,
    *,
    system: Optional[str] = None,
    temperature: float = 0.4,
    max_output_tokens: int = 2048,
) -> Optional[Any]:
    """Return parsed JSON from the model, or ``None`` on any failure."""
    raw = await _call(prompt, system, temperature, max_output_tokens, json_mode=True)
    if not raw:
        return None
    try:
        return json.loads(_strip_code_fences(raw))
    except (json.JSONDecodeError, ValueError):
        return None


async def diagnose() -> dict:
    """One live round-trip that surfaces the real error instead of swallowing it.

    Used by the /api/health/ai diagnostic endpoint. Never raises.
    """
    provider = _provider()
    info: dict[str, Any] = {"provider": provider, "model": None, "ok": False, "error": None, "sample": None}
    if provider is None:
        info["error"] = "no provider key configured"
        return info
    info["model"] = settings.OPENROUTER_MODEL if provider == "openrouter" else _GEMINI_MODEL
    try:
        if provider == "openrouter":
            text = await _openrouter_call("Say the single word: pong", None, 0.0, 20, False)
        else:
            text = await _gemini_call("Say the single word: pong", None, 0.0, 20, False)
        info["ok"] = bool(text)
        info["sample"] = (text or "")[:120]
        if not text:
            info["error"] = "call returned empty (see extract/response shape)"
    except httpx.HTTPStatusError as exc:
        info["error"] = f"HTTP {exc.response.status_code}: {exc.response.text[:300]}"
    except Exception as exc:  # noqa: BLE001
        info["error"] = f"{type(exc).__name__}: {str(exc)[:300]}"
    return info
