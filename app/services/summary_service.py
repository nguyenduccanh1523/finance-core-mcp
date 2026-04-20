from app.repositories.summary_repository import SummaryRepository


class SummaryService:
    def __init__(self) -> None:
        self.repo = SummaryRepository()

    def get_monthly_summary(self, workspace_id: str, month: int) -> dict | None:
        data = self.repo.get_monthly_summary(workspace_id, month)

        income_total_cents = int(data.get("income_total_cents") or 0)
        expense_total_cents = int(data.get("expense_total_cents") or 0)

        net_cashflow_cents = income_total_cents - expense_total_cents

        top_categories = [
            {
                "category_id": item.get("category_id"),
                "amount_cents": int(item.get("amount_cents") or 0),
            }
            for item in data.get("top_categories", [])
        ]

        return {
            "month": data.get("month"),
            "income_total_cents": income_total_cents,
            "expense_total_cents": expense_total_cents,
            "transaction_count": data.get("transaction_count", 0),
            "net_cashflow_cents": net_cashflow_cents,
            "top_categories": top_categories,
        }
