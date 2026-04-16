from pydantic import BaseModel


class SearchTransactionsInput(BaseModel):
    workspace_id: str
    window_days: int = 30
    limit: int = 200


class TransactionItem(BaseModel):
    transaction_id: str
    account_id: str
    category_id: str | None = None
    amount_cents: int
    type: str
    currency: str
    occurred_at: str
    note: str | None = None
    counterparty: str | None = None


class SearchTransactionsOutput(BaseModel):
    count: int
    items: list[TransactionItem]
