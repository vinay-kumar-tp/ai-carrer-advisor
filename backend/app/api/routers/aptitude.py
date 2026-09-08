from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.models.models import MCQQuestion, QuizAttempt, XPLog, LeaderboardEntry
from app.schemas.schemas import QuizSubmission, QuestionResponse, QuizResultResponse
from app.core.security import get_current_user_id
import datetime

router = APIRouter()

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
    
    query = query.limit(limit)
    result = await db.execute(query)
    questions = result.scalars().all()
    
    return [
        QuestionResponse(
            id=str(q.id),
            question_text=q.question_text,
            options=q.options,
            topic=q.topic,
            difficulty=q.difficulty
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
    detailed_answers = []

    for qid, ans in zip(data.question_ids, data.answers):
        res = await db.execute(select(MCQQuestion).where(MCQQuestion.id == qid))
        q = res.scalar_one_or_none()
        is_correct = False
        if q and q.correct_index == ans:
            is_correct = True
            correct_count += 1
        detailed_answers.append({"question_id": qid, "chosen": ans, "correct": is_correct})

    percentage = round((correct_count / total) * 100, 2) if total > 0 else 0.0

    attempt = QuizAttempt(
        user_id=user_id,
        quiz_type="aptitude",
        topic=topic,
        score=correct_count,
        total=total,
        percentage=percentage,
        answers=detailed_answers,
        completed_at=datetime.datetime.now(datetime.timezone.utc)
    )
    db.add(attempt)

    # Award XP
    xp_gained = correct_count * 5
    if xp_gained > 0:
        db.add(XPLog(user_id=user_id, action=f"quiz_{topic}", points=xp_gained))
        lb_res = await db.execute(select(LeaderboardEntry).where(LeaderboardEntry.user_id == user_id))
        lb = lb_res.scalar_one_or_none()
        if lb:
            lb.total_xp += xp_gained
            lb.quizzes_passed += 1

    await db.flush()

    return QuizResultResponse(
        id=str(attempt.id),
        quiz_type=attempt.quiz_type,
        topic=attempt.topic,
        score=attempt.score,
        total=attempt.total,
        percentage=attempt.percentage,
        time_taken_seconds=None,
        completed_at=attempt.completed_at
    )

@router.get("/history", response_model=list[QuizResultResponse])
async def get_quiz_history(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    query = select(QuizAttempt).where(QuizAttempt.user_id == user_id).order_by(QuizAttempt.completed_at.desc())
    result = await db.execute(query)
    attempts = result.scalars().all()
    return [
        QuizResultResponse(
            id=str(a.id),
            quiz_type=a.quiz_type,
            topic=a.topic,
            score=a.score,
            total=a.total,
            percentage=a.percentage,
            time_taken_seconds=a.time_taken_seconds,
            completed_at=a.completed_at
        )
        for a in attempts
    ]
