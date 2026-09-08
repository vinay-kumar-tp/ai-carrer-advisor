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


class JobResponse(BaseModel):
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

    class Config:
        from_attributes = True


class ApplicationCreate(BaseModel):
    job_id: str
    resume_id: Optional[str] = None
    cover_letter: Optional[str] = None


class ApplicationResponse(BaseModel):
    id: str
    job_id: str
    status: str
    applied_at: datetime

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


# ─── Personality Schemas ─────────────────────────────────────────

class PersonalitySubmission(BaseModel):
    answers: list[int]  # 1-5 Likert scale responses


class PersonalityResponse(BaseModel):
    openness: float
    conscientiousness: float
    extraversion: float
    agreeableness: float
    neuroticism: float

    class Config:
        from_attributes = True


# ─── Interview Schemas ───────────────────────────────────────────

class InterviewStartRequest(BaseModel):
    mode: str = "structured"  # structured or adaptive
    job_context: Optional[str] = None


class InterviewAnswerRequest(BaseModel):
    answer_text: str


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
