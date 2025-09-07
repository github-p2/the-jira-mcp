# Testing Utilities

This directory contains testing and debugging utilities for the JIRA MCP Server.

## Files

### `setup_testing.sh`
Automated setup script for testing environment:
- Creates virtual environment with uv
- Installs dependencies
- Generates sample .env file
- Sets up testing prerequisites

### `test_mcp_client.py`
Direct MCP protocol testing client:
- Tests MCP server initialization
- Validates tool registration
- Tests JIRA connection
- Executes natural language queries
- Useful for debugging MCP protocol issues

### `jira_auth_tests.sh`
JIRA authentication debugging script:
- Tests different authentication methods
- Validates Bearer token vs Basic auth
- Helps diagnose corporate JIRA authentication issues
- Includes curl-based testing

## Usage

These utilities were used during development and debugging. They can be helpful for:
- Setting up development environments
- Debugging authentication issues
- Testing MCP protocol integration
- Validating server functionality

For production usage, refer to the main documentation and examples in the `examples/` directory.
