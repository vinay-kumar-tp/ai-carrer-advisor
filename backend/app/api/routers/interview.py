"""AI Mock Interview — conversational, voice-led practice + performance report.

Flow
----
1. ``GET  /config``              — dropdown data for the setup screen.
2. ``POST /start``               — create a session, return the opening question.
3. ``POST /{id}/turn``           — send the candidate's answer, get the next
                                    interviewer line (adaptive) or the finished
                                    report when the interview is complete.
4. ``POST /{id}/feedback``       — store the post-interview satisfaction survey.
5. ``GET  /{id}/report``         — fetch a completed session's report.
6. ``GET  /history``             — list the user's past attempts.

The heavy lifting (adaptive questioning + grading) lives in
``app.services.interview_engine`` and degrades gracefully without a Gemini key.
"""

import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user_id
from app.db.session import get_db
from app.models.models import (
    InterviewSession,
    LeaderboardEntry,
    Resume,
    User,
    XPLog,
)
from app.schemas.schemas import (
    InterviewAnswerRequest,
    InterviewFeedbackRequest,
    InterviewStartRequest,
)
from app.services import interview_engine as engine

router = APIRouter()

XP_REWARD = 50


def _now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _turn(role: str, content: str) -> dict:
    return {"role": role, "content": content, "timestamp": _now_iso()}


def _scored_answers(transcript: list[dict]) -> int:
    """Candidate answers that count toward the question total.

    Q1 (the interviewer's opening) is a warm-up: the first candidate answer is
    the response to it, so scored answers are candidate turns beyond the first.
    """
    return max(sum(1 for m in transcript if m["role"] == "candidate") - 1, 0)


# ─── Setup metadata ──────────────────────────────────────────────

@router.get("/config")
async def interview_config(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    res = await db.execute(
        select(Resume).where(Resume.user_id == user_id).order_by(Resume.created_at.desc())
    )
    resumes = res.scalars().all()
    return {
        "job_titles": engine.STANDARD_JOB_TITLES,
        "skills": engine.SKILLS,
        "difficulty_levels": engine.DIFFICULTY_LEVELS,
        "question_mixes": engine.QUESTION_MIXES,
        "interviewer_name": engine.INTERVIEWER_NAME,
        "total_questions": engine.DEFAULT_TOTAL_QUESTIONS,
        "resumes": [
            {"id": r.id, "name": r.name, "source": r.source, "is_primary": bool(r.is_primary)}
            for r in resumes
        ],
    }


# ─── Start ───────────────────────────────────────────────────────

@router.post("/start")
async def start_interview(
    data: InterviewStartRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    config = {
        "source": data.source,
        "job_title": data.job_title,
        "job_description": data.job_description,
        "skill": data.skill,
        "resume_id": data.resume_id,
        "difficulty": data.difficulty,
        "question_mix": data.question_mix,
    }

    # Basic validation so the interviewer has something to anchor on.
    if data.source == "job" and not (data.job_title or (data.job_description or "").strip()):
        raise HTTPException(status_code=400, detail="Select a job title or paste a job description.")
    if data.source == "skill" and not data.skill:
        raise HTTPException(status_code=400, detail="Select a skill to practise.")

    user = await db.get(User, user_id)
    candidate_name = user.full_name if user else ""

    label = engine.build_context_label(config)
    opening = engine.opening_question(config, candidate_name)

    session = InterviewSession(
        user_id=user_id,
        mode="adaptive",
        job_context=label,
        title=f"{label} Practice",
        config=config,
        transcript=[_turn("interviewer", opening)],
        is_completed=False,
    )
    db.add(session)
    await db.flush()

    return {
        "session_id": str(session.id),
        "title": session.title,
        "interviewer_name": engine.INTERVIEWER_NAME,
        "total_questions": engine.DEFAULT_TOTAL_QUESTIONS,
        "question_number": 1,
        "question": opening,
        "is_warmup": True,
        "completed": False,
    }


# ─── Turn (adaptive) ─────────────────────────────────────────────

@router.post("/{session_id}/turn")
async def take_turn(
    session_id: str,
    data: InterviewAnswerRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    res = await db.execute(
        select(InterviewSession).where(
            InterviewSession.id == session_id,
            InterviewSession.user_id == user_id,
        )
    )
    session = res.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")
    if session.is_completed:
        raise HTTPException(status_code=400, detail="This interview is already completed")

    config = dict(session.config or {})
    transcript = list(session.transcript or [])
    transcript.append(_turn("candidate", (data.answer_text or "").strip()))

    answered = _scored_answers(transcript)  # scored answers captured so far

    # Finished: warm-up + all scored questions answered → grade the session.
    if answered >= engine.DEFAULT_TOTAL_QUESTIONS:
        return await _finish(session, config, transcript, user_id, db)

    # Otherwise ask the next adaptive question.
    next_line = await engine.next_interviewer_turn(config, transcript, answered)
    transcript.append(_turn("interviewer", next_line))
    session.transcript = transcript
    await db.flush()

    return {
        "completed": False,
        "question": next_line,
        "question_number": answered + 2,  # +1 warm-up, +1 for 1-based display
        "total_questions": engine.DEFAULT_TOTAL_QUESTIONS,
        "is_warmup": False,
    }


async def _finish(
    session: InterviewSession,
    config: dict,
    transcript: list[dict],
    user_id: str,
    db: AsyncSession,
) -> dict:
    report = await engine.generate_report(config, transcript)
    breakdown = report["breakdown"]

    session.transcript = transcript
    session.report = report
    session.scores = {
        "overall": report["overall_score"],
        "response_quality": breakdown["response_quality"]["score"],
        "behavioural_competency": breakdown["behavioural_competency"]["score"],
        "speech_quality": breakdown["speech_quality"]["score"],
    }
    session.feedback = report["recruiter_perspective"]
    session.is_completed = True
    session.completed_at = datetime.datetime.now(datetime.timezone.utc)

    # Gamification — award XP once per completed interview.
    db.add(XPLog(user_id=user_id, action="mock_interview", points=XP_REWARD))
    lb_res = await db.execute(
        select(LeaderboardEntry).where(LeaderboardEntry.user_id == user_id)
    )
    lb = lb_res.scalar_one_or_none()
    if lb:
        lb.total_xp += XP_REWARD

    await db.flush()

    return {
        "completed": True,
        "session_id": str(session.id),
        "report": _report_payload(session),
    }


# ─── Post-interview satisfaction survey ──────────────────────────

@router.post("/{session_id}/feedback")
async def submit_feedback(
    session_id: str,
    data: InterviewFeedbackRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    res = await db.execute(
        select(InterviewSession).where(
            InterviewSession.id == session_id,
            InterviewSession.user_id == user_id,
        )
    )
    session = res.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")

    session.user_feedback = {
        "rating": data.rating,
        "hoping_to_improve": data.hoping_to_improve,
        "what_should_be_better": data.what_should_be_better,
        "comment": data.comment,
        "submitted_at": _now_iso(),
    }
    await db.flush()
    return {"message": "Thanks for the feedback", "success": True}


# ─── Report ──────────────────────────────────────────────────────

def _report_payload(session: InterviewSession) -> dict:
    report = dict(session.report or {})
    duration_min = None
    if session.completed_at and session.created_at:
        # SQLite returns naive datetimes; normalise both sides before subtracting.
        started = session.created_at.replace(tzinfo=None)
        finished = session.completed_at.replace(tzinfo=None)
        delta = finished - started
        duration_min = max(1, round(delta.total_seconds() / 60))
    config = dict(session.config or {})
    spoken = sum(1 for m in (session.transcript or []) if m["role"] == "candidate")
    return {
        "session_id": str(session.id),
        "title": session.title,
        "context_label": session.job_context,
        "source": config.get("source"),
        "difficulty": config.get("difficulty"),
        "created_at": session.created_at.isoformat() if session.created_at else None,
        "duration_min": duration_min,
        "questions_spoken": spoken,
        "questions_reviewed": len(report.get("questions", [])),
        **report,
    }


@router.get("/{session_id}/report")
async def get_report(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    res = await db.execute(
        select(InterviewSession).where(
            InterviewSession.id == session_id,
            InterviewSession.user_id == user_id,
        )
    )
    session = res.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")
    if not session.is_completed:
        raise HTTPException(status_code=400, detail="This interview is not completed yet")
    return _report_payload(session)


# ─── History ─────────────────────────────────────────────────────

@router.get("/history")
async def interview_history(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    res = await db.execute(
        select(InterviewSession)
        .where(InterviewSession.user_id == user_id)
        .order_by(InterviewSession.created_at.desc())
    )
    sessions = res.scalars().all()
    return [
        {
            "id": str(s.id),
            "title": s.title or s.job_context,
            "context_label": s.job_context,
            "difficulty": (s.config or {}).get("difficulty"),
            "overall_score": (s.scores or {}).get("overall"),
            "band": (s.report or {}).get("band"),
            "is_completed": s.is_completed,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        }
        for s in sessions
    ]
