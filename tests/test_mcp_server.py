"""Tests for MCP server functionality."""

from unittest.mock import Mock, patch

import pytest

from jira_mcp_server.config import Config, JiraConfig, ServerConfig
from jira_mcp_server.mcp_server import JiraMCPServer


class TestJiraMCPServer:
    """Test suite for JiraMCPServer."""

    @pytest.fixture
    def mock_config(self) -> Config:
        """Create a mock configuration."""
        config = Mock(spec=Config)
        config.jira = Mock(spec=JiraConfig)
        config.jira.url = "https://test.atlassian.net"
        config.jira.token = "test-token"
        config.jira.username = "test-user"
        config.server = Mock(spec=ServerConfig)
        config.server.knowledge_store_path = "test_knowledge.yaml"
        config.server.max_results = 50
        return config

    @patch("jira_mcp_server.mcp_server.JiraClient")
    @patch("jira_mcp_server.mcp_server.KnowledgeStoreFactory")
    @patch("jira_mcp_server.mcp_server.Server")
    def test_initialization(
        self, mock_server, mock_knowledge_factory, mock_jira_client, mock_config
    ) -> None:
        """Test server initialization."""
        mock_jira_instance = Mock()
        mock_jira_client.return_value = mock_jira_instance

        mock_knowledge_instance = Mock()
        mock_knowledge_factory.create_store.return_value = mock_knowledge_instance

        mock_server_instance = Mock()
        mock_server.return_value = mock_server_instance

        server = JiraMCPServer(mock_config)

        assert server.config == mock_config
        assert server.jira_client == mock_jira_instance
        assert server.knowledge_store == mock_knowledge_instance
        assert server.server == mock_server_instance

        mock_jira_client.assert_called_once_with(mock_config.jira)
        mock_knowledge_factory.create_store.assert_called_once_with(
            "yaml", file_path="test_knowledge.yaml"
        )

    @patch("jira_mcp_server.mcp_server.Config")
    @patch("jira_mcp_server.mcp_server.JiraClient")
    @patch("jira_mcp_server.mcp_server.KnowledgeStoreFactory")
    @patch("jira_mcp_server.mcp_server.Server")
    def test_initialization_without_config(
        self, mock_server, mock_knowledge_factory, mock_jira_client, mock_config_class
    ) -> None:
        """Test server initialization without config."""
        mock_config_class.from_env.return_value = Mock()

        _ = JiraMCPServer()

        mock_config_class.from_env.assert_called_once()

    @patch("jira_mcp_server.mcp_server.JiraClient")
    @patch("jira_mcp_server.mcp_server.KnowledgeStoreFactory")
    @patch("jira_mcp_server.mcp_server.Server")
    def test_execute_jql_tool_success(
        self, mock_server, mock_knowledge_factory, mock_jira_client, mock_config
    ) -> None:
        """Test successful JQL execution tool."""
        # Mock JIRA client response
        mock_jira_instance = Mock()
        mock_jira_instance.execute_jql.return_value = {
            "jql": "project = TEST",
            "total": 1,
            "issues": [
                {
                    "key": "TEST-123",
                    "summary": "Test issue",
                    "status": "Open",
                    "issuetype": "Bug",
                    "project": "TEST",
                    "assignee": "Test User",
                    "priority": "High",
                    "created": "2023-01-01T10:00:00.000+0000",
                }
            ],
        }
        mock_jira_client.return_value = mock_jira_instance

        server = JiraMCPServer(mock_config)

        # Test the tool execution
        result = server._execute_jql_tool({"jql": "project = TEST", "max_results": 50})

        # Since this is an async method, we need to await it
        import asyncio

        result = asyncio.run(result)

        assert not result.isError
        assert "TEST-123" in result.content[0].text
        mock_jira_instance.execute_jql.assert_called_once_with("project = TEST", 50)

    @patch("jira_mcp_server.mcp_server.JiraClient")
    @patch("jira_mcp_server.mcp_server.KnowledgeStoreFactory")
    @patch("jira_mcp_server.mcp_server.Server")
    def test_execute_jql_tool_missing_jql(
        self, mock_server, mock_knowledge_factory, mock_jira_client, mock_config
    ) -> None:
        """Test JQL execution tool with missing JQL."""
        server = JiraMCPServer(mock_config)

        import asyncio

        result = asyncio.run(server._execute_jql_tool({}))

        assert result.isError
        assert "JQL query is required" in result.content[0].text

    @patch("jira_mcp_server.mcp_server.JiraClient")
    @patch("jira_mcp_server.mcp_server.KnowledgeStoreFactory")
    @patch("jira_mcp_server.mcp_server.Server")
    def test_answer_question_tool_success(
        self, mock_server, mock_knowledge_factory, mock_jira_client, mock_config
    ) -> None:
        """Test successful question answering tool."""
        # Mock knowledge store
        mock_knowledge_instance = Mock()
        mock_knowledge_instance.get_jql_for_question.return_value = (
            "type = Bug AND status != Done"
        )
        mock_knowledge_factory.create_store.return_value = mock_knowledge_instance

        # Mock JIRA client response
        mock_jira_instance = Mock()
        mock_jira_instance.execute_jql.return_value = {
            "jql": "type = Bug AND status != Done",
            "total": 1,
            "issues": [
                {
                    "key": "BUG-123",
                    "summary": "Test bug",
                    "status": "Open",
                    "issuetype": "Bug",
                    "project": "TEST",
                    "assignee": None,
                    "priority": "Medium",
                    "created": "2023-01-01T10:00:00.000+0000",
                }
            ],
        }
        mock_jira_client.return_value = mock_jira_instance

        server = JiraMCPServer(mock_config)

        import asyncio

        result = asyncio.run(
            server._answer_question_tool(
                {"question": "show me open bugs", "max_results": 50}
            )
        )

        assert not result.isError
        assert "BUG-123" in result.content[0].text
        assert "type = Bug AND status != Done" in result.content[0].text
        mock_knowledge_instance.get_jql_for_question.assert_called_once_with(
            "show me open bugs"
        )

    @patch("jira_mcp_server.mcp_server.JiraClient")
    @patch("jira_mcp_server.mcp_server.KnowledgeStoreFactory")
    @patch("jira_mcp_server.mcp_server.Server")
    def test_answer_question_tool_no_match(
        self, mock_server, mock_knowledge_factory, mock_jira_client, mock_config
    ) -> None:
        """Test question answering tool with no JQL match."""
        # Mock knowledge store
        mock_knowledge_instance = Mock()
        mock_knowledge_instance.get_jql_for_question.return_value = None
        mock_knowledge_instance.list_available_queries.return_value = [
            Mock(description="Find open bugs"),
            Mock(description="Find critical issues"),
        ]
        mock_knowledge_factory.create_store.return_value = mock_knowledge_instance

        server = JiraMCPServer(mock_config)

        import asyncio

        result = asyncio.run(
            server._answer_question_tool({"question": "unknown question"})
        )

        assert not result.isError
        assert "Could not find a JQL query" in result.content[0].text
        assert "Find open bugs" in result.content[0].text

    @patch("jira_mcp_server.mcp_server.JiraClient")
    @patch("jira_mcp_server.mcp_server.KnowledgeStoreFactory")
    @patch("jira_mcp_server.mcp_server.Server")
    def test_list_projects_tool_success(
        self, mock_server, mock_knowledge_factory, mock_jira_client, mock_config
    ) -> None:
        """Test successful list projects tool."""
        mock_jira_instance = Mock()
        mock_jira_instance.get_projects.return_value = [
            {
                "key": "TEST",
                "name": "Test Project",
                "description": "Test description",
                "lead": "Project Lead",
            }
        ]
        mock_jira_client.return_value = mock_jira_instance

        server = JiraMCPServer(mock_config)

        import asyncio

        result = asyncio.run(server._list_projects_tool())

        assert not result.isError
        assert "TEST: Test Project" in result.content[0].text
        assert "Project Lead" in result.content[0].text

    @patch("jira_mcp_server.mcp_server.JiraClient")
    @patch("jira_mcp_server.mcp_server.KnowledgeStoreFactory")
    @patch("jira_mcp_server.mcp_server.Server")
    def test_list_knowledge_queries_tool(
        self, mock_server, mock_knowledge_factory, mock_jira_client, mock_config
    ) -> None:
        """Test list knowledge queries tool."""
        mock_mapping = Mock()
        mock_mapping.description = "Find open bugs"
        mock_mapping.jql_query = "type = Bug AND status != Done"
        mock_mapping.question_patterns = ["open bugs", "active bugs"]
        mock_mapping.examples = ["Show me open bugs"]

        mock_knowledge_instance = Mock()
        mock_knowledge_instance.list_available_queries.return_value = [mock_mapping]
        mock_knowledge_factory.create_store.return_value = mock_knowledge_instance

        server = JiraMCPServer(mock_config)

        import asyncio

        result = asyncio.run(server._list_knowledge_queries_tool())

        assert not result.isError
        assert "Find open bugs" in result.content[0].text
        assert "type = Bug AND status != Done" in result.content[0].text

    @patch("jira_mcp_server.mcp_server.JiraClient")
    @patch("jira_mcp_server.mcp_server.KnowledgeStoreFactory")
    @patch("jira_mcp_server.mcp_server.Server")
    def test_test_connection_tool_success(
        self, mock_server, mock_knowledge_factory, mock_jira_client, mock_config
    ) -> None:
        """Test successful connection test tool."""
        mock_jira_instance = Mock()
        mock_jira_instance.test_connection.return_value = True
        mock_jira_client.return_value = mock_jira_instance

        server = JiraMCPServer(mock_config)

        import asyncio

        result = asyncio.run(server._test_connection_tool())

        assert not result.isError
        assert "connection test successful" in result.content[0].text

    @patch("jira_mcp_server.mcp_server.JiraClient")
    @patch("jira_mcp_server.mcp_server.KnowledgeStoreFactory")
    @patch("jira_mcp_server.mcp_server.Server")
    def test_test_connection_tool_failure(
        self, mock_server, mock_knowledge_factory, mock_jira_client, mock_config
    ) -> None:
        """Test connection test tool failure."""
        mock_jira_instance = Mock()
        mock_jira_instance.test_connection.return_value = False
        mock_jira_client.return_value = mock_jira_instance

        server = JiraMCPServer(mock_config)

        import asyncio

        result = asyncio.run(server._test_connection_tool())

        assert result.isError
        assert "connection test failed" in result.content[0].text
