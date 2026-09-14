"""Authoring primitives for the Aptitude Quest question bank.

A topic module exposes a single ``topic()`` function returning a :class:`Topic`.
Each topic belongs to one of four sections and holds one or more subtopics, and
each subtopic holds 5–15 :class:`Question` items. The catalog stitches every
topic module together and flattens the questions into DB rows, assigning a
stable ``slug`` per question so seeding is idempotent (upsert by slug).

Keeping content as plain Python (not JSON) lets us author quickly, compute
counts automatically, and validate at import time.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

# The four top-level sections shown as filter chips in the UI.
SECTIONS = ("quant", "logical", "verbal", "technical")

SECTION_LABELS = {
    "quant": "Quantitative Aptitude",
    "logical": "Logical Reasoning",
    "verbal": "Verbal Ability",
    "technical": "Technical MCQs",
}

DIFFICULTY_POINTS = {"easy": 5, "medium": 8, "hard": 12}


def slugify(*parts: str) -> str:
    raw = "-".join(p for p in parts if p)
    raw = raw.lower().strip()
    raw = re.sub(r"[^a-z0-9]+", "-", raw)
    return re.sub(r"-+", "-", raw).strip("-")


@dataclass(frozen=True)
class Question:
    """A single MCQ. ``answer`` is the 0-based index into ``options``."""
    text: str
    options: list[str]
    answer: int
    explanation: str = ""
    difficulty: str = "easy"

    def __post_init__(self):
        if not (0 <= self.answer < len(self.options)):
            raise ValueError(f"answer index out of range for question: {self.text[:50]!r}")
        if self.difficulty not in DIFFICULTY_POINTS:
            raise ValueError(f"bad difficulty {self.difficulty!r} for question: {self.text[:50]!r}")


@dataclass(frozen=True)
class Subtopic:
    name: str
    questions: list[Question]


@dataclass(frozen=True)
class Topic:
    section: str
    name: str
    subtopics: list[Subtopic]
    icon: str = ""            # optional emoji shown on the topic card
    blurb: str = ""

    def __post_init__(self):
        if self.section not in SECTIONS:
            raise ValueError(f"bad section {self.section!r} for topic {self.name!r}")

    @property
    def slug(self) -> str:
        return slugify(self.section, self.name)

    @property
    def question_count(self) -> int:
        return sum(len(s.questions) for s in self.subtopics)


# Convenience constructors used by the topic modules ─────────────

def Q(text: str, options: list[str], answer: int, explanation: str = "", difficulty: str = "easy") -> Question:
    return Question(text=text, options=options, answer=answer, explanation=explanation, difficulty=difficulty)


def S(name: str, questions: list[Question]) -> Subtopic:
    return Subtopic(name=name, questions=questions)


def T(section: str, name: str, subtopics: list[Subtopic], icon: str = "", blurb: str = "") -> Topic:
    return Topic(section=section, name=name, subtopics=subtopics, icon=icon, blurb=blurb)


# Flatten a topic into DB-ready question payloads ────────────────

def flatten_topic(topic: Topic) -> list[dict]:
    """Return one dict per question, carrying its section/topic/subtopic + slug."""
    rows: list[dict] = []
    order = 0
    for sub in topic.subtopics:
        for i, q in enumerate(sub.questions):
            slug = slugify(topic.section, topic.name, sub.name, str(i))
            rows.append({
                "slug": slug,
                "section": topic.section,
                "topic": topic.name,
                "subtopic": sub.name,
                "question_text": q.text,
                "options": list(q.options),
                "correct_index": q.answer,
                "explanation": q.explanation,
                "difficulty": q.difficulty,
                "points": DIFFICULTY_POINTS[q.difficulty],
                "display_order": order,
            })
            order += 1
    return rows
