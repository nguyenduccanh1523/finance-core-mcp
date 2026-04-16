from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "finance-core-mcp"
    app_env: str = "local"
    app_host: str = "0.0.0.0"
    app_port: int = 8001
    app_log_level: str = "INFO"

    database_url: str

    mcp_server_name: str = "finance-core-mcp"
    mcp_server_instructions: str = (
        "Finance MCP server for budgets, goals, transactions and monthly summaries."
    )
    mcp_auth_token: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()
