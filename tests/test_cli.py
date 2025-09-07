"""Tests for CLI functionality."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import yaml
from click.testing import CliRunner

from jira_mcp_server.cli import cli


class TestCLI:
    """Test suite for CLI commands."""

    def test_cli_help(self) -> None:
        """Test CLI help output."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "JIRA MCP Server" in result.output

    def test_cli_with_log_level(self) -> None:
        """Test CLI with log level option."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--log-level", "DEBUG", "--help"])

        assert result.exit_code == 0

    @patch("jira_mcp_server.cli.Config")
    @patch("jira_mcp_server.jira_client.JiraClient")
    def test_test_connection_success(self, mock_jira_client, mock_config) -> None:
        """Test successful connection test command."""
        # Mock config
        mock_config_instance = Mock()
        mock_config.from_env.return_value = mock_config_instance

        # Mock JIRA client
        mock_client_instance = Mock()
        mock_client_instance.test_connection.return_value = True
        mock_client_instance.get_projects.return_value = [
            {"key": "TEST", "name": "Test Project"},
            {"key": "DEMO", "name": "Demo Project"},
        ]
        mock_jira_client.return_value = mock_client_instance

        runner = CliRunner()
        result = runner.invoke(cli, ["test-connection"])

        assert result.exit_code == 0
        assert "connection successful" in result.output
        assert "Found 2 projects" in result.output
        assert "TEST: Test Project" in result.output

    @patch("jira_mcp_server.cli.Config")
    @patch("jira_mcp_server.jira_client.JiraClient")
    def test_test_connection_failure(self, mock_jira_client, mock_config) -> None:
        """Test connection test command failure."""
        mock_config_instance = Mock()
        mock_config.from_env.return_value = mock_config_instance

        mock_client_instance = Mock()
        mock_client_instance.test_connection.return_value = False
        mock_jira_client.return_value = mock_client_instance

        runner = CliRunner()
        result = runner.invoke(cli, ["test-connection"])

        assert result.exit_code == 1
        assert "connection failed" in result.output

    @patch("jira_mcp_server.cli.Config")
    def test_test_connection_exception(self, mock_config) -> None:
        """Test connection test command with exception."""
        mock_config.from_env.side_effect = Exception("Config error")

        runner = CliRunner()
        result = runner.invoke(cli, ["test-connection"])

        assert result.exit_code == 1
        assert "Error testing connection" in result.output

    def test_validate_knowledge_store_success(self) -> None:
        """Test successful knowledge store validation."""
        # Create temporary YAML file
        data = {
            "queries": [
                {
                    "question_patterns": ["test pattern"],
                    "jql_query": "project = TEST",
                    "description": "Test mapping",
                }
            ]
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(data, f)
            temp_path = f.name

        try:
            runner = CliRunner()
            result = runner.invoke(
                cli, ["validate-knowledge-store", "--knowledge-store", temp_path]
            )

            assert result.exit_code == 0
            assert "loaded successfully" in result.output
            assert "1 query mappings" in result.output
            assert "Test mapping" in result.output
        finally:
            Path(temp_path).unlink()

    def test_validate_knowledge_store_empty(self) -> None:
        """Test knowledge store validation with empty file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("")
            temp_path = f.name

        try:
            runner = CliRunner()
            result = runner.invoke(
                cli, ["validate-knowledge-store", "--knowledge-store", temp_path]
            )

            assert result.exit_code == 0
            assert "empty or file not found" in result.output
        finally:
            Path(temp_path).unlink()

    def test_validate_knowledge_store_invalid_yaml(self) -> None:
        """Test knowledge store validation with invalid YAML."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("invalid: yaml: content: [")
            temp_path = f.name

        try:
            runner = CliRunner()
            result = runner.invoke(
                cli, ["validate-knowledge-store", "--knowledge-store", temp_path]
            )

            assert result.exit_code == 1
            assert "Error validating knowledge store" in result.output
        finally:
            Path(temp_path).unlink()

    def test_validate_knowledge_store_nonexistent(self) -> None:
        """Test knowledge store validation with non-existent file."""
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "validate-knowledge-store",
                "--knowledge-store",
                "/non/existent/file.yaml",
            ],
        )

        assert result.exit_code == 0
        assert "empty or file not found" in result.output

    @patch("jira_mcp_server.cli.JiraMCPServer")
    @patch("jira_mcp_server.cli.Config")
    def test_stdio_command(self, mock_config, mock_server) -> None:
        """Test STDIO command initialization."""
        # Mock config
        mock_config_instance = Mock()
        mock_config.from_env.return_value = mock_config_instance

        # Mock server
        mock_server_instance = Mock()
        mock_server_instance.run_stdio = Mock()
        mock_server.return_value = mock_server_instance

        # We can't easily test the full async execution in CLI tests,
        # but we can test that the command is properly defined
        runner = CliRunner()
        result = runner.invoke(cli, ["stdio", "--help"])

        assert result.exit_code == 0
        assert "STDIO mode" in result.output
