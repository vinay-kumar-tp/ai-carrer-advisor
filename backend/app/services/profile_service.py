"""Serialization, completion scoring and PDF export for the My Profile section."""

from typing import Any, Optional

from app.models.models import (
    Award,
    BenchmarkScore,
    Certification,
    Education,
    PositionOfResponsibility,
    Profile,
    ProfileProject,
    User,
    WorkExperience,
)

BENCHMARK_STAGES = ("baseline", "midline", "endline")


# ─── Small helpers ───────────────────────────────────────────────

def as_list(value: Any) -> list:
    """JSON columns added by the additive migration start out as NULL."""
    return list(value) if isinstance(value, (list, tuple)) else []


def as_text(value: Any) -> str:
    return value if isinstance(value, str) else ("" if value is None else str(value))


def has_value(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, dict)):
        return len(value) > 0
    if isinstance(value, bool):
        return value
    return True


# ─── Section serializers ─────────────────────────────────────────

def serialize_basic(user: User, profile: Profile) -> dict:
    return {
        "full_name": user.full_name,
        "headline": as_text(profile.headline),
        "enrollment_id": as_text(profile.enrollment_id),
        "location": as_text(profile.location),
        "experience_level": as_text(profile.experience_level),
        "avatar_url": profile.avatar_url or "",
    }


def serialize_contact(user: User, profile: Profile) -> dict:
    return {"email": user.email, "phone": as_text(profile.phone)}


def serialize_personal(profile: Profile) -> dict:
    return {
        "gender": as_text(profile.gender),
        "country": as_text(profile.country),
        "state": as_text(profile.state),
        "city": as_text(profile.city),
        "date_of_birth": as_text(profile.date_of_birth),
    }


def serialize_social(profile: Profile) -> dict:
    return {
        "github_url": as_text(profile.github_url),
        "linkedin_url": as_text(profile.linkedin_url),
        "dribbble_url": as_text(profile.dribbble_url),
        "behance_url": as_text(profile.behance_url),
        "portfolio_url": as_text(profile.portfolio_url),
        "other_links": as_list(profile.other_links),
    }


def serialize_program(profile: Profile) -> dict:
    return {
        "program_name": as_text(profile.program_name),
        "program_year": as_text(profile.program_year),
        "institution_rating": as_text(profile.institution_rating),
        "program_extra": as_list(profile.program_extra),
    }


def serialize_mentorship(profile: Profile) -> dict:
    return {
        "is_mentee": bool(profile.is_mentee),
        "mentor_name": as_text(profile.mentor_name),
        "mentorship_notes": as_text(profile.mentorship_notes),
    }


def serialize_academic_summary(profile: Profile) -> dict:
    return {
        "class_10_percentage": profile.class_10_percentage,
        "class_10_board": as_text(profile.class_10_board),
        "class_12_percentage": profile.class_12_percentage,
        "class_12_board": as_text(profile.class_12_board),
    }


def serialize_job_preferences(profile: Profile) -> dict:
    return {
        "open_for": as_list(profile.open_for),
        "job_roles": as_list(profile.job_roles),
        "available_for_hire": bool(profile.available_for_hire),
        "willing_to_relocate": bool(profile.willing_to_relocate),
        "preferred_locations": as_list(profile.preferred_locations),
        "industry": as_text(profile.industry),
        "expected_ctc": profile.expected_ctc,
        "ctc_period": as_text(profile.ctc_period) or "Year",
    }


def serialize_education(row: Education) -> dict:
    return {
        "id": row.id,
        "institute": row.institute,
        "degree": as_text(row.degree),
        "specialization": as_text(row.specialization),
        "start_year": as_text(row.start_year),
        "end_year": as_text(row.end_year),
        "cgpa": row.cgpa,
        "cgpa_scale": row.cgpa_scale or 10.0,
        "percentage": row.percentage,
        "is_current": bool(row.is_current),
        "ongoing_backlogs": row.ongoing_backlogs or 0,
        "total_backlogs": row.total_backlogs or 0,
        "semesters": as_list(row.semesters),
        "display_order": row.display_order or 0,
    }


def serialize_work(row: WorkExperience) -> dict:
    return {
        "id": row.id,
        "company": row.company,
        "role": row.role,
        "employment_type": as_text(row.employment_type),
        "location": as_text(row.location),
        "start_date": as_text(row.start_date),
        "end_date": as_text(row.end_date),
        "is_current": bool(row.is_current),
        "highlights": as_list(row.highlights),
        "display_order": row.display_order or 0,
    }


def serialize_position(row: PositionOfResponsibility) -> dict:
    return {
        "id": row.id,
        "title": row.title,
        "event_name": as_text(row.event_name),
        "department": as_text(row.department),
        "organization": as_text(row.organization),
        "start_date": as_text(row.start_date),
        "end_date": as_text(row.end_date),
        "highlights": as_list(row.highlights),
        "display_order": row.display_order or 0,
    }


def serialize_project(row: ProfileProject) -> dict:
    return {
        "id": row.id,
        "title": row.title,
        "subtitle": as_text(row.subtitle),
        "description": as_text(row.description),
        "tech_stack": as_list(row.tech_stack),
        "highlights": as_list(row.highlights),
        "start_date": as_text(row.start_date),
        "end_date": as_text(row.end_date),
        "is_ongoing": bool(row.is_ongoing),
        "project_url": as_text(row.project_url),
        "repo_url": as_text(row.repo_url),
        "display_order": row.display_order or 0,
    }


def serialize_award(row: Award) -> dict:
    return {
        "id": row.id,
        "title": row.title,
        "issued_by": as_text(row.issued_by),
        "issue_date": as_text(row.issue_date),
        "achievement_type": as_text(row.achievement_type),
        "description": as_text(row.description),
        "award_url": as_text(row.award_url),
        "certificate_doc_id": row.certificate_doc_id,
        "display_order": row.display_order or 0,
    }


def serialize_certification(row: Certification) -> dict:
    return {
        "id": row.id,
        "name": row.name,
        "issuer": as_text(row.issuer),
        "course_duration": as_text(row.course_duration),
        "validity": as_text(row.validity),
        "cert_type": as_text(row.cert_type),
        "specialization": as_text(row.specialization),
        "courses": as_text(row.courses),
        "pre_assessment_score": as_text(row.pre_assessment_score),
        "marks_obtained": as_text(row.marks_obtained),
        "points_earned": as_text(row.points_earned),
        "conclusion": as_text(row.conclusion),
        "credential_url": as_text(row.credential_url),
        "certificate_doc_id": row.certificate_doc_id,
        "display_order": row.display_order or 0,
    }


def serialize_benchmark(row: Optional[BenchmarkScore], stage: str) -> dict:
    if row is None:
        return {
            "id": None,
            "stage": stage,
            "provider": "",
            "analytical_score": None,
            "logical_score": None,
            "verbal_score": None,
            "quantitative_score": None,
            "total_score": None,
            "taken_on": "",
        }
    return {
        "id": row.id,
        "stage": row.stage,
        "provider": as_text(row.provider),
        "analytical_score": row.analytical_score,
        "logical_score": row.logical_score,
        "verbal_score": row.verbal_score,
        "quantitative_score": row.quantitative_score,
        "total_score": row.total_score,
        "taken_on": as_text(row.taken_on),
    }


def serialize_resume(row) -> dict:
    return {
        "id": row.id,
        "name": row.name,
        "source": as_text(row.source),
        "template": as_text(row.template),
        "ats_score": row.ats_score,
        "status": as_text(row.status),
        "is_primary": bool(row.is_primary),
        "target_job_id": row.target_job_id,
        "document_id": row.document_id,
        "sections": list(row.sections or []),
        "job_context": dict(row.job_context or {}),
        "analysis_score": (row.analysis or {}).get("overall_score"),
        "has_content": bool(row.content),
        "created_at": row.created_at.isoformat() if row.created_at else None,
        "updated_at": row.updated_at.isoformat() if row.updated_at else None,
    }


def serialize_scorecard_entry(row) -> dict:
    return {
        "id": row.id,
        "category": as_text(row.category),
        "title": row.title,
        "score": row.score or 0,
        "max_score": row.max_score,
        "scored_on": as_text(row.scored_on),
        "notes": as_text(row.notes),
    }


# ─── Profile completion ──────────────────────────────────────────
# Weights sum to 100. Each entry reports exactly which fields are missing so the
# UI can render the "Missing Fields (+x%)" nudge cards from the design.

def compute_completion(
    user: User,
    profile: Profile,
    skills: list,
    educations: list,
    projects: list,
    work: list,
    positions: list,
    awards: list,
    certifications: list,
    resumes: list,
) -> dict:
    checks: list[dict] = []

    def add(key: str, title: str, weight: float, missing: list[str], action_label: str):
        checks.append(
            {
                "key": key,
                "title": title,
                "weight": weight,
                "complete": not missing,
                "missing_fields": missing,
                "action_label": action_label,
            }
        )

    # Header / identity
    missing = []
    if not has_value(profile.headline):
        missing.append("Professional headline")
    if not has_value(profile.location):
        missing.append("Location")
    if not has_value(profile.experience_level):
        missing.append("Experience level")
    if not has_value(profile.avatar_url):
        missing.append("Profile photo")
    add("basic", "Basic Details", 10, missing, "Complete Basic Details")

    # Contact
    missing = [] if has_value(profile.phone) else ["Contact number"]
    add("contact", "Contact Details", 5, missing, "Add Contact Details")

    # Personal
    missing = [
        label
        for label, value in (("Gender", profile.gender), ("Country", profile.country), ("State", profile.state))
        if not has_value(value)
    ]
    add("personal", "Personal Details", 5, missing, "Add Personal Details")

    # Social
    social_present = any(
        has_value(v)
        for v in (
            profile.github_url,
            profile.linkedin_url,
            profile.dribbble_url,
            profile.behance_url,
            profile.portfolio_url,
        )
    ) or bool(as_list(profile.other_links))
    add("social", "Social Links", 5, [] if social_present else ["At least one social link"], "Add Social Links")

    # About
    add("about", "About Me", 10, [] if has_value(profile.about_me) else ["About me summary"], "Add About Me")

    # Skills
    missing = []
    if len(skills) == 0:
        missing.append("Skills")
    elif len(skills) < 3:
        missing.append(f"{3 - len(skills)} more skill(s)")
    add("skills", "Skills", 10, missing, "Add Skills")

    # Education
    add("education", "Education", 15, [] if educations else ["Education"], "Add Education")

    # Projects
    add("projects", "Projects", 10, [] if projects else ["Projects"], "Add Projects")

    # Experience or leadership
    add(
        "experience",
        "Experience",
        5,
        [] if (work or positions) else ["Work experience or position of responsibility"],
        "Add Experience",
    )

    add("awards", "Awards or Achievements", 5, [] if awards else ["Awards or achievements"], "Add Achievements")
    add("certifications", "Certifications", 5, [] if certifications else ["Certifications"], "Add Certifications")

    # Job preferences
    missing = []
    if not as_list(profile.open_for):
        missing.append("Open for")
    if not as_list(profile.job_roles):
        missing.append("Job roles")
    if not as_list(profile.preferred_locations):
        missing.append("Preferred location")
    add("job_preferences", "Job Preferences", 10, missing, "Set Job Preferences")

    # Resume
    add("resume", "Resume", 5, [] if resumes else ["Resume"], "Add Resume")

    earned = 0.0
    for check in checks:
        if check["complete"]:
            earned += check["weight"]
        elif check["key"] == "skills" and skills:
            earned += check["weight"] * (len(skills) / 3.0)  # partial credit
        elif check["missing_fields"] and check["key"] in {"basic", "personal", "job_preferences"}:
            # partial credit proportional to how many sub-fields are filled
            total_fields = {"basic": 4, "personal": 3, "job_preferences": 3}[check["key"]]
            filled = total_fields - len(check["missing_fields"])
            earned += check["weight"] * (max(filled, 0) / total_fields)

    percentage = round(min(earned, 100.0), 2)
    incomplete = [c for c in checks if not c["complete"]]
    incomplete.sort(key=lambda c: c["weight"], reverse=True)

    return {
        "percentage": percentage,
        "items": checks,
        "next_suggestions": incomplete[:3],
    }


# ─── Resume content snapshot ─────────────────────────────────────

def build_resume_content(aggregate: dict) -> dict:
    """Structured snapshot used by generated resumes and the ATS scorer."""
    return {
        "name": aggregate["full_name"],
        "headline": aggregate["basic"]["headline"],
        "email": aggregate["contact"]["email"],
        "phone": aggregate["contact"]["phone"],
        "location": aggregate["basic"]["location"],
        "about": aggregate["about_me"],
        "skills": [s["name"] for s in aggregate["skills"]],
        "educations": aggregate["educations"],
        "work_experiences": aggregate["work_experiences"],
        "positions": aggregate["positions"],
        "projects": aggregate["projects"],
        "awards": aggregate["awards"],
        "certifications": aggregate["certifications"],
        "social": aggregate["social"],
    }


def resume_plain_text(content: dict) -> str:
    """Flatten a resume snapshot for keyword-based ATS scoring."""
    parts: list[str] = [
        as_text(content.get("name")),
        as_text(content.get("headline")),
        as_text(content.get("about")),
        " ".join(content.get("skills") or []),
    ]
    for edu in content.get("educations") or []:
        parts.append(" ".join(filter(None, [edu.get("institute"), edu.get("degree"), edu.get("specialization")])))
    for job in content.get("work_experiences") or []:
        parts.append(" ".join(filter(None, [job.get("company"), job.get("role")])))
        parts.extend(job.get("highlights") or [])
    for pos in content.get("positions") or []:
        parts.append(" ".join(filter(None, [pos.get("title"), pos.get("organization")])))
        parts.extend(pos.get("highlights") or [])
    for project in content.get("projects") or []:
        parts.append(" ".join(filter(None, [project.get("title"), project.get("description")])))
        parts.extend(project.get("tech_stack") or [])
        parts.extend(project.get("highlights") or [])
    for cert in content.get("certifications") or []:
        parts.append(" ".join(filter(None, [cert.get("name"), cert.get("issuer"), cert.get("specialization")])))
    for award in content.get("awards") or []:
        parts.append(" ".join(filter(None, [award.get("title"), award.get("issued_by")])))
    return " \n".join(p for p in parts if p)
