from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from app.db.session import get_db
from app.models.models import JobListing, Application
from app.schemas.schemas import JobCreate, JobResponse, ApplicationCreate, ApplicationResponse, MessageResponse
from app.core.security import get_current_user_id, decode_token, oauth2_scheme

router = APIRouter()


@router.get("/", response_model=list[JobResponse])
async def list_jobs(
    keyword: str = Query(None),
    location: str = Query(None),
    remote: bool = Query(None),
    experience_level: str = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    query = select(JobListing).where(JobListing.is_active == True)

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
    if remote is not None:
        query = query.where(JobListing.remote == remote)
    if experience_level:
        query = query.where(JobListing.experience_level == experience_level)

    query = query.order_by(JobListing.posted_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    jobs = result.scalars().all()
    return [
        JobResponse(
            id=str(j.id), title=j.title, company=j.company, description=j.description,
            location=j.location, remote=j.remote, salary_range=j.salary_range,
            required_skills=j.required_skills, experience_level=j.experience_level,
            job_type=j.job_type, posted_at=j.posted_at,
        )
        for j in jobs
    ]


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(JobListing).where(JobListing.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobResponse(
        id=str(job.id), title=job.title, company=job.company, description=job.description,
        location=job.location, remote=job.remote, salary_range=job.salary_range,
        required_skills=job.required_skills, experience_level=job.experience_level,
        job_type=job.job_type, posted_at=job.posted_at,
    )


@router.post("/", response_model=JobResponse, status_code=201)
async def create_job(data: JobCreate, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    payload = decode_token(token)
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    job = JobListing(**data.model_dump())
    db.add(job)
    await db.flush()

    return JobResponse(
        id=str(job.id), title=job.title, company=job.company, description=job.description,
        location=job.location, remote=job.remote, salary_range=job.salary_range,
        required_skills=job.required_skills, experience_level=job.experience_level,
        job_type=job.job_type, posted_at=job.posted_at,
    )


@router.post("/{job_id}/apply", response_model=ApplicationResponse, status_code=201)
async def apply_to_job(
    job_id: str,
    data: ApplicationCreate = None,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    # Check job exists
    result = await db.execute(select(JobListing).where(JobListing.id == job_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Job not found")

    # Check not already applied
    result = await db.execute(
        select(Application).where(Application.user_id == user_id, Application.job_id == job_id)
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Already applied to this job")

    app = Application(user_id=user_id, job_id=job_id)
    if data:
        if data.cover_letter:
            app.cover_letter = data.cover_letter
        if data.resume_id:
            app.resume_id = data.resume_id
    db.add(app)
    await db.flush()

    return ApplicationResponse(
        id=str(app.id), job_id=str(app.job_id), status=app.status, applied_at=app.applied_at,
    )


@router.get("/applications/mine", response_model=list[ApplicationResponse])
async def my_applications(user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Application).where(Application.user_id == user_id).order_by(Application.applied_at.desc())
    )
    apps = result.scalars().all()
    return [
        ApplicationResponse(id=str(a.id), job_id=str(a.job_id), status=a.status, applied_at=a.applied_at)
        for a in apps
    ]
