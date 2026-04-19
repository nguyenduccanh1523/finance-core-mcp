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
    output_model: type[BaseModel], result: dict[str, Any]
) -> dict[str, Any]:
    return output_model.model_validate(result).model_dump()


def _run_tool(
    tool_name: str, output_model: type[BaseModel], handler: Callable[[], dict[str, Any]]
) -> dict[str, Any]:
    logger.info("MCP tool called: %s", tool_name)

    try:
        result = handler()
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
        return _run_tool(
            tool_name="search_transactions",
            output_model=SearchTransactionsOutput,
            handler=lambda: services.transaction.search(
                workspace_id=input.workspace_id,
                window_days=input.window_days,
                limit=input.limit,
            ),
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
