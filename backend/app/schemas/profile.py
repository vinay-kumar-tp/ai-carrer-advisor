"""Schemas for the My Profile section.

Kept in its own module because the profile is by far the largest aggregate in
the app. Every "section" of the profile page maps to one update schema so the
frontend can PATCH a single card without touching the rest of the profile.
"""

from typing import Optional, Any
from pydantic import BaseModel, Field, field_validator


# ─── Shared helpers ──────────────────────────────────────────────

class LabelValue(BaseModel):
    label: str = ""
    value: str = ""


class LabelUrl(BaseModel):
    label: str = ""
    url: str = ""


class TrainingItem(BaseModel):
    name: str = ""
    status: str = ""
    score: str = ""
    notes: str = ""


class SemesterRecord(BaseModel):
    semester: str = ""
    cgpa: Optional[float] = None
    ongoing_backlogs: Optional[int] = None
    total_backlogs: Optional[int] = None
    marksheet_doc_id: Optional[str] = None


# ─── Section updates (all fields optional → partial update) ──────

class BasicInfoUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    headline: Optional[str] = Field(None, max_length=500)
    enrollment_id: Optional[str] = Field(None, max_length=64)
    location: Optional[str] = Field(None, max_length=255)
    experience_level: Optional[str] = Field(None, max_length=50)
    avatar_url: Optional[str] = Field(None, max_length=500)


class ContactUpdate(BaseModel):
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=32)


class PersonalDetailsUpdate(BaseModel):
    gender: Optional[str] = Field(None, max_length=30)
    country: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    city: Optional[str] = Field(None, max_length=100)
    date_of_birth: Optional[str] = Field(None, max_length=20)


class SocialLinksUpdate(BaseModel):
    github_url: Optional[str] = Field(None, max_length=500)
    linkedin_url: Optional[str] = Field(None, max_length=500)
    dribbble_url: Optional[str] = Field(None, max_length=500)
    behance_url: Optional[str] = Field(None, max_length=500)
    portfolio_url: Optional[str] = Field(None, max_length=500)
    other_links: Optional[list[LabelUrl]] = None


class AboutUpdate(BaseModel):
    about_me: Optional[str] = Field(None, max_length=5000)


class AdditionalInfoUpdate(BaseModel):
    additional_info: list[LabelValue] = []


class JobPreferencesUpdate(BaseModel):
    open_for: Optional[list[str]] = None
    job_roles: Optional[list[str]] = None
    available_for_hire: Optional[bool] = None
    willing_to_relocate: Optional[bool] = None
    preferred_locations: Optional[list[str]] = None
    industry: Optional[str] = Field(None, max_length=255)
    expected_ctc: Optional[int] = Field(None, ge=0)
    ctc_period: Optional[str] = Field(None, max_length=20)


class ProgramDetailsUpdate(BaseModel):
    program_name: Optional[str] = Field(None, max_length=255)
    program_year: Optional[str] = Field(None, max_length=50)
    institution_rating: Optional[str] = Field(None, max_length=50)
    program_extra: Optional[list[LabelValue]] = None


class MentorshipUpdate(BaseModel):
    is_mentee: Optional[bool] = None
    mentor_name: Optional[str] = Field(None, max_length=255)
    mentorship_notes: Optional[str] = Field(None, max_length=2000)


class TrainingUpdate(BaseModel):
    training_details: list[TrainingItem] = []


class AcademicSummaryUpdate(BaseModel):
    class_10_percentage: Optional[float] = Field(None, ge=0, le=100)
    class_10_board: Optional[str] = Field(None, max_length=255)
    class_12_percentage: Optional[float] = Field(None, ge=0, le=100)
    class_12_board: Optional[str] = Field(None, max_length=255)


class SkillsBulkUpdate(BaseModel):
    """The design shows skills as a flat chip list, so the whole set is replaced at once."""
    skills: list[str] = []

    @field_validator("skills")
    @classmethod
    def clean(cls, value: list[str]) -> list[str]:
        seen, out = set(), []
        for raw in value:
            name = (raw or "").strip()
            key = name.lower()
            if name and key not in seen:
                seen.add(key)
                out.append(name)
        return out[:60]


# ─── Repeatable sections ─────────────────────────────────────────

class EducationInput(BaseModel):
    institute: str = Field(min_length=1, max_length=255)
    degree: str = ""
    specialization: str = ""
    start_year: str = ""
    end_year: str = ""
    cgpa: Optional[float] = Field(None, ge=0, le=100)
    cgpa_scale: Optional[float] = Field(10.0, gt=0, le=100)
    percentage: Optional[float] = Field(None, ge=0, le=100)
    is_current: bool = True
    ongoing_backlogs: int = Field(0, ge=0)
    total_backlogs: int = Field(0, ge=0)
    semesters: list[SemesterRecord] = []
    display_order: int = 0


class WorkExperienceInput(BaseModel):
    company: str = Field(min_length=1, max_length=255)
    role: str = Field(min_length=1, max_length=255)
    employment_type: str = "Internship"
    location: str = ""
    start_date: str = ""
    end_date: str = ""
    is_current: bool = False
    highlights: list[str] = []
    display_order: int = 0


class PositionInput(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    event_name: str = ""
    department: str = ""
    organization: str = ""
    start_date: str = ""
    end_date: str = ""
    highlights: list[str] = []
    display_order: int = 0


class ProjectInput(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    subtitle: str = ""
    description: str = ""
    tech_stack: list[str] = []
    highlights: list[str] = []
    start_date: str = ""
    end_date: str = ""
    is_ongoing: bool = False
    project_url: str = ""
    repo_url: str = ""
    display_order: int = 0


class AwardInput(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    issued_by: str = ""
    issue_date: str = ""
    achievement_type: str = "Academic"
    description: str = ""
    award_url: str = ""
    certificate_doc_id: Optional[str] = None
    display_order: int = 0


class CertificationInput(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    issuer: str = ""
    course_duration: str = ""
    validity: str = "Lifetime Validity"
    cert_type: str = ""
    specialization: str = ""
    courses: str = ""
    pre_assessment_score: str = ""
    marks_obtained: str = ""
    points_earned: str = ""
    conclusion: str = ""
    credential_url: str = ""
    certificate_doc_id: Optional[str] = None
    display_order: int = 0


class BenchmarkInput(BaseModel):
    stage: str = Field(pattern="^(baseline|midline|endline)$")
    provider: str = ""
    analytical_score: Optional[float] = Field(None, ge=0, le=100)
    logical_score: Optional[float] = Field(None, ge=0, le=100)
    verbal_score: Optional[float] = Field(None, ge=0, le=100)
    quantitative_score: Optional[float] = Field(None, ge=0, le=100)
    total_score: Optional[float] = Field(None, ge=0, le=100)
    taken_on: str = ""


# ─── Resume library ──────────────────────────────────────────────

class ResumeInput(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    source: str = "existing"
    template: str = ""
    document_id: Optional[str] = None
    status: str = "ready"


class ResumeRename(BaseModel):
    name: str = Field(min_length=1, max_length=255)


class ResumeGenerateInput(BaseModel):
    template: str = "Template 1"
    name: Optional[str] = None
    sections: Optional[list[str]] = None


class ResumeTailorInput(BaseModel):
    job_id: str
    name: Optional[str] = None


class ResumeDesignUpdate(BaseModel):
    """Template switch and/or section visibility change from the builder sidebar."""

    template: Optional[str] = None
    sections: Optional[list[str]] = None


class ResumeContentUpdate(BaseModel):
    """Direct edit of the structured resume snapshot from the builder."""

    content: dict


class ResumeTailorPreviewInput(BaseModel):
    """Ask for a match breakdown + reviewable suggestions without writing anything."""

    job_id: Optional[str] = None
    job_title: Optional[str] = None
    job_description: Optional[str] = None


class SuggestionDecision(BaseModel):
    suggestion_id: str
    accepted: bool = True
    user_detail: Optional[str] = None


class ResumeApplySuggestionsInput(BaseModel):
    """Apply the accepted subset of a tailoring run.

    ``as_copy`` keeps the original resume untouched and writes a new tailored row.
    """

    decisions: list[SuggestionDecision] = Field(default_factory=list)
    as_copy: bool = True
    name: Optional[str] = None


# ─── Scorecard ───────────────────────────────────────────────────

class ScorecardEntryInput(BaseModel):
    category: str = Field("other", pattern="^(other|custom_event)$")
    title: str = Field(min_length=1, max_length=255)
    score: float = 0
    max_score: Optional[float] = None
    scored_on: str = ""
    notes: str = ""


# ─── Documents ───────────────────────────────────────────────────

class DocumentVisibilityUpdate(BaseModel):
    document_ids: list[str] = []
    is_public: bool = True


class DocumentLabelUpdate(BaseModel):
    label: str = Field(min_length=1, max_length=255)


# ─── Output ──────────────────────────────────────────────────────

class CompletionItem(BaseModel):
    key: str
    title: str
    weight: float
    complete: bool
    missing_fields: list[str] = []
    action_label: str = ""


class CompletionResponse(BaseModel):
    percentage: float
    items: list[CompletionItem]
    next_suggestions: list[CompletionItem] = []


class FullProfileResponse(BaseModel):
    """Free-form on purpose: the aggregate stitches together a dozen sections
    and the frontend consumes it as one document."""
    model_config = {"extra": "allow"}

    user_id: str
    email: str
    full_name: str
    role: str
    basic: dict[str, Any]
    contact: dict[str, Any]
    personal: dict[str, Any]
    social: dict[str, Any]
    about_me: str
    additional_info: list[Any]
    program: dict[str, Any]
    mentorship: dict[str, Any]
    training: list[Any]
    academic_summary: dict[str, Any]
    job_preferences: dict[str, Any]
    skills: list[Any]
    educations: list[Any]
    work_experiences: list[Any]
    positions: list[Any]
    projects: list[Any]
    awards: list[Any]
    certifications: list[Any]
    benchmarks: dict[str, Any]
    completion: CompletionResponse
