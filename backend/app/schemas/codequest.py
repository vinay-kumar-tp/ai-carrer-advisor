"""Schemas for the Code Quest problem browser and judge."""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field

LANGUAGES = ("python", "javascript", "cpp", "java")


class RunRequest(BaseModel):
    code: str = Field(max_length=200_000)
    language: str = Field(pattern="^(python|javascript|cpp|java)$")
    # When present, the code runs once against this input instead of the samples.
    custom_input: Optional[str] = Field(None, max_length=100_000)


class SubmitRequest(BaseModel):
    code: str = Field(min_length=1, max_length=200_000)
    language: str = Field(pattern="^(python|javascript|cpp|java)$")


class DraftRequest(BaseModel):
    code: str = Field(max_length=200_000)
    language: str = Field(pattern="^(python|javascript|cpp|java)$")


class CaseResult(BaseModel):
    index: int
    is_sample: bool
    verdict: str
    runtime_ms: int
    input: Optional[str] = None
    expected: Optional[str] = None
    got: Optional[str] = None
    stderr: Optional[str] = None


class RunResponse(BaseModel):
    mode: str                    # "samples" | "custom"
    verdict: str
    passed: int
    total: int
    runtime_ms: int
    results: list[CaseResult] = []
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    error: Optional[str] = None


class SubmitResponse(BaseModel):
    submission_id: str
    verdict: str
    passed: int
    total: int
    runtime_ms: int
    score: int
    points_awarded: int
    first_solve: bool
    total_points: int
    solved_count: int
    streak_days: int
    results: list[CaseResult] = []
    error: Optional[str] = None


class FacetValue(BaseModel):
    name: str
    count: int


class Facets(BaseModel):
    topics: list[FacetValue]
    patterns: list[FacetValue]
    companies: list[FacetValue]
    sheets: list[FacetValue]


class ProblemListItem(BaseModel):
    slug: str
    title: str
    difficulty: str
    topics: list[str]
    patterns: list[str]
    companies: list[str]
    sheets: list[str]
    points: int
    status: str                  # "unsolved" | "attempted" | "solved"
    acceptance: Optional[float] = None


class ProblemListResponse(BaseModel):
    items: list[ProblemListItem]
    total: int
    page: int
    page_size: int
    showing_from: int
    showing_to: int


class StatsResponse(BaseModel):
    total_problems: int
    solved: int
    attempted: int
    points: int
    streak_days: int
    by_difficulty: dict[str, dict[str, int]]


class ProblemDetail(BaseModel):
    model_config = {"extra": "allow"}

    slug: str
    title: str
    difficulty: str
    points: int
    time_limit_ms: int
    description: str
    notes: list[str]
    input_format: list[str]
    output_format: list[str]
    constraints: list[str]
    examples: list[dict[str, Any]]
    topics: list[str]
    patterns: list[str]
    companies: list[str]
    sheets: list[str]
    languages: list[str]
    starter_code: dict[str, str]
    hint_count: int
    revealed_hints: list[str]
    pattern_note: str
    status: str
    attempts: int
    best_score: int
    last_language: Optional[str] = None
    draft: Optional[str] = None
    acceptance: Optional[float] = None
    position: Optional[int] = None
    total_in_filter: Optional[int] = None
    prev_slug: Optional[str] = None
    next_slug: Optional[str] = None
    related: list[ProblemListItem] = []


class HintResponse(BaseModel):
    revealed_hints: list[str]
    hint_count: int


class SubmissionItem(BaseModel):
    id: str
    language: str
    verdict: str
    passed: int
    total: int
    score: int
    runtime_ms: Optional[int]
    points_awarded: int
    created_at: Optional[str]
    code: Optional[str] = None


class ProgressResponse(BaseModel):
    total_problems: int
    solved: int
    attempted: int
    points: int
    level: int
    streak_days: int
    by_difficulty: dict[str, dict[str, int]]
    by_topic: list[dict[str, Any]]
    recent: list[SubmissionItem]
