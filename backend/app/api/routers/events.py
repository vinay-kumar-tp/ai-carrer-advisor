from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.models.models import Event, EventRegistration, User
from app.schemas.schemas import EventCreate, EventResponse, MessageResponse
from app.core.security import get_current_user_id, decode_token, oauth2_scheme

router = APIRouter()

@router.get("/", response_model=list[EventResponse])
async def list_events(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Event).order_by(Event.event_date.asc()))
    events = result.scalars().all()
    return [
        EventResponse(
            id=str(e.id),
            title=e.title,
            description=e.description,
            event_date=e.event_date,
            location=e.location,
            event_url=e.event_url,
            capacity=e.capacity
        )
        for e in events
    ]

@router.post("/", response_model=EventResponse, status_code=201)
async def create_event(
    data: EventCreate,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    payload = decode_token(token)
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    event = Event(**data.model_dump())
    db.add(event)
    await db.flush()

    return EventResponse(
        id=str(event.id),
        title=event.title,
        description=event.description,
        event_date=event.event_date,
        location=event.location,
        event_url=event.event_url,
        capacity=event.capacity
    )

@router.post("/{event_id}/register", response_model=MessageResponse)
async def register_event(
    event_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    res = await db.execute(select(Event).where(Event.id == event_id))
    if not res.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Event not found")

    existing = await db.execute(
        select(EventRegistration).where(EventRegistration.user_id == user_id, EventRegistration.event_id == event_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Already registered for this event")

    reg = EventRegistration(user_id=user_id, event_id=event_id)
    db.add(reg)
    return MessageResponse(message="Successfully registered for event")
