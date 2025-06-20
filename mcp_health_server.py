#!/usr/bin/env python3
"""
Health Data MCP Server

A custom MCP server that provides intelligent access to personal health data
stored in DuckDB. This server understands the medical domain and provides
context-aware tools for querying health information.
"""

import asyncio
import json
import logging
from datetime import datetime, date
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

import duckdb
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)
import mcp.types as types
from health_queries import HealthQueryEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("health-mcp-server")

class HealthDataServer:
    """Main health data MCP server class."""
    
    def __init__(self, db_path: str = "/Users/Shared/health_data.duckdb"):
        self.db_path = Path(db_path)
        self.conn = None
        self.query_engine = None
        self.server = Server("health-data-server")
        self.setup_handlers()
    
    def setup_handlers(self):
        """Set up all MCP server handlers."""
        
        @self.server.list_resources()
        async def handle_list_resources() -> list[Resource]:
            """List available health data resources."""
            return [
                Resource(
                    uri="health://database/schema",
                    name="Health Database Schema",
                    description="Complete schema of the health database including all tables and relationships",
                    mimeType="application/json",
                ),
                Resource(
                    uri="health://database/summary",
                    name="Health Data Summary",
                    description="High-level summary of all health data including record counts and date ranges",
                    mimeType="application/json",
                ),
            ]
        
        @self.server.read_resource()
        async def handle_read_resource(uri: str) -> str:
            """Read a specific health data resource."""
            if uri == "health://database/schema":
                return await self._get_database_schema()
            elif uri == "health://database/summary":
                return await self._get_database_summary()
            else:
                raise ValueError(f"Unknown resource: {uri}")
        
        @self.server.list_tools()
        async def handle_list_tools() -> list[Tool]:
            """List available health data tools."""
            return [
                Tool(
                    name="get_medications",
                    description="Get medication information with optional filters",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": "string",
                                "enum": ["active", "completed", "discontinued", "all"],
                                "description": "Filter by medication status"
                            },
                            "medication_name": {
                                "type": "string",
                                "description": "Search for specific medication name (partial match)"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Limit number of results (default: 50)"
                            }
                        }
                    }
                ),
                Tool(
                    name="get_lab_results",
                    description="Get lab results with optional filters and trend analysis",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "test_name": {
                                "type": "string",
                                "description": "Search for specific test name (partial match)"
                            },
                            "date_from": {
                                "type": "string",
                                "format": "date",
                                "description": "Start date for results (YYYY-MM-DD)"
                            },
                            "date_to": {
                                "type": "string",
                                "format": "date",
                                "description": "End date for results (YYYY-MM-DD)"
                            },
                            "abnormal_only": {
                                "type": "boolean",
                                "description": "Show only abnormal results"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Limit number of results (default: 100)"
                            }
                        }
                    }
                ),
                Tool(
                    name="get_vitals",
                    description="Get vital signs with trend analysis",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "date_from": {
                                "type": "string",
                                "format": "date",
                                "description": "Start date for vitals (YYYY-MM-DD)"
                            },
                            "date_to": {
                                "type": "string",
                                "format": "date",
                                "description": "End date for vitals (YYYY-MM-DD)"
                            },
                            "vital_type": {
                                "type": "string",
                                "enum": ["bp", "weight", "height", "bmi", "heart_rate", "temperature", "all"],
                                "description": "Specific vital sign type"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Limit number of results (default: 100)"
                            }
                        }
                    }
                ),
                Tool(
                    name="get_conditions",
                    description="Get current medical conditions and problems",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": "string",
                                "enum": ["active", "resolved", "all"],
                                "description": "Filter by condition status"
                            },
                            "condition_name": {
                                "type": "string",
                                "description": "Search for specific condition (partial match)"
                            }
                        }
                    }
                ),
                Tool(
                    name="get_health_summary",
                    description="Get comprehensive health summary with key metrics",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "include_trends": {
                                "type": "boolean",
                                "description": "Include trend analysis in summary"
                            }
                        }
                    }
                ),
                Tool(
                    name="search_health_data",
                    description="Search across all health data using natural language",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Natural language query about health data"
                            },
                            "data_types": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "enum": ["medications", "lab_results", "vitals", "conditions", "procedures", "immunizations"]
                                },
                                "description": "Limit search to specific data types"
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="analyze_trends",
                    description="Analyze trends in health metrics over time",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "metric_type": {
                                "type": "string",
                                "enum": ["lab_results", "vitals", "medications"],
                                "description": "Type of metric to analyze"
                            },
                            "metric_name": {
                                "type": "string",
                                "description": "Specific metric name to analyze"
                            },
                            "date_from": {
                                "type": "string",
                                "format": "date",
                                "description": "Start date for trend analysis"
                            },
                            "date_to": {
                                "type": "string",
                                "format": "date",
                                "description": "End date for trend analysis"
                            }
                        },
                        "required": ["metric_type", "metric_name"]
                    }
                ),
                Tool(
                    name="get_health_timeline",
                    description="Get chronological timeline of health events",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "date_from": {
                                "type": "string",
                                "format": "date",
                                "description": "Start date for timeline"
                            },
                            "date_to": {
                                "type": "string",
                                "format": "date",
                                "description": "End date for timeline"
                            },
                            "event_types": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "enum": ["medications", "procedures", "lab_results", "conditions", "immunizations"]
                                },
                                "description": "Types of events to include"
                            }
                        }
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
            """Handle tool calls."""
            try:
                await self._connect_db()
                
                if name == "get_medications":
                    result = await self._get_medications(**arguments)
                elif name == "get_lab_results":
                    result = await self.query_engine.get_lab_results(**arguments)
                elif name == "get_vitals":
                    result = await self.query_engine.get_vitals(**arguments)
                elif name == "get_conditions":
                    result = await self.query_engine.get_conditions(**arguments)
                elif name == "get_health_summary":
                    result = await self.query_engine.get_health_summary(**arguments)
                elif name == "search_health_data":
                    result = await self._search_health_data(**arguments)
                elif name == "analyze_trends":
                    result = await self._analyze_trends(**arguments)
                elif name == "get_health_timeline":
                    result = await self._get_health_timeline(**arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
                
                return [types.TextContent(type="text", text=result)]
            
            except Exception as e:
                logger.error(f"Error in tool {name}: {e}")
                return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    async def _connect_db(self):
        """Connect to the health database."""
        if self.conn is None:
            if not self.db_path.exists():
                raise FileNotFoundError(f"Health database not found at {self.db_path}")
            self.conn = duckdb.connect(str(self.db_path))
            self.query_engine = HealthQueryEngine(self.conn)
            logger.info(f"Connected to health database at {self.db_path}")
    
    async def _get_database_schema(self) -> str:
        """Get the complete database schema."""
        await self._connect_db()
        
        schema = {
            "tables": {},
            "description": "Personal health data extracted from C-CDA documents"
        }
        
        # Get all tables
        tables = self.conn.execute("SHOW TABLES").fetchall()
        
        for (table_name,) in tables:
            # Get table structure
            columns = self.conn.execute(f"DESCRIBE {table_name}").fetchall()
            schema["tables"][table_name] = {
                "columns": [{"name": col[0], "type": col[1]} for col in columns],
                "description": self._get_table_description(table_name)
            }
        
        return json.dumps(schema, indent=2)
    
    async def _get_database_summary(self) -> str:
        """Get high-level database summary."""
        await self._connect_db()
        
        summary = {
            "total_records": 0,
            "tables": {},
            "date_ranges": {},
            "generated_at": datetime.now().isoformat()
        }
        
        # Get record counts and date ranges for each table
        table_queries = {
            "medications": ("SELECT COUNT(*), MIN(start_date), MAX(start_date) FROM medications", "start_date"),
            "results": ("SELECT COUNT(*), MIN(test_date), MAX(test_date) FROM results", "test_date"),
            "vitals": ("SELECT COUNT(*), MIN(measurement_date), MAX(measurement_date) FROM vitals", "measurement_date"),
            "problems": ("SELECT COUNT(*), MIN(onset_date), MAX(onset_date) FROM problems", "onset_date"),
            "procedures": ("SELECT COUNT(*), MIN(procedure_date), MAX(procedure_date) FROM procedures", "procedure_date"),
            "immunizations": ("SELECT COUNT(*), MIN(administration_date), MAX(administration_date) FROM immunizations", "administration_date")
        }
        
        for table, (query, date_col) in table_queries.items():
            try:
                result = self.conn.execute(query).fetchone()
                count, min_date, max_date = result
                summary["tables"][table] = {
                    "record_count": count,
                    "date_range": {
                        "earliest": str(min_date) if min_date else None,
                        "latest": str(max_date) if max_date else None
                    }
                }
                summary["total_records"] += count
            except Exception as e:
                logger.warning(f"Could not get summary for table {table}: {e}")
        
        return json.dumps(summary, indent=2)
    
    def _get_table_description(self, table_name: str) -> str:
        """Get human-readable description of table purpose."""
        descriptions = {
            "medications": "Current and historical medications including dosages, prescribers, and status",
            "results": "Laboratory test results including values, reference ranges, and abnormal flags",
            "vitals": "Vital signs measurements including blood pressure, weight, height, and BMI",
            "problems": "Medical conditions and diagnoses with ICD-10 codes and status",
            "procedures": "Medical procedures performed with CPT codes and providers",
            "immunizations": "Vaccination history with dates and manufacturers",
            "allergies": "Known allergies and reactions with severity levels",
            "encounters": "Healthcare visits and encounters with providers",
            "social_history": "Social history including lifestyle factors",
            "family_history": "Family medical history and genetic predispositions",
            "medical_history": "Past medical history and resolved conditions",
            "care_plans": "Treatment goals and care plans"
        }
        return descriptions.get(table_name, f"Data table: {table_name}")
    
    async def _get_medications(self, status: str = "all", medication_name: str = None, limit: int = 50) -> str:
        """Get medication information."""
        await self._connect_db()
        
        query = "SELECT medication_name, dosage, frequency, status, start_date, end_date, prescriber FROM medications"
        params = []
        conditions = []
        
        if status != "all":
            conditions.append("LOWER(status) = ?")
            params.append(status.lower())
        
        if medication_name:
            conditions.append("LOWER(medication_name) LIKE ?")
            params.append(f"%{medication_name.lower()}%")
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY start_date DESC LIMIT ?"
        params.append(limit)
        
        results = self.conn.execute(query, params).fetchall()
        
        if not results:
            return "No medications found matching the criteria."
        
        # Format results
        medications = []
        for row in results:
            med = {
                "name": row[0],
                "dosage": row[1] or "Not specified",
                "frequency": row[2] or "Not specified",
                "status": row[3],
                "start_date": str(row[4]) if row[4] else None,
                "end_date": str(row[5]) if row[5] else None,
                "prescriber": row[6] or "Not specified"
            }
            medications.append(med)
        
        return json.dumps({
            "total_found": len(medications),
            "medications": medications
        }, indent=2)
    
    async def _search_health_data(self, query: str, data_types: List[str] = None) -> str:
        """Search across health data using natural language query."""
        await self._connect_db()
        
        search_results = {
            "query": query,
            "results": {},
            "total_matches": 0
        }
        
        # Define search targets based on data_types or default to all
        targets = data_types or ["medications", "lab_results", "conditions", "procedures"]
        
        query_lower = query.lower()
        
        # Search medications
        if "medications" in targets:
            med_results = self.conn.execute("""
                SELECT medication_name, status, start_date, prescriber
                FROM medications 
                WHERE LOWER(medication_name) LIKE ? OR LOWER(instructions) LIKE ?
                ORDER BY start_date DESC
                LIMIT 10
            """, [f"%{query_lower}%", f"%{query_lower}%"]).fetchall()
            
            if med_results:
                search_results["results"]["medications"] = [
                    {
                        "name": row[0],
                        "status": row[1],
                        "start_date": str(row[2]) if row[2] else None,
                        "prescriber": row[3]
                    }
                    for row in med_results
                ]
                search_results["total_matches"] += len(med_results)
        
        # Search lab results
        if "lab_results" in targets:
            lab_results = self.conn.execute("""
                SELECT test_name, test_date, result_value, unit, abnormal_flag
                FROM results 
                WHERE LOWER(test_name) LIKE ? 
                ORDER BY test_date DESC
                LIMIT 10
            """, [f"%{query_lower}%"]).fetchall()
            
            if lab_results:
                search_results["results"]["lab_results"] = [
                    {
                        "test": row[0],
                        "date": str(row[1]) if row[1] else None,
                        "value": row[2],
                        "unit": row[3],
                        "abnormal": row[4] != "Normal" if row[4] else False
                    }
                    for row in lab_results
                ]
                search_results["total_matches"] += len(lab_results)
        
        # Search conditions
        if "conditions" in targets:
            condition_results = self.conn.execute("""
                SELECT problem_name, status, onset_date, icd10_code
                FROM problems 
                WHERE LOWER(problem_name) LIKE ? OR LOWER(notes) LIKE ?
                ORDER BY onset_date DESC
                LIMIT 10
            """, [f"%{query_lower}%", f"%{query_lower}%"]).fetchall()
            
            if condition_results:
                search_results["results"]["conditions"] = [
                    {
                        "condition": row[0],
                        "status": row[1],
                        "onset_date": str(row[2]) if row[2] else None,
                        "icd10_code": row[3]
                    }
                    for row in condition_results
                ]
                search_results["total_matches"] += len(condition_results)
        
        if search_results["total_matches"] == 0:
            return f"No health data found matching '{query}'"
        
        return json.dumps(search_results, indent=2)
    
    async def _analyze_trends(self, metric_type: str, metric_name: str, 
                             date_from: str = None, date_to: str = None) -> str:
        """Analyze trends in health metrics over time."""
        await self._connect_db()
        
        if metric_type == "lab_results":
            query = """
                SELECT test_date, result_value, unit, reference_range
                FROM results 
                WHERE LOWER(test_name) LIKE ?
            """
            params = [f"%{metric_name.lower()}%"]
            
            if date_from:
                query += " AND test_date >= ?"
                params.append(date_from)
            if date_to:
                query += " AND test_date <= ?"
                params.append(date_to)
            
            query += " ORDER BY test_date ASC"
            
            results = self.conn.execute(query, params).fetchall()
            
            if not results:
                return f"No lab results found for {metric_name}"
            
            # Process numeric values for trend analysis
            data_points = []
            for row in results:
                try:
                    value_str = str(row[1]).strip()
                    if value_str and value_str.replace(".", "").replace("-", "").isdigit():
                        data_points.append({
                            "date": str(row[0]),
                            "value": float(value_str),
                            "unit": row[2] or "",
                            "reference_range": row[3] or ""
                        })
                except (ValueError, TypeError):
                    continue
            
            if len(data_points) < 2:
                return f"Insufficient numeric data for trend analysis of {metric_name}"
            
            # Calculate trend statistics
            values = [dp["value"] for dp in data_points]
            trend_analysis = {
                "metric": metric_name,
                "metric_type": "lab_result",
                "data_points": len(data_points),
                "date_range": {
                    "from": data_points[0]["date"],
                    "to": data_points[-1]["date"]
                },
                "statistics": {
                    "min": min(values),
                    "max": max(values),
                    "average": sum(values) / len(values),
                    "latest": values[-1],
                    "change": values[-1] - values[0],
                    "percent_change": ((values[-1] - values[0]) / values[0] * 100) if values[0] != 0 else 0
                },
                "trend": "increasing" if values[-1] > values[0] else "decreasing" if values[-1] < values[0] else "stable",
                "data": data_points
            }
            
            return json.dumps(trend_analysis, indent=2)
        
        elif metric_type == "vitals":
            # Handle vital signs trends
            vital_columns = {
                "blood_pressure": ["systolic_bp", "diastolic_bp"],
                "weight": ["weight_kg"],
                "bmi": ["bmi"],
                "heart_rate": ["heart_rate"]
            }
            
            metric_lower = metric_name.lower()
            columns = []
            
            for vital, cols in vital_columns.items():
                if vital in metric_lower:
                    columns = cols
                    break
            
            if not columns:
                return f"Unknown vital metric: {metric_name}"
            
            query = f"""
                SELECT measurement_date, {', '.join(columns)}
                FROM vitals 
                WHERE {' IS NOT NULL OR '.join(columns)} IS NOT NULL
            """
            
            params = []
            if date_from:
                query += " AND measurement_date >= ?"
                params.append(date_from)
            if date_to:
                query += " AND measurement_date <= ?"
                params.append(date_to)
            
            query += " ORDER BY measurement_date ASC"
            
            results = self.conn.execute(query, params).fetchall()
            
            if not results:
                return f"No vital signs data found for {metric_name}"
            
            # Process results for trend analysis
            data_points = []
            for row in results:
                point = {"date": str(row[0])}
                for i, col in enumerate(columns):
                    if row[i + 1] is not None:
                        point[col] = row[i + 1]
                
                if len(point) > 1:  # Has date and at least one value
                    data_points.append(point)
            
            return json.dumps({
                "metric": metric_name,
                "metric_type": "vital_signs",
                "data_points": len(data_points),
                "data": data_points
            }, indent=2)
        
        else:
            return f"Trend analysis not supported for metric type: {metric_type}"
    
    async def _get_health_timeline(self, date_from: str = None, date_to: str = None, 
                                  event_types: List[str] = None) -> str:
        """Get chronological timeline of health events."""
        await self._connect_db()
        
        timeline_events = []
        
        # Default to all event types if none specified
        if not event_types:
            event_types = ["medications", "procedures", "lab_results", "conditions", "immunizations"]
        
        # Collect events from different tables
        if "medications" in event_types:
            med_query = """
                SELECT 'medication' as event_type, medication_name as description, 
                       start_date as event_date, status, prescriber as provider
                FROM medications 
                WHERE start_date IS NOT NULL
            """
            params = []
            if date_from:
                med_query += " AND start_date >= ?"
                params.append(date_from)
            if date_to:
                med_query += " AND start_date <= ?"
                params.append(date_to)
            
            med_results = self.conn.execute(med_query, params).fetchall()
            for row in med_results:
                timeline_events.append({
                    "type": row[0],
                    "description": f"Started {row[1]}",
                    "date": str(row[2]),
                    "status": row[3],
                    "provider": row[4]
                })
        
        if "procedures" in event_types:
            proc_query = """
                SELECT 'procedure' as event_type, procedure_name as description,
                       procedure_date as event_date, status, provider
                FROM procedures 
                WHERE procedure_date IS NOT NULL
            """
            params = []
            if date_from:
                proc_query += " AND procedure_date >= ?"
                params.append(date_from)
            if date_to:
                proc_query += " AND procedure_date <= ?"
                params.append(date_to)
            
            proc_results = self.conn.execute(proc_query, params).fetchall()
            for row in proc_results:
                timeline_events.append({
                    "type": row[0],
                    "description": row[1],
                    "date": str(row[2]),
                    "status": row[3],
                    "provider": row[4]
                })
        
        if "conditions" in event_types:
            cond_query = """
                SELECT 'condition' as event_type, problem_name as description,
                       onset_date as event_date, status, NULL as provider
                FROM problems 
                WHERE onset_date IS NOT NULL
            """
            params = []
            if date_from:
                cond_query += " AND onset_date >= ?"
                params.append(date_from)
            if date_to:
                cond_query += " AND onset_date <= ?"
                params.append(date_to)
            
            cond_results = self.conn.execute(cond_query, params).fetchall()
            for row in cond_results:
                timeline_events.append({
                    "type": row[0],
                    "description": f"Diagnosed with {row[1]}",
                    "date": str(row[2]),
                    "status": row[3],
                    "provider": row[4]
                })
        
        if "immunizations" in event_types:
            imm_query = """
                SELECT 'immunization' as event_type, vaccine_name as description,
                       administration_date as event_date, NULL as status, provider
                FROM immunizations 
                WHERE administration_date IS NOT NULL
            """
            params = []
            if date_from:
                imm_query += " AND administration_date >= ?"
                params.append(date_from)
            if date_to:
                imm_query += " AND administration_date <= ?"
                params.append(date_to)
            
            imm_results = self.conn.execute(imm_query, params).fetchall()
            for row in imm_results:
                timeline_events.append({
                    "type": row[0],
                    "description": f"Received {row[1]}",
                    "date": str(row[2]),
                    "status": row[3],
                    "provider": row[4]
                })
        
        # Sort timeline by date
        timeline_events.sort(key=lambda x: x["date"], reverse=True)
        
        return json.dumps({
            "total_events": len(timeline_events),
            "date_range": {
                "from": date_from,
                "to": date_to
            },
            "event_types": event_types,
            "timeline": timeline_events
        }, indent=2)

async def main():
    """Main entry point for the MCP server."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Health Data MCP Server")
    parser.add_argument(
        "--db-path",
        default="/Users/Shared/health_data.duckdb", 
        help="Path to health database file"
    )
    args = parser.parse_args()
    
    server = HealthDataServer(args.db_path)
    
    # Run the server using stdio transport
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await server.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="health-data-server",
                server_version="1.0.0",
                capabilities=server.server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())