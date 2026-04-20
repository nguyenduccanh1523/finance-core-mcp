from sqlalchemy import text
from app.repositories.db import SessionLocal


class SummaryRepository:
    def get_monthly_summary(self, workspace_id: str, month: str) -> dict:
        summary_sql = text(
            """
            SELECT
                :month AS month,
                COALESCE(SUM(CASE WHEN type = 'INCOME' THEN amount_cents ELSE 0 END), 0)::bigint AS income_total_cents,
                COALESCE(SUM(CASE WHEN type = 'EXPENSE' THEN ABS(amount_cents) ELSE 0 END), 0)::bigint AS expense_total_cents,
                COUNT(*)::int AS transaction_count
            FROM transactions
            WHERE workspace_id = :workspace_id
              AND deleted_at IS NULL
              AND TO_CHAR(occurred_at, 'YYYY-MM') = :month
        """
        )

        top_categories_sql = text(
            """
            SELECT
                category_id::text AS category_id,
                COALESCE(SUM(ABS(amount_cents)), 0)::bigint AS amount_cents
            FROM transactions
            WHERE workspace_id = :workspace_id
              AND deleted_at IS NULL
              AND type = 'EXPENSE'
              AND TO_CHAR(occurred_at, 'YYYY-MM') = :month
            GROUP BY category_id
            ORDER BY amount_cents DESC
            LIMIT 5
        """
        )

        with SessionLocal() as session:
            summary_row = (
                session.execute(
                    summary_sql,
                    {"workspace_id": workspace_id, "month": month},
                )
                .mappings()
                .first()
            )

            top_categories_rows = (
                session.execute(
                    top_categories_sql,
                    {"workspace_id": workspace_id, "month": month},
                )
                .mappings()
                .all()
            )
            
        base_summary = dict(summary_row) if summary_row else {
            "month": month,
            "income_total_cents": 0,
            "expense_total_cents": 0,
            "transaction_count": 0,
        }

        return {
            **base_summary,
            "top_categories": [dict(r) for r in top_categories_rows],
        }
