from enum import StrEnum


class CompanySize(StrEnum):
    SOLO = "solo"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    ENTERPRISE = "enterprise"


class BudgetRange(StrEnum):
    FREE = "free"
    UNDER_100 = "under_100"
    FROM_100_TO_500 = "100_to_500"
    FROM_500_TO_2000 = "500_to_2000"
    ENTERPRISE = "enterprise"


class TechnicalMaturity(StrEnum):
    NON_TECHNICAL = "non_technical"
    LOW_CODE = "low_code"
    DEVELOPER = "developer"


class ToolCategory(StrEnum):
    SALES_MARKETING_AI = "sales_marketing_ai"
    CUSTOMER_SUPPORT_AI = "customer_support_ai"
    OPERATIONS_WORKFLOW_AI = "operations_workflow_ai"
    ANALYTICS_FORECASTING_AI = "analytics_forecasting_ai"
    DEVELOPER_AI = "developer_ai"
    GENERAL_AUTOMATION = "general_automation"


class SessionStatus(StrEnum):
    COLLECTING = "collecting"
    CLARIFYING = "clarifying"
    RECOMMENDING = "recommending"
    REFINING = "refining"
    COMPLETED = "completed"


class FeedbackRating(StrEnum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class IntakeMode(StrEnum):
    QUICK_ASK = "quick_ask"
    WIZARD = "wizard"
    GUIDED = "guided"
