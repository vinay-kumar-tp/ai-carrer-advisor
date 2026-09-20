"""Optional automatic seeding on application startup.

Runs when the SEED_ON_STARTUP env var is truthy. Every underlying seed
function is idempotent (guards on existing rows / upserts by slug), so this is
safe to run on every boot — which also makes the app self-healing on hosts
with ephemeral disks (e.g. Render free tier), where the SQLite file can be
wiped on a restart.

Kept separate from main.py and wrapped in broad error handling so a seeding
hiccup can never stop the API itself from coming up.
"""

from __future__ import annotations


async def run_startup_seed() -> None:
    try:
        # Catalog + demo users + demo profile.
        from seed import seed_content, seed_demo_profile

        await seed_content()
        await seed_demo_profile()

        # Rich content modules (idempotent upserts).
        from seed_jobs import sync_jobs
        from seed_aptitude import sync_questions
        from seed_problems import sync_problems
        from seed_events import sync_events

        await sync_jobs()
        await sync_questions(verbose=False)
        await sync_problems(verbose=False)
        await sync_events()

        print("[INFO] Startup seed complete.")
    except Exception as exc:  # noqa: BLE001 — never let seeding crash startup
        print(f"[WARN] Startup seed skipped/failed (API still starting): {exc}")
