"""Builds the Aptitude Quest question bank and syncs it into the database.

Safe to re-run: questions are matched by ``slug``, so an existing row is updated
in place and user progress (which references question ids) survives. Legacy rows
without a slug (from the original seed.py) are removed so the catalog is the
single source of truth.
"""

import asyncio
import sys

from sqlalchemy import select

from app.content.aptitude.catalog import build_all
from app.db.session import async_session_factory, init_db
from app.models.models import MCQQuestion

FIELDS = (
    "section", "topic", "subtopic", "question_text", "options",
    "correct_index", "explanation", "difficulty", "points", "display_order",
)


async def sync_questions(verbose: bool = True) -> dict:
    rows = build_all()
    print(f"[INFO] Built {len(rows)} aptitude questions from the catalog.")

    created = 0
    updated = 0

    async with async_session_factory() as session:
        all_rows = (await session.execute(select(MCQQuestion))).scalars().all()
        existing = {row.slug: row for row in all_rows if row.slug}

        # Drop legacy rows that predate the catalog (no slug).
        legacy = [row for row in all_rows if not row.slug]
        for row in legacy:
            await session.delete(row)
        if legacy:
            print(f"[INFO] Removed {len(legacy)} legacy question row(s) without a slug.")

        for payload in rows:
            slug = payload["slug"]
            row = existing.get(slug)
            if row is None:
                row = MCQQuestion(slug=slug)
                session.add(row)
                created += 1
            else:
                updated += 1
            for field in FIELDS:
                setattr(row, field, payload[field])

        await session.commit()

    print(f"[SUCCESS] Synced aptitude questions: {created} created, {updated} updated.")
    return {"total": len(rows), "created": created, "updated": updated}


async def main():
    await init_db()
    await sync_questions()


if __name__ == "__main__":
    asyncio.run(main())
    sys.exit(0)
