"""Builds the Code Quest catalog and syncs it into the database.

Safe to re-run: problems are matched by slug, so an existing row is updated in
place and user progress (which references problem ids) survives.
"""

import asyncio
import sys

from sqlalchemy import select

from app.content.codequest.catalog import build_all
from app.db.session import async_session_factory, init_db
from app.models.models import CodingProblem

FIELDS = (
    "title", "description", "difficulty", "tags", "companies", "languages",
    "sample_input", "sample_output", "test_cases", "starter_code", "xp_reward",
    "notes", "input_format", "output_format", "constraints", "examples", "hints",
    "pattern_note", "topics", "patterns", "sheets", "points", "time_limit_ms",
    "display_order",
)


async def sync_problems(verbose: bool = True) -> dict:
    print("[INFO] Building problem catalog (this executes every reference solution)...")
    problems = build_all()
    print(f"[INFO] Built {len(problems)} problems.")

    created = 0
    updated = 0

    async with async_session_factory() as session:
        existing = {
            row.slug: row
            for row in (await session.execute(select(CodingProblem))).scalars().all()
            if row.slug
        }

        # Legacy rows from the original seed have no slug; drop them so the
        # catalog is the single source of truth.
        legacy = [
            row for row in (await session.execute(select(CodingProblem))).scalars().all()
            if not row.slug
        ]
        for row in legacy:
            await session.delete(row)
        if legacy:
            print(f"[INFO] Removed {len(legacy)} legacy problem row(s) without a slug.")

        for payload in problems:
            slug = payload["slug"]
            row = existing.get(slug)
            if row is None:
                row = CodingProblem(slug=slug)
                session.add(row)
                created += 1
            else:
                updated += 1
            for field in FIELDS:
                setattr(row, field, payload[field])

        await session.commit()

    print(f"[SUCCESS] Synced problems: {created} created, {updated} updated.")
    return {"total": len(problems), "created": created, "updated": updated}


async def main():
    await init_db()
    await sync_problems()

    # Drop the API's in-memory index so a running server picks up the change.
    try:
        from app.api.routers.codequest import invalidate_index

        invalidate_index()
    except Exception:  # noqa: BLE001 — only relevant in-process
        pass


if __name__ == "__main__":
    asyncio.run(main())
    sys.exit(0)
