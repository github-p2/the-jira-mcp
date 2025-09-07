# 🧪 JIRA MCP Server Testing Summary

## Quick Start Testing

### 1. 🚀 **Immediate Setup**
```bash
# Clone and setup
git clone <your-repo>
cd the-jira-mcp

# Run setup script
./setup_testing.sh

# Edit .env with your JIRA credentials
nano .env
```

### 2. 🔧 **Basic Tests**
```bash
# Test JIRA connection
uv run jira-mcp-server test-connection

# Validate knowledge store
uv run jira-mcp-server validate-knowledge-store

# Run direct MCP test
python3 test_mcp_client.py
```

## MCP Client Integration

### 🤖 **Claude Desktop**

1. **Install Claude Desktop**: https://claude.ai/download

2. **Configure** (`~/Library/Application Support/Claude/claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "jira": {
      "command": "uv",
      "args": ["run", "jira-mcp-server", "stdio"],
      "cwd": "/Users/priyeshpotdar/Code/Priyesh/the-jira-mcp",
      "env": {
        "JIRA_URL": "https://your-company.atlassian.net",
        "JIRA_TOKEN": "your-api-token",
        "JIRA_USERNAME": "your-email@company.com"
      }
    }
  }
}
```

3. **Test with prompts**:
   - "Show me all open bugs"
   - "What are my assigned issues?"
   - "List JIRA projects"

### 🔍 **Cursor**

1. **Install Cursor**: https://cursor.sh/

2. **Configure** (`.cursor-settings/settings.json`):
```json
{
  "mcp.servers": {
    "jira": {
      "command": "uv",
      "args": ["run", "jira-mcp-server", "stdio"],
      "cwd": "/Users/priyeshpotdar/Code/Priyesh/the-jira-mcp",
      "env": {
        "JIRA_URL": "https://your-company.atlassian.net",
        "JIRA_TOKEN": "your-api-token"
      }
    }
  }
}
```

3. **Test with**: `@jira show me critical issues`

## 🎯 Available MCP Tools

Your JIRA MCP Server provides these tools:

1. **`execute_jql`** - Direct JQL query execution
2. **`answer_question`** - Natural language to JQL mapping
3. **`list_projects`** - Get all JIRA projects
4. **`list_knowledge_queries`** - Show available patterns
5. **`test_connection`** - Validate JIRA connectivity

## 🧪 Test Scenarios

### Natural Language Queries
- "Show me all open bugs"
- "What are my assigned issues?"
- "Find critical priority issues"
- "Show me work in progress"
- "What was updated today?"
- "Find blocked issues"
- "Show me recent issues"

### Direct JQL Queries
- `project = MYPROJ AND status = Open`
- `assignee = currentUser() AND status != Done`
- `priority = Critical OR priority = High`
- `created >= -7d`
- `type = Epic`

### Metadata Operations
- List all projects
- Show knowledge patterns
- Test connection

## 📊 Success Indicators

✅ **Everything is working when**:
- Connection test passes
- Knowledge store validates
- MCP client lists 5 tools
- Natural language queries return results
- JQL execution works
- No errors in logs

## 🔧 Troubleshooting

### Common Issues:
1. **JIRA connection fails**: Check URL/token
2. **MCP client can't connect**: Verify paths in config
3. **No results**: Check JIRA permissions
4. **Server won't start**: Ensure `uv` is installed

### Debug Commands:
```bash
# Check environment
env | grep JIRA

# Debug mode
export MCP_LOG_LEVEL=DEBUG
uv run jira-mcp-server stdio

# Test individual components
uv run jira-mcp-server test-connection
uv run jira-mcp-server validate-knowledge-store
```

## 📁 Example Configurations

- `examples/claude_desktop_config.json` - Claude Desktop setup
- `examples/cursor_settings.json` - Cursor configuration
- `test_mcp_client.py` - Direct testing script
- `setup_testing.sh` - Automated setup

## 🎉 Next Steps

1. **Production Setup**: Configure with real JIRA instance
2. **Team Sharing**: Distribute configurations
3. **Custom Queries**: Add patterns to `knowledge_store.yaml`
4. **Monitoring**: Set up logging and alerts

For detailed instructions, see `MCP_CLIENT_TESTING.md`!
