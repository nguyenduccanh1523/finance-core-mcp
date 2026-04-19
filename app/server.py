from fastmcp import FastMCP

from app.config import settings
from app.tools.finance_tools import register_finance_tools


def create_mcp_server() -> FastMCP:
    mcp = FastMCP(
        name=settings.mcp_server_name,
        instructions=settings.mcp_server_instructions,
    )

    register_finance_tools(mcp)
    return mcp
