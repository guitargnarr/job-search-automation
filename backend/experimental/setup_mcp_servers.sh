#!/bin/bash

# Setup MCP Servers for Job Search Automation
# This script registers the MCP servers with Claude Code

echo "🚀 Setting up MCP Servers for Job Search Automation"
echo "=================================================="

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Claude is available
if ! command -v claude &> /dev/null; then
    echo -e "${RED}❌ Claude Code is not installed or not in PATH${NC}"
    exit 1
fi

echo -e "${BLUE}📦 Current Claude version:${NC}"
claude --version

# Set paths
PROJECT_DIR="/Users/matthewscott/Desktop/Job_Search"
MCP_DIR="${PROJECT_DIR}/backend/mcp"

# Check if MCP servers exist
echo -e "\n${BLUE}🔍 Checking MCP server files...${NC}"

servers=("job_search_server.py" "email_server.py" "document_server.py")
for server in "${servers[@]}"; do
    if [ -f "${MCP_DIR}/${server}" ]; then
        echo -e "${GREEN}✅ Found: ${server}${NC}"
    else
        echo -e "${RED}❌ Missing: ${server}${NC}"
        exit 1
    fi
done

# Make servers executable
echo -e "\n${BLUE}🔧 Making servers executable...${NC}"
chmod +x ${MCP_DIR}/*.py

# Test Python imports
echo -e "\n${BLUE}🐍 Testing Python environment...${NC}"
python3 -c "import mcp.server.fastmcp; print('✅ MCP SDK installed')" 2>/dev/null || {
    echo -e "${RED}❌ MCP SDK not installed. Run: pip install mcp${NC}"
    exit 1
}

python3 -c "import backend.core.database; print('✅ Job Search backend accessible')" 2>/dev/null || {
    echo -e "${YELLOW}⚠️  Backend modules not in PYTHONPATH${NC}"
    echo "Adding to PYTHONPATH..."
    export PYTHONPATH="${PROJECT_DIR}:${PYTHONPATH}"
}

# Register servers with Claude
echo -e "\n${BLUE}📝 Registering MCP servers with Claude...${NC}"

# Job Search Server
echo -e "\n${GREEN}1. Job Search Automation Server${NC}"
echo "   - Job discovery and tracking"
echo "   - ATS optimization"
echo "   - Application management"

# Note: Claude MCP registration would be done through the Claude desktop app
# This script prepares the environment and provides instructions

echo -e "\n${BLUE}📋 To register the servers with Claude:${NC}"
echo ""
echo "1. Open Claude Desktop settings"
echo "2. Navigate to the MCP Servers section"
echo "3. Add each server with these configurations:"
echo ""
echo -e "${YELLOW}Job Search Server:${NC}"
echo "   Name: job-search"
echo "   Command: python3"
echo "   Args: ${MCP_DIR}/job_search_server.py"
echo ""
echo -e "${YELLOW}Email Intelligence Server:${NC}"
echo "   Name: email-intel"
echo "   Command: python3"
echo "   Args: ${MCP_DIR}/email_server.py"
echo ""
echo -e "${YELLOW}Document Generation Server:${NC}"
echo "   Name: doc-gen"
echo "   Command: python3"
echo "   Args: ${MCP_DIR}/document_server.py"
echo ""

# Alternative: Update Claude config directly (if config location is known)
CLAUDE_CONFIG_DIR="$HOME/Library/Application Support/Claude"
if [ -d "$CLAUDE_CONFIG_DIR" ]; then
    echo -e "\n${BLUE}💾 Claude configuration directory found${NC}"
    echo "You can also copy the mcp_config.json to Claude's config directory"
    echo ""
    echo "To apply the configuration:"
    echo "cp ${PROJECT_DIR}/mcp_config.json \"${CLAUDE_CONFIG_DIR}/\""
else
    echo -e "\n${YELLOW}ℹ️  Claude config directory not found at expected location${NC}"
fi

echo -e "\n${GREEN}✨ Setup complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Register the servers in Claude Desktop (see instructions above)"
echo "2. Restart Claude to load the MCP servers"
echo "3. Test with: claude mcp list"
echo ""
echo "Usage examples:"
echo '  Claude: "Search for data analyst jobs in Louisville"'
echo '  Claude: "Scan my inbox for interview invitations"'
echo '  Claude: "Generate an optimized resume for job #5"'
echo ""
echo -e "${BLUE}📚 Documentation available at:${NC} ${PROJECT_DIR}/backend/mcp/README.md"