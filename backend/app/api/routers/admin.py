from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.session import get_db
from app.models.models import User, JobListing, CodingProblem, MCQQuestion, Application, QuizAttempt, InterviewSession
from app.core.security import decode_token, oauth2_scheme

router = APIRouter()

def require_admin(token: str = Depends(oauth2_scheme)):
    payload = decode_token(token)
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return payload.get("sub")

@router.get("/stats")
async def get_admin_stats(
    admin_id: str = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    users_count = (await db.execute(select(func.count(User.id)))).scalar_one()
    jobs_count = (await db.execute(select(func.count(JobListing.id)))).scalar_one()
    problems_count = (await db.execute(select(func.count(CodingProblem.id)))).scalar_one()
    mcqs_count = (await db.execute(select(func.count(MCQQuestion.id)))).scalar_one()
    apps_count = (await db.execute(select(func.count(Application.id)))).scalar_one()
    quizzes_count = (await db.execute(select(func.count(QuizAttempt.id)))).scalar_one()
    interviews_count = (await db.execute(select(func.count(InterviewSession.id)))).scalar_one()

    return {
        "total_users": users_count,
        "total_jobs": jobs_count,
        "total_coding_problems": problems_count,
        "total_mcq_questions": mcqs_count,
        "total_applications": apps_count,
        "total_quizzes_taken": quizzes_count,
        "total_mock_interviews": interviews_count,
    }

@router.get("/users")
async def get_users_list(
    admin_id: str = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    res = await db.execute(select(User).order_by(User.created_at.desc()))
    users = res.scalars().all()
    return [
        {
            "id": str(u.id),
            "email": u.email,
            "full_name": u.full_name,
            "role": u.role,
            "is_active": u.is_active,
            "created_at": u.created_at.isoformat()
        }
        for u in users
    ]
