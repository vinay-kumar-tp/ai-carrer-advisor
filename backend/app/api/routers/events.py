"""Events — career fairs, hackathons, webinars, bootcamps and more.

Mirrors the Job Board's shape: a faceted list endpoint, a rich detail endpoint
that attaches the registration form plus profile prefill, and a registration
endpoint that validates the standard attendee details and the event's own
custom questions, enforces capacity, awards XP and drops a notification.
"""

from __future__ import annotations

import datetime
import secrets

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.routers.profile import _build_aggregate
from app.core.security import decode_token, get_current_user_id, oauth2_scheme
from app.db.session import get_db
from app.models.models import (
    Event,
    EventRegistration,
    LeaderboardEntry,
    Notification,
    XPLog,
)
from app.schemas.events import (
    EventCard,
    EventCreateRequest,
    EventDetail,
    EventFacets,
    EventListResponse,
    EventRegisterRequest,
    EventRegisterResponse,
    FacetCount,
    MyRegistration,
)
from app.schemas.schemas import MessageResponse
from app.services import eligibility as elig

router = APIRouter()

REGISTER_XP = 10


def _now():
    return datetime.datetime.now(datetime.timezone.utc)


def _aware(value):
    """SQLite hands back naive datetimes — normalise before comparing."""
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=datetime.timezone.utc)
    return value


# ─── Serializers ─────────────────────────────────────────────────

def _card(event: Event, seats_taken: int = 0, registration: EventRegistration | None = None) -> dict:
    capacity = event.capacity
    seats_left = max(0, capacity - seats_taken) if capacity else None
    start = _aware(event.event_date)
    return {
        "id": str(event.id),
        "slug": event.slug,
        "title": event.title,
        "description": event.description or "",
        "event_type": event.event_type or "webinar",
        "mode": event.mode or "Online",
        "event_date": event.event_date,
        "end_date": event.end_date,
        "timezone_label": event.timezone_label or "IST",
        "duration_minutes": event.duration_minutes,
        "registration_deadline": event.registration_deadline,
        "location": event.location or "",
        "venue": event.venue or "",
        "city": event.city or "",
        "event_url": event.event_url,
        "host_company": event.host_company or "",
        "host_domain": event.host_domain or "",
        "host_logo": event.host_logo or "",
        "host_tagline": event.host_tagline or "",
        "capacity": capacity,
        "seats_taken": seats_taken,
        "seats_left": seats_left,
        "price": event.price or 0,
        "currency": event.currency or "INR",
        "is_certified": bool(event.is_certified),
        "is_featured": bool(event.is_featured),
        "tags": event.tags or [],
        "registered": registration is not None and registration.status != "cancelled",
        "registration_status": registration.status if registration else None,
        "is_full": bool(capacity and seats_taken >= capacity),
        "is_past": bool(start and start < _now()),
    }


def _detail(event: Event, seats_taken: int, registration, aggregate: dict) -> dict:
    data = _card(event, seats_taken, registration)
    prefill = elig.build_prefill(aggregate)
    data.update(
        {
            "about": event.about or "",
            "agenda": event.agenda or [],
            "speakers": event.speakers or [],
            "prizes": event.prizes or [],
            "perks": event.perks or [],
            "eligibility": event.eligibility or [],
            "registration_questions": event.registration_questions or [],
            "prefill": prefill,
        }
    )
    return data


async def _seats_taken_map(db: AsyncSession, event_ids: list[str]) -> dict[str, int]:
    if not event_ids:
        return {}
    rows = (
        await db.execute(
            select(EventRegistration.event_id, func.count(EventRegistration.id))
            .where(
                EventRegistration.event_id.in_(event_ids),
                EventRegistration.status != "cancelled",
            )
            .group_by(EventRegistration.event_id)
        )
    ).all()
    return {event_id: count for event_id, count in rows}


async def _award_xp(db: AsyncSession, user_id: str, points: int, action: str):
    if points <= 0:
        return
    db.add(XPLog(user_id=user_id, action=action, points=points))
    lb = (
        await db.execute(select(LeaderboardEntry).where(LeaderboardEntry.user_id == user_id))
    ).scalar_one_or_none()
    if lb is None:
        lb = LeaderboardEntry(user_id=user_id, total_xp=0)
        db.add(lb)
        await db.flush()
    lb.total_xp = (lb.total_xp or 0) + points
    lb.level = max(1, (lb.total_xp or 0) // 100 + 1)
    lb.last_active = _now()


async def _find_event(db: AsyncSession, event_id: str) -> Event:
    row = (
        await db.execute(select(Event).where(or_(Event.id == event_id, Event.slug == event_id)))
    ).scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Event not found")
    return row


# ─── List + filters ──────────────────────────────────────────────

@router.get("/", response_model=EventListResponse)
@router.get("", response_model=EventListResponse)
async def list_events(
    keyword: str = Query(None),
    event_type: str = Query(None),
    mode: str = Query(None),
    host: str = Query(None),
    city: str = Query(None),
    price: str = Query(None),            # free | paid
    status: str = Query(None),           # upcoming | past | registered
    sort: str = Query("soonest"),        # soonest | newest | seats
    skip: int = Query(0, ge=0),
    limit: int = Query(24, ge=1, le=100),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    query = select(Event).where(Event.is_active == True)  # noqa: E712

    if keyword:
        like = f"%{keyword}%"
        query = query.where(
            or_(
                Event.title.ilike(like),
                Event.description.ilike(like),
                Event.host_company.ilike(like),
                Event.about.ilike(like),
            )
        )
    if event_type:
        query = query.where(Event.event_type == event_type)
    if mode:
        query = query.where(Event.mode == mode)
    if host:
        query = query.where(Event.host_company == host)
    if city:
        query = query.where(Event.city.ilike(f"%{city}%"))
    if price == "free":
        query = query.where(or_(Event.price == 0, Event.price.is_(None)))
    elif price == "paid":
        query = query.where(Event.price > 0)

    if sort == "newest":
        query = query.order_by(Event.created_at.desc())
    else:
        query = query.order_by(Event.event_date.asc())

    events = list((await db.execute(query)).scalars().all())

    # The user's registrations, so cards can show their state after a reload.
    regs = {
        r.event_id: r
        for r in (
            await db.execute(select(EventRegistration).where(EventRegistration.user_id == user_id))
        ).scalars().all()
    }

    now = _now()
    if status == "upcoming":
        events = [e for e in events if (_aware(e.event_date) or now) >= now]
    elif status == "past":
        events = [e for e in events if (_aware(e.event_date) or now) < now]
    elif status == "registered":
        events = [e for e in events if e.id in regs and regs[e.id].status != "cancelled"]

    seats = await _seats_taken_map(db, [e.id for e in events])

    if sort == "seats":
        events.sort(key=lambda e: seats.get(e.id, 0), reverse=True)

    total = len(events)
    page = events[skip : skip + limit]

    return EventListResponse(
        items=[EventCard(**_card(e, seats.get(e.id, 0), regs.get(e.id))) for e in page],
        total=total,
        skip=skip,
        limit=limit,
    )


# ─── Facets ──────────────────────────────────────────────────────

@router.get("/facets", response_model=EventFacets)
async def event_facets(db: AsyncSession = Depends(get_db)):
    events = (
        await db.execute(select(Event).where(Event.is_active == True))  # noqa: E712
    ).scalars().all()

    def tally(values) -> list[FacetCount]:
        counts: dict[str, int] = {}
        for v in values:
            if v:
                counts[v] = counts.get(v, 0) + 1
        return [
            FacetCount(name=name, count=count)
            for name, count in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
        ]

    return EventFacets(
        event_types=tally(e.event_type for e in events),
        modes=tally(e.mode for e in events),
        hosts=tally(e.host_company for e in events),
        cities=tally(e.city for e in events),
        total=len(events),
    )


# ─── My registrations ────────────────────────────────────────────

@router.get("/my-registrations", response_model=list[MyRegistration])
async def my_registrations(
    user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)
):
    rows = (
        await db.execute(
            select(EventRegistration, Event)
            .join(Event, EventRegistration.event_id == Event.id)
            .where(EventRegistration.user_id == user_id)
            .order_by(EventRegistration.registered_at.desc())
        )
    ).all()

    seats = await _seats_taken_map(db, [event.id for _, event in rows])
    return [
        MyRegistration(
            registration_id=str(reg.id),
            ticket_code=reg.ticket_code or "",
            status=reg.status or "registered",
            registered_at=reg.registered_at,
            event=EventCard(**_card(event, seats.get(event.id, 0), reg)),
        )
        for reg, event in rows
    ]


# ─── Detail ──────────────────────────────────────────────────────

@router.get("/{event_id}", response_model=EventDetail)
async def get_event(
    event_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    event = await _find_event(db, event_id)
    seats = (await _seats_taken_map(db, [event.id])).get(event.id, 0)
    registration = (
        await db.execute(
            select(EventRegistration).where(
                EventRegistration.user_id == user_id, EventRegistration.event_id == event.id
            )
        )
    ).scalar_one_or_none()
    aggregate = await _build_aggregate(db, user_id)
    return EventDetail(**_detail(event, seats, registration, aggregate))


# ─── Register ────────────────────────────────────────────────────

@router.post("/{event_id}/register", response_model=EventRegisterResponse, status_code=201)
async def register_event(
    event_id: str,
    data: EventRegisterRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    event = await _find_event(db, event_id)

    existing = (
        await db.execute(
            select(EventRegistration).where(
                EventRegistration.user_id == user_id, EventRegistration.event_id == event.id
            )
        )
    ).scalar_one_or_none()
    if existing and existing.status != "cancelled":
        raise HTTPException(status_code=400, detail="Already registered for this event")

    if not data.agree_terms:
        raise HTTPException(
            status_code=400, detail="Please accept the event terms and code of conduct to register"
        )

    start = _aware(event.event_date)
    if start and start < _now():
        raise HTTPException(status_code=400, detail="This event has already taken place")

    deadline = _aware(event.registration_deadline)
    if deadline and deadline < _now():
        raise HTTPException(status_code=400, detail="Registration for this event has closed")

    # Validate the event's own custom questions (presence only, as with jobs).
    answers = dict(data.answers or {})
    for q in event.registration_questions or []:
        if q.get("required"):
            val = answers.get(q.get("key"))
            if val is None or (isinstance(val, str) and not val.strip()) or (isinstance(val, list) and not val):
                raise HTTPException(
                    status_code=400, detail=f"'{q.get('label') or q.get('key')}' is required"
                )

    # Capacity: fill seats, then waitlist rather than hard-failing.
    seats_taken = (await _seats_taken_map(db, [event.id])).get(event.id, 0)
    status = "registered"
    if event.capacity and seats_taken >= event.capacity:
        status = "waitlisted"

    snapshot = data.model_dump(exclude={"answers"})
    ticket_code = f"CP-{secrets.token_hex(3).upper()}"

    if existing:
        # Re-registering after a cancellation reuses the row.
        existing.answers = answers
        existing.profile_snapshot = snapshot
        existing.status = status
        existing.ticket_code = ticket_code
        existing.registered_at = _now()
        registration = existing
    else:
        registration = EventRegistration(
            user_id=user_id,
            event_id=event.id,
            answers=answers,
            profile_snapshot=snapshot,
            status=status,
            ticket_code=ticket_code,
        )
        db.add(registration)

    await db.flush()

    await _award_xp(db, user_id, REGISTER_XP, "event_registration")
    host = f" hosted by {event.host_company}" if event.host_company else ""
    db.add(
        Notification(
            user_id=user_id,
            message=(
                f"You're {'waitlisted for' if status == 'waitlisted' else 'registered for'} "
                f"{event.title}{host}. Ticket {ticket_code}."
            ),
            notification_type="event",
        )
    )

    return EventRegisterResponse(
        message=(
            "You're on the waitlist — we'll email you if a seat frees up."
            if status == "waitlisted"
            else "Registration confirmed. Check your notifications for the ticket."
        ),
        registration_id=str(registration.id),
        ticket_code=ticket_code,
        status=status,
    )


# ─── Cancel ──────────────────────────────────────────────────────

@router.delete("/{event_id}/register", response_model=MessageResponse)
async def cancel_registration(
    event_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    event = await _find_event(db, event_id)
    registration = (
        await db.execute(
            select(EventRegistration).where(
                EventRegistration.user_id == user_id, EventRegistration.event_id == event.id
            )
        )
    ).scalar_one_or_none()
    if not registration or registration.status == "cancelled":
        raise HTTPException(status_code=404, detail="You are not registered for this event")

    registration.status = "cancelled"
    return MessageResponse(message="Registration cancelled")


# ─── Admin create ────────────────────────────────────────────────

@router.post("/", response_model=EventCard, status_code=201)
async def create_event(
    data: EventCreateRequest,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    payload = decode_token(token)
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    event = Event(**data.model_dump())
    db.add(event)
    await db.flush()
    return EventCard(**_card(event, 0, None))
