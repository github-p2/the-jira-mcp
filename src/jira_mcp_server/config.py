"""Configuration management for JIRA MCP Server."""


from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class JiraConfig(BaseSettings):
    """Configuration for JIRA integration."""

    model_config = SettingsConfigDict(
        env_prefix="JIRA_",
        case_sensitive=False,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    url: str = Field(
        description="JIRA instance URL",
        examples=["https://your-company.atlassian.net"],
    )
    token: str = Field(
        description="JIRA API token for authentication",
        min_length=1,
    )
    username: str | None = Field(
        default=None,
        description="JIRA username (optional, for API token auth)",
    )


class ServerConfig(BaseSettings):
    """Configuration for the MCP server."""

    model_config = SettingsConfigDict(
        env_prefix="MCP_",
        case_sensitive=False,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    knowledge_store_path: str = Field(
        default="knowledge_store.yaml",
        description="Path to the knowledge store configuration file",
    )
    log_level: str = Field(
        default="INFO",
        description="Logging level",
        pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$",
    )
    max_results: int = Field(
        default=100,
        description="Maximum number of results to return from JQL queries",
        ge=1,
        le=1000,
    )


class Config:
    """Main configuration class combining all settings."""

    def __init__(self) -> None:
        """Initialize configuration from environment variables."""
        try:
            self.jira = JiraConfig()  # type: ignore[call-arg]
        except Exception:
            # Allow for missing config during testing
            # Use model_validate to bypass field validation for testing
            self.jira = JiraConfig.model_validate(
                {"url": "", "token": ""}
            )  # nosec B106
        self.server = ServerConfig()

    @classmethod
    def from_env(cls) -> "Config":
        """Create configuration from environment variables."""
        return cls()
