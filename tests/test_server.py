"""Tests for the JIRA MCP Server."""

import pytest  # type: ignore

from jira_mcp_server import JiraMCPServer, add_numbers, hello_world


def test_hello_world() -> None:
    """Test the hello_world function."""
    result = hello_world()
    assert result == "Hello from JIRA MCP Server!"
    assert isinstance(result, str)


def test_add_numbers() -> None:
    """Test the add_numbers function."""
    assert add_numbers(2, 3) == 5
    assert add_numbers(0, 0) == 0
    assert add_numbers(-1, 1) == 0
    assert add_numbers(10, -5) == 5


@pytest.mark.parametrize(
    "a,b,expected",
    [
        (1, 2, 3),
        (0, 0, 0),
        (-1, -1, -2),
        (100, 200, 300),
    ],
)
def test_add_numbers_parametrized(a: int, b: int, expected: int) -> None:
    """Test add_numbers with multiple parameter sets."""
    assert add_numbers(a, b) == expected


class TestJiraMCPServer:
    """Test suite for JiraMCPServer class."""

    def test_server_initialization(self) -> None:
        """Test server can be initialized."""
        server = JiraMCPServer()
        assert server.config is None
        assert server.is_running is False

    def test_server_initialization_with_config(self) -> None:
        """Test server can be initialized with config."""
        config = {"test": "value"}
        server = JiraMCPServer(config=config)
        assert server.config == config
        assert server.is_running is False

    @pytest.mark.asyncio
    async def test_server_start_stop(self) -> None:
        """Test server start and stop functionality."""
        server = JiraMCPServer()

        # Initially not running
        assert server.is_running is False

        # Start server
        await server.start()
        assert server.is_running is True

        # Stop server
        await server.stop()
        assert server.is_running is False
