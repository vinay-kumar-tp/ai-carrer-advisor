"""Position AI — Skill Gap & Fit Analyzer.

Reuses the profile aggregate (candidate skills) and JobListing.required_skills
(saved JDs) already established by the Job Board / Profile routers, adding:
  - candidate skills read/update (thin wrappers around the profile skill CRUD)
  - gap analysis against up to 3 saved JDs and/or pasted JD text
  - a history log of past analysis runs
  - a feedback capture endpoint
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete as sa_delete
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.routers.profile import _build_aggregate, _get_skills
from app.core.security import get_current_user_id
from app.db.session import get_db
from app.models.models import JobListing, PositionAnalysis, PositionFeedback, Skill, UserSkill
from app.schemas.position_ai import (
    GapScopeJd,
    JdOption,
    MissingSkillItem,
    PositionAnalysisResponse,
    PositionAnalyzeRequest,
    PositionFeedbackRequest,
    PositionFeedbackResponse,
    PositionHistoryItem,
    PositionHistoryResponse,
)
from app.schemas.profile import SkillsBulkUpdate
from app.services import position_ai as svc

router = APIRouter()

# Mounted separately at /api/candidate so the candidate skill endpoints live at
# the paths the feature spec defines (GET/PUT /api/candidate/skills).
candidate_router = APIRouter()


# ─── Candidate skills ─────────────────────────────────────────────
# Thin wrappers so the Position AI page has its own stable contract, even
# though they operate on the same UserSkill rows as My Profile.

@router.get("/candidate/skills")
@candidate_router.get("/skills")
async def get_candidate_skills(user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    skills = await _get_skills(db, user_id)
    return {"skills": [s["name"] for s in skills], "total": len(skills)}


@router.put("/candidate/skills")
@candidate_router.put("/skills")
async def update_candidate_skills(
    data: SkillsBulkUpdate, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)
):
    """Replace the candidate's whole skill list (mirrors profile.replace_skills)."""
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
    skills = await _get_skills(db, user_id)
    return {"skills": [s["name"] for s in skills], "total": len(skills)}


# ─── Target JD picker ─────────────────────────────────────────────

@router.get("/jobs", response_model=list[JdOption])
async def list_jd_options(db: AsyncSession = Depends(get_db)):
    """Feeds the 'Select up to 3 job descriptions' dropdown."""
    rows = (
        await db.execute(
            select(JobListing).where(JobListing.is_active == True).order_by(JobListing.posted_at.desc())  # noqa: E712
        )
    ).scalars().all()
    return [
        JdOption(
            id=job.id,
            title=job.title,
            company=job.company,
            location=job.location or "",
            required_skills_count=len(job.required_skills or []),
            required_skills=list(job.required_skills or []),
        )
        for job in rows
    ]


# ─── Analyze ──────────────────────────────────────────────────────

async def _run_analysis(
    db: AsyncSession, user_id: str, data: PositionAnalyzeRequest
) -> tuple[dict, list, list, list]:
    aggregate = await _build_aggregate(db, user_id)
    profile_skills = [s["name"] for s in aggregate["skills"]]

    job_ids = (data.job_ids or [])[:3]
    jobs: list[JobListing] = []
    if job_ids:
        jobs = (await db.execute(select(JobListing).where(JobListing.id.in_(job_ids)))).scalars().all()
        # Preserve the order the user picked them in.
        by_id = {j.id: j for j in jobs}
        jobs = [by_id[jid] for jid in job_ids if jid in by_id]

    jd_skill_lists: list[list[str]] = [list(job.required_skills or []) for job in jobs]
    jd_titles = [job.title for job in jobs]

    scope: list[GapScopeJd] = []
    for job in jobs:
        skills = list(job.required_skills or [])
        scope.append(
            GapScopeJd(
                id=job.id,
                title=job.title,
                company=job.company,
                location=job.location or "",
                source="job",
                sample_skills=skills[:4],
                extra_count=max(0, len(skills) - 4),
            )
        )

    pasted_text = (data.jd_text or "").strip()
    if pasted_text:
        pasted_skills = await svc.extract_jd_skills(pasted_text)
        jd_skill_lists.append(pasted_skills)
        pasted_title = "Pasted Job Description"
        jd_titles.append(pasted_title)
        scope.append(
            GapScopeJd(
                id="pasted",
                title=pasted_title,
                company="",
                location="",
                source="text",
                sample_skills=pasted_skills[:4],
                extra_count=max(0, len(pasted_skills) - 4),
            )
        )

    gap = svc.compute_gap(profile_skills, jd_skill_lists, jd_titles)
    jd_title = ", ".join(jd_titles) if jd_titles else "No job description selected"

    jd_snapshots = [
        {"job_id": job.id, "title": job.title, "company": job.company, "required_skills": list(job.required_skills or [])}
        for job in jobs
    ]
    if pasted_text:
        jd_snapshots.append({"job_id": None, "title": "Pasted Job Description", "company": "", "required_skills": jd_skill_lists[-1]})

    return gap, jd_snapshots, profile_skills, scope


@router.post("/analyze", response_model=PositionAnalysisResponse)
async def analyze(
    data: PositionAnalyzeRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    if not data.job_ids and not (data.jd_text or "").strip():
        raise HTTPException(status_code=400, detail="Select at least one job description or paste JD text")

    gap, jd_snapshots, profile_skills, scope = await _run_analysis(db, user_id, data)
    jd_title = ", ".join(s["title"] for s in jd_snapshots) or "No job description selected"

    analysis_id = None
    if data.save:
        row = PositionAnalysis(
            user_id=user_id,
            job_ids=list(data.job_ids or []),
            jd_snapshots=jd_snapshots,
            pasted_jd_text=(data.jd_text or "").strip(),
            profile_skills=profile_skills,
            profile_skill_count=len(profile_skills),
            match_percentage=gap["match_percentage"],
            matched_skills=gap["matched_skills"],
            missing_skills=gap["missing_skills"],
            jd_title=jd_title,
        )
        db.add(row)
        await db.flush()
        analysis_id = row.id

    return PositionAnalysisResponse(
        id=analysis_id,
        matchPercentage=gap["match_percentage"],
        matchedSkills=gap["matched_skills"],
        missingSkills=[MissingSkillItem(**m) for m in gap["missing_skills"]],
        jdTitle=jd_title,
        profileSkillCount=len(profile_skills),
        selectedJdCount=len(jd_snapshots),
        scope=scope,
    )


# ─── History ──────────────────────────────────────────────────────

@router.get("/history", response_model=PositionHistoryResponse)
async def get_history(user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    rows = (
        await db.execute(
            select(PositionAnalysis)
            .where(PositionAnalysis.user_id == user_id)
            .order_by(PositionAnalysis.created_at.desc())
            .limit(100)
        )
    ).scalars().all()

    items = [
        PositionHistoryItem(
            id=row.id,
            analyzed_at=row.created_at.isoformat() if row.created_at else "",
            jd_titles=[s.get("title", "") for s in (row.jd_snapshots or [])],
            jd_snapshots=row.jd_snapshots or [],
            missing_skills=[MissingSkillItem(**m) for m in (row.missing_skills or [])],
            profile_skill_count=row.profile_skill_count or 0,
            match_percentage=row.match_percentage or 0,
        )
        for row in rows
    ]

    # Aggregate the most commonly missing skills across recent runs for the banner.
    tally: dict[str, int] = {}
    for row in rows[:10]:
        for m in row.missing_skills or []:
            name = m.get("skill")
            if name:
                tally[name] = tally.get(name, 0) + 1
    latest_missing = [name for name, _ in sorted(tally.items(), key=lambda kv: -kv[1])][:3]

    return PositionHistoryResponse(items=items, latest_missing_skills=latest_missing)


# ─── Feedback ─────────────────────────────────────────────────────

@router.post("/feedback", response_model=PositionFeedbackResponse)
async def submit_feedback(
    data: PositionFeedbackRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    if data.analysis_id:
        exists = (
            await db.execute(
                select(PositionAnalysis).where(
                    PositionAnalysis.id == data.analysis_id, PositionAnalysis.user_id == user_id
                )
            )
        ).scalar_one_or_none()
        if not exists:
            raise HTTPException(status_code=404, detail="Analysis not found")

    row = PositionFeedback(
        user_id=user_id,
        analysis_id=data.analysis_id,
        score_satisfaction=data.score_satisfaction,
        skill_breakdown_accuracy=data.skill_breakdown_accuracy,
        relevance_weighting_ok=data.relevance_weighting_ok,
        missing_skill_accuracy=data.missing_skill_accuracy,
        relevance_comment=data.relevance_comment.strip(),
        missing_skill_comment=data.missing_skill_comment.strip(),
        comments=data.comments.strip(),
    )
    db.add(row)
    await db.flush()
    return PositionFeedbackResponse()
