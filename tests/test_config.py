"""Tests for configuration management."""

import pytest
from pydantic import ValidationError

from jira_mcp_server.config import Config, JiraConfig, ServerConfig


class TestJiraConfig:
    """Test suite for JiraConfig."""

    def test_valid_config(self, monkeypatch) -> None:
        """Test valid JIRA configuration."""
        monkeypatch.setenv("JIRA_URL", "https://test.atlassian.net")
        monkeypatch.setenv("JIRA_TOKEN", "test-token-123")
        monkeypatch.setenv("JIRA_USERNAME", "test-user")

        config = JiraConfig()
        assert config.url == "https://test.atlassian.net"
        assert config.token == "test-token-123"
        assert config.username == "test-user"

    def test_missing_url(self, monkeypatch) -> None:
        """Test configuration with missing URL."""
        monkeypatch.setenv("JIRA_TOKEN", "test-token-123")

        with pytest.raises(ValidationError):
            JiraConfig()

    def test_missing_token(self, monkeypatch) -> None:
        """Test configuration with missing token."""
        monkeypatch.setenv("JIRA_URL", "https://test.atlassian.net")

        with pytest.raises(ValidationError):
            JiraConfig()

    def test_empty_token(self, monkeypatch) -> None:
        """Test configuration with empty token."""
        monkeypatch.setenv("JIRA_URL", "https://test.atlassian.net")
        monkeypatch.setenv("JIRA_TOKEN", "")

        with pytest.raises(ValidationError):
            JiraConfig()

    def test_optional_username(self, monkeypatch) -> None:
        """Test that username is optional."""
        monkeypatch.setenv("JIRA_URL", "https://test.atlassian.net")
        monkeypatch.setenv("JIRA_TOKEN", "test-token-123")

        config = JiraConfig()
        assert config.username is None


class TestServerConfig:
    """Test suite for ServerConfig."""

    def test_default_config(self) -> None:
        """Test default server configuration."""
        config = ServerConfig()
        assert config.knowledge_store_path == "knowledge_store.yaml"
        assert config.log_level == "INFO"
        assert config.max_results == 100

    def test_custom_config(self, monkeypatch) -> None:
        """Test custom server configuration."""
        monkeypatch.setenv("MCP_KNOWLEDGE_STORE_PATH", "/custom/path.yaml")
        monkeypatch.setenv("MCP_LOG_LEVEL", "DEBUG")
        monkeypatch.setenv("MCP_MAX_RESULTS", "500")

        config = ServerConfig()
        assert config.knowledge_store_path == "/custom/path.yaml"
        assert config.log_level == "DEBUG"
        assert config.max_results == 500

    def test_invalid_log_level(self, monkeypatch) -> None:
        """Test invalid log level."""
        monkeypatch.setenv("MCP_LOG_LEVEL", "INVALID")

        with pytest.raises(ValidationError):
            ServerConfig()

    def test_invalid_max_results_too_low(self, monkeypatch) -> None:
        """Test max_results below minimum."""
        monkeypatch.setenv("MCP_MAX_RESULTS", "0")

        with pytest.raises(ValidationError):
            ServerConfig()

    def test_invalid_max_results_too_high(self, monkeypatch) -> None:
        """Test max_results above maximum."""
        monkeypatch.setenv("MCP_MAX_RESULTS", "1001")

        with pytest.raises(ValidationError):
            ServerConfig()


class TestConfig:
    """Test suite for main Config class."""

    def test_config_initialization(self, monkeypatch) -> None:
        """Test main config initialization."""
        # Set required JIRA config
        monkeypatch.setenv("JIRA_URL", "https://test.atlassian.net")
        monkeypatch.setenv("JIRA_TOKEN", "test-token-123")

        config = Config()
        assert isinstance(config.jira, JiraConfig)
        assert isinstance(config.server, ServerConfig)

    def test_config_from_env(self, monkeypatch) -> None:
        """Test creating config from environment."""
        monkeypatch.setenv("JIRA_URL", "https://test.atlassian.net")
        monkeypatch.setenv("JIRA_TOKEN", "test-token-123")

        config = Config.from_env()
        assert isinstance(config.jira, JiraConfig)
        assert isinstance(config.server, ServerConfig)
