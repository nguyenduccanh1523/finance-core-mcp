from sqlalchemy import text
from app.repositories.db import SessionLocal


class TransactionRepository:
    def search_transactions(
        self, workspace_id: str, window_days: int, limit: int
    ) -> list[dict] | None:
        sql = text(
            """
              SELECT
                t.id::text AS transaction_id,
                t.account_id::text AS account_id,
                t.category_id::text AS category_id,
                t.amount_cents::bigint AS amount_cents,
                t.type::text AS type,
                t.currency::text AS currency,
                t.occurred_at::text AS occurred_at,
                t.note::text AS note,
                t.counterparty::text AS counterparty
                
              FROM transactions t           
              WHERE t.workspace_id = :workspace_id AND t.deleted_at IS NULL AND t.occurred_at >= NOW() - (:window_days || ' days')::interval
              
              ORDER BY occurred_at DESC
                
              LIMIT :limit

              """
        )

        with SessionLocal() as session:
            row = (
                session.execute(
                    sql,
                    {"workspace_id": workspace_id, "window_days": window_days, "limit": limit},
                )
                .mappings()
                .all()
            )

        return [dict(r) for r in row] if row else None
