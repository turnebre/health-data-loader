#!/bin/bash
# Wrapper script for Health Data MCP Server
# This ensures the virtual environment is activated and dependencies are available

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Change to the project directory
cd "$SCRIPT_DIR"

# Activate the virtual environment
source venv/bin/activate

# Run the MCP server with all arguments passed through
exec python mcp_health_server.py "$@"