from pydantic import BaseModel


class GetGoalProgressInput(BaseModel):
    workspace_id: str
    goal_id: str


class GetGoalProgressOutput(BaseModel):
    goal_id: str
    workspace_id: str
    account_id: str
    name: str
    target_amount_cents: int
    current_amount_cents: int
    progress_percent: float
    remaining_amount_cents: int
    target_date: str
    status: str
    currency: str
    is_completed: bool