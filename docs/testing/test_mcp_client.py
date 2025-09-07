#!/usr/bin/env python3
"""Simple MCP client for testing JIRA MCP Server."""

import asyncio
import json
from pathlib import Path


async def test_mcp_server():
    """Test the JIRA MCP Server directly."""

    print("🚀 Starting JIRA MCP Server Test...")

    # Start the server process
    proc = await asyncio.create_subprocess_exec(
        "uv",
        "run",
        "jira-mcp-server",
        "stdio",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=Path(__file__).parent,
    )

    async def send_message(message):
        """Send a message to the MCP server."""
        json_msg = json.dumps(message)
        proc.stdin.write(f"{json_msg}\n".encode())
        await proc.stdin.drain()

        # Read response
        response_line = await proc.stdout.readline()
        if not response_line:
            return None
        return json.loads(response_line.decode().strip())

    try:
        # Test 1: List available tools
        print("\n🔧 Testing: List Tools")
        list_tools_msg = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {},
        }

        response = await send_message(list_tools_msg)
        if response and "result" in response:
            tools = response["result"].get("tools", [])
            print(f"✅ Found {len(tools)} tools:")
            for tool in tools:
                print(f"   - {tool['name']}: {tool['description']}")
        else:
            print("❌ Failed to get tools list")
            return

        # Test 2: Test JIRA connection
        print("\n🔗 Testing: JIRA Connection")
        test_connection_msg = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {"name": "test_connection", "arguments": {}},
        }

        response = await send_message(test_connection_msg)
        if response and "result" in response:
            result_text = response["result"].get("content", [{}])[0].get("text", "")
            print("✅ Connection test result:")
            print(f"   {result_text}")
        else:
            print("❌ Connection test failed")

        # Test 3: List knowledge queries
        print("\n📚 Testing: Knowledge Store")
        list_queries_msg = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {"name": "list_knowledge_queries", "arguments": {}},
        }

        response = await send_message(list_queries_msg)
        if response and "result" in response:
            result_text = response["result"].get("content", [{}])[0].get("text", "")
            print("✅ Knowledge store loaded:")
            # Show first 3 lines of the result
            lines = result_text.split("\n")[:5]
            for line in lines:
                if line.strip():
                    print(f"   {line}")
        else:
            print("❌ Failed to load knowledge store")

        # Test 4: Answer a question
        print("\n❓ Testing: Natural Language Query")
        answer_question_msg = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "answer_question",
                "arguments": {"question": "show me open bugs", "max_results": 3},
            },
        }

        response = await send_message(answer_question_msg)
        if response and "result" in response:
            result_text = response["result"].get("content", [{}])[0].get("text", "")
            print("✅ Natural language query executed:")
            # Show first few lines
            lines = result_text.split("\n")[:8]
            for line in lines:
                if line.strip():
                    print(f"   {line}")
        else:
            print("❌ Natural language query failed")

        # Test 5: List projects (if connection is working)
        print("\n🗂️  Testing: List Projects")
        list_projects_msg = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {"name": "list_projects", "arguments": {}},
        }

        response = await send_message(list_projects_msg)
        if response and "result" in response:
            result_text = response["result"].get("content", [{}])[0].get("text", "")
            print("✅ Projects retrieved:")
            # Show first few projects
            lines = result_text.split("\n")[:6]
            for line in lines:
                if line.strip():
                    print(f"   {line}")
        else:
            print("❌ Failed to list projects")

        print("\n🎉 All tests completed!")
        print("\n📋 Next Steps:")
        print("1. If connection test passed, your JIRA integration is working!")
        print("2. Configure Claude Desktop or Cursor with the MCP server")
        print("3. Try natural language queries in your MCP client")
        print("4. See MCP_CLIENT_TESTING.md for detailed setup instructions")

    except Exception as e:
        print(f"❌ Error during testing: {e}")
        # Check if server process had any stderr output
        try:
            stderr_output = await asyncio.wait_for(proc.stderr.read(), timeout=1.0)
            if stderr_output:
                print(f"📝 Server stderr: {stderr_output.decode()}")
        except asyncio.TimeoutError:
            pass
    finally:
        proc.terminate()
        await proc.wait()


if __name__ == "__main__":
    print("🧪 JIRA MCP Server Test Client")
    print("=" * 50)
    print("This script tests your JIRA MCP Server implementation.")
    print("Make sure you have set up your JIRA credentials in environment variables.")
    print("")

    # Check if environment variables are set
    import os

    if not os.getenv("JIRA_URL"):
        print("⚠️  Warning: JIRA_URL environment variable not set")
        print("   Please set your JIRA credentials before running tests:")
        print("   export JIRA_URL=https://your-company.atlassian.net")
        print("   export JIRA_TOKEN=your-api-token")
        print("")

    asyncio.run(test_mcp_server())
