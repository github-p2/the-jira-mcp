"""Tests for the JIRA MCP Server."""

import pytest

from jira_mcp_server import add_numbers, hello_world


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
