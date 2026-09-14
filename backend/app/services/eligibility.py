"""System-checked eligibility + application auto-fill for the Job Board.

Everything here is deterministic and reads only from the profile aggregate
returned by ``profile._build_aggregate`` — no AI, no external calls. Each job
carries an ``eligibility`` list of criteria; :func:`evaluate` checks each one
against the candidate and returns a per-criterion verdict so the UI can show
exactly which requirements are met or missed.
"""

from __future__ import annotations

import datetime
import re
from typing import Any, Optional


# ─── Small parsing helpers ───────────────────────────────────────

def _num(value: Any) -> Optional[float]:
    """Best-effort numeric parse from ints/floats/strings ('8.2 CGPA')."""
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    match = re.search(r"-?\d+(?:\.\d+)?", str(value))
    return float(match.group()) if match else None


def _norm(text: Any) -> str:
    return re.sub(r"[^a-z0-9+#]", "", str(text or "").lower())


def _year(value: Any) -> Optional[int]:
    match = re.search(r"(19|20)\d{2}", str(value or ""))
    return int(match.group()) if match else None


# ─── Profile -> normalized facts ─────────────────────────────────

def _best_cgpa(aggregate: dict) -> Optional[float]:
    """Highest CGPA across education rows, normalized to a /10 scale."""
    best: Optional[float] = None
    for edu in aggregate.get("educations") or []:
        cgpa = _num(edu.get("cgpa"))
        if cgpa is None:
            continue
        scale = _num(edu.get("cgpa_scale")) or 10.0
        if scale and scale > 0:
            normalized = cgpa / scale * 10.0
        else:
            normalized = cgpa
        if best is None or normalized > best:
            best = round(normalized, 2)
    # Fall back to the top-level profile cgpa (already /10 in this app).
    if best is None:
        top = _num(aggregate.get("basic", {}).get("cgpa"))
        if top is not None:
            best = top
    return best


def _max_backlogs(aggregate: dict) -> int:
    total = 0
    for edu in aggregate.get("educations") or []:
        total = max(total, int(_num(edu.get("total_backlogs")) or 0))
    return total


def _months_between(start: str, end: str, is_current: bool) -> int:
    """Rough months of experience from free-form 'Mon YYYY' / 'YYYY-MM' strings."""
    def parse(text: str) -> Optional[datetime.date]:
        text = (text or "").strip()
        if not text:
            return None
        for fmt in ("%b %Y", "%B %Y", "%Y-%m", "%m/%Y", "%Y"):
            try:
                dt = datetime.datetime.strptime(text, fmt)
                return dt.date()
            except ValueError:
                continue
        year = _year(text)
        return datetime.date(year, 1, 1) if year else None

    start_d = parse(start)
    if start_d is None:
        return 0
    end_d = datetime.date.today() if (is_current or not end) else (parse(end) or datetime.date.today())
    months = (end_d.year - start_d.year) * 12 + (end_d.month - start_d.month)
    return max(0, months)


def total_experience_years(aggregate: dict) -> float:
    months = 0
    for job in aggregate.get("work_experiences") or []:
        emp_type = str(job.get("employment_type") or "").lower()
        weight = 0.5 if "intern" in emp_type else 1.0
        months += _months_between(job.get("start_date"), job.get("end_date"), bool(job.get("is_current"))) * weight
    return round(months / 12.0, 1)


def _candidate_skills(aggregate: dict) -> set[str]:
    return {_norm(s.get("name")) for s in (aggregate.get("skills") or []) if s.get("name")}


def _latest_grad_year(aggregate: dict) -> Optional[int]:
    years = [_year(edu.get("end_year")) for edu in (aggregate.get("educations") or [])]
    years = [y for y in years if y]
    return max(years) if years else None


def _degrees(aggregate: dict) -> list[str]:
    out = []
    for edu in aggregate.get("educations") or []:
        for field in ("degree", "specialization"):
            if edu.get(field):
                out.append(_norm(edu.get(field)))
    return out


def _candidate_location(aggregate: dict) -> str:
    basic = aggregate.get("basic", {})
    personal = aggregate.get("personal", {})
    return " ".join(
        _norm(v)
        for v in (basic.get("location"), personal.get("city"), personal.get("state"))
        if v
    )


# ─── Criterion evaluation ────────────────────────────────────────

def _evaluate_one(crit: dict, aggregate: dict) -> dict:
    """Return {label, met, requirement, candidate_value, note}."""
    ctype = str(crit.get("type") or "custom")
    label = crit.get("label") or ctype.replace("_", " ").title()
    result = {"key": crit.get("key") or ctype, "type": ctype, "label": label, "met": True,
              "requirement": "", "candidate_value": "", "note": ""}

    if ctype == "min_cgpa":
        need = _num(crit.get("value")) or 0.0
        have = _best_cgpa(aggregate)
        result["requirement"] = f"CGPA ≥ {need:g}"
        result["candidate_value"] = f"{have:g}" if have is not None else "Not provided"
        result["met"] = have is not None and have >= need

    elif ctype == "min_experience":
        need = _num(crit.get("value")) or 0.0
        have = total_experience_years(aggregate)
        result["requirement"] = f"Experience ≥ {need:g} yr"
        result["candidate_value"] = f"{have:g} yr"
        result["met"] = have >= need

    elif ctype == "max_experience":
        cap = _num(crit.get("value")) or 0.0
        have = total_experience_years(aggregate)
        result["requirement"] = f"Experience ≤ {cap:g} yr"
        result["candidate_value"] = f"{have:g} yr"
        result["met"] = have <= cap

    elif ctype == "required_skills":
        wanted = crit.get("value") or []
        if isinstance(wanted, str):
            wanted = [wanted]
        have = _candidate_skills(aggregate)
        missing = [s for s in wanted if _norm(s) not in have]
        result["requirement"] = "Skills: " + ", ".join(wanted)
        result["candidate_value"] = ("Missing: " + ", ".join(missing)) if missing else "All matched"
        result["met"] = not missing

    elif ctype == "allowed_degrees":
        allowed = crit.get("value") or []
        if isinstance(allowed, str):
            allowed = [allowed]
        have = _degrees(aggregate)
        matched = any(_norm(a) and any(_norm(a) in d or d in _norm(a) for d in have) for a in allowed)
        result["requirement"] = "Degree: " + ", ".join(allowed)
        result["candidate_value"] = ", ".join(
            e.get("degree") or e.get("specialization") or "—" for e in (aggregate.get("educations") or [])
        ) or "Not provided"
        result["met"] = matched if have else False

    elif ctype == "max_backlogs":
        cap = int(_num(crit.get("value")) or 0)
        have = _max_backlogs(aggregate)
        result["requirement"] = f"Backlogs ≤ {cap}"
        result["candidate_value"] = str(have)
        result["met"] = have <= cap

    elif ctype == "graduation_year":
        years = crit.get("value") or []
        if not isinstance(years, list):
            years = [years]
        allowed = {int(_num(y)) for y in years if _num(y) is not None}
        have = _latest_grad_year(aggregate)
        result["requirement"] = "Graduating in " + ", ".join(str(y) for y in sorted(allowed))
        result["candidate_value"] = str(have) if have else "Not provided"
        result["met"] = have in allowed if (have and allowed) else False

    elif ctype == "location":
        wanted = crit.get("value") or []
        if isinstance(wanted, str):
            wanted = [wanted]
        cand = _candidate_location(aggregate)
        relocate = bool(aggregate.get("job_preferences", {}).get("willing_to_relocate"))
        matched = relocate or any(_norm(w) and _norm(w) in cand for w in wanted)
        result["requirement"] = "Location: " + ", ".join(wanted)
        result["candidate_value"] = "Open to relocate" if relocate else (
            aggregate.get("basic", {}).get("location") or "Not provided"
        )
        result["met"] = matched

    else:  # custom / informational — always considered met
        result["requirement"] = str(crit.get("value") or crit.get("label") or "")
        result["candidate_value"] = "—"
        result["met"] = True
        result["note"] = "Self-declared"

    return result


def evaluate(aggregate: dict, job) -> dict:
    """Evaluate all of a job's eligibility criteria against the candidate.

    ``job`` is a ``JobListing`` ORM row (or any object exposing ``eligibility``).
    """
    criteria = list(getattr(job, "eligibility", None) or [])
    checks = [_evaluate_one(c, aggregate) for c in criteria]
    met = sum(1 for c in checks if c["met"])
    total = len(checks)
    return {
        "eligible": total == 0 or met == total,
        "met_count": met,
        "total": total,
        "criteria": checks,
        "has_criteria": total > 0,
    }


# ─── Application auto-fill ────────────────────────────────────────

def build_prefill(aggregate: dict) -> dict:
    """The personal details auto-pulled from the profile into the application."""
    basic = aggregate.get("basic", {})
    contact = aggregate.get("contact", {})
    personal = aggregate.get("personal", {})
    social = aggregate.get("social", {})
    prefs = aggregate.get("job_preferences", {})
    top_edu = (aggregate.get("educations") or [{}])[0]

    return {
        "full_name": aggregate.get("full_name", ""),
        "email": contact.get("email", ""),
        "phone": contact.get("phone", ""),
        "headline": basic.get("headline", ""),
        "location": basic.get("location", "") or " ".join(
            filter(None, [personal.get("city"), personal.get("state")])
        ),
        "gender": personal.get("gender", ""),
        "date_of_birth": personal.get("date_of_birth", ""),
        "linkedin_url": social.get("linkedin_url", ""),
        "github_url": social.get("github_url", ""),
        "portfolio_url": social.get("portfolio_url", ""),
        "current_institute": top_edu.get("institute", ""),
        "degree": top_edu.get("degree", ""),
        "specialization": top_edu.get("specialization", ""),
        "graduation_year": top_edu.get("end_year", ""),
        "cgpa": _best_cgpa(aggregate),
        "total_experience_years": total_experience_years(aggregate),
        "skills": [s.get("name") for s in (aggregate.get("skills") or []) if s.get("name")],
        "expected_ctc": prefs.get("expected_ctc"),
        "willing_to_relocate": bool(prefs.get("willing_to_relocate")),
        "preferred_locations": prefs.get("preferred_locations") or [],
    }
