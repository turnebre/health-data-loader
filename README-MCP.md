# Health Data MCP Server

A custom Model Context Protocol (MCP) server that provides intelligent access to personal health data stored in DuckDB. This server understands medical terminology and provides context-aware tools for querying and analyzing health information.

## 🎯 Why This MCP Server?

Generic database MCP servers like MotherDuck's server lack medical domain knowledge and often generate invalid SQL queries when working with health data. This custom server solves that problem by:

- **Understanding Medical Data**: Knows about medications, lab results, vital signs, and medical conditions
- **Intelligent Queries**: Converts natural language questions into proper medical data queries  
- **Context-Aware Results**: Provides medically relevant interpretations and trend analysis
- **Safe Operations**: Validates queries and prevents errors common with generic SQL servers

## 🚀 Quick Start

### Prerequisites

1. **Health Database**: You need a DuckDB database with health data. Use the [Health Data Pipeline](README.md) to create one from C-CDA XML files.

2. **MCP SDK**: Install the MCP SDK for Python:
   ```bash
   pip install mcp
   ```

### Installation

1. **Clone or Download**: Get this repository
   ```bash
   git clone <your-repo-url>
   cd health-data-loader
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements-mcp.txt
   ```

3. **Test the Server**:
   ```bash
   python mcp_health_server.py --db-path /path/to/your/health_data.duckdb
   ```

### Usage with Claude Desktop

Add this server to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "health-data": {
      "command": "python",
      "args": ["/path/to/health-data-loader/mcp_health_server.py", "--db-path", "/Users/Shared/health_data.duckdb"],
      "env": {}
    }
  }
}
```

**Configuration File Locations:**
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

## 🔧 Available Tools

The MCP server provides these intelligent health data tools:

### Core Data Access

- **`get_medications`**: Get medication information with status filtering
- **`get_lab_results`**: Get lab results with trend analysis and abnormal value detection
- **`get_vitals`**: Get vital signs with medical interpretation (BP categories, BMI analysis)
- **`get_conditions`**: Get medical conditions and diagnoses with duration calculations

### Advanced Analytics

- **`get_health_summary`**: Comprehensive health overview with key metrics and alerts
- **`search_health_data`**: Natural language search across all health data types
- **`analyze_trends`**: Statistical trend analysis for lab values and vital signs
- **`get_health_timeline`**: Chronological timeline of health events

### Resources

- **Database Schema**: Complete description of health database structure
- **Data Summary**: High-level overview of available health data

## 📋 Example Queries

Once connected to Claude Desktop, you can ask natural language questions:

### Medication Questions
- "What medications am I currently taking?"
- "Show me my blood pressure medications from the last year"
- "When did I start taking metformin?"

### Lab Results Analysis  
- "What are my recent cholesterol trends?"
- "Show me all abnormal lab results from this year"
- "How has my A1C changed over time?"

### Vital Signs Monitoring
- "What's my latest blood pressure reading?"
- "Show me my weight trends over the past 6 months" 
- "How has my BMI changed?"

### Health Overview
- "Give me a comprehensive health summary"
- "What health alerts do I have?"
- "Show me my health timeline for 2023"

### Medical History
- "What chronic conditions do I have?"
- "When was I diagnosed with diabetes?"
- "Show me all my immunizations"

## 🏥 Medical Domain Intelligence

This server includes medical domain knowledge for:

### Blood Pressure Categories
- Normal: <120/<80
- Elevated: 120-129/<80  
- Stage 1 Hypertension: 130-139/80-89
- Stage 2 Hypertension: ≥140/≥90
- Hypertensive Crisis: ≥180/≥120

### BMI Classifications
- Underweight: <18.5
- Normal: 18.5-24.9
- Overweight: 25-29.9
- Obese: ≥30

### Lab Result Analysis
- Automatic abnormal value detection
- Trend analysis with statistical calculations
- Reference range interpretation
- Historical comparisons

### Medical Terminology
- Understands common medication names
- Recognizes medical condition patterns
- Interprets medical codes (ICD-10, LOINC, CPT)

## 🔒 Privacy & Security

- **Local Processing**: All data stays on your computer
- **No External Calls**: Server only accesses your local DuckDB database
- **Read-Only Access**: Server cannot modify your health data
- **Secure Queries**: Input validation prevents SQL injection

## 🛠️ Technical Details

### Database Schema Support

The server works with health databases containing these tables:

- `medications` - Current and historical medications
- `results` - Laboratory test results  
- `vitals` - Vital signs measurements
- `problems` - Medical conditions/diagnoses
- `procedures` - Medical procedures performed
- `immunizations` - Vaccination history
- `allergies` - Known allergies and reactions
- `encounters` - Healthcare visits

### Query Optimization

- Efficient SQL query generation
- Automatic result limiting to prevent performance issues
- Smart filtering based on medical relevance
- Caching for frequently accessed data summaries

### Error Handling

- Validates all input parameters
- Provides helpful error messages
- Graceful handling of missing data
- Automatic recovery from connection issues

## 🔧 Development

### Running in Development Mode

```bash
# Install development dependencies
pip install -e .[dev]

# Run with debug logging
python mcp_health_server.py --db-path /path/to/test_data.duckdb
```

### Testing

```bash
# Run tests (when available)
pytest tests/

# Type checking
mypy mcp_health_server.py health_queries.py

# Code formatting
black mcp_health_server.py health_queries.py
isort mcp_health_server.py health_queries.py
```

### Extending the Server

To add new tools:

1. Add the tool definition in `setup_handlers()` method
2. Implement the tool logic in `handle_call_tool()`
3. Add any complex query logic to `health_queries.py`
4. Update the documentation

## 📝 Troubleshooting

### Common Issues

**"Health database not found"**
- Verify the database file path is correct
- Ensure the database was created using the health data pipeline
- Check file permissions

**"No data found matching criteria"**
- Your database might not contain the requested data type
- Try broader search terms
- Check the database summary resource for available data

**"MCP connection failed"**
- Ensure Claude Desktop configuration is correct
- Check that Python and dependencies are properly installed
- Verify the server script path in the configuration

### Getting Help

1. Check the logs in Claude Desktop for error messages
2. Test the server manually: `python mcp_health_server.py --help`
3. Verify your health database has data: use the original pipeline's summary feature
4. Review the [MCP documentation](https://docs.anthropic.com/en/docs/build-with-claude/mcp) for general MCP issues

## 📊 Comparison with Generic MCP Servers

| Feature | Generic SQL MCP | Health Data MCP |
|---------|----------------|-----------------|
| Medical terminology | ❌ | ✅ |
| Domain-aware queries | ❌ | ✅ |
| Health data validation | ❌ | ✅ |
| Medical interpretations | ❌ | ✅ |
| Trend analysis | ❌ | ✅ |
| Error prevention | ❌ | ✅ |
| Natural language search | ❌ | ✅ |

## 🤝 Contributing

Contributions welcome! Areas for improvement:

- Additional medical domain knowledge
- More sophisticated trend analysis algorithms  
- Support for additional health data formats
- Performance optimizations
- Test coverage improvements

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Disclaimer**: This tool is for personal health data management and analysis. Always consult healthcare professionals for medical decisions. Ensure compliance with relevant privacy regulations when handling health data.