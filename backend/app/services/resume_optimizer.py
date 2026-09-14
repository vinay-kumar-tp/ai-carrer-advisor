"""AI-assisted resume optimization for a target job.

Given a candidate's resume text and a job context (title / description / skills),
produce a structured optimization report. Uses the shared LLM client when
available and falls back to a deterministic keyword/ATS analysis otherwise, so
the feature always returns a useful result.
"""

from __future__ import annotations

import re

from app.ai import gemini

# Baseline ATS keyword pool used when a job has no explicit skills.
_BASELINE_KEYWORDS = [
    "python", "javascript", "typescript", "react", "node", "sql", "git", "api",
    "rest", "fastapi", "django", "docker", "kubernetes", "aws", "communication",
    "leadership", "problem solving", "agile", "testing", "database", "cloud",
]

_ACTION_VERBS = ("achieved", "managed", "led", "built", "developed", "designed",
                 "improved", "delivered", "launched", "spearheaded", "optimized")


def _tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-zA-Z][a-zA-Z0-9+#.\-]{1,}", (text or "").lower()))


def _keyword_report(resume_text: str, target_terms: list[str]) -> dict:
    text_lower = (resume_text or "").lower()
    terms = [t.lower() for t in target_terms if t] or _BASELINE_KEYWORDS
    matched = sorted({t for t in terms if t in text_lower})
    missing = sorted({t for t in terms if t not in text_lower})
    raw = int((len(matched) / max(len(terms), 1)) * 100)
    score = max(30, min(98, raw))
    return {"match_score": score, "matched_keywords": matched, "missing_keywords": missing}


def _local_report(resume_text: str, job_context: dict) -> dict:
    target = job_context.get("skills") or []
    kw = _keyword_report(resume_text, target)
    text_lower = (resume_text or "").lower()

    gaps = []
    if kw["missing_keywords"]:
        gaps.append(f"Missing relevant keywords: {', '.join(kw['missing_keywords'][:6])}.")
    if not any(v in text_lower for v in _ACTION_VERBS):
        gaps.append("Bullet points lack strong action verbs (e.g. led, built, improved).")
    if len((resume_text or "").split()) < 120:
        gaps.append("Resume is short — expand on projects, impact, and measurable results.")
    if not re.search(r"\d", resume_text or ""):
        gaps.append("Add quantified impact (numbers, %, scale) to demonstrate results.")

    strengths = []
    if kw["matched_keywords"]:
        strengths.append(f"Already covers key skills: {', '.join(kw['matched_keywords'][:6])}.")
    if any(v in text_lower for v in _ACTION_VERBS):
        strengths.append("Uses strong action verbs in experience descriptions.")
    if not strengths:
        strengths.append("Clear, readable structure to build on.")

    title = job_context.get("title") or "the target role"
    tailored_summary = (
        f"Results-driven candidate targeting {title}. "
        f"Strengths in {', '.join(kw['matched_keywords'][:4]) or 'core skills'}; "
        f"recommend emphasising {', '.join(kw['missing_keywords'][:4]) or 'relevant achievements'} "
        "with quantified outcomes."
    )

    rewritten = []
    for kwd in kw["missing_keywords"][:3]:
        rewritten.append(
            f"Consider a bullet showcasing {kwd}: e.g. 'Applied {kwd} to deliver a measurable result "
            "(add the metric).'"
        )

    return {
        "match_score": kw["match_score"],
        "matched_keywords": kw["matched_keywords"],
        "missing_keywords": kw["missing_keywords"],
        "summary": (
            f"Your resume matches about {kw['match_score']}% of what this role emphasises. "
            "Close the gaps below to strengthen alignment."
        ),
        "strengths": strengths,
        "gaps": gaps or ["No major gaps detected — polish for clarity and impact."],
        "tailored_summary": tailored_summary,
        "rewritten_bullets": rewritten or [
            "Lead each bullet with an action verb and end with a quantified result.",
        ],
        "section_suggestions": [
            "Move the most job-relevant experience and skills to the top.",
            "Mirror the exact terminology used in the job description where truthful.",
        ],
        "engine": "local",
    }


async def _ai_report(resume_text: str, job_context: dict) -> dict | None:
    title = job_context.get("title") or ""
    description = job_context.get("description") or ""
    skills = job_context.get("skills") or []
    jd_block = description[:2500] if description else ""
    skills_line = ", ".join(skills) if skills else ""

    schema = """
Return STRICT JSON:
{
  "match_score": 0-100,
  "matched_keywords": ["..."],
  "missing_keywords": ["..."],
  "summary": "2-3 sentence recruiter-voice fit summary",
  "strengths": ["specific strengths vs this job"],
  "gaps": ["specific, actionable gaps to fix"],
  "tailored_summary": "a rewritten 2-3 sentence professional summary tailored to this job",
  "rewritten_bullets": ["3-5 improved, quantified resume bullet points tailored to the job"],
  "section_suggestions": ["structural/keyword suggestions"]
}
Base everything ONLY on the resume text provided; never invent employers, titles, or facts. Suggestions may propose adding measurable detail as placeholders.
"""
    prompt = (
        f"You are an expert technical recruiter and resume coach optimising a candidate's resume "
        f"for this job.\n\nTARGET ROLE: {title}\nKEY SKILLS: {skills_line}\n"
        f"JOB DESCRIPTION:\n{jd_block}\n\nCANDIDATE RESUME TEXT:\n{resume_text[:6000]}\n\n{schema}"
    )
    data = await gemini.generate_json(prompt, temperature=0.3, max_output_tokens=1800)
    if not isinstance(data, dict):
        return None
    # normalise + guard
    def _clamp(v):
        try:
            return max(0, min(100, int(round(float(v)))))
        except (TypeError, ValueError):
            return 0

    def _list(x):
        return [str(i) for i in x][:8] if isinstance(x, list) else []

    return {
        "match_score": _clamp(data.get("match_score")),
        "matched_keywords": _list(data.get("matched_keywords")),
        "missing_keywords": _list(data.get("missing_keywords")),
        "summary": str(data.get("summary") or "").strip(),
        "strengths": _list(data.get("strengths")),
        "gaps": _list(data.get("gaps")),
        "tailored_summary": str(data.get("tailored_summary") or "").strip(),
        "rewritten_bullets": _list(data.get("rewritten_bullets")),
        "section_suggestions": _list(data.get("section_suggestions")),
        "engine": "ai",
    }


async def optimize_resume(resume_text: str, job_context: dict) -> dict:
    """Return a structured optimization report (AI when available, else local)."""
    if resume_text and gemini.is_enabled():
        ai = await _ai_report(resume_text, job_context)
        if ai:
            # ensure keyword lists are populated even if the model omitted them
            if not ai["matched_keywords"] and not ai["missing_keywords"]:
                kw = _keyword_report(resume_text, job_context.get("skills") or [])
                ai["matched_keywords"] = kw["matched_keywords"]
                ai["missing_keywords"] = kw["missing_keywords"]
                if not ai["match_score"]:
                    ai["match_score"] = kw["match_score"]
            return ai
    return _local_report(resume_text, job_context)
