"""Multi-language code judge for Code Quest.

Each run happens in a throwaway temp directory as a separate OS process with a
wall-clock timeout and capped output. Verdicts follow the usual competitive
programming vocabulary so the UI can speak the language students already know.

SECURITY NOTE
-------------
This executes arbitrary student code as the same OS user as the API process.
That is acceptable for a local, single-user development setup, which is what
this project targets. Before exposing Code Quest to real users the runners must
be moved behind a real sandbox (container per submission, seccomp/nsjail, or a
hosted execution API) — a subprocess boundary alone does not stop file access
or outbound network calls.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from typing import Optional

MAX_OUTPUT_CHARS = 64_000
COMPILE_TIMEOUT_S = 20.0

# Verdicts
ACCEPTED = "accepted"
WRONG_ANSWER = "wrong_answer"
RUNTIME_ERROR = "runtime_error"
TIME_LIMIT = "time_limit"
COMPILE_ERROR = "compile_error"


@dataclass
class LanguageSpec:
    key: str
    label: str
    extension: str
    filename: Optional[str] = None          # fixed name when the toolchain demands one
    compile_cmd: Optional[list[str]] = None  # {src} / {out} / {dir} placeholders
    run_cmd: list[str] = field(default_factory=list)
    comment: str = "#"


def _python_executable() -> str:
    return sys.executable or "python"


LANGUAGES: dict[str, LanguageSpec] = {
    "python": LanguageSpec(
        key="python",
        label="Python",
        extension=".py",
        run_cmd=[_python_executable(), "-I", "-S", "{src}"],
        comment="#",
    ),
    "javascript": LanguageSpec(
        key="javascript",
        label="JavaScript",
        extension=".js",
        run_cmd=["node", "{src}"],
        comment="//",
    ),
    "cpp": LanguageSpec(
        key="cpp",
        label="C++",
        extension=".cpp",
        compile_cmd=["g++", "-std=c++17", "-O2", "-o", "{out}", "{src}"],
        run_cmd=["{out}"],
        comment="//",
    ),
    "java": LanguageSpec(
        key="java",
        label="Java",
        extension=".java",
        filename="Main.java",
        compile_cmd=["javac", "-d", "{dir}", "{src}"],
        run_cmd=["java", "-cp", "{dir}", "Main"],
        comment="//",
    ),
}


def available_languages() -> list[dict]:
    """Only advertise toolchains that actually exist on this machine."""
    out = []
    for spec in LANGUAGES.values():
        binary = (spec.compile_cmd or spec.run_cmd)[0]
        ok = binary.startswith("{") or shutil.which(binary) is not None or os.path.exists(binary)
        if ok:
            out.append({"key": spec.key, "label": spec.label})
    return out


def _truncate(text: str) -> str:
    if len(text) <= MAX_OUTPUT_CHARS:
        return text
    return text[:MAX_OUTPUT_CHARS] + "\n... output truncated ..."


def normalize_output(text: str) -> str:
    """Trailing whitespace and line endings must not decide a verdict."""
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    while lines and lines[-1].strip() == "":
        lines.pop()
    return "\n".join(line.rstrip() for line in lines)


@dataclass
class CaseOutcome:
    verdict: str
    stdout: str = ""
    stderr: str = ""
    runtime_ms: int = 0


@dataclass
class Workspace:
    """A compiled (or interpreted) program ready to be fed many test cases."""

    directory: str
    run_cmd: list[str]
    compile_error: Optional[str] = None

    def cleanup(self) -> None:
        shutil.rmtree(self.directory, ignore_errors=True)


def prepare(code: str, language: str) -> Workspace:
    spec = LANGUAGES.get(language)
    if spec is None:
        raise ValueError(f"Unsupported language: {language}")

    directory = tempfile.mkdtemp(prefix="cq_")
    source_name = spec.filename or f"solution{spec.extension}"
    source_path = os.path.join(directory, source_name)
    with open(source_path, "w", encoding="utf-8") as handle:
        handle.write(code)

    binary_path = os.path.join(directory, "program.exe" if os.name == "nt" else "program")

    def fill(parts: list[str]) -> list[str]:
        return [p.format(src=source_path, out=binary_path, dir=directory) for p in parts]

    if spec.compile_cmd:
        try:
            proc = subprocess.run(
                fill(spec.compile_cmd),
                capture_output=True,
                text=True,
                timeout=COMPILE_TIMEOUT_S,
                cwd=directory,
            )
        except subprocess.TimeoutExpired:
            return Workspace(directory, [], compile_error="Compilation timed out.")
        except FileNotFoundError:
            return Workspace(directory, [], compile_error=f"{spec.label} toolchain is not installed on the server.")

        if proc.returncode != 0:
            message = _truncate((proc.stderr or proc.stdout or "Compilation failed.").strip())
            return Workspace(directory, [], compile_error=message)

    return Workspace(directory, fill(spec.run_cmd))


def run_case(workspace: Workspace, stdin_text: str, time_limit_ms: int) -> CaseOutcome:
    started = time.perf_counter()
    try:
        proc = subprocess.run(
            workspace.run_cmd,
            input=stdin_text,
            capture_output=True,
            text=True,
            timeout=max(time_limit_ms, 1000) / 1000.0,
            cwd=workspace.directory,
        )
    except subprocess.TimeoutExpired:
        return CaseOutcome(TIME_LIMIT, runtime_ms=time_limit_ms)
    except FileNotFoundError as exc:
        return CaseOutcome(RUNTIME_ERROR, stderr=f"Runtime not available: {exc}")

    runtime_ms = int((time.perf_counter() - started) * 1000)
    if proc.returncode != 0:
        return CaseOutcome(
            RUNTIME_ERROR,
            stdout=_truncate(proc.stdout or ""),
            stderr=_truncate((proc.stderr or "").strip()) or f"Process exited with code {proc.returncode}.",
            runtime_ms=runtime_ms,
        )

    return CaseOutcome(
        ACCEPTED,
        stdout=_truncate(proc.stdout or ""),
        stderr=_truncate((proc.stderr or "").strip()),
        runtime_ms=runtime_ms,
    )


def judge(
    code: str,
    language: str,
    cases: list[dict],
    time_limit_ms: int = 5000,
    stop_on_first_failure: bool = True,
    reveal_hidden: bool = False,
) -> dict:
    """Compile once, then run every case.

    ``cases`` entries use ``{"input", "expected_output", "is_sample"}``. Payloads
    for non-sample cases are withheld from the response unless ``reveal_hidden``.
    """
    if not code.strip():
        return {
            "verdict": COMPILE_ERROR,
            "passed": 0,
            "total": len(cases),
            "results": [],
            "error": "Write some code before running.",
            "runtime_ms": 0,
        }

    try:
        workspace = prepare(code, language)
    except ValueError as exc:
        return {
            "verdict": COMPILE_ERROR,
            "passed": 0,
            "total": len(cases),
            "results": [],
            "error": str(exc),
            "runtime_ms": 0,
        }

    try:
        if workspace.compile_error:
            return {
                "verdict": COMPILE_ERROR,
                "passed": 0,
                "total": len(cases),
                "results": [],
                "error": workspace.compile_error,
                "runtime_ms": 0,
            }

        results: list[dict] = []
        passed = 0
        slowest = 0
        overall = ACCEPTED
        error_message = ""

        for index, case in enumerate(cases):
            is_sample = bool(case.get("is_sample"))
            expected = normalize_output(str(case.get("expected_output", "")))
            outcome = run_case(workspace, str(case.get("input", "")), time_limit_ms)
            slowest = max(slowest, outcome.runtime_ms)

            if outcome.verdict == ACCEPTED:
                got = normalize_output(outcome.stdout)
                verdict = ACCEPTED if got == expected else WRONG_ANSWER
            else:
                got = normalize_output(outcome.stdout)
                verdict = outcome.verdict

            if verdict == ACCEPTED:
                passed += 1
            elif overall == ACCEPTED:
                overall = verdict
                error_message = outcome.stderr

            entry = {
                "index": index + 1,
                "is_sample": is_sample,
                "verdict": verdict,
                "runtime_ms": outcome.runtime_ms,
            }
            if is_sample or reveal_hidden:
                entry.update(
                    {
                        "input": str(case.get("input", "")),
                        "expected": expected,
                        "got": got,
                        "stderr": outcome.stderr,
                    }
                )
            elif verdict in (RUNTIME_ERROR, TIME_LIMIT):
                entry["stderr"] = outcome.stderr
            results.append(entry)

            if verdict != ACCEPTED and stop_on_first_failure:
                break

        return {
            "verdict": overall if passed == len(cases) else (overall if overall != ACCEPTED else WRONG_ANSWER),
            "passed": passed,
            "total": len(cases),
            "results": results,
            "error": error_message,
            "runtime_ms": slowest,
        }
    finally:
        workspace.cleanup()


def run_free(code: str, language: str, stdin_text: str, time_limit_ms: int = 5000) -> dict:
    """Execute once against arbitrary input (the "Run" button with custom input)."""
    try:
        workspace = prepare(code, language)
    except ValueError as exc:
        return {"verdict": COMPILE_ERROR, "stdout": "", "stderr": str(exc), "runtime_ms": 0}

    try:
        if workspace.compile_error:
            return {"verdict": COMPILE_ERROR, "stdout": "", "stderr": workspace.compile_error, "runtime_ms": 0}
        outcome = run_case(workspace, stdin_text, time_limit_ms)
        return {
            "verdict": outcome.verdict,
            "stdout": outcome.stdout,
            "stderr": outcome.stderr,
            "runtime_ms": outcome.runtime_ms,
        }
    finally:
        workspace.cleanup()
