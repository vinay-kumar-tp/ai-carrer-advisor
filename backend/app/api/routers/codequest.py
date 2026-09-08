"""Code Quest — problem browser, judge and progress tracking.

Classification lives in JSON columns, which SQLite cannot filter efficiently, so
a small in-memory index of all problems is built once and filtered in Python.
With a few thousand problems that is far cheaper than the alternative and keeps
facet counts exact.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user_id
from app.db.session import get_db
from app.models.models import (
    CodeSubmission,
    CodingProblem,
    LeaderboardEntry,
    User,
    UserProblemStatus,
    XPLog,
)
from app.schemas.codequest import (
    DraftRequest,
    Facets,
    HintResponse,
    ProblemDetail,
    ProblemListItem,
    ProblemListResponse,
    ProgressResponse,
    RunRequest,
    RunResponse,
    StatsResponse,
    SubmissionItem,
    SubmitRequest,
    SubmitResponse,
)
from app.services import judge

router = APIRouter()

DIFFICULTY_ORDER = {"easy": 0, "medium": 1, "hard": 2}


# ─── In-memory problem index ─────────────────────────────────────

@dataclass(frozen=True)
class IndexRow:
    id: str
    slug: str
    title: str
    difficulty: str
    topics: tuple[str, ...]
    patterns: tuple[str, ...]
    companies: tuple[str, ...]
    sheets: tuple[str, ...]
    points: int
    display_order: int
    solved_count: int
    attempt_count: int


_index: Optional[list[IndexRow]] = None


def invalidate_index() -> None:
    """Called by the seeder after problems change."""
    global _index
    _index = None


async def _get_index(db: AsyncSession) -> list[IndexRow]:
    global _index
    if _index is not None:
        return _index

    result = await db.execute(
        select(
            CodingProblem.id,
            CodingProblem.slug,
            CodingProblem.title,
            CodingProblem.difficulty,
            CodingProblem.topics,
            CodingProblem.patterns,
            CodingProblem.companies,
            CodingProblem.sheets,
            CodingProblem.points,
            CodingProblem.display_order,
            CodingProblem.solved_count,
            CodingProblem.attempt_count,
        )
    )

    rows = []
    for row in result.all():
        rows.append(
            IndexRow(
                id=row.id,
                slug=row.slug or row.id,
                title=row.title,
                difficulty=row.difficulty or "easy",
                topics=tuple(row.topics or []),
                patterns=tuple(row.patterns or []),
                companies=tuple(row.companies or []),
                sheets=tuple(row.sheets or []),
                points=row.points or 10,
                display_order=row.display_order or 0,
                solved_count=row.solved_count or 0,
                attempt_count=row.attempt_count or 0,
            )
        )

    rows.sort(key=lambda r: (r.display_order, r.title))
    _index = rows
    return _index


async def _status_map(db: AsyncSession, user_id: str) -> dict[str, str]:
    result = await db.execute(
        select(UserProblemStatus.problem_id, UserProblemStatus.status).where(
            UserProblemStatus.user_id == user_id
        )
    )
    return {row.problem_id: row.status for row in result.all()}


def _acceptance(row: IndexRow) -> Optional[float]:
    if not row.attempt_count:
        return None
    return round(row.solved_count / row.attempt_count * 100, 1)


def _to_list_item(row: IndexRow, statuses: dict[str, str]) -> ProblemListItem:
    return ProblemListItem(
        slug=row.slug,
        title=row.title,
        difficulty=row.difficulty,
        topics=list(row.topics),
        patterns=list(row.patterns),
        companies=list(row.companies),
        sheets=list(row.sheets),
        points=row.points,
        status=statuses.get(row.id, "unsolved"),
        acceptance=_acceptance(row),
    )


def _filter_rows(
    rows: list[IndexRow],
    statuses: dict[str, str],
    q: Optional[str],
    difficulty: Optional[str],
    topic: Optional[str],
    pattern: Optional[str],
    company: Optional[str],
    sheet: Optional[str],
    status: Optional[str],
) -> list[IndexRow]:
    needle = (q or "").strip().lower()
    out = []
    for row in rows:
        if needle and needle not in row.title.lower():
            continue
        if difficulty and difficulty != "all" and row.difficulty != difficulty:
            continue
        if topic and topic not in row.topics:
            continue
        if pattern and pattern not in row.patterns:
            continue
        if company and company not in row.companies:
            continue
        if sheet and sheet not in row.sheets:
            continue
        if status and status != "all":
            current = statuses.get(row.id, "unsolved")
            if status == "solved" and current != "solved":
                continue
            if status == "unsolved" and current == "solved":
                continue
        out.append(row)
    return out


# ─── Metadata & facets ───────────────────────────────────────────

@router.get("/meta")
async def get_meta(db: AsyncSession = Depends(get_db)):
    rows = await _get_index(db)
    return {
        "total_problems": len(rows),
        "languages": judge.available_languages(),
        "difficulties": ["easy", "medium", "hard"],
    }


@router.get("/facets", response_model=Facets)
async def get_facets(db: AsyncSession = Depends(get_db)):
    rows = await _get_index(db)

    def tally(attribute: str) -> list[dict]:
        counts: dict[str, int] = {}
        for row in rows:
            for value in getattr(row, attribute):
                counts[value] = counts.get(value, 0) + 1
        return [{"name": name, "count": counts[name]} for name in sorted(counts)]

    return Facets(
        topics=tally("topics"),
        patterns=tally("patterns"),
        companies=tally("companies"),
        sheets=tally("sheets"),
    )


@router.get("/stats", response_model=StatsResponse)
async def get_stats(user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    rows = await _get_index(db)
    statuses = await _status_map(db, user_id)

    by_difficulty = {
        level: {"total": 0, "solved": 0}
        for level in ("easy", "medium", "hard")
    }
    for row in rows:
        bucket = by_difficulty.setdefault(row.difficulty, {"total": 0, "solved": 0})
        bucket["total"] += 1
        if statuses.get(row.id) == "solved":
            bucket["solved"] += 1

    points = (
        await db.execute(
            select(func.coalesce(func.sum(UserProblemStatus.points_earned), 0)).where(
                UserProblemStatus.user_id == user_id
            )
        )
    ).scalar_one()

    return StatsResponse(
        total_problems=len(rows),
        solved=sum(1 for value in statuses.values() if value == "solved"),
        attempted=len(statuses),
        points=int(points or 0),
        streak_days=await _current_streak(db, user_id),
        by_difficulty=by_difficulty,
    )


async def _current_streak(db: AsyncSession, user_id: str) -> int:
    """Consecutive days up to today with at least one accepted submission."""
    result = await db.execute(
        select(CodeSubmission.created_at).where(
            CodeSubmission.user_id == user_id, CodeSubmission.status == judge.ACCEPTED
        )
    )
    days = {row[0].date() for row in result.all() if row[0]}
    if not days:
        return 0

    today = datetime.now(timezone.utc).date()
    if today not in days and (today - timedelta(days=1)) not in days:
        return 0

    cursor = today if today in days else today - timedelta(days=1)
    streak = 0
    while cursor in days:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


# ─── Problem list ────────────────────────────────────────────────

@router.get("/problems", response_model=ProblemListResponse)
async def list_problems(
    q: Optional[str] = Query(None, max_length=200),
    difficulty: Optional[str] = Query(None),
    topic: Optional[str] = Query(None),
    pattern: Optional[str] = Query(None),
    company: Optional[str] = Query(None),
    sheet: Optional[str] = Query(None),
    status: Optional[str] = Query(None, pattern="^(all|solved|unsolved)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(40, ge=1, le=100),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    rows = await _get_index(db)
    statuses = await _status_map(db, user_id)
    matching = _filter_rows(rows, statuses, q, difficulty, topic, pattern, company, sheet, status)

    total = len(matching)
    start = (page - 1) * page_size
    window = matching[start:start + page_size]

    return ProblemListResponse(
        items=[_to_list_item(row, statuses) for row in window],
        total=total,
        page=page,
        page_size=page_size,
        showing_from=start + 1 if window else 0,
        showing_to=start + len(window),
    )


@router.get("/problems/random")
async def random_problem(
    difficulty: Optional[str] = Query(None),
    topic: Optional[str] = Query(None),
    pattern: Optional[str] = Query(None),
    company: Optional[str] = Query(None),
    sheet: Optional[str] = Query(None),
    status: Optional[str] = Query(None, pattern="^(all|solved|unsolved)$"),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Backs the "Pick One" button, honouring whatever filters are active."""
    rows = await _get_index(db)
    statuses = await _status_map(db, user_id)
    matching = _filter_rows(rows, statuses, None, difficulty, topic, pattern, company, sheet, status)
    if not matching:
        raise HTTPException(status_code=404, detail="No problem matches the current filters")

    # Prefer something not yet solved so the button keeps being useful.
    unsolved = [row for row in matching if statuses.get(row.id) != "solved"]
    return {"slug": random.choice(unsolved or matching).slug}


# ─── Problem detail ──────────────────────────────────────────────

async def _load_problem(db: AsyncSession, slug: str) -> CodingProblem:
    problem = (
        await db.execute(select(CodingProblem).where(CodingProblem.slug == slug))
    ).scalar_one_or_none()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    return problem


async def _get_or_create_status(db: AsyncSession, user_id: str, problem_id: str) -> UserProblemStatus:
    row = (
        await db.execute(
            select(UserProblemStatus).where(
                UserProblemStatus.user_id == user_id, UserProblemStatus.problem_id == problem_id
            )
        )
    ).scalar_one_or_none()
    if row is None:
        row = UserProblemStatus(user_id=user_id, problem_id=problem_id, status="attempted", attempts=0)
        db.add(row)
        await db.flush()
    return row


@router.get("/problems/{slug}", response_model=ProblemDetail)
async def get_problem(
    slug: str,
    difficulty: Optional[str] = Query(None),
    topic: Optional[str] = Query(None),
    pattern: Optional[str] = Query(None),
    company: Optional[str] = Query(None),
    sheet: Optional[str] = Query(None),
    status: Optional[str] = Query(None, pattern="^(all|solved|unsolved)$"),
    q: Optional[str] = Query(None, max_length=200),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    problem = await _load_problem(db, slug)
    rows = await _get_index(db)
    statuses = await _status_map(db, user_id)

    # Prev/next follow the same filtered ordering the list view used.
    matching = _filter_rows(rows, statuses, q, difficulty, topic, pattern, company, sheet, status)
    position = next((i for i, row in enumerate(matching) if row.slug == slug), None)

    progress = (
        await db.execute(
            select(UserProblemStatus).where(
                UserProblemStatus.user_id == user_id, UserProblemStatus.problem_id == problem.id
            )
        )
    ).scalar_one_or_none()

    hints = list(problem.hints or [])
    revealed = min(progress.revealed_hints if progress else 0, len(hints))
    drafts = (progress.drafts if progress and isinstance(progress.drafts, dict) else {}) or {}
    last_language = (progress.last_language if progress else "") or "python"

    index_row = next((row for row in rows if row.slug == slug), None)

    # Related problems: same pattern first, then same topic, excluding this one.
    related_pool = [
        row for row in rows
        if row.slug != slug and (set(row.patterns) & set(problem.patterns or []))
    ]
    if len(related_pool) < 8:
        related_pool += [
            row for row in rows
            if row.slug != slug and row not in related_pool
            and (set(row.topics) & set(problem.topics or []))
        ]
    related_pool.sort(key=lambda row: (DIFFICULTY_ORDER.get(row.difficulty, 9), row.display_order))
    related = [_to_list_item(row, statuses) for row in related_pool[:8]]

    return ProblemDetail(
        slug=problem.slug,
        title=problem.title,
        difficulty=problem.difficulty,
        points=problem.points or 10,
        time_limit_ms=problem.time_limit_ms or 5000,
        description=problem.description,
        notes=list(problem.notes or []),
        input_format=list(problem.input_format or []),
        output_format=list(problem.output_format or []),
        constraints=list(problem.constraints or []),
        examples=list(problem.examples or []),
        topics=list(problem.topics or []),
        patterns=list(problem.patterns or []),
        companies=list(problem.companies or []),
        sheets=list(problem.sheets or []),
        languages=[lang["key"] for lang in judge.available_languages()],
        starter_code=dict(problem.starter_code or {}),
        hint_count=len(hints),
        revealed_hints=hints[:revealed],
        pattern_note=problem.pattern_note or "",
        status=statuses.get(problem.id, "unsolved"),
        attempts=progress.attempts if progress else 0,
        best_score=progress.best_score if progress else 0,
        last_language=last_language,
        draft=drafts.get(last_language),
        acceptance=_acceptance(index_row) if index_row else None,
        position=(position + 1) if position is not None else None,
        total_in_filter=len(matching) if position is not None else None,
        prev_slug=matching[position - 1].slug if position not in (None, 0) else None,
        next_slug=(
            matching[position + 1].slug
            if position is not None and position + 1 < len(matching)
            else None
        ),
        related=related,
    )


@router.post("/problems/{slug}/hint", response_model=HintResponse)
async def reveal_hint(
    slug: str, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)
):
    problem = await _load_problem(db, slug)
    hints = list(problem.hints or [])
    progress = await _get_or_create_status(db, user_id, problem.id)
    progress.revealed_hints = min((progress.revealed_hints or 0) + 1, len(hints))
    await db.flush()
    return HintResponse(revealed_hints=hints[:progress.revealed_hints], hint_count=len(hints))


@router.put("/problems/{slug}/draft")
async def save_draft(
    slug: str,
    data: DraftRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Keeps the editor's contents so a reload does not lose work."""
    problem = await _load_problem(db, slug)
    progress = await _get_or_create_status(db, user_id, problem.id)
    drafts = dict(progress.drafts or {})
    drafts[data.language] = data.code
    progress.drafts = drafts
    progress.last_language = data.language
    await db.flush()
    return {"saved": True}


# ─── Judging ─────────────────────────────────────────────────────

@router.post("/problems/{slug}/run", response_model=RunResponse)
async def run_code(
    slug: str,
    data: RunRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Runs against the visible samples, or once against custom input."""
    problem = await _load_problem(db, slug)
    limit = problem.time_limit_ms or 5000

    if data.custom_input is not None and data.custom_input.strip() != "":
        outcome = judge.run_free(data.code, data.language, data.custom_input, limit)
        return RunResponse(
            mode="custom",
            verdict=outcome["verdict"],
            passed=1 if outcome["verdict"] == judge.ACCEPTED else 0,
            total=1,
            runtime_ms=outcome["runtime_ms"],
            stdout=outcome["stdout"],
            stderr=outcome["stderr"],
        )

    samples = [case for case in (problem.test_cases or []) if case.get("is_sample")]
    if not samples:
        raise HTTPException(status_code=400, detail="This problem has no sample cases to run")

    outcome = judge.judge(data.code, data.language, samples, limit, stop_on_first_failure=False)
    return RunResponse(
        mode="samples",
        verdict=outcome["verdict"],
        passed=outcome["passed"],
        total=outcome["total"],
        runtime_ms=outcome["runtime_ms"],
        results=outcome["results"],
        error=outcome["error"] or None,
    )


@router.post("/problems/{slug}/submit", response_model=SubmitResponse)
async def submit_code(
    slug: str,
    data: SubmitRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    problem = await _load_problem(db, slug)
    cases = list(problem.test_cases or [])
    if not cases:
        raise HTTPException(status_code=400, detail="This problem has no test cases")

    outcome = judge.judge(
        data.code, data.language, cases, problem.time_limit_ms or 5000, stop_on_first_failure=True
    )

    accepted = outcome["verdict"] == judge.ACCEPTED and outcome["passed"] == outcome["total"]
    score = int(outcome["passed"] / max(outcome["total"], 1) * 100)

    progress = await _get_or_create_status(db, user_id, problem.id)
    progress.attempts = (progress.attempts or 0) + 1
    progress.best_score = max(progress.best_score or 0, score)
    progress.last_language = data.language
    drafts = dict(progress.drafts or {})
    drafts[data.language] = data.code
    progress.drafts = drafts

    problem.attempt_count = (problem.attempt_count or 0) + 1

    first_solve = False
    points_awarded = 0
    if accepted:
        if progress.status != "solved":
            first_solve = True
            progress.status = "solved"
            progress.first_solved_at = datetime.now(timezone.utc)
            points_awarded = problem.points or 10
            progress.points_earned = (progress.points_earned or 0) + points_awarded
            problem.solved_count = (problem.solved_count or 0) + 1

            db.add(XPLog(user_id=user_id, action=f"solved_{problem.difficulty}", points=points_awarded))
            board = (
                await db.execute(
                    select(LeaderboardEntry).where(LeaderboardEntry.user_id == user_id)
                )
            ).scalar_one_or_none()
            if board is None:
                board = LeaderboardEntry(user_id=user_id, total_xp=0)
                db.add(board)
                await db.flush()
            board.total_xp = (board.total_xp or 0) + points_awarded
            board.problems_solved = (board.problems_solved or 0) + 1
            board.level = max(1, board.total_xp // 100 + 1)
            board.last_active = datetime.now(timezone.utc)
    elif progress.status != "solved":
        progress.status = "attempted"

    submission = CodeSubmission(
        user_id=user_id,
        problem_id=problem.id,
        code=data.code,
        language=data.language,
        status=outcome["verdict"],
        score=score,
        runtime_ms=outcome["runtime_ms"],
        output="",
        error_message=outcome["error"] or "",
        passed_count=outcome["passed"],
        total_count=outcome["total"],
        points_awarded=points_awarded,
        test_results=outcome["results"],
    )
    db.add(submission)
    await db.flush()

    # The index caches solved/attempt counters, so refresh it after a change.
    invalidate_index()

    total_points = int(
        (
            await db.execute(
                select(func.coalesce(func.sum(UserProblemStatus.points_earned), 0)).where(
                    UserProblemStatus.user_id == user_id
                )
            )
        ).scalar_one()
        or 0
    )
    solved_count = int(
        (
            await db.execute(
                select(func.count()).select_from(UserProblemStatus).where(
                    UserProblemStatus.user_id == user_id, UserProblemStatus.status == "solved"
                )
            )
        ).scalar_one()
        or 0
    )

    return SubmitResponse(
        submission_id=submission.id,
        verdict=outcome["verdict"],
        passed=outcome["passed"],
        total=outcome["total"],
        runtime_ms=outcome["runtime_ms"],
        score=score,
        points_awarded=points_awarded,
        first_solve=first_solve,
        total_points=total_points,
        solved_count=solved_count,
        streak_days=await _current_streak(db, user_id),
        results=outcome["results"],
        error=outcome["error"] or None,
    )


@router.get("/problems/{slug}/submissions", response_model=list[SubmissionItem])
async def list_submissions(
    slug: str,
    limit: int = Query(20, ge=1, le=100),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    problem = await _load_problem(db, slug)
    result = await db.execute(
        select(CodeSubmission)
        .where(CodeSubmission.user_id == user_id, CodeSubmission.problem_id == problem.id)
        .order_by(CodeSubmission.created_at.desc())
        .limit(limit)
    )
    return [
        SubmissionItem(
            id=row.id,
            language=row.language,
            verdict=row.status,
            passed=row.passed_count or 0,
            total=row.total_count or 0,
            score=row.score or 0,
            runtime_ms=row.runtime_ms,
            points_awarded=row.points_awarded or 0,
            created_at=row.created_at.isoformat() if row.created_at else None,
            code=row.code,
        )
        for row in result.scalars().all()
    ]


# ─── Progress & leaderboard ──────────────────────────────────────

@router.get("/progress", response_model=ProgressResponse)
async def my_progress(user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    rows = await _get_index(db)
    statuses = await _status_map(db, user_id)

    by_difficulty = {level: {"total": 0, "solved": 0} for level in ("easy", "medium", "hard")}
    topic_totals: dict[str, dict[str, int]] = {}
    for row in rows:
        bucket = by_difficulty.setdefault(row.difficulty, {"total": 0, "solved": 0})
        bucket["total"] += 1
        solved = statuses.get(row.id) == "solved"
        if solved:
            bucket["solved"] += 1
        for topic in row.topics:
            entry = topic_totals.setdefault(topic, {"total": 0, "solved": 0})
            entry["total"] += 1
            if solved:
                entry["solved"] += 1

    points = int(
        (
            await db.execute(
                select(func.coalesce(func.sum(UserProblemStatus.points_earned), 0)).where(
                    UserProblemStatus.user_id == user_id
                )
            )
        ).scalar_one()
        or 0
    )

    recent_rows = (
        await db.execute(
            select(CodeSubmission, CodingProblem.title)
            .join(CodingProblem, CodeSubmission.problem_id == CodingProblem.id)
            .where(CodeSubmission.user_id == user_id)
            .order_by(CodeSubmission.created_at.desc())
            .limit(15)
        )
    ).all()

    recent = [
        SubmissionItem(
            id=submission.id,
            language=submission.language,
            verdict=submission.status,
            passed=submission.passed_count or 0,
            total=submission.total_count or 0,
            score=submission.score or 0,
            runtime_ms=submission.runtime_ms,
            points_awarded=submission.points_awarded or 0,
            created_at=submission.created_at.isoformat() if submission.created_at else None,
            code=title,  # reuse the field to carry the problem title to the UI
        )
        for submission, title in recent_rows
    ]

    return ProgressResponse(
        total_problems=len(rows),
        solved=sum(1 for value in statuses.values() if value == "solved"),
        attempted=len(statuses),
        points=points,
        level=max(1, points // 100 + 1),
        streak_days=await _current_streak(db, user_id),
        by_difficulty=by_difficulty,
        by_topic=sorted(
            ({"topic": name, **counts} for name, counts in topic_totals.items()),
            key=lambda item: (-item["solved"], item["topic"]),
        ),
        recent=recent,
    )


@router.get("/leaderboard")
async def leaderboard(limit: int = Query(20, ge=1, le=100), db: AsyncSession = Depends(get_db)):
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
            "rank": index + 1,
            "user_id": board.user_id,
            "full_name": user.full_name,
            "total_xp": board.total_xp or 0,
            "level": board.level or 1,
            "problems_solved": board.problems_solved or 0,
            "streak_days": board.streak_days or 0,
        }
        for index, (board, user) in enumerate(rows)
    ]
