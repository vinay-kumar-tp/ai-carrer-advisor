"""My Profile — aggregate read + per-section writes.

The profile page is one screen with ~18 independently editable cards, so the
API is shaped accordingly: a single aggregate GET feeds the whole page, and each
card saves through its own narrow endpoint.
"""

from datetime import datetime, timezone
from typing import Optional, Type

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import delete as sa_delete
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user_id
from app.db.session import get_db
from app.models.models import (
    Award,
    BenchmarkScore,
    Certification,
    CodeSubmission,
    CodingProblem,
    Document,
    Education,
    InterviewSession,
    MCQQuestion,
    PersonalityResult,
    PositionOfResponsibility,
    Profile,
    ProfileProject,
    QuizAttempt,
    Resume,
    ScorecardEntry,
    Skill,
    User,
    UserSkill,
    WorkExperience,
)
from app.schemas.profile import (
    AboutUpdate,
    AcademicSummaryUpdate,
    AdditionalInfoUpdate,
    AwardInput,
    BasicInfoUpdate,
    BenchmarkInput,
    CertificationInput,
    ContactUpdate,
    DocumentLabelUpdate,
    DocumentVisibilityUpdate,
    EducationInput,
    JobPreferencesUpdate,
    MentorshipUpdate,
    PersonalDetailsUpdate,
    PositionInput,
    ProgramDetailsUpdate,
    ProjectInput,
    ResumeGenerateInput,
    ResumeInput,
    ResumeRename,
    ResumeTailorInput,
    ScorecardEntryInput,
    SkillsBulkUpdate,
    SocialLinksUpdate,
    TrainingUpdate,
    WorkExperienceInput,
)
from app.schemas.schemas import MessageResponse, SkillResponse, UserSkillCreate
from app.services import profile_service as ps
from app.services.profile_pdf import build_profile_pdf

router = APIRouter()


# ─── Loading helpers ─────────────────────────────────────────────

async def _get_user(db: AsyncSession, user_id: str) -> User:
    user = (await db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def _get_or_create_profile(db: AsyncSession, user_id: str) -> Profile:
    profile = (await db.execute(select(Profile).where(Profile.user_id == user_id))).scalar_one_or_none()
    if not profile:
        profile = Profile(user_id=user_id)
        db.add(profile)
        await db.flush()
    return profile


async def _list_rows(db: AsyncSession, model, user_id: str):
    order_by = [model.display_order] if hasattr(model, "display_order") else []
    order_by.append(model.created_at.desc() if hasattr(model, "created_at") else model.id)
    result = await db.execute(select(model).where(model.user_id == user_id).order_by(*order_by))
    return list(result.scalars().all())


async def _own_row(db: AsyncSession, model, row_id: str, user_id: str):
    row = (
        await db.execute(select(model).where(model.id == row_id, model.user_id == user_id))
    ).scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail=f"{model.__name__} not found")
    return row


async def _get_skills(db: AsyncSession, user_id: str) -> list[dict]:
    result = await db.execute(
        select(UserSkill, Skill)
        .join(Skill, UserSkill.skill_id == Skill.id)
        .where(UserSkill.user_id == user_id)
        .order_by(Skill.name)
    )
    return [
        {"skill_id": us.skill_id, "name": s.name, "proficiency": us.proficiency, "category": s.category}
        for us, s in result.all()
    ]


def _apply_partial(target, payload) -> None:
    """Assign only the fields the client actually sent (so one card can't blank another)."""
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(target, field, value)


async def _build_aggregate(db: AsyncSession, user_id: str) -> dict:
    user = await _get_user(db, user_id)
    profile = await _get_or_create_profile(db, user_id)

    skills = await _get_skills(db, user_id)
    educations = await _list_rows(db, Education, user_id)
    work = await _list_rows(db, WorkExperience, user_id)
    positions = await _list_rows(db, PositionOfResponsibility, user_id)
    projects = await _list_rows(db, ProfileProject, user_id)
    awards = await _list_rows(db, Award, user_id)
    certifications = await _list_rows(db, Certification, user_id)
    resumes = await _list_rows(db, Resume, user_id)

    benchmark_rows = {
        row.stage: row
        for row in (await db.execute(select(BenchmarkScore).where(BenchmarkScore.user_id == user_id))).scalars().all()
    }

    completion = ps.compute_completion(
        user=user,
        profile=profile,
        skills=skills,
        educations=educations,
        projects=projects,
        work=work,
        positions=positions,
        awards=awards,
        certifications=certifications,
        resumes=resumes,
    )

    return {
        "user_id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "basic": ps.serialize_basic(user, profile),
        "contact": ps.serialize_contact(user, profile),
        "personal": ps.serialize_personal(profile),
        "social": ps.serialize_social(profile),
        "about_me": ps.as_text(profile.about_me),
        "additional_info": ps.as_list(profile.additional_info),
        "program": ps.serialize_program(profile),
        "mentorship": ps.serialize_mentorship(profile),
        "training": ps.as_list(profile.training_details),
        "academic_summary": ps.serialize_academic_summary(profile),
        "job_preferences": ps.serialize_job_preferences(profile),
        "skills": skills,
        "educations": [ps.serialize_education(r) for r in educations],
        "work_experiences": [ps.serialize_work(r) for r in work],
        "positions": [ps.serialize_position(r) for r in positions],
        "projects": [ps.serialize_project(r) for r in projects],
        "awards": [ps.serialize_award(r) for r in awards],
        "certifications": [ps.serialize_certification(r) for r in certifications],
        "benchmarks": {
            stage: ps.serialize_benchmark(benchmark_rows.get(stage), stage) for stage in ps.BENCHMARK_STAGES
        },
        "resume_count": len(resumes),
        "completion": completion,
    }


# ─── Aggregate read ──────────────────────────────────────────────

@router.get("")
@router.get("/")
async def get_full_profile(user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    return await _build_aggregate(db, user_id)


@router.get("/completion")
async def get_completion(user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    return (await _build_aggregate(db, user_id))["completion"]


# ─── Single-record section updates ───────────────────────────────

@router.put("/basic")
async def update_basic(
    data: BasicInfoUpdate, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)
):
    user = await _get_user(db, user_id)
    profile = await _get_or_create_profile(db, user_id)

    payload = data.model_dump(exclude_unset=True)
    if "full_name" in payload and payload["full_name"]:
        user.full_name = payload.pop("full_name").strip()
    else:
        payload.pop("full_name", None)
    for field, value in payload.items():
        setattr(profile, field, value)

    await db.flush()
    return await _build_aggregate(db, user_id)


@router.put("/contact")
async def update_contact(
    data: ContactUpdate, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)
):
    user = await _get_user(db, user_id)
    profile = await _get_or_create_profile(db, user_id)
    payload = data.model_dump(exclude_unset=True)

    if "email" in payload and payload["email"]:
        new_email = payload["email"].strip().lower()
        if new_email != user.email:
            clash = (
                await db.execute(select(User).where(User.email == new_email, User.id != user_id))
            ).scalar_one_or_none()
            if clash:
                raise HTTPException(status_code=400, detail="That email is already in use")
            user.email = new_email
    if "phone" in payload:
        profile.phone = payload["phone"]

    await db.flush()
    return await _build_aggregate(db, user_id)


@router.put("/personal")
async def update_personal(
    data: PersonalDetailsUpdate, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)
):
    _apply_partial(await _get_or_create_profile(db, user_id), data)
    await db.flush()
    return await _build_aggregate(db, user_id)


@router.put("/social")
async def update_social(
    data: SocialLinksUpdate, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)
):
    _apply_partial(await _get_or_create_profile(db, user_id), data)
    await db.flush()
    return await _build_aggregate(db, user_id)


@router.put("/about")
async def update_about(
    data: AboutUpdate, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)
):
    _apply_partial(await _get_or_create_profile(db, user_id), data)
    await db.flush()
    return await _build_aggregate(db, user_id)


@router.put("/additional-info")
async def update_additional_info(
    data: AdditionalInfoUpdate, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)
):
    profile = await _get_or_create_profile(db, user_id)
    profile.additional_info = [row.model_dump() for row in data.additional_info]
    await db.flush()
    return await _build_aggregate(db, user_id)


@router.put("/job-preferences")
async def update_job_preferences(
    data: JobPreferencesUpdate, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)
):
    _apply_partial(await _get_or_create_profile(db, user_id), data)
    await db.flush()
    return await _build_aggregate(db, user_id)


@router.put("/program")
async def update_program(
    data: ProgramDetailsUpdate, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)
):
    _apply_partial(await _get_or_create_profile(db, user_id), data)
    await db.flush()
    return await _build_aggregate(db, user_id)


@router.put("/mentorship")
async def update_mentorship(
    data: MentorshipUpdate, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)
):
    _apply_partial(await _get_or_create_profile(db, user_id), data)
    await db.flush()
    return await _build_aggregate(db, user_id)


@router.put("/training")
async def update_training(
    data: TrainingUpdate, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)
):
    profile = await _get_or_create_profile(db, user_id)
    profile.training_details = [row.model_dump() for row in data.training_details]
    await db.flush()
    return await _build_aggregate(db, user_id)


@router.put("/academic-summary")
async def update_academic_summary(
    data: AcademicSummaryUpdate, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)
):
    _apply_partial(await _get_or_create_profile(db, user_id), data)
    await db.flush()
    return await _build_aggregate(db, user_id)


# ─── Skills ──────────────────────────────────────────────────────

@router.put("/skills")
async def replace_skills(
    data: SkillsBulkUpdate, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)
):
    """Replace the whole chip list in one save (matches the Skills card UI)."""
    existing = {row["name"].lower(): row for row in await _get_skills(db, user_id)}
    wanted_keys = {name.lower() for name in data.skills}

    for key, row in existing.items():
        if key not in wanted_keys:
            await db.execute(
                sa_delete(UserSkill).where(UserSkill.user_id == user_id, UserSkill.skill_id == row["skill_id"])
            )

    for name in data.skills:
        if name.lower() in existing:
            continue
        skill = (await db.execute(select(Skill).where(func.lower(Skill.name) == name.lower()))).scalar_one_or_none()
        if not skill:
            skill = Skill(name=name)
            db.add(skill)
            await db.flush()
        db.add(UserSkill(user_id=user_id, skill_id=skill.id, proficiency=70))

    await db.flush()
    return await _build_aggregate(db, user_id)


@router.get("/skills/catalog", response_model=list[SkillResponse])
async def skill_catalog(db: AsyncSession = Depends(get_db)):
    """Suggestion list for the skills autocomplete."""
    result = await db.execute(select(Skill).order_by(Skill.name))
    return [SkillResponse(id=s.id, name=s.name, category=s.category) for s in result.scalars().all()]


@router.get("/my-skills")
async def get_my_skills(user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    return await _get_skills(db, user_id)


@router.post("/skills", response_model=MessageResponse)
async def add_skill(
    data: UserSkillCreate, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)
):
    name = data.skill_name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Skill name is required")

    skill = (await db.execute(select(Skill).where(func.lower(Skill.name) == name.lower()))).scalar_one_or_none()
    if not skill:
        skill = Skill(name=name)
        db.add(skill)
        await db.flush()

    link = (
        await db.execute(select(UserSkill).where(UserSkill.user_id == user_id, UserSkill.skill_id == skill.id))
    ).scalar_one_or_none()
    if link:
        link.proficiency = data.proficiency
    else:
        db.add(UserSkill(user_id=user_id, skill_id=skill.id, proficiency=data.proficiency))

    return MessageResponse(message="Skill saved")


@router.delete("/skills/{skill_name}", response_model=MessageResponse)
async def remove_skill(
    skill_name: str, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)
):
    skill = (
        await db.execute(select(Skill).where(func.lower(Skill.name) == skill_name.strip().lower()))
    ).scalar_one_or_none()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    await db.execute(sa_delete(UserSkill).where(UserSkill.user_id == user_id, UserSkill.skill_id == skill.id))
    return MessageResponse(message="Skill removed")


# ─── Repeatable sections ─────────────────────────────────────────
# One shared implementation, thin explicit routes on top so the OpenAPI schema
# stays accurate.

async def _create_section_row(db: AsyncSession, model: Type, user_id: str, payload) -> dict:
    # model_dump() recurses into sub-models, so JSON columns receive plain dicts.
    row = model(user_id=user_id, **payload.model_dump())
    db.add(row)
    await db.flush()
    return await _build_aggregate(db, user_id)


async def _update_section_row(db: AsyncSession, model: Type, row_id: str, user_id: str, payload) -> dict:
    row = await _own_row(db, model, row_id, user_id)
    for field, value in payload.model_dump().items():
        setattr(row, field, value)
    await db.flush()
    return await _build_aggregate(db, user_id)


async def _delete_section_row(db: AsyncSession, model: Type, row_id: str, user_id: str) -> dict:
    row = await _own_row(db, model, row_id, user_id)
    await db.delete(row)
    await db.flush()
    return await _build_aggregate(db, user_id)


# Education
@router.post("/education")
async def create_education(
    data: EducationInput, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)
):
    return await _create_section_row(db, Education, user_id, data)


@router.put("/education/{row_id}")
async def update_education(
    row_id: str, data: EducationInput, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)
):
    return await _update_section_row(db, Education, row_id, user_id, data)


@router.delete("/education/{row_id}")
async def delete_education(
    row_id: str, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)
):
    return await _delete_section_row(db, Education, row_id, user_id)


# Work experience
@router.post("/work-experience")
async def create_work(
    data: WorkExperienceInput, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)
):
    return await _create_section_row(db, WorkExperience, user_id, data)


@router.put("/work-experience/{row_id}")
async def update_work(
    row_id: str,
    data: WorkExperienceInput,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    return await _update_section_row(db, WorkExperience, row_id, user_id, data)


@router.delete("/work-experience/{row_id}")
async def delete_work(row_id: str, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    return await _delete_section_row(db, WorkExperience, row_id, user_id)


# Positions of responsibility
@router.post("/positions")
async def create_position(
    data: PositionInput, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)
):
    return await _create_section_row(db, PositionOfResponsibility, user_id, data)


@router.put("/positions/{row_id}")
async def update_position(
    row_id: str, data: PositionInput, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)
):
    return await _update_section_row(db, PositionOfResponsibility, row_id, user_id, data)


@router.delete("/positions/{row_id}")
async def delete_position(row_id: str, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    return await _delete_section_row(db, PositionOfResponsibility, row_id, user_id)


# Projects
@router.post("/projects")
async def create_project(
    data: ProjectInput, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)
):
    return await _create_section_row(db, ProfileProject, user_id, data)


@router.put("/projects/{row_id}")
async def update_project(
    row_id: str, data: ProjectInput, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)
):
    return await _update_section_row(db, ProfileProject, row_id, user_id, data)


@router.delete("/projects/{row_id}")
async def delete_project(row_id: str, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    return await _delete_section_row(db, ProfileProject, row_id, user_id)


# Awards
@router.post("/awards")
async def create_award(
    data: AwardInput, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)
):
    return await _create_section_row(db, Award, user_id, data)


@router.put("/awards/{row_id}")
async def update_award(
    row_id: str, data: AwardInput, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)
):
    return await _update_section_row(db, Award, row_id, user_id, data)


@router.delete("/awards/{row_id}")
async def delete_award(row_id: str, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    return await _delete_section_row(db, Award, row_id, user_id)


# Certifications
@router.post("/certifications")
async def create_certification(
    data: CertificationInput, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)
):
    return await _create_section_row(db, Certification, user_id, data)


@router.put("/certifications/{row_id}")
async def update_certification(
    row_id: str,
    data: CertificationInput,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    return await _update_section_row(db, Certification, row_id, user_id, data)


@router.delete("/certifications/{row_id}")
async def delete_certification(
    row_id: str, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)
):
    return await _delete_section_row(db, Certification, row_id, user_id)


# ─── Benchmark scores (baseline / midline / endline) ─────────────

@router.put("/benchmarks/{stage}")
async def upsert_benchmark(
    stage: str, data: BenchmarkInput, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)
):
    if stage not in ps.BENCHMARK_STAGES:
        raise HTTPException(status_code=400, detail=f"stage must be one of {', '.join(ps.BENCHMARK_STAGES)}")
    if data.stage != stage:
        raise HTTPException(status_code=400, detail="Stage in path and body must match")

    row = (
        await db.execute(
            select(BenchmarkScore).where(BenchmarkScore.user_id == user_id, BenchmarkScore.stage == stage)
        )
    ).scalar_one_or_none()
    if not row:
        row = BenchmarkScore(user_id=user_id, stage=stage)
        db.add(row)

    for field, value in data.model_dump().items():
        setattr(row, field, value)

    await db.flush()
    return await _build_aggregate(db, user_id)


# ─── Resume library ──────────────────────────────────────────────

ATS_BASELINE_KEYWORDS = [
    "python", "javascript", "typescript", "react", "sql", "git", "api", "rest",
    "communication", "leadership", "teamwork", "problem solving", "database",
    "docker", "testing", "cloud", "agile",
]


def _score_resume_text(text: str, target_terms: list[str]) -> dict:
    lowered = text.lower()
    matched = [term for term in target_terms if term in lowered]
    missing = [term for term in target_terms if term not in lowered]

    coverage = len(matched) / max(len(target_terms), 1)
    word_count = len(text.split())
    length_bonus = 10 if word_count >= 220 else (5 if word_count >= 120 else 0)
    score = int(min(98, max(20, round(coverage * 85) + length_bonus)))

    suggestions = []
    if missing:
        suggestions.append(f"Add coverage for: {', '.join(missing[:6])}")
    if word_count < 150:
        suggestions.append("Add more detail to projects and experience — the resume reads short for ATS parsing.")
    if not any(verb in lowered for verb in ("built", "led", "developed", "designed", "achieved", "improved")):
        suggestions.append("Open bullet points with strong action verbs (built, led, designed, improved).")
    if not suggestions:
        suggestions.append("Strong keyword coverage. Keep it updated as you add new work.")

    return {
        "ats_score": score,
        "matched_keywords": matched,
        "missing_keywords": missing,
        "suggestions": suggestions,
        "word_count": word_count,
    }


@router.get("/resumes")
async def list_resumes(user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    rows = await _list_rows(db, Resume, user_id)
    rows.sort(key=lambda r: (not r.is_primary, r.created_at or datetime.now(timezone.utc)))
    return {
        "resumes": [ps.serialize_resume(r) for r in rows],
        "total": len(rows),
        "templates": ["Template 1", "Template 2", "Template 3", "Template 4"],
    }


@router.post("/resumes")
async def add_resume(
    data: ResumeInput, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)
):
    """Register an already-uploaded document as a resume in the library."""
    if data.document_id:
        await _own_row(db, Document, data.document_id, user_id)

    existing = await _list_rows(db, Resume, user_id)
    row = Resume(
        user_id=user_id,
        name=data.name.strip(),
        source=data.source,
        template=data.template,
        document_id=data.document_id,
        status=data.status,
        is_primary=not existing,
    )
    db.add(row)
    await db.flush()
    return ps.serialize_resume(row)


@router.post("/resumes/generate")
async def generate_resume(
    data: ResumeGenerateInput, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)
):
    """Snapshot the current profile into a new resume in the library."""
    aggregate = await _build_aggregate(db, user_id)
    content = ps.build_resume_content(aggregate)

    if aggregate["completion"]["percentage"] < 20:
        raise HTTPException(
            status_code=400,
            detail="Add more profile details before generating a resume (profile is under 20% complete).",
        )

    existing = await _list_rows(db, Resume, user_id)
    stamp = datetime.now(timezone.utc).strftime("%d %b %Y")
    name = (data.name or f"{data.template} - {aggregate['full_name']} - {stamp}").strip()

    row = Resume(
        user_id=user_id,
        name=name,
        source="generated",
        template=data.template,
        status="ready",
        content=content,
        is_primary=not existing,
        ats_score=_score_resume_text(ps.resume_plain_text(content), ATS_BASELINE_KEYWORDS)["ats_score"],
    )
    db.add(row)
    await db.flush()
    return ps.serialize_resume(row)


@router.post("/resumes/{resume_id}/tailor")
async def tailor_resume(
    resume_id: str,
    data: ResumeTailorInput,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Copy a resume and optimise it for one job without touching the profile."""
    from app.models.models import JobListing

    source = await _own_row(db, Resume, resume_id, user_id)
    job = (await db.execute(select(JobListing).where(JobListing.id == data.job_id))).scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    content = dict(source.content or ps.build_resume_content(await _build_aggregate(db, user_id)))
    target_terms = [s.lower() for s in (job.required_skills or [])] or ATS_BASELINE_KEYWORDS
    report = _score_resume_text(ps.resume_plain_text(content), target_terms)
    content["tailored_for"] = {"job_id": job.id, "title": job.title, "company": job.company}
    content["ats_report"] = report

    row = Resume(
        user_id=user_id,
        name=(data.name or f"{source.name} → {job.title}")[:255],
        source="tailored",
        template=source.template,
        status="ready",
        content=content,
        target_job_id=job.id,
        ats_score=report["ats_score"],
    )
    db.add(row)
    await db.flush()
    return {"resume": ps.serialize_resume(row), "ats_report": report}


@router.post("/resumes/{resume_id}/ats-score")
async def score_resume(
    resume_id: str,
    job_id: Optional[str] = Query(None),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    from app.models.models import JobListing

    row = await _own_row(db, Resume, resume_id, user_id)

    content = row.content or {}
    text = ps.resume_plain_text(content)
    if not text.strip():
        # Uploaded file with no structured snapshot — fall back to parsed document text.
        if row.document_id:
            doc = (await db.execute(select(Document).where(Document.id == row.document_id))).scalar_one_or_none()
            text = (doc.parsed_text or "") if doc else ""
        if not text.strip():
            text = ps.resume_plain_text(ps.build_resume_content(await _build_aggregate(db, user_id)))

    target_terms = ATS_BASELINE_KEYWORDS
    if job_id:
        job = (await db.execute(select(JobListing).where(JobListing.id == job_id))).scalar_one_or_none()
        if job and job.required_skills:
            target_terms = [s.lower() for s in job.required_skills]

    report = _score_resume_text(text, target_terms)
    row.ats_score = report["ats_score"]
    row.status = "ready"
    await db.flush()
    return {"resume": ps.serialize_resume(row), **report}


@router.post("/resumes/{resume_id}/primary")
async def set_primary_resume(
    resume_id: str, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)
):
    rows = await _list_rows(db, Resume, user_id)
    if not any(r.id == resume_id for r in rows):
        raise HTTPException(status_code=404, detail="Resume not found")
    for row in rows:
        row.is_primary = row.id == resume_id
    await db.flush()
    return {"resumes": [ps.serialize_resume(r) for r in rows]}


@router.put("/resumes/{resume_id}")
async def rename_resume(
    resume_id: str, data: ResumeRename, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)
):
    row = await _own_row(db, Resume, resume_id, user_id)
    row.name = data.name.strip()
    await db.flush()
    return ps.serialize_resume(row)


@router.delete("/resumes/{resume_id}", response_model=MessageResponse)
async def delete_resume(
    resume_id: str, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)
):
    row = await _own_row(db, Resume, resume_id, user_id)
    was_primary = row.is_primary
    await db.delete(row)
    await db.flush()

    if was_primary:
        remaining = await _list_rows(db, Resume, user_id)
        if remaining:
            remaining[0].is_primary = True
            await db.flush()

    return MessageResponse(message="Resume removed")


@router.get("/resumes/{resume_id}/download")
async def download_resume(
    resume_id: str, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)
):
    """Generated resumes render to PDF on the fly; uploaded ones stream the original file."""
    row = await _own_row(db, Resume, resume_id, user_id)

    if row.document_id:
        import os

        doc = (await db.execute(select(Document).where(Document.id == row.document_id))).scalar_one_or_none()
        if doc and os.path.exists(doc.file_path):
            with open(doc.file_path, "rb") as handle:
                payload = handle.read()
            media = "application/pdf" if doc.filename.lower().endswith(".pdf") else "application/octet-stream"
            return Response(
                content=payload,
                media_type=media,
                headers={"Content-Disposition": f'attachment; filename="{doc.filename}"'},
            )

    aggregate = await _build_aggregate(db, user_id)
    pdf = build_profile_pdf(aggregate)
    safe = "".join(ch for ch in row.name if ch.isalnum() or ch in " -_").strip() or "resume"
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{safe}.pdf"'},
    )


# ─── Scorecard ───────────────────────────────────────────────────

@router.get("/scorecard")
async def get_scorecard(
    assess_type: str = Query("all", pattern="^(all|assignment|practice)$"),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Aggregates real attempt data from Aptitude Quest, Code Quest, the
    personality test and AI mock interviews."""
    assessments: list[dict] = []

    # Aptitude topics → one "Practice" assessment per topic.
    topic_rows = (
        await db.execute(
            select(MCQQuestion.topic, func.count(MCQQuestion.id)).group_by(MCQQuestion.topic)
        )
    ).all()
    attempts = (await db.execute(select(QuizAttempt).where(QuizAttempt.user_id == user_id))).scalars().all()

    for topic, question_count in topic_rows:
        topic_attempts = [a for a in attempts if (a.topic or "") == topic]
        best = max((a.percentage or 0) for a in topic_attempts) if topic_attempts else None
        best_attempt = max(topic_attempts, key=lambda a: a.percentage or 0) if topic_attempts else None
        assessments.append(
            {
                "name": f"{topic} Practice",
                "type": "Practice",
                "attempted": bool(topic_attempts),
                "attempts": len(topic_attempts),
                "score": (best_attempt.score if best_attempt else 0),
                "max_score": (best_attempt.total if best_attempt and best_attempt.total else question_count),
                "percentage": round(best, 2) if best is not None else None,
            }
        )

    # Coding problems → "Assignment". Only problems the student actually
    # attempted are listed; the full catalogue runs into the hundreds and belongs
    # in Code Quest's own progress view, not the profile scorecard.
    submissions = (
        await db.execute(select(CodeSubmission).where(CodeSubmission.user_id == user_id))
    ).scalars().all()
    attempted_ids = {s.problem_id for s in submissions}
    if attempted_ids:
        problems = (
            await db.execute(select(CodingProblem).where(CodingProblem.id.in_(attempted_ids)))
        ).scalars().all()
        for problem in problems:
            problem_subs = [s for s in submissions if s.problem_id == problem.id]
            best = max((s.score or 0) for s in problem_subs)
            assessments.append(
                {
                    "name": problem.title,
                    "type": "Assignment",
                    "attempted": True,
                    "attempts": len(problem_subs),
                    "score": best,
                    "max_score": 100,
                    "percentage": float(best),
                }
            )

    if assess_type != "all":
        wanted = assess_type.title()
        assessments = [a for a in assessments if a["type"] == wanted]

    attempted = [a for a in assessments if a["attempted"] and a["percentage"] is not None]
    percentages = [a["percentage"] for a in attempted]
    total = len(assessments)

    stats = {
        "total_available": total,
        "total_attempted": len(attempted),
        "attempt_rate": round(len(attempted) / total * 100, 2) if total else 0.0,
        "avg_score": round(sum(percentages) / len(percentages), 2) if percentages else 0.0,
        "highest_score": round(max(percentages), 2) if percentages else 0.0,
        "lowest_score": round(min(percentages), 2) if percentages else 0.0,
    }

    # AI mock interviews
    sessions = (
        await db.execute(
            select(InterviewSession)
            .where(InterviewSession.user_id == user_id)
            .order_by(InterviewSession.created_at.desc())
        )
    ).scalars().all()

    def _overall(session) -> Optional[float]:
        scores = session.scores or {}
        numeric = [v for v in scores.values() if isinstance(v, (int, float))]
        return round(sum(numeric) / len(numeric), 2) if numeric else None

    mock_interviews = [
        {
            "id": s.id,
            "mode": s.mode,
            "job_context": s.job_context or "General",
            "overall_score": _overall(s),
            "scores": s.scores or {},
            "is_completed": bool(s.is_completed),
            "created_at": s.created_at.isoformat() if s.created_at else None,
        }
        for s in sessions
    ]

    personality = (
        await db.execute(select(PersonalityResult).where(PersonalityResult.user_id == user_id))
    ).scalar_one_or_none()

    custom = await _list_rows(db, ScorecardEntry, user_id)

    return {
        "assessments": assessments,
        "stats": stats,
        "mock_interviews": mock_interviews,
        "personality": (
            {
                "openness": personality.openness,
                "conscientiousness": personality.conscientiousness,
                "extraversion": personality.extraversion,
                "agreeableness": personality.agreeableness,
                "neuroticism": personality.neuroticism,
            }
            if personality
            else None
        ),
        "other_scores": [ps.serialize_scorecard_entry(r) for r in custom if r.category == "other"],
        "custom_event_scores": [ps.serialize_scorecard_entry(r) for r in custom if r.category == "custom_event"],
    }


@router.post("/scorecard/entries")
async def create_scorecard_entry(
    data: ScorecardEntryInput, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)
):
    row = ScorecardEntry(user_id=user_id, **data.model_dump())
    db.add(row)
    await db.flush()
    return ps.serialize_scorecard_entry(row)


@router.put("/scorecard/entries/{row_id}")
async def update_scorecard_entry(
    row_id: str,
    data: ScorecardEntryInput,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    row = await _own_row(db, ScorecardEntry, row_id, user_id)
    for field, value in data.model_dump().items():
        setattr(row, field, value)
    await db.flush()
    return ps.serialize_scorecard_entry(row)


@router.delete("/scorecard/entries/{row_id}", response_model=MessageResponse)
async def delete_scorecard_entry(
    row_id: str, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)
):
    row = await _own_row(db, ScorecardEntry, row_id, user_id)
    await db.delete(row)
    return MessageResponse(message="Score removed")


# ─── Documents tab ───────────────────────────────────────────────

DOC_GROUPS = {
    "resume": "resumes",
    "transcript": "marksheets",
    "certificate": "certificates",
}


@router.get("/documents")
async def profile_documents(user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    docs = (
        await db.execute(
            select(Document).where(Document.user_id == user_id).order_by(Document.created_at.desc())
        )
    ).scalars().all()

    grouped: dict[str, list] = {"resumes": [], "marksheets": [], "certificates": [], "others": []}
    for doc in docs:
        payload = {
            "id": doc.id,
            "filename": doc.filename,
            "label": ps.as_text(doc.label) or doc.filename,
            "doc_type": doc.doc_type,
            "file_size": doc.file_size,
            "is_public": bool(doc.is_public),
            "created_at": doc.created_at.isoformat() if doc.created_at else None,
            "download_url": f"/api/profile/documents/{doc.id}/file",
        }
        grouped[DOC_GROUPS.get(doc.doc_type, "others")].append(payload)

    resumes = await _list_rows(db, Resume, user_id)
    primary = next((r for r in resumes if r.is_primary), resumes[0] if resumes else None)

    return {
        **grouped,
        "resume_library": [ps.serialize_resume(r) for r in resumes],
        "primary_resume": ps.serialize_resume(primary) if primary else None,
        "total": len(docs),
    }


@router.get("/documents/{doc_id}/file")
async def download_profile_document(
    doc_id: str, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)
):
    import mimetypes
    import os

    doc = await _own_row(db, Document, doc_id, user_id)
    if not os.path.exists(doc.file_path):
        raise HTTPException(status_code=404, detail="File is missing from storage")

    with open(doc.file_path, "rb") as handle:
        payload = handle.read()

    media = mimetypes.guess_type(doc.filename)[0] or "application/octet-stream"
    return Response(
        content=payload,
        media_type=media,
        headers={"Content-Disposition": f'inline; filename="{doc.filename}"'},
    )


@router.put("/documents/visibility")
async def update_document_visibility(
    data: DocumentVisibilityUpdate, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)
):
    if not data.document_ids:
        return MessageResponse(message="Nothing to update")

    rows = (
        await db.execute(
            select(Document).where(Document.user_id == user_id, Document.id.in_(data.document_ids))
        )
    ).scalars().all()
    if len(rows) != len(set(data.document_ids)):
        raise HTTPException(status_code=404, detail="One or more documents were not found")

    for row in rows:
        row.is_public = data.is_public
    await db.flush()
    return MessageResponse(message=f"Updated {len(rows)} document(s)")


@router.put("/documents/{doc_id}/label")
async def rename_document(
    doc_id: str,
    data: DocumentLabelUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    doc = await _own_row(db, Document, doc_id, user_id)
    doc.label = data.label.strip()
    await db.flush()
    return MessageResponse(message="Document renamed")


# ─── PDF export ──────────────────────────────────────────────────

@router.get("/export/pdf")
async def export_profile_pdf(user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    aggregate = await _build_aggregate(db, user_id)
    pdf = build_profile_pdf(aggregate)
    safe = "".join(ch for ch in aggregate["full_name"] if ch.isalnum() or ch in " -_").strip() or "profile"
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{safe} - Profile.pdf"'},
    )
