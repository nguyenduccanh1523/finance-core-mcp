from sqlalchemy import text
from app.repositories.db import SessionLocal


class BudgetRepository:
    def get_budget_snapshot(self, workspace_id: str, budget_id: str) -> dict | None:
        sql = text(
            """
              SELECT
                b.id AS budget_id,
                b.workspace_id,
                b.account_id,
                b.period_month,
                b.category_id,
                b.amount_limit_cents,
                b.alert_threshold_percent,
                b.currency,
                
                COALESCE(SUM(CASE
                WHEN t.type = 'EXPENSE' THEN ABS(t.amount_cents)
                ELSE 0
                END), 0) AS spent_amount_cents,
                
              FROM budgets b
              LEFT JOIN budget_transactions bt ON bt.budget_id = b.id
              LEFT JOIN transactions t ON t.id = bt.transaction_id AND t.workspace_id = b.workspace_id AND t.deleted_at IS NULL
                
              WHERE b.id = :budget_id AND b.workspace_id = :workspace_id
              
              GROUP BY b.id, b.workspace_id, b.account_id, b.period_month, b.category_id, b.amount_limit_cents, b.alert_threshold_percent, b.currency 
                
              LIMIT 1

              """
        )

        with SessionLocal() as session:
            row = (
                session.execute(
                    sql,
                    {"workspace_id": workspace_id, "budget_id": budget_id},
                )
                .mappings()
                .first()
            )

        return dict(row) if row else None
