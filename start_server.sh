#!/bin/bash

# Job Search Automation MCP Server Startup Script
# This script starts both the MCP server and the web dashboard

echo "🚀 Starting Job Search Automation System..."
echo "================================================"

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or later."
    exit 1
fi

# Check if in correct directory
if [ ! -f "mcp_server/job_search_server.py" ]; then
    echo "❌ Please run this script from the Job_Search directory"
    exit 1
fi

# Install dependencies if needed
echo "📦 Checking dependencies..."
pip3 install -q sqlite3 aiohttp 2>/dev/null

# Check if MCP SDK is installed
if ! python3 -c "import mcp" 2>/dev/null; then
    echo "⚠️  MCP SDK not installed. Running in fallback mode."
    echo "   To install MCP SDK: pip install mcp"
    FALLBACK_MODE=true
else
    FALLBACK_MODE=false
fi

# Start the MCP server in background
echo ""
echo "🔧 Starting MCP Server..."
python3 mcp_server/job_search_server.py > logs/mcp_server.log 2>&1 &
MCP_PID=$!
echo "   MCP Server PID: $MCP_PID"

# Start a simple HTTP server for the dashboard
echo ""
echo "🌐 Starting Web Dashboard..."
cd web_dashboard
python3 -m http.server 8080 > ../logs/dashboard.log 2>&1 &
DASH_PID=$!
cd ..
echo "   Dashboard PID: $DASH_PID"

# Save PIDs for shutdown
echo $MCP_PID > .server_pids
echo $DASH_PID >> .server_pids

# Wait for services to start
sleep 2

# Display success message
echo ""
echo "✅ Job Search Automation System Started!"
echo "================================================"
echo ""
echo "📊 Dashboard URL: http://localhost:8080"
echo "🔧 MCP Server: localhost:5000"
if [ "$FALLBACK_MODE" = true ]; then
    echo "⚠️  Running in fallback mode (MCP SDK not installed)"
fi
echo ""
echo "📝 Available Tools:"
echo "   • generate_application - Create tailored application packages"
echo "   • search_jobs - Search across multiple platforms"
echo "   • analyze_job_fit - Analyze job compatibility"
echo "   • track_application - Update application status"
echo "   • get_analytics - View job search metrics"
echo "   • bulk_apply - Generate multiple applications"
echo ""
echo "To stop the server, run: ./stop_server.sh"
echo ""
echo "Logs available at:"
echo "   • MCP Server: logs/mcp_server.log"
echo "   • Dashboard: logs/dashboard.log"
echo ""