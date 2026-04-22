from sqlalchemy import text
from app.repositories.db import SessionLocal


class SummaryRepository:
    def get_monthly_summary(self, workspace_id: str, month: str) -> dict:
        summary_sql = text(
            """
            SELECT
                :currency AS currency,
                COALESCE(SUM(CASE WHEN type = 'INCOME' THEN amount_cents ELSE 0 END), 0)::bigint AS income_total_cents,
                COALESCE(SUM(CASE WHEN type = 'EXPENSE' THEN ABS(amount_cents) ELSE 0 END), 0)::bigint AS expense_total_cents,
                COUNT(*)::int AS transaction_count
            FROM transactions
            WHERE workspace_id = :workspace_id
              AND deleted_at IS NULL
              AND TO_CHAR(occurred_at, 'YYYY-MM') = :month
            GROUP BY currency
            ORDER BY currency ASC
        """
        )

        top_categories_sql = text(
            """
            SELECT
                :currency AS currency,
                category_id::text AS category_id,
                COALESCE(SUM(ABS(amount_cents)), 0)::bigint AS amount_cents
            FROM transactions
            WHERE workspace_id = :workspace_id
              AND deleted_at IS NULL
              AND type = 'EXPENSE'
              AND TO_CHAR(occurred_at, 'YYYY-MM') = :month
            GROUP BY currency, category_id
            ORDER BY currency ASC, amount_cents DESC
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

        top_categories_by_currency: dict[str, list[dict]] = {}

        for now in top_categories_rows:
            currency = now["currency"]
            if currency not in top_categories_by_currency:
                top_categories_by_currency[currency] = []

            if len(top_categories_by_currency[currency]) < 5:
                top_categories_by_currency[currency].append(
                    {
                        "category_id": now["category_id"],
                        "amount_cents": int(now["amount_cents"] or 0),
                    }
                )

        summaries = []
        for row in summary_row:
            currency = row["currency"]
            income_total_cents = int(row["income_total_cents"] or 0)
            expense_total_cents = int(row["expense_total_cents"] or 0)

            summaries.append(
                {
                    "currency": currency,
                    "income_total_cents": income_total_cents,
                    "expense_total_cents": expense_total_cents,
                    "transaction_count": int(row["transaction_count"] or 0),
                    "net_cashflow_cents": income_total_cents - expense_total_cents,
                    "top_categories": top_categories_by_currency.get(currency, []),
                }
            )

        return {
            "month": month,
            "summaries": summaries,
        }
