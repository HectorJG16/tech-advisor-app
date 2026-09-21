from pydantic import BaseModel, Field, HttpUrl

from schemas.enums import (
    BudgetRange,
    CompanySize,
    TechnicalMaturity,
    ToolCategory,
)


class PricingTier(BaseModel):
    tier_name: str
    price_monthly: float | None = None
    price_currency: str = "USD"
    per_seat: bool = False
    min_seats: int | None = None
    max_seats: int | None = None
    limits_summary: str | None = None
    company_size_fit: list[CompanySize] = Field(default_factory=list)


class ToolTags(BaseModel):
    category: ToolCategory
    industries: list[str] = Field(default_factory=list)
    goals: list[str] = Field(default_factory=list)
    integrations: list[str] = Field(default_factory=list)
    company_sizes: list[CompanySize] = Field(default_factory=list)
    budget_fits: list[BudgetRange] = Field(default_factory=list)
    technical_maturity_fits: list[TechnicalMaturity] = Field(default_factory=list)


class ToolPlaybook(BaseModel):
    implementation_steps: list[dict] = Field(default_factory=list)
    migration_notes: dict[str, list[str]] = Field(default_factory=dict)


class CatalogSource(BaseModel):
    field_name: str
    source_url: HttpUrl | str
    last_verified: str | None = None
    notes: str | None = None


class ToolRecord(BaseModel):
    """Full catalog record used by report builder and ranker."""

    id: str | None = None
    slug: str
    name: str
    vendor: str
    url: HttpUrl | str
    description: str
    pricing_model: str | None = None
    pricing_tiers: list[PricingTier] = Field(default_factory=list)
    tags: ToolTags | None = None
    pros: list[str] = Field(default_factory=list)
    cons: list[str] = Field(default_factory=list)
    playbook: ToolPlaybook | None = None
    sources: list[CatalogSource] = Field(default_factory=list)
