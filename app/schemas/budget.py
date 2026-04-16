from pydantic import BaseModel

class GetBudgetSnapshotInput(BaseModel):
    workspace_id: str
    budget_id: str
    
class GetBudgetSnapshotOutput(BaseModel):
    budget_id: str
    workspace_id: str
    account_id: str
    period_month: str
    category_id: str | None = None
    amount_limit_cents: int
    spent_amount_cents: int
    remaining_amount_cents: int
    overspent_amount_cents: int
    usage_percent: float
    alert_threshold_percent: float
    currency: str
    is_over_budget: bool
    is_alert: bool
    status: str