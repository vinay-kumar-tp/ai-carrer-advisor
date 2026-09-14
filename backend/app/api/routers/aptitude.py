"""Aptitude Quest — a topic/subtopic MCQ studio with server-checked practice.

Design mirrors Code Quest: a content catalog (sections -> topics -> subtopics),
practice serving that hides answers, a single-answer check endpoint that records
per-user progress, whole-set submission with a review payload, and progress /
leaderboard / history views. XP + leaderboard are awarded on the FIRST correct
answer of each question (so accuracy can't be farmed by re-answering).
"""

from __future__ import annotations

import datetime
import random

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import Integer, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.content.aptitude import catalog
from app.content.aptitude.framework import SECTION_LABELS
from app.core.security import get_current_user_id
from app.db.session import get_db
from app.models.models import (
    AptitudeProgress,
    LeaderboardEntry,
    MCQQuestion,
    QuizAttempt,
    XPLog,
)
from app.schemas.schemas import (
    AptitudeQuestionOut,
    AptitudeSetSubmission,
    CheckAnswerRequest,
    CheckAnswerResponse,
    QuestionResponse,
    QuizResultResponse,
    QuizSubmission,
)

router = APIRouter()


def _now():
    return datetime.datetime.now(datetime.timezone.utc)


async def _award_xp(db: AsyncSession, user_id: str, points: int, action: str):
    """Add XP and keep the leaderboard row in sync (create if missing)."""
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


def _slug_to_topic(slug: str):
    for topic in catalog.iter_topics():
        if topic.slug == slug:
            return topic
    return None


# ─── Catalog ─────────────────────────────────────────────────────

@router.get("/catalog")
async def get_catalog(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Sections -> topics -> subtopics with counts, plus per-user solved counts."""
    data = catalog.build_catalog()

    # per-topic solved counts for this user
    rows = (
        await db.execute(
            select(AptitudeProgress.topic, func.count(AptitudeProgress.id))
            .where(AptitudeProgress.user_id == user_id, AptitudeProgress.solved == True)  # noqa: E712
            .group_by(AptitudeProgress.topic)
        )
    ).all()
    solved_by_topic = {topic: count for topic, count in rows}

    for section in data["sections"]:
        for topic in section["topics"]:
            topic["solved_count"] = solved_by_topic.get(topic["name"], 0)

    return data


# ─── Practice serve ──────────────────────────────────────────────

@router.get("/topics/{slug}/questions", response_model=list[AptitudeQuestionOut])
async def topic_questions(
    slug: str,
    limit: int = Query(10, ge=1, le=30),
    subtopic: str = Query(None),
    shuffle: bool = Query(True),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    topic = _slug_to_topic(slug)
    if topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")

    query = select(MCQQuestion).where(MCQQuestion.topic == topic.name)
    if subtopic:
        query = query.where(MCQQuestion.subtopic == subtopic)
    rows = (await db.execute(query.order_by(MCQQuestion.display_order))).scalars().all()
    if not rows:
        raise HTTPException(status_code=404, detail="No questions seeded for this topic yet")

    rows = list(rows)
    if shuffle:
        random.shuffle(rows)
    rows = rows[:limit]

    # which of these has the user already solved?
    ids = [r.id for r in rows]
    solved_ids = set(
        (
            await db.execute(
                select(AptitudeProgress.question_id).where(
                    AptitudeProgress.user_id == user_id,
                    AptitudeProgress.question_id.in_(ids),
                    AptitudeProgress.solved == True,  # noqa: E712
                )
            )
        ).scalars().all()
    )

    return [
        AptitudeQuestionOut(
            id=str(r.id),
            slug=r.slug,
            section=r.section,
            topic=r.topic,
            subtopic=r.subtopic,
            difficulty=r.difficulty,
            points=r.points or 5,
            question_text=r.question_text,
            options=r.options,
            solved=r.id in solved_ids,
        )
        for r in rows
    ]


# ─── Single-answer check (practice mode) ─────────────────────────

@router.post("/check", response_model=CheckAnswerResponse)
async def check_answer(
    data: CheckAnswerRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    q = (
        await db.execute(select(MCQQuestion).where(MCQQuestion.id == data.question_id))
    ).scalar_one_or_none()
    if q is None:
        raise HTTPException(status_code=404, detail="Question not found")

    correct = data.choice == q.correct_index

    prog = (
        await db.execute(
            select(AptitudeProgress).where(
                AptitudeProgress.user_id == user_id,
                AptitudeProgress.question_id == q.id,
            )
        )
    ).scalar_one_or_none()

    first_attempt = prog is None
    points_earned = 0

    if prog is None:
        prog = AptitudeProgress(
            user_id=user_id,
            question_id=q.id,
            section=q.section,
            topic=q.topic,
            subtopic=q.subtopic or "",
            attempts=0,
            first_correct=correct,
        )
        db.add(prog)

    prog.attempts = (prog.attempts or 0) + 1
    prog.last_choice = data.choice

    # Award points only the first time it's answered correctly.
    if correct and not prog.solved:
        prog.solved = True
        points_earned = q.points or 5
        prog.points_earned = (prog.points_earned or 0) + points_earned
        await _award_xp(db, user_id, points_earned, action=f"aptitude_{q.section}")

    await db.flush()

    return CheckAnswerResponse(
        question_id=str(q.id),
        correct=correct,
        correct_index=q.correct_index,
        explanation=q.explanation,
        points_earned=points_earned,
        first_attempt=first_attempt,
    )


# ─── Whole-set submission (topic quiz) ───────────────────────────

@router.post("/submit-set")
async def submit_set(
    data: AptitudeSetSubmission,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    if len(data.question_ids) != len(data.answers):
        raise HTTPException(status_code=400, detail="Mismatched questions and answers length")
    if not data.question_ids:
        raise HTTPException(status_code=400, detail="No answers submitted")

    q_rows = (
        await db.execute(select(MCQQuestion).where(MCQQuestion.id.in_(data.question_ids)))
    ).scalars().all()
    by_id = {r.id: r for r in q_rows}

    total = len(data.question_ids)
    correct_count = 0
    review = []
    total_points = 0

    # preload existing progress for these questions
    existing = {
        p.question_id: p
        for p in (
            await db.execute(
                select(AptitudeProgress).where(
                    AptitudeProgress.user_id == user_id,
                    AptitudeProgress.question_id.in_(data.question_ids),
                )
            )
        ).scalars().all()
    }

    for qid, choice in zip(data.question_ids, data.answers):
        q = by_id.get(qid)
        if q is None:
            continue
        is_correct = choice == q.correct_index
        if is_correct:
            correct_count += 1

        prog = existing.get(qid)
        if prog is None:
            prog = AptitudeProgress(
                user_id=user_id, question_id=qid, section=q.section,
                topic=q.topic, subtopic=q.subtopic or "", attempts=0,
                first_correct=is_correct,
            )
            db.add(prog)
            existing[qid] = prog
        prog.attempts = (prog.attempts or 0) + 1
        prog.last_choice = choice
        if is_correct and not prog.solved:
            prog.solved = True
            pts = q.points or 5
            total_points += pts
            prog.points_earned = (prog.points_earned or 0) + pts

        review.append({
            "question_id": str(qid),
            "question_text": q.question_text,
            "options": q.options,
            "chosen": choice,
            "correct_index": q.correct_index,
            "correct": is_correct,
            "explanation": q.explanation,
        })

    percentage = round((correct_count / total) * 100, 2) if total else 0.0
    topic_label = None
    if data.topic_slug:
        t = _slug_to_topic(data.topic_slug)
        topic_label = t.name if t else data.topic_slug

    attempt = QuizAttempt(
        user_id=user_id,
        quiz_type="aptitude",
        topic=topic_label or (SECTION_LABELS.get(data.section or "") or "Aptitude"),
        score=correct_count,
        total=total,
        percentage=percentage,
        answers=review,
        time_taken_seconds=data.time_taken_seconds,
        completed_at=_now(),
    )
    db.add(attempt)

    if total_points > 0:
        await _award_xp(db, user_id, total_points, action="aptitude_set")
        lb = (
            await db.execute(select(LeaderboardEntry).where(LeaderboardEntry.user_id == user_id))
        ).scalar_one_or_none()
        if lb:
            lb.quizzes_passed = (lb.quizzes_passed or 0) + 1

    await db.flush()

    return {
        "id": str(attempt.id),
        "topic": attempt.topic,
        "score": correct_count,
        "total": total,
        "percentage": percentage,
        "points_earned": total_points,
        "review": review,
    }


# ─── Progress ────────────────────────────────────────────────────

@router.get("/progress")
async def get_progress(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    cat = catalog.build_catalog()

    # totals per section from the catalog
    section_totals: dict[str, dict] = {}
    for sec in cat["sections"]:
        section_totals[sec["key"]] = {
            "key": sec["key"],
            "label": sec["label"],
            "total_questions": sum(t["question_count"] for t in sec["topics"]),
            "total_topics": len(sec["topics"]),
        }

    # per-user aggregates per section
    rows = (
        await db.execute(
            select(
                AptitudeProgress.section,
                func.count(AptitudeProgress.id),
                func.sum(cast(AptitudeProgress.first_correct, Integer)),
                func.count(func.distinct(AptitudeProgress.topic)),
            )
            .where(AptitudeProgress.user_id == user_id)
            .group_by(AptitudeProgress.section)
        )
    ).all()
    agg = {
        section: {"attempted": attempted or 0, "first_correct": first_correct or 0, "topics_touched": topics_touched or 0}
        for section, attempted, first_correct, topics_touched in rows
    }

    sections_out = []
    scored = []
    for key, meta in section_totals.items():
        a = agg.get(key, {"attempted": 0, "first_correct": 0, "topics_touched": 0})
        attempted = a["attempted"]
        accuracy = round((a["first_correct"] / attempted) * 100) if attempted else 0
        coverage = round((attempted / meta["total_questions"]) * 100) if meta["total_questions"] else 0
        enough = attempted >= 5
        # readiness score blends accuracy (70%) and coverage (30%), only when enough evidence
        score = round(accuracy * 0.7 + coverage * 0.3) if enough else None
        if enough:
            scored.append(score)
        sections_out.append({
            **meta,
            "attempted": attempted,
            "accuracy": accuracy,
            "coverage": coverage,
            "topics_touched": a["topics_touched"],
            "enough_evidence": enough,
            "score": score,
        })

    overall = round(sum(scored) / len(scored)) if scored else None
    total_solved = (
        await db.execute(
            select(func.count(AptitudeProgress.id)).where(
                AptitudeProgress.user_id == user_id, AptitudeProgress.solved == True  # noqa: E712
            )
        )
    ).scalar() or 0
    attempts_count = (
        await db.execute(
            select(func.count(QuizAttempt.id)).where(
                QuizAttempt.user_id == user_id, QuizAttempt.quiz_type == "aptitude"
            )
        )
    ).scalar() or 0

    return {
        "overall_score": overall,
        "total_solved": total_solved,
        "total_questions": cat["total_questions"],
        "assessments_taken": attempts_count,
        "sections": sections_out,
    }


# ─── Leaderboard ─────────────────────────────────────────────────

@router.get("/leaderboard")
async def leaderboard(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    from app.models.models import User

    rows = (
        await db.execute(
            select(LeaderboardEntry, User)
            .join(User, LeaderboardEntry.user_id == User.id)
            .order_by(LeaderboardEntry.total_xp.desc(), User.full_name)
            .limit(limit)
        )
    ).all()
    return [
        {
            "rank": i + 1,
            "user_id": board.user_id,
            "full_name": user.full_name,
            "total_xp": board.total_xp or 0,
            "level": board.level or 1,
            "quizzes_passed": board.quizzes_passed or 0,
        }
        for i, (board, user) in enumerate(rows)
    ]


# ─── History ─────────────────────────────────────────────────────

@router.get("/history", response_model=list[QuizResultResponse])
async def get_quiz_history(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(QuizAttempt)
        .where(QuizAttempt.user_id == user_id)
        .order_by(QuizAttempt.completed_at.desc())
    )
    attempts = (await db.execute(query)).scalars().all()
    return [
        QuizResultResponse(
            id=str(a.id),
            quiz_type=a.quiz_type,
            topic=a.topic,
            score=a.score,
            total=a.total,
            percentage=a.percentage,
            time_taken_seconds=a.time_taken_seconds,
            completed_at=a.completed_at,
        )
        for a in attempts
    ]


# ─── Legacy endpoints (kept for backward compatibility) ──────────

@router.get("/questions", response_model=list[QuestionResponse])
async def get_questions(
    topic: str = Query(None),
    difficulty: str = Query(None),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    query = select(MCQQuestion)
    if topic:
        query = query.where(MCQQuestion.topic == topic)
    if difficulty:
        query = query.where(MCQQuestion.difficulty == difficulty)
    questions = (await db.execute(query.limit(limit))).scalars().all()
    return [
        QuestionResponse(
            id=str(q.id),
            question_text=q.question_text,
            options=q.options,
            topic=q.topic,
            difficulty=q.difficulty,
        )
        for q in questions
    ]


@router.post("/submit", response_model=QuizResultResponse, status_code=201)
async def submit_quiz(
    data: QuizSubmission,
    topic: str = Query("aptitude"),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    if len(data.question_ids) != len(data.answers):
        raise HTTPException(status_code=400, detail="Mismatched questions and answers length")

    total = len(data.question_ids)
    correct_count = 0
    detailed = []
    for qid, ans in zip(data.question_ids, data.answers):
        q = (await db.execute(select(MCQQuestion).where(MCQQuestion.id == qid))).scalar_one_or_none()
        is_correct = bool(q and q.correct_index == ans)
        if is_correct:
            correct_count += 1
        detailed.append({"question_id": qid, "chosen": ans, "correct": is_correct})

    percentage = round((correct_count / total) * 100, 2) if total else 0.0
    attempt = QuizAttempt(
        user_id=user_id, quiz_type="aptitude", topic=topic, score=correct_count,
        total=total, percentage=percentage, answers=detailed, completed_at=_now(),
    )
    db.add(attempt)
    await _award_xp(db, user_id, correct_count * 5, action=f"quiz_{topic}")
    await db.flush()

    return QuizResultResponse(
        id=str(attempt.id), quiz_type=attempt.quiz_type, topic=attempt.topic,
        score=attempt.score, total=attempt.total, percentage=attempt.percentage,
        time_taken_seconds=None, completed_at=attempt.completed_at,
    )
