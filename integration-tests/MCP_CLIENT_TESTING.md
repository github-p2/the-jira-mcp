# Testing JIRA MCP Server with MCP Clients

This guide shows how to test your JIRA MCP Server with various MCP clients like Claude Desktop, Cursor, and other MCP-compatible tools.

## Prerequisites

1. **Set up your environment variables** (create `.env` file in project root):
```bash
JIRA_URL=https://your-company.atlassian.net
JIRA_TOKEN=your-api-token-here
JIRA_USERNAME=your-email@company.com  # Optional
```

2. **Install dependencies**:
```bash
uv sync --extra dev
```

3. **Test your JIRA connection**:
```bash
uv run jira-mcp-server test-connection
```

## 🤖 Testing with Claude Desktop

### 1. Install Claude Desktop
Download from: https://claude.ai/download

### 2. Configure Claude Desktop

Create or edit Claude's MCP configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

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

### 3. Test with Claude

Restart Claude Desktop and try these prompts:

```
Show me all open bugs in JIRA
```

```
What are my assigned issues?
```

```
Execute this JQL: project = MYPROJ AND status = "In Progress"
```

```
List all available JIRA projects
```

## 🔍 Testing with Cursor

### 1. Install Cursor
Download from: https://cursor.sh/

### 2. Configure MCP in Cursor

Add to your Cursor settings (`.cursor-settings/settings.json`):

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

### 3. Test in Cursor

Use Cursor's AI chat and ask:

```
@jira show me critical priority issues
```

```
@jira what work is in progress?
```

## 🧪 Manual Testing with Direct MCP Communication

### Create a Test Script

```bash
# Create a test script
cat > test_mcp_client.py << 'EOF'
#!/usr/bin/env python3
"""Simple MCP client for testing JIRA MCP Server."""

import asyncio
import json
import sys
from pathlib import Path

async def test_mcp_server():
    """Test the JIRA MCP Server directly."""

    # Start the server process
    proc = await asyncio.create_subprocess_exec(
        "uv", "run", "jira-mcp-server", "stdio",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=Path(__file__).parent
    )

    async def send_message(message):
        """Send a message to the MCP server."""
        json_msg = json.dumps(message)
        proc.stdin.write(f"{json_msg}\n".encode())
        await proc.stdin.drain()

        # Read response
        response_line = await proc.stdout.readline()
        return json.loads(response_line.decode().strip())

    try:
        # Test 1: List available tools
        print("🔧 Testing: List Tools")
        list_tools_msg = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        }

        response = await send_message(list_tools_msg)
        print(f"✅ Found {len(response.get('result', {}).get('tools', []))} tools")
        for tool in response.get('result', {}).get('tools', []):
            print(f"   - {tool['name']}: {tool['description']}")

        # Test 2: Test JIRA connection
        print("\n🔗 Testing: JIRA Connection")
        test_connection_msg = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "test_connection",
                "arguments": {}
            }
        }

        response = await send_message(test_connection_msg)
        result_text = response.get('result', {}).get('content', [{}])[0].get('text', '')
        print(f"✅ Connection test: {result_text}")

        # Test 3: List knowledge queries
        print("\n📚 Testing: Knowledge Store")
        list_queries_msg = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "list_knowledge_queries",
                "arguments": {}
            }
        }

        response = await send_message(list_queries_msg)
        result_text = response.get('result', {}).get('content', [{}])[0].get('text', '')
        print("✅ Knowledge store loaded")
        print(result_text[:500] + "..." if len(result_text) > 500 else result_text)

        # Test 4: Answer a question
        print("\n❓ Testing: Natural Language Query")
        answer_question_msg = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "answer_question",
                "arguments": {
                    "question": "show me open bugs",
                    "max_results": 5
                }
            }
        }

        response = await send_message(answer_question_msg)
        result_text = response.get('result', {}).get('content', [{}])[0].get('text', '')
        print("✅ Natural language query executed")
        print(result_text[:300] + "..." if len(result_text) > 300 else result_text)

        print("\n🎉 All tests completed successfully!")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        proc.terminate()
        await proc.wait()

if __name__ == "__main__":
    asyncio.run(test_mcp_server())
EOF

# Make it executable
chmod +x test_mcp_client.py
```

### Run the Test

```bash
python3 test_mcp_client.py
```

## 🛠️ Testing with Generic MCP Client

### Install MCP Client Tools

```bash
# Install MCP Inspector (official MCP testing tool)
npm install -g @anthropic/mcp-inspector

# Or use Python MCP client
pip install mcp
```

### Test with MCP Inspector

```bash
# Test the server
mcp-inspector uv run jira-mcp-server stdio
```

## 🎯 Example Test Scenarios

### 1. Basic Functionality Tests

```bash
# Test connection
uv run jira-mcp-server test-connection

# Validate knowledge store
uv run jira-mcp-server validate-knowledge-store

# Run server and test manually
uv run jira-mcp-server stdio
```

### 2. Natural Language Queries

Test these questions with your MCP client:

- "Show me all open bugs"
- "What are my assigned issues?"
- "Find critical priority issues"
- "Show me work in progress"
- "What was updated today?"
- "Find blocked issues"
- "Show me recent issues"

### 3. Direct JQL Queries

- `project = MYPROJ AND status = Open`
- `assignee = currentUser() AND status != Done`
- `priority = Critical OR priority = High`
- `created >= -7d`
- `type = Epic`

### 4. Metadata Queries

- List all projects
- Show available query patterns
- Test connection status

## 🔧 Troubleshooting

### Common Issues

1. **Environment Variables Not Set**
   - Ensure `.env` file exists with correct JIRA credentials
   - Check environment variables are loaded: `env | grep JIRA`

2. **JIRA Connection Failed**
   - Verify JIRA URL is correct
   - Check API token is valid
   - Test with: `uv run jira-mcp-server test-connection`

3. **MCP Client Can't Find Server**
   - Check file paths in configuration
   - Ensure `uv` is in PATH
   - Verify working directory is correct

4. **Permission Issues**
   - Ensure scripts are executable: `chmod +x test_mcp_client.py`
   - Check file permissions for configuration

### Debug Mode

Run with debug logging:

```bash
# Enable debug logging
export MCP_LOG_LEVEL=DEBUG
uv run jira-mcp-server stdio
```

## 📊 Monitoring and Logs

### View Logs

Server logs will show in stderr when running in STDIO mode. For Claude Desktop, check:

**macOS**: `~/Library/Logs/Claude/mcp-server-jira.log`
**Windows**: `%LOCALAPPDATA%/Claude/logs/mcp-server-jira.log`

### Performance Testing

```bash
# Test with multiple concurrent requests
for i in {1..5}; do
  echo "Testing request $i"
  # Your test commands here
done
```

## 🎉 Success Indicators

You'll know everything is working when:

1. ✅ `test-connection` command succeeds
2. ✅ Knowledge store validation passes
3. ✅ MCP client can list all 5 tools
4. ✅ Natural language queries return JIRA results
5. ✅ Direct JQL execution works
6. ✅ No errors in client or server logs

## 🚀 Next Steps

Once testing is successful:

1. **Production Deployment**: Configure for your production JIRA instance
2. **Team Rollout**: Share configuration with team members
3. **Custom Queries**: Add your own patterns to `knowledge_store.yaml`
4. **Integration**: Connect with CI/CD, monitoring, etc.

Happy testing! 🎯
