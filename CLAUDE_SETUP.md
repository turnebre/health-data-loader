# Claude Desktop Setup Instructions

## 🚨 Fix for "spawn python ENOENT" Error

The error you're seeing happens because Claude Desktop can't find the `python` command. Here are **3 solutions** (try them in order):

## Solution 1: Use the Wrapper Script (Recommended)

**Copy this configuration to your Claude Desktop config:**

```json
{
  "mcpServers": {
    "health-data": {
      "command": "/Users/brendanturner/Projects/health-data-loader/run_mcp_server.sh",
      "args": [
        "--db-path",
        "/Users/brendanturner/Projects/health-data-loader/health_data.duckdb"
      ],
      "env": {}
    }
  }
}
```

## Solution 2: Direct Python Path

**If Solution 1 doesn't work, try this:**

```json
{
  "mcpServers": {
    "health-data": {
      "command": "/Users/brendanturner/.pyenv/shims/python",
      "args": [
        "/Users/brendanturner/Projects/health-data-loader/mcp_health_server.py",
        "--db-path",
        "/Users/brendanturner/Projects/health-data-loader/health_data.duckdb"
      ],
      "env": {
        "PYTHONPATH": "/Users/brendanturner/Projects/health-data-loader"
      }
    }
  }
}
```

## Solution 3: System Python

**If you have Python installed via Homebrew or system Python:**

```json
{
  "mcpServers": {
    "health-data": {
      "command": "/usr/bin/python3",
      "args": [
        "/Users/brendanturner/Projects/health-data-loader/mcp_health_server.py",
        "--db-path",
        "/Users/brendanturner/Projects/health-data-loader/health_data.duckdb"
      ],
      "env": {
        "PYTHONPATH": "/Users/brendanturner/Projects/health-data-loader"
      }
    }
  }
}
```

## 📍 Configuration File Location

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

**If the file doesn't exist, create it with one of the configurations above.**

## 🧪 Test Your Configuration

1. **Save the configuration** to the Claude Desktop config file
2. **Restart Claude Desktop**
3. **Test with a simple query:** "What medications am I taking?"

## 📋 Pre-generated Configuration Files

I've created these files for you:
- `claude_desktop_config_fixed.json` (Solution 1 - Recommended)
- `claude_desktop_config_alternative.json` (Solution 2)
- `run_mcp_server.sh` (Wrapper script)

**Quick setup:**
```bash
# Copy the recommended configuration
cp claude_desktop_config_fixed.json ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

## 🔍 Troubleshooting

**If you still get errors:**

1. **Check the Claude Desktop logs** for more specific error messages
2. **Verify Python path:**
   ```bash
   which python
   which python3
   ```
3. **Test the server manually:**
   ```bash
   ./run_mcp_server.sh --help
   ```
4. **Check dependencies:**
   ```bash
   python -c "import mcp, duckdb; print('OK')"
   ```

## ✅ Success Indicators

When it works, you'll see:
- No error messages in Claude Desktop logs
- Claude can answer health-related questions
- Server shows as connected in Claude Desktop

## 💬 Example Queries to Test

Once connected, try these:
- "What medications am I currently taking?"
- "Show me my recent lab results"
- "Give me a health summary"
- "What's my latest blood pressure reading?"