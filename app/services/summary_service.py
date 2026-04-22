from app.repositories.summary_repository import SummaryRepository


class SummaryService:
    def __init__(self) -> None:
        self.repo = SummaryRepository()

    def get_monthly_summary(self, workspace_id: str, month: int) -> dict | None:
        data = self.repo.get_monthly_summary(workspace_id, month)

        normalized_summaries = []
        for item in data.get("summaries", []):
            normalized_summaries.append(
                {
                    "currency": item.get("currency"),
                    "income_total_cents": int(item.get("income_total_cents") or 0),
                    "expense_total_cents": int(item.get("expense_total_cents") or 0),
                    "transaction_count": int(item.get("transaction_count") or 0),
                    "net_cashflow_cents": int(item.get("net_cashflow_cents") or 0),
                    "top_categories": [
                        {
                            "category_id": cat.get("category_id"),
                            "amount_cents": int(cat.get("amount_cents") or 0),
                        }
                        for cat in item.get("top_categories", [])
                    ],
                }
            )

        return {
            "month": data.get("month"),
            "summaries": normalized_summaries,
        }
