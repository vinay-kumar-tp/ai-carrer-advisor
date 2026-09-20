"""Events — request/response schemas for the events board and registration."""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, EmailStr, Field


# ─── Shared sub-models ────────────────────────────────────────────

class EventQuestion(BaseModel):
    key: str
    label: str
    type: str = "text"  # text|textarea|number|select|multiselect|boolean|url|date
    required: bool = False
    options: list[str] = Field(default_factory=list)
    placeholder: str = ""
    help: str = ""


class AgendaItem(BaseModel):
    time: str = ""
    title: str = ""
    detail: str = ""


class Speaker(BaseModel):
    name: str = ""
    title: str = ""
    company: str = ""


# ─── Requests ─────────────────────────────────────────────────────

class EventRegisterRequest(BaseModel):
    """Everything a standard event registration collects.

    The named fields are the details every event asks for; `answers` carries
    the per-event custom questions (same contract as the job apply flow).
    """

    full_name: str = Field(min_length=2, max_length=255)
    email: EmailStr
    phone: str = Field(min_length=6, max_length=30)

    organization: str = ""          # college or employer
    designation: str = ""           # student / role title
    degree: str = ""
    branch: str = ""
    graduation_year: Optional[int] = None
    experience_level: str = ""      # Fresher | 0-1 years | ...

    city: str = ""
    country: str = ""

    linkedin_url: str = ""
    github_url: str = ""
    portfolio_url: str = ""
    resume_url: str = ""

    heard_from: str = ""            # referral source
    dietary_preference: str = ""    # in-person catering
    tshirt_size: str = ""           # in-person swag
    accessibility_needs: str = ""
    emergency_contact: str = ""     # in-person safety

    motivation: str = ""            # "why do you want to attend"
    consent_updates: bool = False
    agree_terms: bool = False

    answers: dict[str, Any] = Field(default_factory=dict)


class EventCreateRequest(BaseModel):
    title: str
    description: str = ""
    event_date: datetime
    location: str = ""
    event_url: Optional[str] = None
    capacity: Optional[int] = None
    host_company: str = ""
    host_domain: str = ""
    host_logo: str = ""
    event_type: str = "webinar"
    mode: str = "Online"


# ─── Responses ────────────────────────────────────────────────────

class EventCard(BaseModel):
    id: str
    slug: Optional[str] = None
    title: str
    description: str
    event_type: str
    mode: str
    event_date: datetime
    end_date: Optional[datetime] = None
    timezone_label: str = "IST"
    duration_minutes: Optional[int] = None
    registration_deadline: Optional[datetime] = None
    location: str = ""
    venue: str = ""
    city: str = ""
    event_url: Optional[str] = None

    host_company: str = ""
    host_domain: str = ""
    host_logo: str = ""
    host_tagline: str = ""

    capacity: Optional[int] = None
    seats_taken: int = 0
    seats_left: Optional[int] = None
    price: int = 0
    currency: str = "INR"
    is_certified: bool = False
    is_featured: bool = False
    tags: list[str] = Field(default_factory=list)

    registered: bool = False
    registration_status: Optional[str] = None
    is_full: bool = False
    is_past: bool = False


class EventDetail(EventCard):
    about: str = ""
    agenda: list[AgendaItem] = Field(default_factory=list)
    speakers: list[Speaker] = Field(default_factory=list)
    prizes: list[str] = Field(default_factory=list)
    perks: list[str] = Field(default_factory=list)
    eligibility: list[str] = Field(default_factory=list)
    registration_questions: list[EventQuestion] = Field(default_factory=list)
    prefill: dict[str, Any] = Field(default_factory=dict)


class FacetCount(BaseModel):
    name: str
    count: int


class EventFacets(BaseModel):
    event_types: list[FacetCount] = Field(default_factory=list)
    modes: list[FacetCount] = Field(default_factory=list)
    hosts: list[FacetCount] = Field(default_factory=list)
    cities: list[FacetCount] = Field(default_factory=list)
    total: int = 0


class EventListResponse(BaseModel):
    items: list[EventCard]
    total: int
    skip: int
    limit: int


class MyRegistration(BaseModel):
    registration_id: str
    ticket_code: str
    status: str
    registered_at: datetime
    event: EventCard


class EventRegisterResponse(BaseModel):
    message: str
    success: bool = True
    registration_id: str
    ticket_code: str
    status: str
