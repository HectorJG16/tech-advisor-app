from pydantic import BaseModel, Field


class RankedTool(BaseModel):
    tool_id: str
    slug: str
    name: str
    score: float = Field(ge=0.0, le=1.0)
    fit_reason: str


class CostEstimate(BaseModel):
    tier_name: str
    price_monthly: float | None = None
    price_currency: str = "USD"
    per_seat: bool = False
    summary: str


class ImplementationStep(BaseModel):
    step: int
    title: str
    description: str


class AlternativePick(BaseModel):
    tool_id: str
    slug: str
    name: str
    choose_if: str


class AdvisoryReport(BaseModel):
    """Template-filled advisory output. Maps 1:1 to frontend report sections."""

    executive_summary: str
    ranked_list: list[RankedTool]
    why_top_pick: list[str]
    cost_estimate: CostEstimate
    implementation_steps: list[ImplementationStep]
    migration_path: list[str]
    tradeoffs: list[str]
    alternatives: list[AlternativePick]
