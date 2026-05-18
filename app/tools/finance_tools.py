import logging
from dataclasses import dataclass
from typing import Any, Callable

from fastmcp import FastMCP
from pydantic import BaseModel, ValidationError

from app.schemas.budget import GetBudgetSnapshotInput, GetBudgetSnapshotOutput
from app.schemas.goal import GetGoalProgressInput, GetGoalProgressOutput
from app.schemas.transaction import SearchTransactionsInput, SearchTransactionsOutput
from app.schemas.summary import GetMonthlySummaryInput, MonthlySummaryOutput

from app.services.budget_service import BudgetService
from app.services.goal_service import GoalService
from app.services.transaction_service import TransactionService
from app.services.summary_service import SummaryService

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class FinanceToolServices:
    budget: BudgetService
    goal: GoalService
    transaction: TransactionService
    summary: SummaryService


def build_finance_tool_services() -> FinanceToolServices:
    return FinanceToolServices(
        budget=BudgetService(),
        goal=GoalService(),
        transaction=TransactionService(),
        summary=SummaryService(),
    )


def _validate_and_dump(
    output_model: type[BaseModel], result: dict[str, Any] | BaseModel | None
) -> dict[str, Any]:
    if result is None:
        raise ValueError(
            f"{output_model.__name__} received None. "
            "Tool handler must return a valid dictionary."
        )
    if isinstance(result, BaseModel):
        result = result.model_dump()
    return output_model.model_validate(result).model_dump()


def _normalize_search_transactions_result(result: Any) -> dict[str, Any]:
    if result is None:
        return {
            "count": 0,
            "items": [],
        }

    if isinstance(result, BaseModel):
        result = result.model_dump()

    if isinstance(result, list):
        return {
            "count": len(result),
            "items": result,
        }

    if isinstance(result, dict):
        items = result.get("items")

        if items is None:
            items = result.get("transactions")

        if items is None:
            items = []

        count = result.get("count")

        if count is None:
            count = result.get("total")

        if count is None:
            count = len(items)

        return {
            "count": int(count),
            "items": items,
        }

    raise ValueError(
        f"Invalid search_transactions result type: {type(result).__name__}"
    )


def _run_tool(
    tool_name: str,
    output_model: type[BaseModel],
    handler: Callable[[], dict[str, Any] | BaseModel | None],
) -> dict[str, Any]:
    logger.info("MCP tool called: %s", tool_name)

    try:
        result = handler()

        if result is None and output_model is SearchTransactionsOutput:
            logger.warning(
                "MCP tool %s returned None. Fallback to empty transactions output.",
                tool_name,
            )
            result = {
                "count": 0,
                "items": [],
            }

        payload = _validate_and_dump(output_model, result)

        logger.info("MCP tool %s executed successfully", tool_name)
        return payload

    except ValueError as exc:
        logger.warning("MCP tool business error [%s]: %s", tool_name, exc)
        raise

    except ValidationError:
        logger.exception("MCP tool output validation failed: %s", tool_name)
        raise

    except Exception:
        logger.exception("MCP tool unexpected error: %s", tool_name)
        raise


def register_finance_tools(
    mcp: FastMCP, services: FinanceToolServices | None = None
) -> None:
    services = services or build_finance_tool_services()

    @mcp.tool
    def get_budget_snapshot(input: GetBudgetSnapshotInput) -> dict[str, Any]:
        return _run_tool(
            tool_name="get_budget_snapshot",
            output_model=GetBudgetSnapshotOutput,
            handler=lambda: services.budget.get_snapshot(
                workspace_id=input.workspace_id, budget_id=input.budget_id
            ),
        )

    @mcp.tool
    def get_goal_progress(input: GetGoalProgressInput) -> dict[str, Any]:
        return _run_tool(
            tool_name="get_goal_progress",
            output_model=GetGoalProgressOutput,
            handler=lambda: services.goal.get_progress(
                workspace_id=input.workspace_id, goal_id=input.goal_id
            ),
        )

    @mcp.tool
    def search_transactions(input: SearchTransactionsInput) -> dict[str, Any]:
        logger.info(
            "search_transactions input workspace_id=%s window_days=%s limit=%s",
            input.workspace_id,
            input.window_days,
            input.limit,
        )

        def handler() -> dict[str, Any]:
            raw_result = services.transaction.search(
                workspace_id=input.workspace_id,
                window_days=input.window_days,
                limit=input.limit,
            )

            logger.info(
                "search_transactions raw_result type=%s value=%s",
                type(raw_result).__name__,
                raw_result,
            )

            normalized_result = _normalize_search_transactions_result(raw_result)

            logger.info(
                "search_transactions normalized_result=%s",
                normalized_result,
            )

            return normalized_result

        return _run_tool(
            tool_name="search_transactions",
            output_model=SearchTransactionsOutput,
            handler=handler,
        )

    @mcp.tool
    def get_monthly_summary(input: GetMonthlySummaryInput) -> dict[str, Any]:
        return _run_tool(
            tool_name="get_monthly_summary",
            output_model=MonthlySummaryOutput,
            handler=lambda: services.summary.get_monthly_summary(
                workspace_id=input.workspace_id, month=input.month
            ),
        )
