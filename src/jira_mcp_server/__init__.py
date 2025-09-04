"""Enterprise JIRA MCP Server.

A comprehensive Model Context Protocol server for JIRA integration with
enterprise-grade features and dual deployment modes.
"""

__version__ = "0.1.0"
__author__ = "JIRA MCP Server Team"
__email__ = "maintainers@jira-mcp-server.dev"

from typing import Any


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


class JiraMCPServer:
    """Main JIRA MCP Server class.

    This is a placeholder implementation for testing the development setup.
    """

    def __init__(self, config: Any = None) -> None:
        """Initialize the JIRA MCP Server.

        Args:
            config: Configuration object (placeholder)
        """
        self.config = config
        self.is_running = False

    async def start(self) -> None:
        """Start the MCP server."""
        self.is_running = True

    async def stop(self) -> None:
        """Stop the MCP server."""
        self.is_running = False
