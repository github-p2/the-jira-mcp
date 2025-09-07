"""MCP Server implementation for JIRA integration."""

import sys
from typing import Any

import structlog

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        CallToolResult,
        TextContent,
        Tool,
    )
except ImportError:
    # Handle case when MCP is not available (e.g., for static analysis)
    Server = None
    stdio_server = None

from .config import Config
from .jira_client import JiraClient
from .knowledge_store import KnowledgeStoreFactory

logger = structlog.get_logger(__name__)


class JiraMCPServer:
    """MCP Server for JIRA integration."""

    def __init__(self, config: Config | None = None) -> None:
        """Initialize the JIRA MCP Server.

        Args:
            config: Configuration object, will be loaded from env if not provided
        """
        self.config = config or Config.from_env()
        self.jira_client = JiraClient(self.config.jira)
        self.knowledge_store = KnowledgeStoreFactory.create_store(
            "yaml", file_path=self.config.server.knowledge_store_path
        )
        self.server = Server("jira-mcp-server")
        self._setup_tools()

    def _setup_tools(self) -> None:
        """Set up MCP tools for JIRA operations."""

        @self.server.list_tools()  # type: ignore[misc]
        async def handle_list_tools() -> list[Tool]:
            """List available tools."""
            return [
                Tool(
                    name="execute_jql",
                    description="Execute a JQL (JIRA Query Language) query to search for issues",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "jql": {
                                "type": "string",
                                "description": "The JQL query string to execute",
                            },
                            "max_results": {
                                "type": "integer",
                                "description": "Maximum number of results to return (default: 50)",
                                "minimum": 1,
                                "maximum": 1000,
                                "default": 50,
                            },
                        },
                        "required": ["jql"],
                    },
                ),
                Tool(
                    name="answer_question",
                    description="Answer a question about JIRA by finding the appropriate JQL query from knowledge store",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "question": {
                                "type": "string",
                                "description": "The question about JIRA data you want to answer",
                            },
                            "max_results": {
                                "type": "integer",
                                "description": "Maximum number of results to return (default: 50)",
                                "minimum": 1,
                                "maximum": 1000,
                                "default": 50,
                            },
                        },
                        "required": ["question"],
                    },
                ),
                Tool(
                    name="list_projects",
                    description="List all available JIRA projects",
                    inputSchema={"type": "object", "properties": {}},
                ),
                Tool(
                    name="list_knowledge_queries",
                    description="List all available query patterns from the knowledge store",
                    inputSchema={"type": "object", "properties": {}},
                ),
                Tool(
                    name="test_connection",
                    description="Test the connection to JIRA",
                    inputSchema={"type": "object", "properties": {}},
                ),
            ]

        @self.server.call_tool()  # type: ignore[misc]
        async def handle_call_tool(
            name: str, arguments: dict[str, Any]
        ) -> CallToolResult:
            """Handle tool calls."""
            try:
                if name == "execute_jql":
                    return await self._execute_jql_tool(arguments)
                elif name == "answer_question":
                    return await self._answer_question_tool(arguments)
                elif name == "list_projects":
                    return await self._list_projects_tool()
                elif name == "list_knowledge_queries":
                    return await self._list_knowledge_queries_tool()
                elif name == "test_connection":
                    return await self._test_connection_tool()
                else:
                    return CallToolResult(
                        content=[
                            TextContent(type="text", text=f"Unknown tool: {name}")
                        ],
                        isError=True,
                    )
            except Exception as e:
                logger.error("Tool execution failed", tool=name, error=str(e))
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text", text=f"Error executing {name}: {str(e)}"
                        )
                    ],
                    isError=True,
                )

    async def _execute_jql_tool(self, arguments: dict[str, Any]) -> CallToolResult:
        """Execute JQL query tool."""
        jql = arguments.get("jql")
        max_results = arguments.get("max_results", 50)

        if not jql:
            return CallToolResult(
                content=[TextContent(type="text", text="JQL query is required")],
                isError=True,
            )

        try:
            results = self.jira_client.execute_jql(jql, max_results)

            # Format results for display
            output = f"JQL Query: {jql}\n"
            output += f"Total Results: {results['total']}\n\n"

            if results["issues"]:
                for issue in results["issues"]:
                    output += f"🎫 {issue['key']}: {issue['summary']}\n"
                    output += f"   Status: {issue['status']}\n"
                    output += f"   Type: {issue['issuetype']}\n"
                    output += f"   Project: {issue['project']}\n"
                    if issue["assignee"]:
                        output += f"   Assignee: {issue['assignee']}\n"
                    if issue["priority"]:
                        output += f"   Priority: {issue['priority']}\n"
                    output += f"   Created: {issue['created']}\n\n"
            else:
                output += "No issues found matching the query.\n"

            return CallToolResult(content=[TextContent(type="text", text=output)])

        except Exception as e:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text", text=f"Failed to execute JQL query: {str(e)}"
                    )
                ],
                isError=True,
            )

    async def _answer_question_tool(self, arguments: dict[str, Any]) -> CallToolResult:
        """Answer question using knowledge store."""
        question = arguments.get("question")
        max_results = arguments.get("max_results", 50)

        if not question:
            return CallToolResult(
                content=[TextContent(type="text", text="Question is required")],
                isError=True,
            )

        try:
            # Find appropriate JQL from knowledge store
            jql = self.knowledge_store.get_jql_for_question(question)

            if not jql:
                available_queries = self.knowledge_store.list_available_queries()
                suggestions = "\n".join(
                    [f"- {mapping.description}" for mapping in available_queries[:5]]
                )

                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"Could not find a JQL query for your question: '{question}'\n\n"
                            f"Available query types:\n{suggestions}\n\n"
                            f"Try rephrasing your question or use the 'execute_jql' tool directly.",
                        )
                    ]
                )

            # Execute the found JQL
            results = self.jira_client.execute_jql(jql, max_results)

            # Format results with context
            output = f"Question: {question}\n"
            output += f"Matched JQL: {jql}\n"
            output += f"Total Results: {results['total']}\n\n"

            if results["issues"]:
                for issue in results["issues"]:
                    output += f"🎫 {issue['key']}: {issue['summary']}\n"
                    output += f"   Status: {issue['status']}\n"
                    output += f"   Type: {issue['issuetype']}\n"
                    output += f"   Project: {issue['project']}\n"
                    if issue["assignee"]:
                        output += f"   Assignee: {issue['assignee']}\n"
                    if issue["priority"]:
                        output += f"   Priority: {issue['priority']}\n"
                    output += f"   Created: {issue['created']}\n\n"
            else:
                output += "No issues found matching the query.\n"

            return CallToolResult(content=[TextContent(type="text", text=output)])

        except Exception as e:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text", text=f"Failed to answer question: {str(e)}"
                    )
                ],
                isError=True,
            )

    async def _list_projects_tool(self) -> CallToolResult:
        """List JIRA projects tool."""
        try:
            projects = self.jira_client.get_projects()

            output = "Available JIRA Projects:\n\n"
            for project in projects:
                output += f"🗂️  {project['key']}: {project['name']}\n"
                if project["description"]:
                    output += f"   Description: {project['description']}\n"
                if project["lead"]:
                    output += f"   Lead: {project['lead']}\n"
                output += "\n"

            return CallToolResult(content=[TextContent(type="text", text=output)])

        except Exception as e:
            return CallToolResult(
                content=[
                    TextContent(type="text", text=f"Failed to list projects: {str(e)}")
                ],
                isError=True,
            )

    async def _list_knowledge_queries_tool(self) -> CallToolResult:
        """List available knowledge queries tool."""
        try:
            mappings = self.knowledge_store.list_available_queries()

            if not mappings:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text="No query mappings found in knowledge store. "
                            "Please check your knowledge store configuration.",
                        )
                    ]
                )

            output = "Available Query Patterns:\n\n"
            for mapping in mappings:
                output += f"📋 {mapping.description}\n"
                output += f"   JQL: {mapping.jql_query}\n"
                output += f"   Patterns: {', '.join(mapping.question_patterns)}\n"
                if mapping.examples:
                    output += f"   Examples: {', '.join(mapping.examples)}\n"
                output += "\n"

            return CallToolResult(content=[TextContent(type="text", text=output)])

        except Exception as e:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text", text=f"Failed to list knowledge queries: {str(e)}"
                    )
                ],
                isError=True,
            )

    async def _test_connection_tool(self) -> CallToolResult:
        """Test JIRA connection tool."""
        try:
            is_connected = self.jira_client.test_connection()

            if is_connected:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text", text="✅ JIRA connection test successful!"
                        )
                    ]
                )
            else:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text="❌ JIRA connection test failed. Please check your configuration.",
                        )
                    ],
                    isError=True,
                )

        except Exception as e:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text", text=f"❌ JIRA connection test failed: {str(e)}"
                    )
                ],
                isError=True,
            )

    async def run_stdio(self) -> None:
        """Run the server in STDIO mode."""
        logger.info("Starting JIRA MCP Server in STDIO mode")

        # Test JIRA connection on startup
        try:
            if not self.jira_client.test_connection():
                logger.error("JIRA connection test failed during startup")
                sys.exit(1)
        except Exception as e:
            logger.error("Failed to test JIRA connection during startup", error=str(e))
            sys.exit(1)

        # Load knowledge store
        try:
            self.knowledge_store.reload()
            available_queries = len(self.knowledge_store.list_available_queries())
            logger.info(
                f"Knowledge store loaded with {available_queries} query mappings"
            )
        except Exception as e:
            logger.warning("Failed to load knowledge store", error=str(e))

        # Run the STDIO server
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(read_stream, write_stream)
