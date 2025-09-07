"""Tests for JIRA client functionality."""

from unittest.mock import Mock, patch

import pytest
from jira.exceptions import JIRAError

from jira_mcp_server.config import JiraConfig
from jira_mcp_server.jira_client import JiraClient


class TestJiraClient:
    """Test suite for JiraClient."""

    @pytest.fixture
    def jira_config(self) -> JiraConfig:
        """Create a test JIRA configuration."""
        return JiraConfig(
            url="https://test.atlassian.net",
            token="test-token-123",
            username="test-user",
        )

    @patch("jira_mcp_server.jira_client.JIRA")
    def test_initialization_with_username(self, mock_jira, jira_config) -> None:
        """Test client initialization with username (tries Bearer auth first)."""
        mock_jira_instance = Mock()
        mock_jira.return_value = mock_jira_instance

        client = JiraClient(jira_config)

        # Should first try Bearer token authentication
        mock_jira.assert_called_with(
            server="https://test.atlassian.net",
            token_auth="test-token-123",
        )
        assert client.client == mock_jira_instance

    @patch("jira_mcp_server.jira_client.JIRA")
    def test_initialization_with_username_fallback_to_basic(
        self, mock_jira, jira_config
    ) -> None:
        """Test client initialization falls back to basic auth when Bearer fails."""
        mock_jira_instance = Mock()

        # First call (Bearer auth) raises exception, second call (basic auth) succeeds
        mock_jira.side_effect = [Exception("Bearer auth failed"), mock_jira_instance]

        client = JiraClient(jira_config)

        # Should be called twice: first Bearer, then basic auth
        assert mock_jira.call_count == 2

        # First call: Bearer token auth
        first_call = mock_jira.call_args_list[0]
        assert first_call.kwargs == {
            "server": "https://test.atlassian.net",
            "token_auth": "test-token-123",
        }

        # Second call: Basic auth fallback
        second_call = mock_jira.call_args_list[1]
        assert second_call.kwargs == {
            "server": "https://test.atlassian.net",
            "basic_auth": ("test-user", "test-token-123"),
        }

        assert client.client == mock_jira_instance

    @patch("jira_mcp_server.jira_client.JIRA")
    def test_initialization_without_username(self, mock_jira) -> None:
        """Test client initialization without username."""
        config = JiraConfig(url="https://test.atlassian.net", token="test-token-123")
        mock_jira_instance = Mock()
        mock_jira.return_value = mock_jira_instance

        client = JiraClient(config)

        mock_jira.assert_called_once_with(
            server="https://test.atlassian.net", token_auth="test-token-123"
        )
        assert client.client == mock_jira_instance

    @patch("jira_mcp_server.jira_client.JIRA")
    def test_initialization_failure(self, mock_jira, jira_config) -> None:
        """Test client initialization failure."""
        mock_jira.side_effect = Exception("Connection failed")

        with pytest.raises(Exception, match="Connection failed"):
            JiraClient(jira_config)

    @patch("jira_mcp_server.jira_client.JIRA")
    def test_test_connection_success(self, mock_jira, jira_config) -> None:
        """Test successful connection test."""
        mock_jira_instance = Mock()
        mock_jira_instance.server_info.return_value = {"version": "9.0.0"}
        mock_jira.return_value = mock_jira_instance

        client = JiraClient(jira_config)
        result = client.test_connection()

        assert result is True
        mock_jira_instance.server_info.assert_called_once()

    @patch("jira_mcp_server.jira_client.JIRA")
    def test_test_connection_failure(self, mock_jira, jira_config) -> None:
        """Test connection test failure."""
        mock_jira_instance = Mock()
        mock_jira_instance.server_info.side_effect = Exception("Network error")
        mock_jira.return_value = mock_jira_instance

        client = JiraClient(jira_config)
        result = client.test_connection()

        assert result is False

    @patch("jira_mcp_server.jira_client.JIRA")
    def test_execute_jql_success(self, mock_jira, jira_config) -> None:
        """Test successful JQL execution."""
        # Mock issue objects
        mock_issue = Mock()
        mock_issue.key = "TEST-123"
        mock_issue.fields.summary = "Test issue"
        mock_issue.fields.status.name = "Open"
        mock_issue.fields.assignee.displayName = "Test User"
        mock_issue.fields.reporter.displayName = "Reporter User"
        mock_issue.fields.created = "2023-01-01T10:00:00.000+0000"
        mock_issue.fields.updated = "2023-01-02T10:00:00.000+0000"
        mock_issue.fields.priority.name = "High"
        mock_issue.fields.issuetype.name = "Bug"
        mock_issue.fields.project.key = "TEST"
        mock_issue.fields.description = "Test description"

        mock_jira_instance = Mock()
        mock_jira_instance.search_issues.return_value = [mock_issue]
        mock_jira.return_value = mock_jira_instance

        client = JiraClient(jira_config)
        result = client.execute_jql("project = TEST", max_results=50)

        assert result["jql"] == "project = TEST"
        assert result["total"] == 1
        assert result["max_results"] == 50
        assert len(result["issues"]) == 1

        issue = result["issues"][0]
        assert issue["key"] == "TEST-123"
        assert issue["summary"] == "Test issue"
        assert issue["status"] == "Open"
        assert issue["assignee"] == "Test User"
        assert issue["description"] == "Test description"

    @patch("jira_mcp_server.jira_client.JIRA")
    def test_execute_jql_with_none_fields(self, mock_jira, jira_config) -> None:
        """Test JQL execution with None fields."""
        mock_issue = Mock()
        mock_issue.key = "TEST-123"
        mock_issue.fields.summary = "Test issue"
        mock_issue.fields.status.name = "Open"
        mock_issue.fields.assignee = None
        mock_issue.fields.reporter = None
        mock_issue.fields.created = "2023-01-01T10:00:00.000+0000"
        mock_issue.fields.updated = "2023-01-02T10:00:00.000+0000"
        mock_issue.fields.priority = None
        mock_issue.fields.issuetype.name = "Bug"
        mock_issue.fields.project.key = "TEST"

        # Mock hasattr and getattr for description
        def mock_hasattr(obj, attr):
            return attr != "description"

        mock_jira_instance = Mock()
        mock_jira_instance.search_issues.return_value = [mock_issue]
        mock_jira.return_value = mock_jira_instance

        client = JiraClient(jira_config)

        with patch("builtins.hasattr", side_effect=mock_hasattr):
            result = client.execute_jql("project = TEST")

        issue = result["issues"][0]
        assert issue["assignee"] is None
        assert issue["reporter"] is None
        assert issue["priority"] is None
        assert "description" not in issue

    @patch("jira_mcp_server.jira_client.JIRA")
    def test_execute_jql_jira_error(self, mock_jira, jira_config) -> None:
        """Test JQL execution with JIRA error."""
        mock_jira_instance = Mock()
        mock_jira_instance.search_issues.side_effect = JIRAError("Invalid JQL")
        mock_jira.return_value = mock_jira_instance

        client = JiraClient(jira_config)

        # Replace the decorated method with an undecorated version for testing
        original_method = client.execute_jql.__wrapped__

        def undecorated_execute_jql(jql_query, max_results=50, expand=None):
            return original_method(client, jql_query, max_results, expand)

        with patch.object(client, "execute_jql", undecorated_execute_jql):
            with pytest.raises(JIRAError, match="Invalid JQL"):
                client.execute_jql("invalid jql")

    @patch("jira_mcp_server.jira_client.JIRA")
    def test_execute_jql_unexpected_error(self, mock_jira, jira_config) -> None:
        """Test JQL execution with unexpected error."""
        mock_jira_instance = Mock()
        mock_jira_instance.search_issues.side_effect = ValueError("Unexpected error")
        mock_jira.return_value = mock_jira_instance

        client = JiraClient(jira_config)

        # Replace the decorated method with an undecorated version for testing
        original_method = client.execute_jql.__wrapped__

        def undecorated_execute_jql(jql_query, max_results=50, expand=None):
            return original_method(client, jql_query, max_results, expand)

        with patch.object(client, "execute_jql", undecorated_execute_jql):
            with pytest.raises(JIRAError, match="Unexpected error"):
                client.execute_jql("project = TEST")

    @patch("jira_mcp_server.jira_client.JIRA")
    def test_get_projects(self, mock_jira, jira_config) -> None:
        """Test getting projects."""
        mock_project = Mock()
        mock_project.key = "TEST"
        mock_project.name = "Test Project"
        mock_project.description = "Test description"
        mock_project.lead.displayName = "Project Lead"

        mock_jira_instance = Mock()
        mock_jira_instance.projects.return_value = [mock_project]
        mock_jira.return_value = mock_jira_instance

        client = JiraClient(jira_config)
        projects = client.get_projects()

        assert len(projects) == 1
        assert projects[0]["key"] == "TEST"
        assert projects[0]["name"] == "Test Project"
        assert projects[0]["description"] == "Test description"
        assert projects[0]["lead"] == "Project Lead"

    @patch("jira_mcp_server.jira_client.JIRA")
    def test_get_projects_error(self, mock_jira, jira_config) -> None:
        """Test getting projects with error."""
        mock_jira_instance = Mock()
        mock_jira_instance.projects.side_effect = Exception("API error")
        mock_jira.return_value = mock_jira_instance

        client = JiraClient(jira_config)

        with pytest.raises(Exception, match="API error"):
            client.get_projects()

    @patch("jira_mcp_server.jira_client.JIRA")
    def test_get_issue_types(self, mock_jira, jira_config) -> None:
        """Test getting issue types."""
        mock_issue_type = Mock()
        mock_issue_type.id = "1"
        mock_issue_type.name = "Bug"
        mock_issue_type.description = "Bug issue type"

        mock_jira_instance = Mock()
        mock_jira_instance.issue_types.return_value = [mock_issue_type]
        mock_jira.return_value = mock_jira_instance

        client = JiraClient(jira_config)
        issue_types = client.get_issue_types()

        assert len(issue_types) == 1
        assert issue_types[0]["id"] == "1"
        assert issue_types[0]["name"] == "Bug"
        assert issue_types[0]["description"] == "Bug issue type"

    @patch("jira_mcp_server.jira_client.JIRA")
    def test_client_property_not_initialized(self, mock_jira, jira_config) -> None:
        """Test client property when not initialized."""
        mock_jira_instance = Mock()
        mock_jira.return_value = mock_jira_instance

        client = JiraClient(jira_config)
        # Force the client to be None to test the property check
        client._client = None

        with pytest.raises(RuntimeError, match="JIRA client is not initialized"):
            _ = client.client
