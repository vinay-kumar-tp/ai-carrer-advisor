from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.models.models import PersonalityResult, XPLog, LeaderboardEntry
from app.schemas.schemas import PersonalitySubmission, PersonalityResponse
from app.core.security import get_current_user_id
import datetime

router = APIRouter()

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

    traits = {"openness": 0, "conscientiousness": 0, "extraversion": 0, "agreeableness": 0, "neuroticism": 0}
    counts = {"openness": 0, "conscientiousness": 0, "extraversion": 0, "agreeableness": 0, "neuroticism": 0}

    for i, ans in enumerate(data.answers):
        q = BIG_FIVE_QUESTIONS[i]
        trait = q["trait"]
        key = q["key"]
        # Score on 1-5 scale (or reverse scored)
        score = ans if key == 1 else (6 - ans)
        traits[trait] += score
        counts[trait] += 1

    # Convert to 0-100 scale
    normalized = {}
    for t in traits:
        max_possible = counts[t] * 5
        normalized[t] = round((traits[t] / max_possible) * 100, 1)

    # Save to database
    result = await db.execute(select(PersonalityResult).where(PersonalityResult.user_id == user_id))
    p_result = result.scalar_one_or_none()

    if p_result:
        p_result.openness = normalized["openness"]
        p_result.conscientiousness = normalized["conscientiousness"]
        p_result.extraversion = normalized["extraversion"]
        p_result.agreeableness = normalized["agreeableness"]
        p_result.neuroticism = normalized["neuroticism"]
        p_result.raw_answers = data.answers
        p_result.completed_at = datetime.datetime.now(datetime.timezone.utc)
    else:
        p_result = PersonalityResult(
            user_id=user_id,
            openness=normalized["openness"],
            conscientiousness=normalized["conscientiousness"],
            extraversion=normalized["extraversion"],
            agreeableness=normalized["agreeableness"],
            neuroticism=normalized["neuroticism"],
            raw_answers=data.answers,
        )
        db.add(p_result)

    # Award XP for completing test
    db.add(XPLog(user_id=user_id, action="personality_test", points=25))
    lb_res = await db.execute(select(LeaderboardEntry).where(LeaderboardEntry.user_id == user_id))
    lb = lb_res.scalar_one_or_none()
    if lb:
        lb.total_xp += 25

    await db.flush()

    return PersonalityResponse(
        openness=normalized["openness"],
        conscientiousness=normalized["conscientiousness"],
        extraversion=normalized["extraversion"],
        agreeableness=normalized["agreeableness"],
        neuroticism=normalized["neuroticism"]
    )

@router.get("/my-result", response_model=PersonalityResponse)
async def get_my_personality(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(PersonalityResult).where(PersonalityResult.user_id == user_id))
    p = result.scalar_one_or_none()
    if not p:
        raise HTTPException(status_code=404, detail="Personality test not completed yet")
    return PersonalityResponse(
        openness=p.openness,
        conscientiousness=p.conscientiousness,
        extraversion=p.extraversion,
        agreeableness=p.agreeableness,
        neuroticism=p.neuroticism
    )
