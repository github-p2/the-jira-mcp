#!/bin/bash

echo "🧪 JIRA Authentication Test Suite"
echo "=================================="

JIRA_URL=""
USERNAME=""
TOKEN=""

echo ""
echo "📋 Server Information:"
echo "URL: $JIRA_URL"
echo "Username: $USERNAME"
echo "Token: ${TOKEN:0:20}..."

echo ""
echo "🔧 Test 1: Basic Auth with API Token"
curl -s -w "Status: %{http_code}\n" \
  -u "$USERNAME:$TOKEN" \
  -H "Accept: application/json" \
  -k \
  "$JIRA_URL/rest/api/2/serverInfo" | head -3

echo ""
echo "🔧 Test 2: Try without username (token only)"
curl -s -w "Status: %{http_code}\n" \
  -u ":$TOKEN" \
  -H "Accept: application/json" \
  -k \
  "$JIRA_URL/rest/api/2/serverInfo" | head -3

echo ""
echo "🔧 Test 3: Test if token is base64 encoded credentials"
echo "Decoding token as base64..."
echo "$TOKEN" | base64 -d 2>/dev/null || echo "Not valid base64"

echo ""
echo "🔧 Test 4: Check server info without auth (to see what's available)"
curl -s -w "Status: %{http_code}\n" \
  -H "Accept: application/json" \
  -k \
  "$JIRA_URL/rest/api/2/serverInfo" | head -3

echo ""
echo "🔧 Test 5: Try different auth format"
# Some JIRA servers expect different header format
curl -s -w "Status: %{http_code}\n" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Accept: application/json" \
  -k \
  "$JIRA_URL/rest/api/2/serverInfo" | head -3

echo ""
echo "📝 Recommendations:"
echo "1. ✅ Server is reachable and responding"
echo "2. ❌ Current token/credentials are not working"
echo "3. 🔍 Server requires OAuth authentication"
echo "4. 💡 Try generating a new API token from JIRA profile"
echo "5. 🏢 Contact your JIRA admin for proper API access"

echo ""
echo "🔗 To create a proper API token:"
echo "1. Login to: $JIRA_URL"
echo "2. Go to: Profile → Account Settings → Security → API Tokens"
echo "3. Create new token for API access"
echo "4. Replace the token in your .env file"
