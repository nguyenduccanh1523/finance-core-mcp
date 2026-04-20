from pydantic import BaseModel


class GetMonthlySummaryInput(BaseModel):
    workspace_id: str
    month: str


class TopCategoryItem(BaseModel):
    category_id: str | None = None
    amount_cents: int


class MonthlySummaryOutput(BaseModel):
    month: str
    income_total_cents: int
    expense_total_cents: int
    transaction_count: int
    net_cashflow_cents: int
    top_categories: list[TopCategoryItem]
