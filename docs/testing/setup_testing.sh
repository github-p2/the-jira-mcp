#!/bin/bash
# Setup script for testing JIRA MCP Server

echo "🚀 JIRA MCP Server Testing Setup"
echo "================================"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cat > .env << 'EOF'
# JIRA Configuration - Fill in your values
JIRA_URL=https://your-company.atlassian.net
JIRA_TOKEN=your-api-token-here
JIRA_USERNAME=your-email@company.com

# MCP Server Configuration (Optional)
MCP_KNOWLEDGE_STORE_PATH=knowledge_store.yaml
MCP_LOG_LEVEL=INFO
MCP_MAX_RESULTS=100
EOF
    echo "✅ Created .env file. Please edit it with your JIRA credentials."
    echo ""
else
    echo "✅ .env file already exists."
fi

# Check if uv is available
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Please install it first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "🔧 Installing dependencies..."
uv sync --extra dev

echo ""
echo "📋 Testing Steps:"
echo "1. Edit .env file with your JIRA credentials"
echo "2. Get JIRA API token: https://id.atlassian.com/manage-profile/security/api-tokens"
echo "3. Test connection: uv run jira-mcp-server test-connection"
echo "4. Run test client: python3 test_mcp_client.py"
echo "5. Configure MCP client (see MCP_CLIENT_TESTING.md)"

echo ""
echo "🎯 Quick Test Commands:"
echo "  uv run jira-mcp-server test-connection"
echo "  uv run jira-mcp-server validate-knowledge-store"
echo "  python3 test_mcp_client.py"

echo ""
echo "📚 Documentation:"
echo "  - MCP_CLIENT_TESTING.md - Detailed client setup"
echo "  - JIRA_MCP_USAGE.md - Usage examples"
echo "  - README.md - Full documentation"
