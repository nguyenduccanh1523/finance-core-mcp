from sqlalchemy import text
from app.repositories.db import SessionLocal

class GoalRepository:
    def get_goal_progress(self, workspace_id: str, goal_id: str) -> dict | None:
        sql = text(
            """
              SELECT
                g.id::text AS goal_id,
                g.workspace_id::text AS workspace_id,
                g.account_id::text AS account_id,
                g.name,
                g.target_amount_cents,
                g.current_amount_cents,
                g.target_date::text AS target_date,
                g.status,
                g.currency
                
              FROM goals g           
              WHERE g.id = :goal_id AND g.workspace_id = :workspace_id AND g.deleted_at IS NULL
                
              LIMIT 1

              """
        )

        with SessionLocal() as session:
            row = (
                session.execute(
                    sql,
                    {"workspace_id": workspace_id, "goal_id": goal_id},
                )
                .mappings()
                .first()
            )

        return dict(row) if row else None