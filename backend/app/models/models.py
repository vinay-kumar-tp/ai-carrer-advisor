import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, Float, ForeignKey, Integer, Text, JSON
from sqlalchemy.orm import relationship
from app.db.session import Base
import enum


def generate_uuid():
    return str(uuid.uuid4())


class UserRole(str, enum.Enum):
    STUDENT = "student"
    ADMIN = "admin"


class ApplicationStatus(str, enum.Enum):
    APPLIED = "applied"
    SCREENING = "screening"
    INTERVIEW = "interview"
    OFFERED = "offered"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class SubmissionStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    ACCEPTED = "accepted"
    WRONG_ANSWER = "wrong_answer"
    RUNTIME_ERROR = "runtime_error"
    TIME_LIMIT = "time_limit"
    COMPILE_ERROR = "compile_error"


class Difficulty(str, enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class InterviewMode(str, enum.Enum):
    STRUCTURED = "structured"
    ADAPTIVE = "adaptive"


class DocumentType(str, enum.Enum):
    RESUME = "resume"
    CERTIFICATE = "certificate"
    TRANSCRIPT = "transcript"
    PROJECT = "project"
    OTHER = "other"


# ─── Users & Profiles ───────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(20), default=UserRole.STUDENT, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    profile = relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    skills = relationship("UserSkill", back_populates="user", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="user", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")
    code_submissions = relationship("CodeSubmission", back_populates="user", cascade="all, delete-orphan")
    quiz_attempts = relationship("QuizAttempt", back_populates="user", cascade="all, delete-orphan")
    interview_sessions = relationship("InterviewSession", back_populates="user", cascade="all, delete-orphan")
    personality_result = relationship("PersonalityResult", back_populates="user", uselist=False, cascade="all, delete-orphan")
    xp_logs = relationship("XPLog", back_populates="user", cascade="all, delete-orphan")
    leaderboard_entry = relationship("LeaderboardEntry", back_populates="user", uselist=False, cascade="all, delete-orphan")


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    bio = Column(Text, default="")
    education = Column(String(255), default="")
    cgpa = Column(Float, nullable=True)
    major = Column(String(255), default="")
    university = Column(String(255), default="")
    location = Column(String(255), default="")
    interests = Column(JSON, default=list)
    avatar_url = Column(String(500), nullable=True)
    linkedin_url = Column(String(500), nullable=True)
    github_url = Column(String(500), nullable=True)
    portfolio_url = Column(String(500), nullable=True)
    phone = Column(String(20), nullable=True)

    # ── Identity header ────────────────────────────────────────
    headline = Column(String(500), default="")          # "AI & Data Science Undergraduate | Full-Stack Developer"
    enrollment_id = Column(String(64), default="")      # generic student / candidate ID
    experience_level = Column(String(50), default="")   # Fresher | Experienced

    # ── Personal details ───────────────────────────────────────
    gender = Column(String(30), default="")
    country = Column(String(100), default="")
    state = Column(String(100), default="")
    city = Column(String(100), default="")
    date_of_birth = Column(String(20), default="")

    # ── About & extra social links ──────────────────────────────
    about_me = Column(Text, default="")
    dribbble_url = Column(String(500), default="")
    behance_url = Column(String(500), default="")
    other_links = Column(JSON, default=list)            # [{label, url}]
    additional_info = Column(JSON, default=list)        # [{label, value}] — generic key/value rows

    # ── Job preferences ────────────────────────────────────────
    open_for = Column(JSON, default=list)              # ["Full Time", "Internship"]
    job_roles = Column(JSON, default=list)
    available_for_hire = Column(Boolean, default=False)
    willing_to_relocate = Column(Boolean, default=False)
    preferred_locations = Column(JSON, default=list)
    industry = Column(String(255), default="")
    expected_ctc = Column(Integer, nullable=True)
    ctc_period = Column(String(20), default="Year")    # Year | Month

    # ── Program / scholarship details (generic, institution agnostic) ──
    program_name = Column(String(255), default="")
    program_year = Column(String(50), default="")       # e.g. "2026-27"
    institution_rating = Column(String(50), default="")
    program_extra = Column(JSON, default=list)          # [{label, value}]

    # ── Mentorship ─────────────────────────────────────────────
    is_mentee = Column(Boolean, default=False)
    mentor_name = Column(String(255), default="")
    mentorship_notes = Column(Text, default="")

    # ── Training ───────────────────────────────────────────────
    training_details = Column(JSON, default=list)       # [{name, status, score, notes}]

    # ── Academic summary ───────────────────────────────────────
    class_10_percentage = Column(Float, nullable=True)
    class_10_board = Column(String(255), default="")
    class_12_percentage = Column(Float, nullable=True)
    class_12_board = Column(String(255), default="")

    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="profile")


# ─── Skills ──────────────────────────────────────────────────────

class Skill(Base):
    __tablename__ = "skills"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), unique=True, nullable=False, index=True)
    category = Column(String(100), default="general")


class UserSkill(Base):
    __tablename__ = "user_skills"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    skill_id = Column(String(36), ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    proficiency = Column(Integer, default=50)

    user = relationship("User", back_populates="skills")
    skill = relationship("Skill")


# ─── Job Board ───────────────────────────────────────────────────

class JobListing(Base):
    __tablename__ = "job_listings"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    location = Column(String(255), default="")
    remote = Column(Boolean, default=False)
    salary_range = Column(String(100), nullable=True)
    required_skills = Column(JSON, default=list)
    experience_level = Column(String(50), default="entry")
    job_type = Column(String(50), default="full-time")
    posted_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    is_active = Column(Boolean, default=True)

    applications = relationship("Application", back_populates="job", cascade="all, delete-orphan")


class Application(Base):
    __tablename__ = "applications"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(String(36), ForeignKey("job_listings.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(30), default=ApplicationStatus.APPLIED)
    resume_id = Column(String(36), nullable=True)
    cover_letter = Column(Text, nullable=True)
    applied_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="applications")
    job = relationship("JobListing", back_populates="applications")


# ─── Code Quest ──────────────────────────────────────────────────

class CodingProblem(Base):
    __tablename__ = "coding_problems"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    difficulty = Column(String(20), default=Difficulty.EASY)
    tags = Column(JSON, default=list)
    companies = Column(JSON, default=list)
    languages = Column(JSON, default=lambda: ["python", "javascript"])
    sample_input = Column(Text, default="")
    sample_output = Column(Text, default="")
    test_cases = Column(JSON, default=list)
    starter_code = Column(JSON, default=dict)
    xp_reward = Column(Integer, default=10)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # ── Rich problem statement ─────────────────────────────────
    slug = Column(String(160), unique=True, index=True, nullable=True)
    notes = Column(JSON, default=list)            # extra statement paragraphs (definitions etc.)
    input_format = Column(JSON, default=list)     # list[str] — one bullet per input line
    output_format = Column(JSON, default=list)    # list[str]
    constraints = Column(JSON, default=list)      # list[str]
    examples = Column(JSON, default=list)         # [{input, output, explanation}]
    hints = Column(JSON, default=list)            # progressive hints
    pattern_note = Column(Text, default="")       # "Learn the pattern" explainer

    # ── Classification (drives the filter facets) ──────────────
    topics = Column(JSON, default=list)
    patterns = Column(JSON, default=list)
    sheets = Column(JSON, default=list)           # Blind 75, NeetCode 150, Amazon OA ...

    # ── Judge configuration & stats ────────────────────────────
    points = Column(Integer, default=10)
    time_limit_ms = Column(Integer, default=5000)
    solved_count = Column(Integer, default=0)
    attempt_count = Column(Integer, default=0)
    display_order = Column(Integer, default=0)


class CodeSubmission(Base):
    __tablename__ = "code_submissions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    problem_id = Column(String(36), ForeignKey("coding_problems.id", ondelete="CASCADE"), nullable=False)
    code = Column(Text, nullable=False)
    language = Column(String(30), nullable=False)
    status = Column(String(30), default=SubmissionStatus.PENDING)
    score = Column(Integer, default=0)
    runtime_ms = Column(Integer, nullable=True)
    memory_kb = Column(Integer, nullable=True)
    output = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # ── Judge detail ───────────────────────────────────────────
    passed_count = Column(Integer, default=0)
    total_count = Column(Integer, default=0)
    points_awarded = Column(Integer, default=0)
    # [{index, is_sample, verdict, runtime_ms, input?, expected?, got?}] — hidden
    # tests omit the payload so answers can't be scraped from the API.
    test_results = Column(JSON, default=list)

    user = relationship("User", back_populates="code_submissions")
    problem = relationship("CodingProblem")


class UserProblemStatus(Base):
    """Per-user progress on a single problem (drives Solved/Unsolved filters)."""
    __tablename__ = "user_problem_status"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    problem_id = Column(String(36), ForeignKey("coding_problems.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(20), default="attempted")   # attempted | solved
    attempts = Column(Integer, default=0)
    best_score = Column(Integer, default=0)
    points_earned = Column(Integer, default=0)
    revealed_hints = Column(Integer, default=0)
    last_language = Column(String(30), default="")
    drafts = Column(JSON, default=dict)                # {language: code}
    first_solved_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


# ─── Aptitude Quest ──────────────────────────────────────────────

class MCQQuestion(Base):
    __tablename__ = "mcq_questions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    question_text = Column(Text, nullable=False)
    options = Column(JSON, nullable=False)
    correct_index = Column(Integer, nullable=False)
    topic = Column(String(100), default="general")
    subtopic = Column(String(100), nullable=True)
    difficulty = Column(String(20), default=Difficulty.EASY)
    explanation = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    quiz_type = Column(String(50), default="aptitude")
    topic = Column(String(100), nullable=True)
    score = Column(Integer, default=0)
    total = Column(Integer, default=0)
    percentage = Column(Float, default=0.0)
    answers = Column(JSON, default=list)
    time_taken_seconds = Column(Integer, nullable=True)
    started_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="quiz_attempts")


# ─── Personality Test ────────────────────────────────────────────

class PersonalityResult(Base):
    __tablename__ = "personality_results"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    openness = Column(Float, default=0.0)
    conscientiousness = Column(Float, default=0.0)
    extraversion = Column(Float, default=0.0)
    agreeableness = Column(Float, default=0.0)
    neuroticism = Column(Float, default=0.0)
    raw_answers = Column(JSON, default=list)
    completed_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="personality_result")


# ─── Documents ───────────────────────────────────────────────────

class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    doc_type = Column(String(30), default=DocumentType.OTHER)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, default=0)
    parsed_text = Column(Text, nullable=True)
    label = Column(String(255), default="")        # display name, e.g. "3rd year scorecard"
    is_public = Column(Boolean, default=False)     # surfaced to recruiters on the public profile
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="documents")


# ─── Interview Coach ─────────────────────────────────────────────

class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    mode = Column(String(20), default=InterviewMode.STRUCTURED)
    job_context = Column(String(255), nullable=True)
    transcript = Column(JSON, default=list)
    scores = Column(JSON, default=dict)
    feedback = Column(Text, nullable=True)
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="interview_sessions")


# ─── Events ──────────────────────────────────────────────────────

class Event(Base):
    __tablename__ = "events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False)
    description = Column(Text, default="")
    event_date = Column(DateTime(timezone=True), nullable=False)
    location = Column(String(255), default="")
    event_url = Column(String(500), nullable=True)
    capacity = Column(Integer, nullable=True)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class EventRegistration(Base):
    __tablename__ = "event_registrations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    event_id = Column(String(36), ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    registered_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


# ─── Gamification ────────────────────────────────────────────────

class XPLog(Base):
    __tablename__ = "xp_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    action = Column(String(100), nullable=False)
    points = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="xp_logs")


class Badge(Base):
    __tablename__ = "badges"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, default="")
    icon = Column(String(50), default="🏆")
    criteria = Column(JSON, default=dict)


class UserBadge(Base):
    __tablename__ = "user_badges"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    badge_id = Column(String(36), ForeignKey("badges.id", ondelete="CASCADE"), nullable=False)
    earned_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class LeaderboardEntry(Base):
    __tablename__ = "leaderboard"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    total_xp = Column(Integer, default=0)
    level = Column(Integer, default=1)
    problems_solved = Column(Integer, default=0)
    quizzes_passed = Column(Integer, default=0)
    streak_days = Column(Integer, default=0)
    last_active = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="leaderboard_entry")


# ─── Notifications ───────────────────────────────────────────────

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), default="info")
    read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


# ─── Profile Sections ────────────────────────────────────────────
# Every section below is intentionally institution-agnostic so the same
# blueprint works for any student on the platform.


class Education(Base):
    __tablename__ = "educations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    institute = Column(String(255), nullable=False)
    degree = Column(String(255), default="")            # BE/B.Tech, MCA ...
    specialization = Column(String(255), default="")    # Artificial Intelligence and Data Science
    start_year = Column(String(10), default="")
    end_year = Column(String(10), default="")
    cgpa = Column(Float, nullable=True)
    cgpa_scale = Column(Float, default=10.0)
    percentage = Column(Float, nullable=True)
    is_current = Column(Boolean, default=True)
    ongoing_backlogs = Column(Integer, default=0)
    total_backlogs = Column(Integer, default=0)
    # [{semester, cgpa, ongoing_backlogs, total_backlogs, marksheet_doc_id}]
    semesters = Column(JSON, default=list)
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class WorkExperience(Base):
    __tablename__ = "work_experiences"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    company = Column(String(255), nullable=False)
    role = Column(String(255), nullable=False)
    employment_type = Column(String(50), default="Internship")  # Internship | Full-time | Part-time | Freelance
    location = Column(String(255), default="")
    start_date = Column(String(20), default="")
    end_date = Column(String(20), default="")
    is_current = Column(Boolean, default=False)
    highlights = Column(JSON, default=list)             # list[str] bullet points
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class PositionOfResponsibility(Base):
    __tablename__ = "positions_of_responsibility"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)         # Campaigning Coordinator
    event_name = Column(String(255), default="")        # Udbhav College Fest
    department = Column(String(255), default="")        # Department of Co-Curricular Activities
    organization = Column(String(255), default="")
    start_date = Column(String(20), default="")
    end_date = Column(String(20), default="")
    highlights = Column(JSON, default=list)             # list[str]
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class ProfileProject(Base):
    __tablename__ = "profile_projects"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    subtitle = Column(String(255), default="")
    description = Column(Text, default="")
    tech_stack = Column(JSON, default=list)
    highlights = Column(JSON, default=list)             # list[str]
    start_date = Column(String(20), default="")
    end_date = Column(String(20), default="")
    is_ongoing = Column(Boolean, default=False)
    project_url = Column(String(500), default="")
    repo_url = Column(String(500), default="")
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Award(Base):
    __tablename__ = "awards"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    issued_by = Column(String(255), default="")
    issue_date = Column(String(20), default="")
    achievement_type = Column(String(100), default="Academic")   # Academic | Sports | Cultural | Technical | Other
    description = Column(Text, default="")
    award_url = Column(String(500), default="")
    certificate_doc_id = Column(String(36), nullable=True)
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Certification(Base):
    __tablename__ = "certifications"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    issuer = Column(String(255), default="")
    course_duration = Column(String(100), default="")
    validity = Column(String(100), default="Lifetime Validity")
    cert_type = Column(String(100), default="")          # English | Aptitude | Mock Interviews | Others
    specialization = Column(String(255), default="")
    courses = Column(String(500), default="")
    pre_assessment_score = Column(String(50), default="")
    marks_obtained = Column(String(50), default="")
    points_earned = Column(String(50), default="")
    conclusion = Column(String(100), default="")         # Completed | In Progress
    credential_url = Column(String(500), default="")
    certificate_doc_id = Column(String(36), nullable=True)
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class BenchmarkScore(Base):
    """Generic replacement for a vendor-specific aptitude benchmark
    (baseline / midline / endline employability assessment)."""
    __tablename__ = "benchmark_scores"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    stage = Column(String(20), nullable=False)           # baseline | midline | endline
    provider = Column(String(100), default="")
    analytical_score = Column(Float, nullable=True)
    logical_score = Column(Float, nullable=True)
    verbal_score = Column(Float, nullable=True)
    quantitative_score = Column(Float, nullable=True)
    total_score = Column(Float, nullable=True)
    taken_on = Column(String(20), default="")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    source = Column(String(50), default="generated")     # generated | existing | tailored
    template = Column(String(100), default="")
    ats_score = Column(Integer, nullable=True)
    status = Column(String(30), default="ready")         # ready | processing | draft
    is_primary = Column(Boolean, default=False)
    target_job_id = Column(String(36), nullable=True)    # set for tailored copies
    document_id = Column(String(36), nullable=True)      # link to uploaded file, if any
    content = Column(JSON, default=dict)                 # structured snapshot for generated resumes
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class ScorecardEntry(Base):
    """Manually tracked scores shown under "Other Scores" / "Custom Event Score"."""
    __tablename__ = "scorecard_entries"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    category = Column(String(30), default="other")       # other | custom_event
    title = Column(String(255), nullable=False)
    score = Column(Float, default=0)
    max_score = Column(Float, nullable=True)
    scored_on = Column(String(20), default="")
    notes = Column(Text, default="")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
