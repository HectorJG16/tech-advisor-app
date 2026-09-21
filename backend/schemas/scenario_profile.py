from pydantic import BaseModel, Field

from schemas.enums import (
    BudgetRange,
    CompanySize,
    TechnicalMaturity,
)


class ScenarioProfile(BaseModel):
    """Canonical representation of a user's business scenario.

    Produced by the intake normalizer from wizard fields, chat, or quick-ask text.
    Used by retrieval, ranker, cache keys, and report template slot-filling.
    """

    industry: str | None = None
    company_size: CompanySize | None = None
    budget_range: BudgetRange | None = None
    technical_maturity: TechnicalMaturity | None = None
    primary_goals: list[str] = Field(default_factory=list)
    existing_stack: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    free_text_summary: str | None = None

    # Populated after normalization / embedding (not from raw user input)
    embedding: list[float] | None = Field(default=None, exclude=True)
    normalized_hash: str | None = Field(default=None, exclude=True)


class ScenarioProfileCreate(BaseModel):
    """Partial profile submitted by the client before normalization."""

    industry: str | None = None
    company_size: CompanySize | None = None
    budget_range: BudgetRange | None = None
    technical_maturity: TechnicalMaturity | None = None
    primary_goals: list[str] = Field(default_factory=list)
    existing_stack: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    free_text_summary: str | None = None


class ClarifyingQuestion(BaseModel):
    field: str
    question: str
    options: list[str] | None = None
