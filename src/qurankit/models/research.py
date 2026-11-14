"""Research execution and reproducibility models for QuranKit."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from qurankit.models.enums import ClaimCategory


class ResearchRun(BaseModel):
    """Records an executed research operation."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

    run_id: str = Field(..., description="Unique run identifier")
    operation: str = Field(..., description="Search, comparison, frequency, similarity, etc.")
    algorithm_name: str = Field(..., description="Method identifier")
    algorithm_version: str = Field(..., description="Algorithm version")
    parameters_json: dict[str, Any] = Field(..., description="Exact parameters")
    normalization_profile_id: str | None = Field(None, description="Profile used")
    software_version: str = Field(..., description="QuranKit version")
    started_at: datetime = Field(default_factory=datetime.utcnow, description="Run timestamp")
    completed_at: datetime | None = Field(None, description="Completion timestamp")
    status: str = Field(default="running", description="completed, failed, partial")
    environment_json: dict[str, Any] | None = Field(None, description="Relevant runtime details")


class ResearchInput(BaseModel):
    """Links a research run to its inputs."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

    research_input_id: str = Field(..., description="Internal ID")
    run_id: str = Field(..., description="Research run ID")
    input_type: str = Field(..., description="Ayah, token, dataset, query, etc.")
    input_reference: str = Field(..., description="Stable reference")
    dataset_id: str | None = Field(None, description="Dataset version used")


class ResearchResult(BaseModel):
    """Stores or indexes the output of a research run."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

    result_id: str = Field(..., description="Internal ID")
    run_id: str = Field(..., description="Producing run ID")
    result_type: str = Field(..., description="Exact match, similarity candidate, statistic, etc.")
    claim_category: ClaimCategory = Field(
        ...,
        description="Source annotation, deterministic result, suggestion, hypothesis"
    )
    result_payload_json: dict[str, Any] = Field(..., description="Structured result")
    evidence_json: dict[str, Any] | None = Field(None, description="Supporting references")
    limitations: str | None = Field(None, description="Known caveats")


class ComparisonResult(BaseModel):
    """Records a textual comparison between two passages."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

    comparison_id: str = Field(..., description="Comparison identifier")
    left_reference: str = Field(..., description="Left ayah or span reference")
    right_reference: str = Field(..., description="Right ayah or span reference")
    comparison_method: str = Field(..., description="Exact, token edit distance, lemma overlap, etc.")
    method_version: str = Field(..., description="Algorithm version")
    normalization_profile_id: str | None = Field(None, description="Used profile")
    score: float | None = Field(None, ge=0.0, le=1.0, description="Method-specific score")
    alignment_json: dict[str, Any] = Field(..., description="Matched and differing spans/tokens")
    claim_category: ClaimCategory = Field(
        default=ClaimCategory.DETERMINISTIC_RESULT,
        description="Usually deterministic result or suggestion"
    )
    review_status: str = Field(default="unreviewed", description="Unreviewed, reviewed, disputed")
    run_id: str | None = Field(None, description="Reproducibility link")
