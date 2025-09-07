"""Enterprise JIRA MCP Server.

A comprehensive Model Context Protocol server for JIRA integration with
enterprise-grade features and dual deployment modes.
"""

__version__ = "0.1.0"
__author__ = "JIRA MCP Server Team"
__email__ = "maintainers@jira-mcp-server.dev"

# Import main components
from .config import Config, JiraConfig, ServerConfig
from .jira_client import JiraClient
from .knowledge_store import (
    KnowledgeStoreFactory,
    KnowledgeStoreInterface,
    QueryMapping,
    YamlKnowledgeStore,
)
from .mcp_server import JiraMCPServer


# Legacy functions for backward compatibility
def hello_world() -> str:
    """Return a greeting message.

    Returns:
        A simple greeting message for testing purposes.
    """
    return "Hello from JIRA MCP Server!"


def add_numbers(a: int, b: int) -> int:
    """Add two numbers together.

    Args:
        a: First number
        b: Second number

    Returns:
        The sum of a and b
    """
    return a + b


__all__ = [
    "JiraMCPServer",
    "JiraClient",
    "Config",
    "JiraConfig",
    "ServerConfig",
    "KnowledgeStoreFactory",
    "KnowledgeStoreInterface",
    "QueryMapping",
    "YamlKnowledgeStore",
    "hello_world",
    "add_numbers",
]
