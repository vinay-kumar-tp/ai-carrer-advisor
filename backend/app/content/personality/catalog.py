"""Form registry + deterministic OCEAN scoring + workplace insights.

Scoring is exact per the psychometric key (never AI-generated):
  * reverse-key negatively-keyed items (6 - response)
  * raw = sum of item scores in a trait
  * percentage = (raw - min) / (max - min) * 100
  * level: Low < 35, Moderate 35–65, High > 65
"""

from __future__ import annotations

from functools import lru_cache

from app.content.personality import bfi44, ipip120
from app.content.personality.framework import TRAIT_LABELS, TRAITS, Form

_BUILDERS = {"bfi44": bfi44.form, "ipip120": ipip120.form}


@lru_cache(maxsize=None)
def get_form(key: str) -> Form:
    if key not in _BUILDERS:
        raise KeyError(f"unknown personality form: {key}")
    return _BUILDERS[key]()


def list_forms() -> list[dict]:
    out = []
    for key in ("bfi44", "ipip120"):
        f = get_form(key)
        out.append({
            "key": f.key,
            "name": f.name,
            "short_name": f.short_name,
            "description": f.description,
            "est_minutes": f.est_minutes,
            "total_questions": f.total_questions,
        })
    return out


def level_for(pct: float) -> str:
    if pct < 35:
        return "Low"
    if pct <= 65:
        return "Moderate"
    return "High"


def score_form(key: str, responses: list[int]) -> dict:
    """Deterministically score a completed form.

    ``responses`` is a list of 1–5 integers, one per item in form order.
    """
    form = get_form(key)
    if len(responses) != form.total_questions:
        raise ValueError(
            f"expected {form.total_questions} responses, got {len(responses)}"
        )

    bounds = form.trait_bounds()
    raw: dict[str, int] = {t: 0 for t in TRAITS}
    for item, resp in zip(form.items, responses):
        raw[item.trait] += item.score(resp)

    scores: dict[str, dict] = {}
    for t in TRAITS:
        b = bounds[t]
        span = b["max_score"] - b["min_score"]
        pct = round(((raw[t] - b["min_score"]) / span) * 100, 1) if span else 0.0
        scores[t] = {
            "raw_score": raw[t],
            "min_score": b["min_score"],
            "max_score": b["max_score"],
            "percentage": pct,
            "level": level_for(pct),
        }
    return scores


# ─── Compliance monitoring ───────────────────────────────────────

def check_compliance(responses: list[int], max_uniform_run: int = 15) -> dict:
    """Flag long uniform runs (potential random/straight-line answering)."""
    longest = 0
    current = 0
    prev = None
    for r in responses:
        if r == prev:
            current += 1
        else:
            current = 1
            prev = r
        longest = max(longest, current)

    neutral = sum(1 for r in responses if r == 3)
    flagged = longest > max_uniform_run
    return {
        "status": "Flagged" if flagged else "Passed",
        "longest_uniform_run": longest,
        "neutral_responses": neutral,
        "neutral_ratio": round(neutral / len(responses), 3) if responses else 0.0,
        "notes": (
            f"{longest} consecutive identical answers exceed the {max_uniform_run}-item threshold."
            if flagged else "Response pattern within normal variation."
        ),
    }


# ─── Workplace behavioural insights (deterministic, from levels) ─

_STRENGTHS = {
    "openness": {
        "High": "Brings creativity and openness to new ideas and approaches.",
        "Moderate": "Balances fresh thinking with practical, proven methods.",
        "Low": "Prefers reliable, established methods and consistent execution.",
    },
    "conscientiousness": {
        "High": "Highly organized, dependable, and thorough in following through.",
        "Moderate": "Dependable while staying flexible when priorities shift.",
        "Low": "Comfortable with flexibility and improvisation under changing plans.",
    },
    "extraversion": {
        "High": "Energizes groups, communicates readily, and takes initiative socially.",
        "Moderate": "Adapts between collaborative and independent work as needed.",
        "Low": "Works well independently with focused, deep concentration.",
    },
    "agreeableness": {
        "High": "Collaborative, empathetic, and skilled at building trust.",
        "Moderate": "Cooperative while able to hold a position when it matters.",
        "Low": "Direct and objective, comfortable with candid, tough calls.",
    },
    "neuroticism": {
        "Low": "Emotionally resilient and steady under pressure.",
        "Moderate": "Generally composed with normal sensitivity to stress.",
        "High": "Attuned to risks and emotionally aware of team dynamics.",
    },
}

_CHALLENGES = {
    "openness": {
        "Low": "May resist novel approaches or large changes to routine.",
        "High": "May lose interest in repetitive or highly structured tasks.",
    },
    "conscientiousness": {
        "Low": "May need support with structure, deadlines, and follow-through.",
        "High": "May over-plan or set exacting standards under time pressure.",
    },
    "extraversion": {
        "Low": "May under-communicate progress or avoid group visibility.",
        "High": "May dominate discussions or prefer talking over reflecting.",
    },
    "agreeableness": {
        "Low": "May come across as blunt in sensitive conversations.",
        "High": "May avoid necessary conflict or over-accommodate others.",
    },
    "neuroticism": {
        "High": "May feel stress acutely; benefits from clear expectations.",
    },
}


def _team_style(levels: dict[str, str]) -> str:
    e = levels["extraversion"]
    a = levels["agreeableness"]
    c = levels["conscientiousness"]
    if e == "High" and a == "High":
        return "A natural connector — energizes the team and builds consensus across people."
    if e == "Low" and c == "High":
        return "A focused, independent contributor who delivers reliable work with minimal oversight."
    if a == "High" and c == "High":
        return "A dependable collaborator who supports others while consistently meeting commitments."
    if e == "High" and c == "Low":
        return "An energetic idea-generator who thrives with a structured teammate to execute plans."
    return "A balanced contributor who adapts their style to what the team and task require."


def build_insights(scores: dict[str, dict]) -> dict:
    levels = {t: scores[t]["level"] for t in TRAITS}

    strengths: list[str] = []
    challenges: list[str] = []
    for t in TRAITS:
        lvl = levels[t]
        s = _STRENGTHS.get(t, {}).get(lvl)
        if s:
            strengths.append(s)
        ch = _CHALLENGES.get(t, {}).get(lvl)
        if ch:
            challenges.append(ch)

    # keep the most salient few, prioritising extreme levels
    return {
        "key_strengths": strengths[:4],
        "potential_challenges": challenges[:3] or ["No notable behavioural risk flags from this profile."],
        "team_collaboration_style": _team_style(levels),
    }
