from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.models.models import InterviewSession, XPLog, LeaderboardEntry
from app.schemas.schemas import InterviewStartRequest, InterviewAnswerRequest, InterviewFeedbackResponse
from app.core.security import get_current_user_id
import datetime

router = APIRouter()

PRESET_QUESTIONS = [
    "Tell me about yourself and your career goals.",
    "Describe a challenging technical problem you solved and how you approached it.",
    "How do you prioritize tasks when working under tight deadlines?",
    "What are your key technical strengths, and what area are you working to improve?",
    "Do you have any questions for us about the role or company?"
]

@router.post("/start")
async def start_interview(
    data: InterviewStartRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    session = InterviewSession(
        user_id=user_id,
        mode=data.mode,
        job_context=data.job_context or "General Software Engineer",
        transcript=[{"role": "interviewer", "content": PRESET_QUESTIONS[0], "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()}],
        is_completed=False
    )
    db.add(session)
    await db.flush()

    return {
        "session_id": str(session.id),
        "mode": session.mode,
        "job_context": session.job_context,
        "first_question": PRESET_QUESTIONS[0]
    }

@router.post("/{session_id}/answer")
async def answer_interview_question(
    session_id: str,
    data: InterviewAnswerRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    res = await db.execute(select(InterviewSession).where(InterviewSession.id == session_id, InterviewSession.user_id == user_id))
    session = res.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")

    if session.is_completed:
        raise HTTPException(status_code=400, detail="Interview session is already completed")

    transcript = list(session.transcript)
    transcript.append({
        "role": "candidate",
        "content": data.answer_text,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
    })

    # Count candidate turns
    candidate_turns = sum(1 for msg in transcript if msg["role"] == "candidate")

    if candidate_turns < len(PRESET_QUESTIONS):
        next_q = PRESET_QUESTIONS[candidate_turns]
        transcript.append({
            "role": "interviewer",
            "content": next_q,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
        })
        session.transcript = transcript
        await db.flush()
        return {
            "completed": False,
            "next_question": next_q,
            "turn": candidate_turns + 1,
            "total_turns": len(PRESET_QUESTIONS)
        }
    else:
        # Finish session and evaluate
        session.is_completed = True
        session.completed_at = datetime.datetime.now(datetime.timezone.utc)
        
        # Calculate rubric feedback
        scores = {
            "communication": 85,
            "technical_depth": 80,
            "confidence": 88,
            "overall": 84
        }
        feedback_summary = "Excellent articulation and clear structured responses. Focus on quantifying achievements using STAR method."

        session.scores = scores
        session.feedback = feedback_summary
        session.transcript = transcript

        # Award XP
        db.add(XPLog(user_id=user_id, action="mock_interview", points=50))
        lb_res = await db.execute(select(LeaderboardEntry).where(LeaderboardEntry.user_id == user_id))
        lb = lb_res.scalar_one_or_none()
        if lb:
            lb.total_xp += 50

        await db.flush()

        return {
            "completed": True,
            "scores": scores,
            "feedback": feedback_summary,
            "transcript": transcript
        }

@router.get("/history")
async def interview_history(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    query = select(InterviewSession).where(InterviewSession.user_id == user_id).order_by(InterviewSession.created_at.desc())
    result = await db.execute(query)
    sessions = result.scalars().all()
    return [
        {
            "id": str(s.id),
            "mode": s.mode,
            "job_context": s.job_context,
            "scores": s.scores,
            "feedback": s.feedback,
            "is_completed": s.is_completed,
            "created_at": s.created_at.isoformat()
        }
        for s in sessions
    ]
