from app.repositories.budget_repository import BudgetRepository


class BudgetService:
    def __init__(self):
        self.repo = BudgetRepository()

    def get_snapshot(self, workspace_id: str, budget_id: str) -> dict | None:
        data = self.repo.get_budget_snapshot(workspace_id, budget_id)
        if not data:
            raise ValueError("Budget not found")
        limit_cents = int(data["amount_limit_cents"] or 0)
        spent_cents = int(data["spent_amount_cents"] or 0)
        alert_threshold_percent = int(data["alert_threshold_percent"] or 80)
        
        remaining_cents = limit_cents - spent_cents
        overspent_cents = abs(remaining_cents) if remaining_cents < 0 else 0
        
        usage_percent = (spent_cents / limit_cents * 100) if limit_cents > 0 else 0.0
        usage_percent = round(usage_percent, 2)
        
        is_over_budget = spent_cents > limit_cents
        is_alert = usage_percent >= alert_threshold_percent
        
        if is_over_budget:
            status = "OVER_BUDGET"
        elif is_alert:
            status = "AT_RISK"
        else:
            status = "HEALTHY"

        return {
            **data,
            "remaining_amount_cents": remaining_cents,
            "overspent_amount_cents": overspent_cents,
            "usage_percent": usage_percent,
            "is_over_budget": is_over_budget,
            "is_alert": is_alert,
            "status": status
        }
