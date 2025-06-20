#!/usr/bin/env python3
"""
Complete test suite for Health Data MCP Server
Run this to verify your server is working correctly before using with Claude Desktop.
"""

import asyncio
import json
import sys
import os
from pathlib import Path

def check_prerequisites():
    """Check that all prerequisites are met."""
    print("🔍 Checking Prerequisites...")
    
    # Check database exists
    if not os.path.exists("health_data.duckdb"):
        print("❌ Health database not found at health_data.duckdb")
        print("   Create it with: python health_pipeline.py your_health_data.xml")
        return False
    
    # Check dependencies
    try:
        import mcp
        import duckdb
        print("✅ All dependencies available")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("   Install with: pip install mcp duckdb")
        return False
    
    # Check server files exist
    required_files = ["mcp_health_server.py", "health_queries.py"]
    for file in required_files:
        if not os.path.exists(file):
            print(f"❌ Required file missing: {file}")
            return False
    
    print("✅ All prerequisites met")
    return True

async def test_core_functionality():
    """Test core MCP server functionality."""
    print("\n🧪 Testing Core Functionality...")
    
    sys.path.append('.')
    from mcp_health_server import HealthDataServer
    
    server = HealthDataServer('health_data.duckdb')
    await server._connect_db()
    
    tests = {
        "Database Connection": lambda: server._connect_db(),
        "Medications Query": lambda: server._get_medications(limit=3),
        "Lab Results Query": lambda: server.query_engine.get_lab_results(limit=3),
        "Health Summary": lambda: server.query_engine.get_health_summary(include_trends=False),
        "Database Schema": lambda: server._get_database_schema(),
        "Search Functionality": lambda: server._search_health_data("test", ["medications"]),
        "Timeline Query": lambda: server._get_health_timeline(event_types=["medications"])
    }
    
    results = {}
    for test_name, test_func in tests.items():
        try:
            result = await test_func()
            if result is not None:
                results[test_name] = "✅ PASS"
            else:
                results[test_name] = "❌ FAIL - No result"
        except Exception as e:
            results[test_name] = f"❌ FAIL - {str(e)[:50]}..."
    
    # Print results
    for test_name, status in results.items():
        print(f"  {status} {test_name}")
    
    passed = sum(1 for status in results.values() if "✅" in status)
    total = len(results)
    
    return passed, total

def test_server_startup():
    """Test that the server can start properly."""
    print("\n🚀 Testing Server Startup...")
    
    import subprocess
    import time
    
    try:
        # Start server in background
        process = subprocess.Popen(
            ["python", "mcp_health_server.py", "--db-path", "health_data.duckdb"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Let it run for 2 seconds
        time.sleep(2)
        
        # Check if it's still running (good sign)
        if process.poll() is None:
            print("✅ Server started successfully")
            process.terminate()
            process.wait(timeout=5)
            return True
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Server failed to start")
            if stderr:
                print(f"   Error: {stderr[:100]}...")
            return False
            
    except Exception as e:
        print(f"❌ Startup test failed: {e}")
        return False

def show_integration_instructions():
    """Show how to integrate with Claude Desktop."""
    print("\n📱 Claude Desktop Integration")
    print("=" * 40)
    
    config_path = Path.home() / "Library/Application Support/Claude/claude_desktop_config.json"
    
    print(f"1. Open your Claude Desktop configuration file:")
    print(f"   📁 {config_path}")
    print(f"   (Create the file if it doesn't exist)")
    
    print(f"\n2. Add this configuration:")
    
    with open("claude_desktop_config.json", "r") as f:
        config = f.read()
    print(f"   {config}")
    
    print(f"\n3. Restart Claude Desktop")
    
    print(f"\n4. Test with these example queries:")
    example_queries = [
        "What medications am I currently taking?",
        "Show me my recent lab results with any abnormal values",
        "Give me a comprehensive health summary",
        "What are my cholesterol trends over time?",
        "Search for any diabetes-related data",
        "Show me my health timeline for the past year"
    ]
    
    for i, query in enumerate(example_queries, 1):
        print(f"   {i}. \"{query}\"")

async def main():
    """Run complete test suite."""
    print("🏥 Health Data MCP Server - Complete Test Suite")
    print("=" * 55)
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites not met. Please fix issues above.")
        sys.exit(1)
    
    # Test core functionality
    passed, total = await test_core_functionality()
    
    # Test server startup
    startup_ok = test_server_startup()
    
    # Summary
    print(f"\n📊 Test Summary")
    print(f"   Core Functionality: {passed}/{total} tests passed")
    print(f"   Server Startup: {'✅ OK' if startup_ok else '❌ Failed'}")
    
    if passed == total and startup_ok:
        print(f"\n🎉 ALL TESTS PASSED!")
        print(f"Your Health Data MCP Server is ready for use.")
        show_integration_instructions()
    else:
        print(f"\n⚠️  Some tests failed. Please check the errors above.")
        print(f"The server may still work, but some features might have issues.")

if __name__ == "__main__":
    asyncio.run(main())