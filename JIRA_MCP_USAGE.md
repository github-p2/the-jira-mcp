# JIRA MCP Server Usage Guide

## Quick Start

### 1. Environment Setup

Create a `.env` file in the project root with your JIRA configuration:

```bash
# JIRA Configuration
JIRA_URL=https://your-company.atlassian.net
JIRA_TOKEN=your-api-token-here
JIRA_USERNAME=your-email@company.com

# MCP Server Configuration (optional)
MCP_KNOWLEDGE_STORE_PATH=knowledge_store.yaml
MCP_LOG_LEVEL=INFO
MCP_MAX_RESULTS=100
```

### 2. Install Dependencies

```bash
uv sync --extra dev
```

### 3. Test JIRA Connection

```bash
uv run jira-mcp-server test-connection
```

### 4. Validate Knowledge Store

```bash
uv run jira-mcp-server validate-knowledge-store
```

### 5. Run in STDIO Mode

```bash
uv run jira-mcp-server stdio
```

## Available MCP Tools

### `execute_jql`
Execute a JQL query directly:
```json
{
  "name": "execute_jql",
  "arguments": {
    "jql": "project = PROJ AND status = Open",
    "max_results": 50
  }
}
```

### `answer_question`
Ask natural language questions that get mapped to JQL:
```json
{
  "name": "answer_question",
  "arguments": {
    "question": "show me open bugs",
    "max_results": 25
  }
}
```

### `list_projects`
List all available JIRA projects:
```json
{
  "name": "list_projects",
  "arguments": {}
}
```

### `list_knowledge_queries`
Show available question patterns in the knowledge store:
```json
{
  "name": "list_knowledge_queries",
  "arguments": {}
}
```

### `test_connection`
Test the JIRA connection:
```json
{
  "name": "test_connection",
  "arguments": {}
}
```

## Knowledge Store Configuration

The knowledge store maps natural language questions to JQL queries. Example `knowledge_store.yaml`:

```yaml
queries:
  - description: "Find all open bugs"
    question_patterns:
      - "open bugs"
      - "active bugs"
      - "unresolved bugs"
    jql_query: "type = Bug AND status != Done AND status != Closed"
    examples:
      - "Show me all open bugs"
      - "What are the active bugs?"
```

## Getting JIRA API Token

1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Give it a label and copy the token
4. Use your email as the username and the token as the password

## Integration with MCP Clients

This server implements the Model Context Protocol (MCP) and can be used with any MCP-compatible client like Claude Desktop or other AI tools that support MCP.

Example MCP client configuration:
```json
{
  "servers": {
    "jira": {
      "command": "uv",
      "args": ["run", "jira-mcp-server", "stdio"],
      "cwd": "/path/to/jira-mcp-server"
    }
  }
}
```
