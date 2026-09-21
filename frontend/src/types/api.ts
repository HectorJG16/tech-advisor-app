/**
 * API contracts — mirror backend/schemas (Phase 0).
 * Keep in sync when Pydantic models change.
 */

export type CompanySize =
  | "solo"
  | "small"
  | "medium"
  | "large"
  | "enterprise";

export type BudgetRange =
  | "free"
  | "under_100"
  | "100_to_500"
  | "500_to_2000"
  | "enterprise";

export type TechnicalMaturity =
  | "non_technical"
  | "low_code"
  | "developer";

export type ToolCategory =
  | "sales_marketing_ai"
  | "customer_support_ai"
  | "operations_workflow_ai"
  | "analytics_forecasting_ai"
  | "developer_ai"
  | "general_automation";

export type SessionStatus =
  | "collecting"
  | "clarifying"
  | "recommending"
  | "refining"
  | "completed";

export type FeedbackRating = "positive" | "negative" | "neutral";

export type IntakeMode = "quick_ask" | "wizard" | "guided";

export interface ScenarioProfileCreate {
  industry?: string | null;
  company_size?: CompanySize | null;
  budget_range?: BudgetRange | null;
  technical_maturity?: TechnicalMaturity | null;
  primary_goals?: string[];
  existing_stack?: string[];
  constraints?: string[];
  free_text_summary?: string | null;
}

export interface ScenarioProfile extends ScenarioProfileCreate {
  // embedding and normalized_hash are server-side only
}

export interface ClarifyingQuestion {
  field: string;
  question: string;
  options?: string[] | null;
}

export interface SessionCreateResponse {
  session_id: string;
  status: SessionStatus;
}

export interface SessionResponse {
  session_id: string;
  status: SessionStatus;
  created_at: string;
  updated_at: string;
}

export interface IntakeRequest {
  mode: IntakeMode;
  profile: ScenarioProfileCreate;
}

export interface IntakeResponse {
  session_id: string;
  status: SessionStatus;
  profile: ScenarioProfile;
  clarifying_questions: ClarifyingQuestion[];
  ready_for_recommendation: boolean;
}

export interface RankedTool {
  tool_id: string;
  slug: string;
  name: string;
  score: number;
  fit_reason: string;
}

export interface CostEstimate {
  tier_name: string;
  price_monthly: number | null;
  price_currency: string;
  per_seat: boolean;
  summary: string;
}

export interface ImplementationStep {
  step: number;
  title: string;
  description: string;
}

export interface AlternativePick {
  tool_id: string;
  slug: string;
  name: string;
  choose_if: string;
}

/** Maps 1:1 to frontend report sections */
export interface AdvisoryReport {
  executive_summary: string;
  ranked_list: RankedTool[];
  why_top_pick: string[];
  cost_estimate: CostEstimate;
  implementation_steps: ImplementationStep[];
  migration_path: string[];
  tradeoffs: string[];
  alternatives: AlternativePick[];
}

export interface RecommendRequest {
  profile?: ScenarioProfileCreate | null;
}

export interface RecommendResponse {
  session_id: string;
  scenario_id: string;
  recommendation_id: string;
  report: AdvisoryReport;
  model_version?: string | null;
  cache_hit: boolean;
}

export interface FeedbackRequest {
  recommendation_id: string;
  rating?: FeedbackRating | null;
  selected_tool_id?: string | null;
  comment?: string | null;
}

export interface FeedbackResponse {
  feedback_id: string;
  recommendation_id: string;
}

export interface HealthResponse {
  status: string;
}
