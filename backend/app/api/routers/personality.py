"""Big Five (OCEAN) assessment engine.

Serves two forms (BFI-44 quick, IPIP-NEO-120 comprehensive), scores them
deterministically per the psychometric key, monitors response compliance, and
returns a structured candidate profile with workplace behavioural insights.
"""

from __future__ import annotations

import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.content.personality import catalog
from app.content.personality.framework import SCALE, TRAIT_LABELS, TRAITS
from app.core.security import get_current_user_id
from app.db.session import get_db
from app.models.models import LeaderboardEntry, PersonalityResult, XPLog
from app.schemas.schemas import (
    PersonalityFormMeta,
    PersonalityResponse,
    PersonalitySubmission,
    PersonalitySubmitRequest,
)

router = APIRouter()

XP_REWARD = 30


def _now():
    return datetime.datetime.now(datetime.timezone.utc)


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


def _structured(row: PersonalityResult) -> dict:
    """Build the spec's structured JSON output from a stored result row."""
    detail = dict(row.scores_detail or {})
    scores = {}
    for t in TRAITS:
        d = detail.get(t) or {}
        scores[t] = {
            "label": TRAIT_LABELS[t],
            "raw_score": d.get("raw_score", 0),
            "min_score": d.get("min_score", 0),
            "max_score": d.get("max_score", 0),
            "percentage": d.get("percentage", 0.0),
            "level": d.get("level", "Moderate"),
        }
    compliance = dict(row.compliance or {})
    return {
        "assessment_metadata": {
            "form": row.form or "legacy",
            "total_questions": row.total_questions or 0,
            "completed_questions": row.total_questions or 0,
            "compliance_status": compliance.get("status", "Passed"),
            "completion_time_seconds": row.completion_time_seconds,
        },
        "scores": scores,
        "workplace_behavioral_insights": dict(row.insights or {}),
        "compliance": compliance,
        "completed_at": row.completed_at.isoformat() if row.completed_at else None,
    }


# ─── Forms metadata ──────────────────────────────────────────────

@router.get("/forms", response_model=list[PersonalityFormMeta])
async def get_forms():
    return catalog.list_forms()


@router.get("/forms/{key}/questions")
async def get_form_questions(key: str):
    try:
        form = catalog.get_form(key)
    except KeyError:
        raise HTTPException(status_code=404, detail="Unknown assessment form")
    return {
        "form": {
            "key": form.key,
            "name": form.name,
            "short_name": form.short_name,
            "description": form.description,
            "est_minutes": form.est_minutes,
            "total_questions": form.total_questions,
        },
        "prompt_prefix": "I see myself as someone who…",
        "scale": SCALE,
        "questions": [
            {"index": i, "text": item.text}
            for i, item in enumerate(form.items)
        ],
    }


# ─── Submit + score ──────────────────────────────────────────────

@router.post("/forms/{key}/submit")
async def submit_form(
    key: str,
    data: PersonalitySubmitRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    try:
        form = catalog.get_form(key)
    except KeyError:
        raise HTTPException(status_code=404, detail="Unknown assessment form")

    if len(data.responses) != form.total_questions:
        raise HTTPException(
            status_code=400,
            detail=f"Expected {form.total_questions} responses, got {len(data.responses)}",
        )
    if any(not (1 <= r <= 5) for r in data.responses):
        raise HTTPException(status_code=400, detail="Every response must be an integer 1–5")

    detail = catalog.score_form(key, data.responses)          # {trait: {raw,min,max,pct,level}}
    compliance = catalog.check_compliance(data.responses)
    insights = catalog.build_insights(detail)

    percentages = {t: detail[t]["percentage"] for t in TRAITS}
    levels = {t: detail[t]["level"] for t in TRAITS}
    raw_scores = {t: detail[t]["raw_score"] for t in TRAITS}

    # Upsert the single result row for this user.
    row = (
        await db.execute(select(PersonalityResult).where(PersonalityResult.user_id == user_id))
    ).scalar_one_or_none()
    if row is None:
        row = PersonalityResult(user_id=user_id)
        db.add(row)

    row.form = key
    row.total_questions = form.total_questions
    row.raw_answers = data.responses
    row.raw_scores = raw_scores
    row.percentages = percentages
    row.levels = levels
    row.scores_detail = detail
    row.compliance = compliance
    row.insights = insights
    row.completion_time_seconds = data.completion_time_seconds
    row.completed_at = _now()
    # keep the legacy flat trait % columns in sync
    row.openness = percentages["openness"]
    row.conscientiousness = percentages["conscientiousness"]
    row.extraversion = percentages["extraversion"]
    row.agreeableness = percentages["agreeableness"]
    row.neuroticism = percentages["neuroticism"]

    await _award_xp(db, user_id, XP_REWARD, action=f"personality_{key}")
    await db.flush()

    return _structured(row)


@router.get("/my-result")
async def get_my_result(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    row = (
        await db.execute(select(PersonalityResult).where(PersonalityResult.user_id == user_id))
    ).scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="No assessment completed yet")
    # Full structured result when a v2 form was taken; else a minimal shape.
    if row.form:
        return _structured(row)
    return {
        "assessment_metadata": {"form": "legacy", "total_questions": 10, "completed_questions": 10,
                                "compliance_status": "Passed", "completion_time_seconds": None},
        "scores": {
            t: {
                "label": TRAIT_LABELS[t],
                "raw_score": 0, "min_score": 0, "max_score": 100,
                "percentage": getattr(row, t) or 0.0,
                "level": catalog.level_for(getattr(row, t) or 0.0),
            }
            for t in TRAITS
        },
        "workplace_behavioral_insights": {},
        "compliance": {"status": "Passed"},
        "completed_at": row.completed_at.isoformat() if row.completed_at else None,
    }


# ─── Legacy 10-item form (kept for backward compatibility) ───────

BIG_FIVE_QUESTIONS = [
    {"id": 1, "text": "I am the life of the party.", "trait": "extraversion", "key": 1},
    {"id": 2, "text": "I feel little concern for others.", "trait": "agreeableness", "key": -1},
    {"id": 3, "text": "I am always prepared.", "trait": "conscientiousness", "key": 1},
    {"id": 4, "text": "I get stressed out easily.", "trait": "neuroticism", "key": 1},
    {"id": 5, "text": "I have a rich vocabulary.", "trait": "openness", "key": 1},
    {"id": 6, "text": "I don't talk a lot.", "trait": "extraversion", "key": -1},
    {"id": 7, "text": "I am interested in people.", "trait": "agreeableness", "key": 1},
    {"id": 8, "text": "I leave my belongings around.", "trait": "conscientiousness", "key": -1},
    {"id": 9, "text": "I am relaxed most of the time.", "trait": "neuroticism", "key": -1},
    {"id": 10, "text": "I have difficulty understanding abstract ideas.", "trait": "openness", "key": -1},
]


@router.get("/questions")
async def get_personality_questions():
    return BIG_FIVE_QUESTIONS


@router.post("/submit", response_model=PersonalityResponse)
async def submit_personality(
    data: PersonalitySubmission,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    if len(data.answers) != len(BIG_FIVE_QUESTIONS):
        raise HTTPException(status_code=400, detail="Answer count does not match question count")

    traits = {t: 0 for t in TRAITS}
    counts = {t: 0 for t in TRAITS}
    for i, ans in enumerate(data.answers):
        q = BIG_FIVE_QUESTIONS[i]
        score = ans if q["key"] == 1 else (6 - ans)
        traits[q["trait"]] += score
        counts[q["trait"]] += 1

    normalized = {t: round((traits[t] / (counts[t] * 5)) * 100, 1) if counts[t] else 0.0 for t in TRAITS}

    row = (
        await db.execute(select(PersonalityResult).where(PersonalityResult.user_id == user_id))
    ).scalar_one_or_none()
    if row is None:
        row = PersonalityResult(user_id=user_id)
        db.add(row)
    for t in TRAITS:
        setattr(row, t, normalized[t])
    row.raw_answers = data.answers
    row.form = ""  # legacy marker
    row.completed_at = _now()

    await _award_xp(db, user_id, 25, action="personality_test")
    await db.flush()

    return PersonalityResponse(**normalized)
