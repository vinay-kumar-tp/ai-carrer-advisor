"""Tailor-to-Job engine for the AI Resume Builder.

Given a resume ``content`` snapshot and a job (title + description + skills),
produce a match breakdown (hard skills / soft skills / title), keyword gaps, and
a list of discrete, reviewable suggestions the user can accept or reject. Each
suggestion targets a specific field in the content snapshot so it can be applied
deterministically. Uses the LLM when available, deterministic logic otherwise.
"""

from __future__ import annotations

import re
import uuid

from app.ai import gemini
from app.services import resume_builder as rb

_SOFT_SKILLS = {
    "communication", "leadership", "teamwork", "collaboration", "problem solving",
    "problem-solving", "time management", "adaptability", "creativity", "critical thinking",
    "ownership", "mentoring", "stakeholder management", "presentation",
}

# Words we ignore when mining keywords from a JD. Beyond grammar glue this also
# covers recruiter filler and seniority words, which are not skills and must never
# be proposed as something to add to a candidate's skill list.
_STOP = {
    "the", "and", "for", "with", "you", "our", "are", "will", "have", "this", "that",
    "your", "work", "role", "team", "job", "who", "all", "can", "not", "but", "from",
    "was", "were", "into", "out", "per", "etc", "eg", "ie", "a", "an", "to", "of", "in",
    "on", "as", "is", "we", "be", "or", "at", "by", "it", "&",
    # recruiter filler / non-skill nouns
    "need", "needs", "needed", "want", "wants", "looking", "seeking", "hiring", "join",
    "senior", "junior", "mid", "lead", "principal", "staff", "intern", "fresher",
    "year", "years", "experience", "experienced", "candidate", "candidates", "applicant",
    "responsibility", "responsibilities", "requirement", "requirements", "qualification",
    "qualifications", "must", "should", "would", "could", "plus", "nice", "bonus",
    "strong", "good", "excellent", "solid", "proven", "ability", "able", "skills",
    "skill", "knowledge", "understanding", "familiarity", "proficiency", "proficient",
    "hands", "using", "use", "used", "including", "such", "other", "more", "most",
    "company", "client", "clients", "customer", "customers", "business", "product",
    "help", "support", "ensure", "across", "within", "well", "also", "day", "days",
    "opportunity", "environment", "culture", "benefits", "salary", "location", "remote",
    "onsite", "hybrid", "fulltime", "part", "time", "apply", "resume", "about", "what",
    "how", "why", "when", "where", "which", "their", "them", "they", "his", "her",
    "you'll", "we're", "etc.", "any", "new", "great", "high", "best", "own", "one",
}

# Recognised multi-word skill phrases worth surfacing as a unit.
_KNOWN_PHRASES = [
    "machine learning", "deep learning", "natural language processing", "computer vision",
    "data engineering", "data pipeline", "data pipelines", "data modelling", "data modeling",
    "ci/cd", "rest api", "rest apis", "graphql", "unit testing", "integration testing",
    "test automation", "distributed systems", "system design", "object oriented",
    "microservices", "model deployment", "model monitoring", "feature engineering",
    "version control", "code review", "cloud computing", "infrastructure as code",
    "continuous integration", "continuous deployment", "message queue", "event driven",
    "agile", "scrum", "kanban", "mlops", "devops", "sre", "etl", "elt",
]

# Single tokens we trust as real technical skills even out of context.
_KNOWN_TOKENS = {
    "python", "java", "javascript", "typescript", "go", "golang", "rust", "c", "c++",
    "c#", "ruby", "php", "scala", "kotlin", "swift", "r", "matlab", "perl", "bash",
    "shell", "powershell", "sql", "nosql", "plsql",
    "react", "angular", "vue", "svelte", "next.js", "nuxt", "node", "node.js", "express",
    "django", "flask", "fastapi", "spring", "rails", "laravel", "dotnet", ".net",
    "html", "css", "sass", "tailwind", "bootstrap", "redux", "jquery",
    "postgresql", "postgres", "mysql", "sqlite", "mongodb", "redis", "cassandra",
    "elasticsearch", "dynamodb", "snowflake", "bigquery", "redshift", "oracle",
    "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ansible", "jenkins",
    "github", "gitlab", "git", "linux", "unix", "nginx", "kafka", "rabbitmq", "spark",
    "hadoop", "airflow", "dbt", "databricks", "prometheus", "grafana", "datadog",
    "pandas", "numpy", "scikit-learn", "sklearn", "tensorflow", "pytorch", "keras",
    "opencv", "huggingface", "langchain", "llm", "nlp", "xgboost",
    "pytest", "jest", "cypress", "selenium", "playwright", "junit", "mocha",
    "jira", "confluence", "figma", "tableau", "powerbi", "excel", "looker",
    "graphql", "grpc", "websocket", "oauth", "jwt", "api", "sdk", "cli",
    "monitoring", "observability", "logging", "caching", "scalability", "security",
    "automation", "infrastructure", "cloud", "serverless", "lambda", "microservices",
    "testing", "debugging", "profiling", "optimization", "refactoring",
}

_PUNCT = ".,;:!?()[]{}\"'`/\\|*"


def _normalize(token: str) -> str:
    """Trim stray JD punctuation while keeping meaningful symbols (c++, ci/cd, .net)."""
    token = token.strip().lower()
    token = token.strip(_PUNCT)
    # Re-attach known symbol-bearing forms that the strip above may have damaged.
    return token.strip()


def _tokens(text: str) -> list[str]:
    raw = re.findall(r"[a-zA-Z][a-zA-Z0-9+#.\-/]{1,}", (text or "").lower())
    return [t for t in (_normalize(r) for r in raw) if t]


def _is_skill_like(token: str) -> bool:
    """Only accept tokens we can defend as a skill, so gaps stay actionable."""
    if len(token) < 2 or token in _STOP:
        return False
    if token in _KNOWN_TOKENS or token in _SOFT_SKILLS:
        return True
    # Symbol-bearing tech terms (ci/cd, c++, node.js, .net) are usually real.
    if any(ch in token for ch in "+#/.") and len(token) >= 3:
        return True
    return False


def _phrases(text: str, extra_skills: list[str] | None = None) -> list[str]:
    """Extract defensible skill keywords from a JD, in priority order.

    Explicit ``extra_skills`` (the job's own required-skill list) rank first, then
    recognised multi-word phrases, then single tokens we can vouch for. Generic
    recruiter prose is dropped so the "missing keywords" list stays actionable.
    """
    lowered = (text or "").lower()
    seen: list[str] = []

    def add(term: str):
        term = _normalize(term)
        if term and term not in seen and len(seen) < 40:
            seen.append(term)

    for skill in extra_skills or []:
        add(skill)

    for phrase in _KNOWN_PHRASES:
        if phrase in lowered:
            add(phrase)

    for token in _tokens(lowered):
        if _is_skill_like(token):
            add(token)

    # Drop single tokens already covered by an accepted multi-word phrase.
    phrase_words = {w for s in seen if " " in s for w in s.split()}
    return [s for s in seen if " " in s or s not in phrase_words]


def _resume_terms(content: dict) -> set[str]:
    text = rb._plain(content) + " " + " ".join(content.get("skills") or []) + " " + (content.get("headline") or "")
    return set(_tokens(text))


def _match_breakdown(content: dict, job: dict) -> dict:
    jd = f"{job.get('title', '')} {job.get('description', '')} {' '.join(job.get('skills') or [])}"
    jd_terms = _phrases(jd, job.get("skills") or [])
    resume_terms = _resume_terms(content)
    resume_text = rb._plain(content).lower()

    hard_targets = [t for t in jd_terms if t not in _SOFT_SKILLS]
    soft_targets = [t for t in jd_terms if t in _SOFT_SKILLS] or ["communication", "teamwork", "leadership"]

    def covered(term: str) -> bool:
        return term in resume_text or all(w in resume_terms for w in term.split())

    hard_hit = [t for t in hard_targets if covered(t)]
    hard_miss = [t for t in hard_targets if not covered(t)]
    soft_hit = [t for t in soft_targets if covered(t)]

    hard_pct = int(round(100 * len(hard_hit) / max(len(hard_targets), 1)))
    soft_pct = int(round(100 * len(soft_hit) / max(len(soft_targets), 1)))

    # Title match: overlap between job title tokens and resume headline/roles.
    title_tokens = [t for t in _tokens(job.get("title", "")) if t not in _STOP]
    role_text = " ".join(
        [content.get("headline") or ""] + [j.get("role", "") for j in (content.get("work_experiences") or [])]
    ).lower()
    title_hit = [t for t in title_tokens if t in role_text]
    title_pct = int(round(100 * len(title_hit) / max(len(title_tokens), 1))) if title_tokens else 0

    overall = int(round(0.55 * hard_pct + 0.2 * soft_pct + 0.25 * title_pct))
    return {
        "overall": max(0, min(100, overall)),
        "hard_skills": hard_pct,
        "soft_skills": soft_pct,
        "title_match": title_pct,
        "keyword_gaps": {
            "hard_skills": hard_miss[:12],
            "soft_skills": [t for t in soft_targets if t not in soft_hit][:8],
        },
        "matched": hard_hit[:16],
    }


def _new_id() -> str:
    return uuid.uuid4().hex[:12]


def _local_suggestions(content: dict, job: dict, breakdown: dict) -> list[dict]:
    """Deterministic, reviewable suggestions with explicit content targets."""
    suggestions: list[dict] = []
    title = job.get("title") or "the role"
    hard_miss = breakdown["keyword_gaps"]["hard_skills"]

    # 1) Professional summary tailored to the role.
    matched = breakdown.get("matched") or []
    current_about = (content.get("about") or "").strip()
    proposed_summary = (
        f"{title}-focused professional with hands-on experience in "
        f"{', '.join(matched[:4]) or 'the core skills for this role'}. "
        f"Proven ability to deliver measurable results; strengthening alignment with "
        f"{', '.join(hard_miss[:3]) or 'the role priorities'} through applied project work."
    )
    needs_detail = not current_about
    suggestions.append({
        "id": _new_id(),
        "type": "summary",
        "section": "SUMMARY",
        "kind": "CONTENT",
        "target": {"field": "about"},
        "original": current_about or "empty",
        "proposed": proposed_summary if not needs_detail else "empty",
        "status": "pending",
        "needs_detail": needs_detail,
        "detail_prompt": "Which relevant role, strengths, and verified experience should this summary emphasise?",
        "detail_chip": (job.get("description") or "").strip()[:60] or title,
        "rationale": "A targeted summary tailored to the job improves recruiter and ATS match.",
    })

    # 2) Skills to add (only ones truthfully addable are proposed as ADD candidates).
    if hard_miss:
        suggestions.append({
            "id": _new_id(),
            "type": "skills",
            "section": "SKILLS",
            "kind": "KEYWORDS",
            "target": {"field": "skills"},
            "original": ", ".join(content.get("skills") or []) or "empty",
            "proposed_add": hard_miss[:8],
            "status": "pending",
            "needs_detail": False,
            "rationale": "These job keywords are missing from your skills. Add the ones you genuinely have.",
        })

    # 3) Bullet rewrites for weak/unquantified bullets.
    weak_targets = []
    for gi, group in enumerate(("work_experiences", "projects", "positions")):
        for ei, entry in enumerate(content.get(group) or []):
            for bi, bullet in enumerate(entry.get("highlights") or []):
                if not re.search(r"\d", bullet) or bullet.lower().startswith(("responsible for", "worked on", "helped")):
                    weak_targets.append((group, ei, bi, bullet))
    for group, ei, bi, bullet in weak_targets[:3]:
        first = bullet.strip().split()
        verb = "Delivered" if not first else first[0].capitalize()
        proposed = re.sub(r"^(responsible for|worked on|helped with|involved in)\s*", "", bullet, flags=re.I)
        proposed = f"{verb} {proposed[0].lower() + proposed[1:] if proposed else 'measurable impact'} — add a metric (e.g. %, count, time saved)."
        suggestions.append({
            "id": _new_id(),
            "type": "bullet",
            "section": "EXPERIENCE",
            "kind": "REWRITE",
            "target": {"group": group, "entry_index": ei, "bullet_index": bi},
            "original": bullet,
            "proposed": proposed,
            "status": "pending",
            "needs_detail": False,
            "rationale": "Lead with an action verb and quantify the outcome for stronger impact.",
        })

    return suggestions


async def _ai_suggestions(content: dict, job: dict, breakdown: dict) -> list[dict] | None:
    resume_text = rb._plain(content)[:5000]
    if not resume_text.strip():
        return None
    schema = """
Return STRICT JSON: {"suggestions":[
  {"type":"summary","proposed":"a 2-3 sentence tailored professional summary"},
  {"type":"bullet","original":"<an EXACT bullet from the resume>","proposed":"<stronger, quantified rewrite>"}
]}
Rules: base everything ONLY on the resume text; never invent employers, titles or achievements.
Rewrites may include placeholders like (add metric). Max 5 suggestions.
"""
    prompt = (
        f"You are an expert resume coach tailoring a resume to a job.\n"
        f"JOB TITLE: {job.get('title','')}\nJOB DESCRIPTION:\n{(job.get('description') or '')[:2500]}\n\n"
        f"RESUME TEXT:\n{resume_text}\n\n{schema}"
    )
    data = await gemini.generate_json(prompt, temperature=0.3, max_output_tokens=1500)
    if not isinstance(data, dict) or not isinstance(data.get("suggestions"), list):
        return None

    out: list[dict] = []
    # map AI bullet rewrites back onto exact content targets
    bullet_index = _build_bullet_index(content)
    for item in data["suggestions"][:5]:
        if not isinstance(item, dict):
            continue
        stype = item.get("type")
        if stype == "summary" and item.get("proposed"):
            out.append({
                "id": _new_id(), "type": "summary", "section": "SUMMARY", "kind": "CONTENT",
                "target": {"field": "about"}, "original": (content.get("about") or "").strip() or "empty",
                "proposed": str(item["proposed"]).strip(), "status": "pending", "needs_detail": False,
                "rationale": "AI-tailored professional summary for this job.",
            })
        elif stype == "bullet" and item.get("original") and item.get("proposed"):
            target = bullet_index.get(str(item["original"]).strip().lower())
            if target:
                out.append({
                    "id": _new_id(), "type": "bullet", "section": "EXPERIENCE", "kind": "REWRITE",
                    "target": target, "original": item["original"], "proposed": str(item["proposed"]).strip(),
                    "status": "pending", "needs_detail": False,
                    "rationale": "AI-improved, quantified bullet aligned to the job.",
                })
    # Always include the missing-skills keyword suggestion (deterministic).
    hard_miss = breakdown["keyword_gaps"]["hard_skills"]
    if hard_miss:
        out.append({
            "id": _new_id(), "type": "skills", "section": "SKILLS", "kind": "KEYWORDS",
            "target": {"field": "skills"}, "original": ", ".join(content.get("skills") or []) or "empty",
            "proposed_add": hard_miss[:8], "status": "pending", "needs_detail": False,
            "rationale": "Job keywords missing from your skills — add the ones you genuinely have.",
        })
    return out or None


def _build_bullet_index(content: dict) -> dict:
    index: dict[str, dict] = {}
    for group in ("work_experiences", "projects", "positions"):
        for ei, entry in enumerate(content.get(group) or []):
            for bi, bullet in enumerate(entry.get("highlights") or []):
                index[str(bullet).strip().lower()] = {"group": group, "entry_index": ei, "bullet_index": bi}
    return index


async def build_tailoring(content: dict, job: dict) -> dict:
    """Full tailoring payload: match breakdown + suggestions."""
    breakdown = _match_breakdown(content, job)
    suggestions = None
    if gemini.is_enabled():
        try:
            suggestions = await _ai_suggestions(content, job, breakdown)
        except Exception:
            suggestions = None
    if not suggestions:
        suggestions = _local_suggestions(content, job, breakdown)
    return {
        "job": {"title": job.get("title", ""), "description": (job.get("description") or "")[:600]},
        "match": breakdown,
        "suggestions": suggestions,
    }


def apply_suggestion(content: dict, suggestion: dict, user_detail: str | None = None) -> dict:
    """Apply an accepted suggestion to the content snapshot (returns new content)."""
    content = dict(content or {})
    stype = suggestion.get("type")
    target = suggestion.get("target") or {}

    if stype == "summary":
        proposed = suggestion.get("proposed") or ""
        if user_detail:
            proposed = f"{proposed} {user_detail}".strip() if proposed and proposed != "empty" else user_detail
        content["about"] = proposed
    elif stype == "skills":
        existing = list(content.get("skills") or [])
        lowered = {s.lower() for s in existing}
        for skill in suggestion.get("proposed_add") or []:
            if skill.lower() not in lowered:
                existing.append(skill)
                lowered.add(skill.lower())
        content["skills"] = existing
    elif stype == "bullet":
        group = target.get("group")
        ei = target.get("entry_index")
        bi = target.get("bullet_index")
        entries = list(content.get(group) or [])
        if isinstance(ei, int) and 0 <= ei < len(entries):
            entry = dict(entries[ei])
            highlights = list(entry.get("highlights") or [])
            if isinstance(bi, int) and 0 <= bi < len(highlights):
                highlights[bi] = suggestion.get("proposed") or highlights[bi]
                entry["highlights"] = highlights
                entries[ei] = entry
                content[group] = entries
    return content
