"""Job Board — rich company postings across 20 portals with system-checked
eligibility, auto-filled applications, job alerts and an upgraded tracker.

The list endpoint powers the faceted filter sidebar (type/status/role/location/
industry/employer/mode/experience/posted-in/CTC/stipend); the detail endpoint
attaches a per-candidate eligibility verdict and the application prefill; apply
records the answers + a profile snapshot, awards XP and drops a notification.
"""

from __future__ import annotations

import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.routers.profile import _build_aggregate
from app.core.security import decode_token, get_current_user_id, oauth2_scheme
from app.db.session import get_db
from app.models.models import (
    Application,
    JobListing,
    LeaderboardEntry,
    Notification,
    Profile,
    XPLog,
)
from app.schemas.schemas import (
    ApplicationCreate,
    ApplicationResponse,
    JobAlertToggle,
    JobCreate,
    JobResponse,
    MessageResponse,
)
from app.services import eligibility as elig

router = APIRouter()

APPLY_XP = 15
POSTED_WINDOWS = {"7": 7, "30": 30, "60": 60}


def _now():
    return datetime.datetime.now(datetime.timezone.utc)


# ─── Serializers ─────────────────────────────────────────────────

def _card(job: JobListing) -> dict:
    return {
        "id": str(job.id),
        "title": job.title,
        "company": job.company,
        "description": job.description,
        "location": job.location or "",
        "remote": bool(job.remote),
        "salary_range": job.salary_range,
        "required_skills": job.required_skills or [],
        "experience_level": job.experience_level or "entry",
        "job_type": job.job_type or "full-time",
        "posted_at": job.posted_at,
        "slug": job.slug,
        "source_portal": job.source_portal or "LinkedIn",
        "company_logo": job.company_logo or "",
        "company_tagline": job.company_tagline or "",
        "industry": job.industry or "",
        "employment_mode": job.employment_mode or "In Office",
        "openings": job.openings or 1,
        "application_deadline": job.application_deadline or "",
        "ctc_min": job.ctc_min,
        "ctc_max": job.ctc_max,
        "stipend_min": job.stipend_min,
        "stipend_max": job.stipend_max,
        "experience_min_years": job.experience_min_years or 0.0,
        "experience_max_years": job.experience_max_years,
    }


def _detail(job: JobListing) -> dict:
    data = _card(job)
    data.update(
        {
            "about_company": job.about_company or "",
            "responsibilities": job.responsibilities or [],
            "qualifications": job.qualifications or [],
            "perks": job.perks or [],
            "ctc_breakdown": job.ctc_breakdown or [],
            "eligibility_criteria": job.eligibility or [],
            "apply_questions": job.apply_questions or [],
        }
    )
    return data


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


# ─── List + filters ──────────────────────────────────────────────

@router.get("/")
async def list_jobs(
    keyword: str = Query(None),
    location: str = Query(None),
    job_type: str = Query(None),
    role: str = Query(None),
    industry: str = Query(None),
    employer: str = Query(None),
    employment_mode: str = Query(None),
    source_portal: str = Query(None),
    experience_level: str = Query(None),
    remote: bool = Query(None),
    min_experience: float = Query(None),
    max_experience: float = Query(None),
    posted_in: str = Query(None),          # "7" | "30" | "60"
    min_ctc: int = Query(None),
    max_ctc: int = Query(None),
    min_stipend: int = Query(None),
    max_stipend: int = Query(None),
    status: str = Query(None),             # applied | not_applied
    sort: str = Query("recent"),           # recent | ctc_high | ctc_low
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    query = select(JobListing).where(JobListing.is_active == True)  # noqa: E712

    if keyword:
        search = f"%{keyword}%"
        query = query.where(
            or_(
                JobListing.title.ilike(search),
                JobListing.company.ilike(search),
                JobListing.description.ilike(search),
            )
        )
    if location:
        query = query.where(JobListing.location.ilike(f"%{location}%"))
    if job_type:
        query = query.where(JobListing.job_type == job_type)
    if role:
        query = query.where(JobListing.title.ilike(f"%{role}%"))
    if industry:
        query = query.where(JobListing.industry == industry)
    if employer:
        query = query.where(JobListing.company == employer)
    if employment_mode:
        query = query.where(JobListing.employment_mode == employment_mode)
    if source_portal:
        query = query.where(JobListing.source_portal == source_portal)
    if experience_level:
        query = query.where(JobListing.experience_level == experience_level)
    if remote is not None:
        query = query.where(JobListing.remote == remote)
    if min_experience is not None:
        query = query.where(JobListing.experience_min_years >= min_experience)
    if max_experience is not None:
        query = query.where(JobListing.experience_min_years <= max_experience)
    if posted_in in POSTED_WINDOWS:
        cutoff = _now() - datetime.timedelta(days=POSTED_WINDOWS[posted_in])
        query = query.where(JobListing.posted_at >= cutoff)
    if min_ctc is not None:
        query = query.where(JobListing.ctc_max >= min_ctc)
    if max_ctc is not None:
        query = query.where(JobListing.ctc_min <= max_ctc)
    if min_stipend is not None:
        query = query.where(JobListing.stipend_max >= min_stipend)
    if max_stipend is not None:
        query = query.where(JobListing.stipend_min <= max_stipend)

    if sort == "ctc_high":
        query = query.order_by(JobListing.ctc_max.desc().nullslast(), JobListing.posted_at.desc())
    elif sort == "ctc_low":
        query = query.order_by(JobListing.ctc_min.asc().nullsfirst(), JobListing.posted_at.desc())
    else:
        query = query.order_by(JobListing.posted_at.desc())

    all_matching = (await db.execute(query)).scalars().all()

    # Application status filter is applied in Python (needs the user's set).
    applied_ids = {
        row.job_id
        for row in (
            await db.execute(select(Application).where(Application.user_id == user_id))
        ).scalars().all()
    }
    if status == "applied":
        all_matching = [j for j in all_matching if j.id in applied_ids]
    elif status == "not_applied":
        all_matching = [j for j in all_matching if j.id not in applied_ids]

    total = len(all_matching)
    page = all_matching[skip : skip + limit]

    items = []
    for job in page:
        card = _card(job)
        card["applied"] = job.id in applied_ids
        items.append(card)

    return {"items": items, "total": total, "skip": skip, "limit": limit}


# ─── Facets for the filter sidebar ───────────────────────────────

@router.get("/facets")
async def job_facets(db: AsyncSession = Depends(get_db)):
    jobs = (
        await db.execute(select(JobListing).where(JobListing.is_active == True))  # noqa: E712
    ).scalars().all()

    def tally(values):
        counts: dict[str, int] = {}
        for v in values:
            if v:
                counts[v] = counts.get(v, 0) + 1
        return [
            {"name": name, "count": count}
            for name, count in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
        ]

    roles: dict[str, int] = {}
    for j in jobs:
        roles[j.title] = roles.get(j.title, 0) + 1

    return {
        "job_types": tally(j.job_type for j in jobs),
        "roles": tally(j.title for j in jobs),
        "locations": tally(j.location for j in jobs),
        "industries": tally(j.industry for j in jobs),
        "employers": tally(j.company for j in jobs),
        "employment_modes": tally(j.employment_mode for j in jobs),
        "portals": tally(j.source_portal for j in jobs),
        "total": len(jobs),
    }


# ─── Detail + eligibility + prefill ──────────────────────────────

async def _find_job(db: AsyncSession, job_id: str) -> JobListing:
    row = (
        await db.execute(
            select(JobListing).where(
                or_(JobListing.id == job_id, JobListing.slug == job_id)
            )
        )
    ).scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Job not found")
    return row


@router.get("/{job_id}")
async def get_job(
    job_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    job = await _find_job(db, job_id)
    aggregate = await _build_aggregate(db, user_id)

    data = _detail(job)
    data["eligibility"] = elig.evaluate(aggregate, job)
    data["prefill"] = elig.build_prefill(aggregate)

    existing = (
        await db.execute(
            select(Application).where(
                Application.user_id == user_id, Application.job_id == job.id
            )
        )
    ).scalar_one_or_none()
    data["applied"] = existing is not None
    data["application_status"] = existing.status if existing else None
    return data


# ─── Admin create ────────────────────────────────────────────────

@router.post("/", response_model=JobResponse, status_code=201)
async def create_job(
    data: JobCreate,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    payload = decode_token(token)
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    job = JobListing(**data.model_dump())
    db.add(job)
    await db.flush()
    await _fan_out_alerts(db, job)
    return JobResponse.model_validate(_card(job))


# ─── Apply (auto-filled) ─────────────────────────────────────────

@router.post("/{job_id}/apply", response_model=ApplicationResponse, status_code=201)
async def apply_to_job(
    job_id: str,
    data: ApplicationCreate = None,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    job = await _find_job(db, job_id)

    existing = (
        await db.execute(
            select(Application).where(
                Application.user_id == user_id, Application.job_id == job.id
            )
        )
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Already applied to this job")

    aggregate = await _build_aggregate(db, user_id)
    verdict = elig.evaluate(aggregate, job)
    if not verdict["eligible"]:
        missing = [c["label"] for c in verdict["criteria"] if not c["met"]]
        raise HTTPException(
            status_code=400,
            detail="You do not meet the eligibility criteria: " + ", ".join(missing),
        )

    answers = dict((data.answers if data and data.answers else {}) or {})

    # Validate required custom questions were answered.
    for q in job.apply_questions or []:
        if q.get("required"):
            val = answers.get(q.get("key"))
            if val is None or (isinstance(val, str) and not val.strip()) or (isinstance(val, list) and not val):
                raise HTTPException(
                    status_code=400,
                    detail=f"'{q.get('label') or q.get('key')}' is required",
                )

    app = Application(
        user_id=user_id,
        job_id=job.id,
        answers=answers,
        profile_snapshot=elig.build_prefill(aggregate),
        eligibility_snapshot=verdict,
    )
    if data:
        if data.cover_letter:
            app.cover_letter = data.cover_letter
        if data.resume_id:
            app.resume_id = data.resume_id
    db.add(app)
    await db.flush()

    await _award_xp(db, user_id, APPLY_XP, "job_application")
    db.add(
        Notification(
            user_id=user_id,
            message=f"Application submitted for {job.title} at {job.company} (via {job.source_portal}).",
            notification_type="application",
        )
    )

    return ApplicationResponse(
        id=str(app.id), job_id=str(app.job_id), status=app.status, applied_at=app.applied_at
    )


# ─── My applications (enriched tracker) ──────────────────────────

@router.get("/applications/mine")
async def my_applications(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    apps = (
        await db.execute(
            select(Application)
            .where(Application.user_id == user_id)
            .order_by(Application.applied_at.desc())
        )
    ).scalars().all()

    job_ids = [a.job_id for a in apps]
    jobs = {}
    if job_ids:
        rows = (
            await db.execute(select(JobListing).where(JobListing.id.in_(job_ids)))
        ).scalars().all()
        jobs = {j.id: j for j in rows}

    out = []
    for a in apps:
        job = jobs.get(a.job_id)
        out.append(
            {
                "id": str(a.id),
                "job_id": str(a.job_id),
                "status": a.status,
                "applied_at": a.applied_at,
                "updated_at": a.updated_at,
                "answers": a.answers or {},
                "cover_letter": a.cover_letter,
                "job": _card(job) if job else None,
            }
        )
    return out


# ─── Job alerts ──────────────────────────────────────────────────

@router.get("/alerts/status")
async def alert_status(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    profile = (
        await db.execute(select(Profile).where(Profile.user_id == user_id))
    ).scalar_one_or_none()
    enabled = True if profile is None else bool(profile.job_alerts_enabled)
    return {"enabled": enabled}


@router.put("/alerts")
async def set_alerts(
    data: JobAlertToggle,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    profile = (
        await db.execute(select(Profile).where(Profile.user_id == user_id))
    ).scalar_one_or_none()
    if profile is None:
        profile = Profile(user_id=user_id)
        db.add(profile)
        await db.flush()
    profile.job_alerts_enabled = bool(data.enabled)
    db.add(
        Notification(
            user_id=user_id,
            message="Job alerts turned ON — we'll notify you about matching roles."
            if data.enabled
            else "Job alerts turned OFF.",
            notification_type="alert",
        )
    )
    await db.flush()
    return {"enabled": bool(profile.job_alerts_enabled)}


def _matches_preferences(profile: Profile, job: JobListing) -> bool:
    """Loose match: role keyword, open_for job type, or preferred location."""
    roles = [r.lower() for r in (profile.job_roles or [])]
    open_for = [o.lower().replace(" ", "-") for o in (profile.open_for or [])]
    locs = [l.lower() for l in (profile.preferred_locations or [])]

    title = (job.title or "").lower()
    if roles and any(r and r in title for r in roles):
        return True
    if open_for and (job.job_type or "").lower() in open_for:
        return True
    if locs and any(l and l in (job.location or "").lower() for l in locs):
        return True
    # No preferences set at all -> still alert (opted in by default).
    return not (roles or open_for or locs)


async def _fan_out_alerts(db: AsyncSession, job: JobListing):
    """Notify every alert-subscribed user whose preferences match the new job."""
    profiles = (
        await db.execute(
            select(Profile).where(Profile.job_alerts_enabled == True)  # noqa: E712
        )
    ).scalars().all()
    for profile in profiles:
        if _matches_preferences(profile, job):
            db.add(
                Notification(
                    user_id=profile.user_id,
                    message=f"New {job.job_type} role: {job.title} at {job.company} ({job.location or job.employment_mode}).",
                    notification_type="job_alert",
                )
            )
    await db.flush()
