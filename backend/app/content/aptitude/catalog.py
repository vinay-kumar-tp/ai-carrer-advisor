"""Registry that stitches the aptitude topic modules into one catalog.

Provides:
  * ``iter_topics()``  — every :class:`Topic` in a stable order
  * ``build_catalog()``— section → topic → subtopic tree with counts (for the UI)
  * ``build_all()``    — flat list of DB-ready question payloads (for seeding)
"""

from __future__ import annotations

import importlib
from functools import lru_cache

from app.content.aptitude.framework import SECTION_LABELS, Topic, flatten_topic

MODULES = ["quant", "logical", "verbal", "technical"]


@lru_cache(maxsize=1)
def iter_topics() -> tuple[Topic, ...]:
    topics: list[Topic] = []
    seen: set[str] = set()
    for name in MODULES:
        module = importlib.import_module(f"app.content.aptitude.{name}")
        for topic in module.topics():
            if topic.slug in seen:
                raise ValueError(f"duplicate topic slug {topic.slug!r}")
            seen.add(topic.slug)
            topics.append(topic)
    return tuple(topics)


@lru_cache(maxsize=1)
def build_catalog() -> dict:
    """Section-grouped tree the frontend renders as topic cards."""
    sections: dict[str, dict] = {
        key: {"key": key, "label": label, "topics": []}
        for key, label in SECTION_LABELS.items()
    }
    for topic in iter_topics():
        sections[topic.section]["topics"].append({
            "slug": topic.slug,
            "name": topic.name,
            "icon": topic.icon,
            "blurb": topic.blurb,
            "section": topic.section,
            "section_label": SECTION_LABELS[topic.section],
            "question_count": topic.question_count,
            "subtopics": [
                {"name": s.name, "question_count": len(s.questions)}
                for s in topic.subtopics
            ],
        })
    return {
        "sections": list(sections.values()),
        "section_labels": SECTION_LABELS,
        "total_questions": sum(t.question_count for t in iter_topics()),
        "total_topics": len(iter_topics()),
    }


def build_all() -> list[dict]:
    """Flat DB-ready question rows across every topic."""
    rows: list[dict] = []
    order = 0
    for topic in iter_topics():
        for row in flatten_topic(topic):
            row["global_order"] = order
            rows.append(row)
            order += 1
    return rows


def question_count() -> int:
    return sum(t.question_count for t in iter_topics())
