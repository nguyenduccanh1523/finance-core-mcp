from app.repositories.summary_repository import SummaryRepository


class SummaryService:
    def __init__(self) -> None:
        self.repo = SummaryRepository()

    def get_monthly_summary(self, workspace_id: str, month: int) -> dict | None:
        data = self.repo.get_monthly_summary(workspace_id, month)

        income = int(data.get("income_total_cents") or 0)
        expense = int(data.get("expense_total_cents") or 0)

        net_cashflow_cents = income - expense

        return {**data, "net_cashflow_cents": net_cashflow_cents}
