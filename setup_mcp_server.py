#!/usr/bin/env python3
"""
Setup script for Health Data MCP Server

This script helps you set up and test the MCP server with your health data.
"""

import asyncio
import json
import os
import sys
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed."""
    print("🔍 Checking dependencies...")
    
    missing_deps = []
    
    try:
        import mcp
        print("  ✅ MCP library found")
    except ImportError:
        missing_deps.append("mcp")
        print("  ❌ MCP library missing")
    
    try:
        import duckdb
        print("  ✅ DuckDB library found")
    except ImportError:
        missing_deps.append("duckdb")
        print("  ❌ DuckDB library missing")
    
    if missing_deps:
        print(f"\n❌ Missing dependencies: {', '.join(missing_deps)}")
        print("Install with: pip install " + " ".join(missing_deps))
        return False
    
    print("  ✅ All dependencies available")
    return True

def find_health_database():
    """Find the health database file."""
    print("\n🔍 Looking for health database...")
    
    possible_paths = [
        "health_data.duckdb",
        "/Users/Shared/health_data.duckdb",
        "data/health_data.duckdb"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"  ✅ Found database at: {path}")
            return path
    
    print("  ❌ No health database found")
    print("  Create one using: python health_pipeline.py your_health_data.xml")
    return None

async def test_mcp_server(db_path):
    """Test the MCP server functionality."""
    print(f"\n🧪 Testing MCP server with database: {db_path}")
    
    try:
        # Import the server
        from mcp_health_server import HealthDataServer
        
        # Create server instance
        server = HealthDataServer(db_path)
        await server._connect_db()
        print("  ✅ Server connection successful")
        
        # Test medications query
        result = await server._get_medications(limit=3)
        med_data = json.loads(result)
        print(f"  ✅ Medications test: Found {med_data['total_found']} medications")
        
        # Test lab results query
        result = await server.query_engine.get_lab_results(limit=3)
        lab_data = json.loads(result)
        print(f"  ✅ Lab results test: Found {lab_data['total_found']} results")
        
        # Test health summary
        result = await server.query_engine.get_health_summary()
        summary_data = json.loads(result)
        print(f"  ✅ Health summary test: Generated summary with {len(summary_data)} sections")
        
        # Test database schema
        schema = await server._get_database_schema()
        schema_data = json.loads(schema)
        print(f"  ✅ Schema test: Found {len(schema_data['tables'])} tables")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Server test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def generate_claude_config(db_path):
    """Generate Claude Desktop configuration."""
    print("\n📝 Generating Claude Desktop configuration...")
    
    script_path = os.path.abspath("mcp_health_server.py")
    
    config = {
        "mcpServers": {
            "health-data": {
                "command": "python",
                "args": [script_path, "--db-path", db_path],
                "env": {}
            }
        }
    }
    
    print("Add this to your Claude Desktop configuration:")
    print("📍 Config file locations:")
    print("  macOS: ~/Library/Application Support/Claude/claude_desktop_config.json")
    print("  Windows: %APPDATA%/Claude/claude_desktop_config.json")
    print("\n📋 Configuration to add:")
    print(json.dumps(config, indent=2))
    
    # Save to file
    with open("claude_desktop_config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print(f"\n💾 Configuration saved to: claude_desktop_config.json")

def print_usage_examples():
    """Print example queries for the MCP server."""
    print("\n💬 Example queries you can ask Claude:")
    
    examples = [
        "Medication Management:",
        "  • What medications am I currently taking?",
        "  • Show me my blood pressure medications",
        "  • When did I start taking metformin?",
        "",
        "Lab Results Analysis:",
        "  • What are my recent cholesterol trends?",
        "  • Show me all abnormal lab results",
        "  • How has my A1C changed over time?",
        "",
        "Vital Signs:",
        "  • What's my latest blood pressure reading?",
        "  • Show me my weight trends",
        "  • How has my BMI changed?",
        "",
        "Health Overview:",
        "  • Give me a comprehensive health summary",
        "  • What health alerts do I have?",
        "  • Show me my health timeline for 2023",
        "",
        "Search & Analysis:",
        "  • Search for diabetes-related data",
        "  • Analyze trends in my cholesterol levels",
        "  • Show me my vaccination history"
    ]
    
    for example in examples:
        print(example)

async def main():
    """Main setup function."""
    print("🏥 Health Data MCP Server Setup")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Please install missing dependencies and try again.")
        sys.exit(1)
    
    # Find database
    db_path = find_health_database()
    if not db_path:
        print("\n❌ Please create a health database first using the health pipeline.")
        sys.exit(1)
    
    # Test server
    success = await test_mcp_server(db_path)
    if not success:
        print("\n❌ Server testing failed. Please check the error messages above.")
        sys.exit(1)
    
    # Generate configuration
    generate_claude_config(db_path)
    
    # Show usage examples
    print_usage_examples()
    
    print("\n🎉 Setup complete! Your Health Data MCP Server is ready to use.")
    print("\n📝 Next steps:")
    print("1. Copy the configuration to your Claude Desktop config file")
    print("2. Restart Claude Desktop")
    print("3. Start asking questions about your health data!")

if __name__ == "__main__":
    asyncio.run(main())