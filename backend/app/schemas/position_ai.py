"""Position AI — Skill Gap & Fit Analyzer request/response schemas."""

from typing import Optional

from pydantic import BaseModel, Field


# ─── Requests ─────────────────────────────────────────────────────

class PositionAnalyzeRequest(BaseModel):
    """Run a gap analysis against up to 3 saved job listings and/or pasted JD text."""

    job_ids: list[str] = Field(default_factory=list, max_length=3)
    jd_text: str = ""
    save: bool = True  # log the run to History


class PositionFeedbackRequest(BaseModel):
    analysis_id: Optional[str] = None
    score_satisfaction: bool = False
    skill_breakdown_accuracy: bool = False
    relevance_weighting_ok: bool = True
    missing_skill_accuracy: bool = True
    relevance_comment: str = ""
    missing_skill_comment: str = ""
    comments: str = ""


# ─── Responses ────────────────────────────────────────────────────

class MissingSkillItem(BaseModel):
    skill: str
    jd_count: int
    total_jds: int
    top_jd_title: str = ""


class JdOption(BaseModel):
    """One selectable entry for the "Target Job Descriptions" dropdown."""

    id: str
    title: str
    company: str
    location: str = ""
    required_skills_count: int = 0
    required_skills: list[str] = Field(default_factory=list)


class GapScopeJd(BaseModel):
    """One JD summarised inside the 'Gap Analysis Scope' panel."""

    id: str
    title: str
    company: str
    location: str = ""
    source: str = "job"  # "job" | "text"
    sample_skills: list[str] = Field(default_factory=list)
    extra_count: int = 0


class PositionAnalysisResponse(BaseModel):
    id: Optional[str] = None
    matchPercentage: int
    matchedSkills: list[str]
    missingSkills: list[MissingSkillItem]
    jdTitle: str
    profileSkillCount: int
    selectedJdCount: int
    scope: list[GapScopeJd] = Field(default_factory=list)


class PositionHistoryItem(BaseModel):
    id: str
    analyzed_at: str
    jd_titles: list[str]
    jd_snapshots: list[dict]
    missing_skills: list[MissingSkillItem]
    profile_skill_count: int
    match_percentage: int


class PositionHistoryResponse(BaseModel):
    items: list[PositionHistoryItem]
    latest_missing_skills: list[str]


class PositionFeedbackResponse(BaseModel):
    message: str = "Feedback submitted"
    success: bool = True
