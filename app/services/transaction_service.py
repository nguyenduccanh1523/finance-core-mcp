from app.repositories.transaction_repository import TransactionRepository


class TransactionService:
    def __init__(self) -> None:
        self.repo = TransactionRepository()

    def search(self, workspace_id: str, window_days: int, limit: int) -> dict | None:
        items = self.repo.search_transactions(workspace_id, window_days, limit)
        return {"count": len(items), "items": items} if items else None
