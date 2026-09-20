from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


# ─── Auth Schemas ────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=2, max_length=255)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: str
    role: str


class RefreshRequest(BaseModel):
    refresh_token: str


# ─── Profile Schemas ────────────────────────────────────────────

class ProfileUpdate(BaseModel):
    bio: Optional[str] = None
    education: Optional[str] = None
    cgpa: Optional[float] = Field(None, ge=0, le=10)
    major: Optional[str] = None
    university: Optional[str] = None
    location: Optional[str] = None
    interests: Optional[list[str]] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    phone: Optional[str] = None


class ProfileResponse(BaseModel):
    user_id: str
    email: str
    full_name: str
    role: str
    bio: str
    education: str
    cgpa: Optional[float]
    major: str
    university: str
    location: str
    interests: list
    linkedin_url: Optional[str]
    github_url: Optional[str]
    portfolio_url: Optional[str]
    phone: Optional[str]

    class Config:
        from_attributes = True


class UserSkillCreate(BaseModel):
    skill_name: str
    proficiency: int = Field(ge=0, le=100, default=50)


class SkillResponse(BaseModel):
    id: str
    name: str
    category: str

    class Config:
        from_attributes = True


# ─── Job Schemas ─────────────────────────────────────────────────

class JobCreate(BaseModel):
    title: str
    company: str
    description: str
    location: Optional[str] = ""
    remote: bool = False
    salary_range: Optional[str] = None
    required_skills: list[str] = []
    experience_level: str = "entry"
    job_type: str = "full-time"
    source_portal: Optional[str] = "LinkedIn"
    company_logo: Optional[str] = ""
    company_tagline: Optional[str] = ""
    industry: Optional[str] = ""
    employment_mode: Optional[str] = "In Office"
    openings: Optional[int] = 1
    application_deadline: Optional[str] = ""
    about_company: Optional[str] = ""
    responsibilities: list[str] = []
    qualifications: list[str] = []
    perks: list[str] = []
    ctc_breakdown: list[dict] = []
    ctc_min: Optional[int] = None
    ctc_max: Optional[int] = None
    stipend_min: Optional[int] = None
    stipend_max: Optional[int] = None
    experience_min_years: float = 0.0
    experience_max_years: Optional[float] = None
    eligibility: list[dict] = []
    apply_questions: list[dict] = []


class JobResponse(BaseModel):
    """Compact card representation used on the list view."""
    id: str
    title: str
    company: str
    description: str
    location: str
    remote: bool
    salary_range: Optional[str]
    required_skills: list
    experience_level: str
    job_type: str
    posted_at: datetime
    slug: Optional[str] = None
    source_portal: str = "LinkedIn"
    company_logo: str = ""
    company_tagline: str = ""
    industry: str = ""
    employment_mode: str = "In Office"
    openings: int = 1
    application_deadline: str = ""
    ctc_min: Optional[int] = None
    ctc_max: Optional[int] = None
    stipend_min: Optional[int] = None
    stipend_max: Optional[int] = None
    experience_min_years: float = 0.0
    experience_max_years: Optional[float] = None

    class Config:
        from_attributes = True


class ApplicationCreate(BaseModel):
    job_id: Optional[str] = None
    resume_id: Optional[str] = None
    cover_letter: Optional[str] = None
    answers: dict = {}


class ApplicationResponse(BaseModel):
    id: str
    job_id: str
    status: str
    applied_at: datetime

    class Config:
        from_attributes = True


class JobAlertToggle(BaseModel):
    enabled: bool


# ─── Notifications ───────────────────────────────────────────────

class NotificationResponse(BaseModel):
    id: str
    message: str
    notification_type: str
    read: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Code Quest Schemas ─────────────────────────────────────────

class CodeSubmissionCreate(BaseModel):
    problem_id: str
    code: str
    language: str


class ProblemResponse(BaseModel):
    id: str
    title: str
    description: str
    difficulty: str
    tags: list
    companies: list
    languages: list
    sample_input: str
    sample_output: str
    xp_reward: int

    class Config:
        from_attributes = True


class SubmissionResponse(BaseModel):
    id: str
    problem_id: str
    status: str
    score: int
    runtime_ms: Optional[int]
    memory_kb: Optional[int]
    output: Optional[str]
    error_message: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Aptitude Schemas ────────────────────────────────────────────

class QuizSubmission(BaseModel):
    question_ids: list[str]
    answers: list[int]  # chosen indices


class QuizResultResponse(BaseModel):
    id: str
    quiz_type: str
    topic: Optional[str]
    score: int
    total: int
    percentage: float
    time_taken_seconds: Optional[int]
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class QuestionResponse(BaseModel):
    id: str
    question_text: str
    options: list
    topic: str
    difficulty: str

    class Config:
        from_attributes = True


# ── Aptitude Studio (expanded) ───────────────────────────────────

class AptitudeQuestionOut(BaseModel):
    """A practice question — answer + explanation are deliberately hidden."""
    id: str
    slug: Optional[str] = None
    section: str
    topic: str
    subtopic: Optional[str] = None
    difficulty: str
    points: int
    question_text: str
    options: list
    solved: bool = False          # per-user: has this been answered correctly before


class CheckAnswerRequest(BaseModel):
    question_id: str
    choice: int                   # chosen option index


class CheckAnswerResponse(BaseModel):
    question_id: str
    correct: bool
    correct_index: int
    explanation: Optional[str] = None
    points_earned: int
    first_attempt: bool           # whether this was the user's first attempt


class AptitudeSetSubmission(BaseModel):
    """Submit a whole practice set at once (topic quiz)."""
    topic_slug: Optional[str] = None
    section: Optional[str] = None
    question_ids: list[str]
    answers: list[int]
    time_taken_seconds: Optional[int] = None


# ─── Personality Schemas ─────────────────────────────────────────

class PersonalitySubmission(BaseModel):
    answers: list[int]  # 1-5 Likert scale responses (legacy 10-item form)


class PersonalityResponse(BaseModel):
    openness: float
    conscientiousness: float
    extraversion: float
    agreeableness: float
    neuroticism: float

    class Config:
        from_attributes = True


# ── Big Five (OCEAN) engine v2 ───────────────────────────────────

class PersonalityFormMeta(BaseModel):
    key: str
    name: str
    short_name: str
    description: str
    est_minutes: int
    total_questions: int


class PersonalitySubmitRequest(BaseModel):
    responses: list[int]                       # 1-5 per item, in form order
    completion_time_seconds: Optional[int] = None


class TraitScore(BaseModel):
    raw_score: int
    min_score: int
    max_score: int
    percentage: float
    level: str                                 # Low | Moderate | High


class PersonalityAssessmentResult(BaseModel):
    assessment_metadata: dict                  # total/completed/compliance_status/time/form
    scores: dict                               # {trait: TraitScore-like}
    workplace_behavioral_insights: dict        # key_strengths/potential_challenges/team_collaboration_style
    compliance: dict
    completed_at: Optional[datetime] = None


# ─── Interview Schemas ───────────────────────────────────────────

class InterviewStartRequest(BaseModel):
    # How the interview is scoped: a job title, a single skill, or the resume.
    source: str = "job"                      # job | skill | resume
    job_title: Optional[str] = None
    job_description: Optional[str] = None
    skill: Optional[str] = None
    resume_id: Optional[str] = None
    difficulty: str = "mixed"                # mixed | easy | medium | hard
    question_mix: str = "technical_behavioral"  # technical_behavioral | behavioral
    # Optional custom interview length (scored questions). Clamped 3–20 server
    # side; omitted → engine default.
    num_questions: Optional[int] = None
    # Legacy field kept so older callers don't break.
    mode: str = "adaptive"


class InterviewAnswerRequest(BaseModel):
    answer_text: str


class InterviewFeedbackRequest(BaseModel):
    rating: Optional[str] = None             # difficult | okay | good | great
    hoping_to_improve: list[str] = []
    what_should_be_better: list[str] = []
    comment: Optional[str] = None


class InterviewFeedbackResponse(BaseModel):
    session_id: str
    scores: dict
    feedback: Optional[str]
    transcript: list

    class Config:
        from_attributes = True


# ─── Event Schemas ───────────────────────────────────────────────

class EventCreate(BaseModel):
    title: str
    description: str = ""
    event_date: datetime
    location: str = ""
    event_url: Optional[str] = None
    capacity: Optional[int] = None


class EventResponse(BaseModel):
    id: str
    title: str
    description: str
    event_date: datetime
    location: str
    event_url: Optional[str]
    capacity: Optional[int]

    class Config:
        from_attributes = True


# ─── Generic ─────────────────────────────────────────────────────

class MessageResponse(BaseModel):
    message: str
    success: bool = True


# ─── Document Vault ──────────────────────────────────────────────

class DocumentLabelUpdate(BaseModel):
    label: str


class ResumeOptimizeRequest(BaseModel):
    job_id: Optional[str] = None
    job_title: Optional[str] = None
    job_description: Optional[str] = None
    skills: Optional[list[str]] = None
