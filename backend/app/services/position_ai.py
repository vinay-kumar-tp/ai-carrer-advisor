"""Position AI — Skill Gap & Fit Analyzer.

Compares a candidate's profile skills against one or more target job
descriptions (saved job listings and/or pasted free text), extracting the
required skills from each JD and computing a readiness/match score.

Extraction prefers the LLM (via ``app.ai.gemini``) for pasted free text where
skills aren't already structured, but every code path has a deterministic
fallback so the feature keeps working with no API key configured — mirrors
the pattern in ``app.services.resume_optimizer``.
"""

from __future__ import annotations

import re
from typing import Any, Optional

from app.ai import gemini

# A small deterministic keyword bank used as a fallback JD-skill extractor and
# to catch common skills the LLM might phrase differently than the profile.
_SKILL_BANK = [
    "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Go", "Rust", "Ruby", "PHP", "Kotlin", "Swift",
    "React", "Angular", "Vue", "Next.js", "Node.js", "Express", "Django", "Flask", "FastAPI", "Spring Boot",
    "HTML", "CSS", "Tailwind", "Bootstrap", "Redux", "GraphQL", "REST APIs", "gRPC",
    "SQL", "MySQL", "PostgreSQL", "MongoDB", "Redis", "SQLite", "Oracle", "NoSQL",
    "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform", "Jenkins", "CI/CD", "Linux", "Git", "GitHub",
    "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "NLP", "Computer Vision", "Data Analysis",
    "Pandas", "NumPy", "Scikit-learn", "Power BI", "Tableau", "Excel", "Business Intelligence",
    "Communication", "Team leadership", "Effective communication", "Problem solving", "AutoCAD",
    "Mechanical engineering", "Data structures", "Algorithms", "Agile", "Scrum", "Testing", "Unit Testing",
    "Microservices", "System Design", "OOP", "Networking", "Cybersecurity",
]

_SKILL_LOOKUP = {s.lower(): s for s in _SKILL_BANK}


def _norm(text: str) -> str:
    return re.sub(r"[^a-z0-9+#. ]", "", text.lower()).strip()


def extract_skills_local(jd_text: str) -> list[str]:
    """Deterministic keyword-bank extraction — the no-AI-key fallback."""
    if not jd_text:
        return []
    hay = _norm(jd_text)
    found: list[str] = []
    for key, label in _SKILL_LOOKUP.items():
        pattern = r"(?<![a-z0-9])" + re.escape(key) + r"(?![a-z0-9])"
        if re.search(pattern, hay):
            found.append(label)
    return found


async def extract_skills_ai(jd_text: str) -> Optional[list[str]]:
    """LLM-based extraction of technical, tool, and soft skills from JD text."""
    if not jd_text.strip() or not gemini.is_enabled():
        return None

    schema = """Return STRICT JSON:
{ "skills": ["..."] }
List every distinct technical skill, tool, platform, framework, language, and soft skill
required or preferred by this job description. Use concise, conventional names
(e.g. "REST APIs" not "restful api development"). Do not invent skills that
aren't implied by the text."""
    prompt = f"You are an expert technical recruiter extracting a skills checklist from a job description.\n\nJOB DESCRIPTION:\n{jd_text[:4000]}\n\n{schema}"

    data = await gemini.generate_json(prompt, temperature=0.2, max_output_tokens=800)
    if not isinstance(data, dict):
        return None
    skills = data.get("skills")
    if not isinstance(skills, list):
        return None
    cleaned = [str(s).strip() for s in skills if str(s).strip()]
    return cleaned[:40] or None


async def extract_jd_skills(jd_text: str) -> list[str]:
    """Extract required skills from free JD text, AI first, local fallback."""
    ai_skills = await extract_skills_ai(jd_text)
    if ai_skills:
        return ai_skills
    return extract_skills_local(jd_text)


def _skill_key(name: str) -> str:
    return re.sub(r"[^a-z0-9+#]", "", name.lower())


def compute_gap(
    profile_skills: list[str],
    jd_skill_lists: list[list[str]],
    jd_titles: Optional[list[str]] = None,
) -> dict[str, Any]:
    """Set-difference gap computation across one or more JD skill lists.

    ``jd_skill_lists`` is a list where each item is the skill list of one
    target JD; ``missing_skills`` reports, per missing skill, how many of the
    selected JDs require it (drives the "2/2 JDs" style badges in the UI) plus
    the first JD title that requires it (shown under the chip).
    """
    profile_keys = {_skill_key(s) for s in profile_skills}
    titles = jd_titles or []

    # Union of all required skills across JDs, deduped by normalized key but
    # keeping the first human-readable label we saw.
    label_by_key: dict[str, str] = {}
    jd_count_by_key: dict[str, int] = {}
    first_title_by_key: dict[str, str] = {}
    total_jds = len(jd_skill_lists) or 0

    for index, jd_skills in enumerate(jd_skill_lists):
        seen_in_this_jd: set[str] = set()
        for skill in jd_skills:
            key = _skill_key(skill)
            if not key or key in seen_in_this_jd:
                continue
            seen_in_this_jd.add(key)
            label_by_key.setdefault(key, skill.strip())
            jd_count_by_key[key] = jd_count_by_key.get(key, 0) + 1
            if key not in first_title_by_key:
                first_title_by_key[key] = titles[index] if index < len(titles) else ""

    required_keys = set(label_by_key.keys())
    matched_keys = required_keys & profile_keys
    missing_keys = required_keys - profile_keys

    matched_skills = [label_by_key[k] for k in matched_keys]
    missing_skills = sorted(
        (
            {
                "skill": label_by_key[k],
                "jd_count": jd_count_by_key.get(k, 0),
                "total_jds": total_jds,
                "top_jd_title": first_title_by_key.get(k, ""),
            }
            for k in missing_keys
        ),
        key=lambda item: (-item["jd_count"], item["skill"].lower()),
    )

    if required_keys:
        match_percentage = round(len(matched_keys) / len(required_keys) * 100)
    else:
        match_percentage = 0

    return {
        "match_percentage": match_percentage,
        "matched_skills": sorted(matched_skills, key=str.lower),
        "missing_skills": missing_skills,
    }
