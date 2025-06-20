"""
Health Data Query Functions

This module contains specialized query functions for health data analysis.
It provides domain-specific logic for medical data interpretation and formatting.
"""

import json
import logging
from datetime import datetime, date, timedelta
from typing import Any, Dict, List, Optional, Union, Tuple

logger = logging.getLogger(__name__)

class HealthQueryEngine:
    """Handles complex health data queries with medical domain knowledge."""
    
    def __init__(self, db_connection):
        self.conn = db_connection
    
    async def get_lab_results(self, test_name: str = None, date_from: str = None, 
                             date_to: str = None, abnormal_only: bool = False, 
                             limit: int = 100) -> str:
        """Get lab results with intelligent filtering and analysis."""
        
        query = """
            SELECT test_name, test_date, result_value, unit, reference_range, 
                   abnormal_flag, status, loinc_code, provider, notes
            FROM results
        """
        params = []
        conditions = []
        
        # Build WHERE clause
        if test_name:
            conditions.append("LOWER(test_name) LIKE ?")
            params.append(f"%{test_name.lower()}%")
        
        if date_from:
            conditions.append("test_date >= ?")
            params.append(date_from)
        
        if date_to:
            conditions.append("test_date <= ?")
            params.append(date_to)
        
        if abnormal_only:
            conditions.append("abnormal_flag IS NOT NULL AND abnormal_flag != 'Normal'")
        
        # Filter out empty results
        conditions.append("result_value IS NOT NULL AND result_value != ''")
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY test_date DESC, test_name LIMIT ?"
        params.append(limit)
        
        try:
            results = self.conn.execute(query, params).fetchall()
            
            if not results:
                return "No lab results found matching the criteria."
            
            # Group results by test name for trend analysis
            test_groups = {}
            for row in results:
                test_name_key = row[0]
                if test_name_key not in test_groups:
                    test_groups[test_name_key] = []
                
                test_groups[test_name_key].append({
                    "date": str(row[1]) if row[1] else None,
                    "value": row[2],
                    "unit": row[3] or "",
                    "reference_range": row[4] or "",
                    "abnormal_flag": row[5] or "Normal",
                    "status": row[6] or "",
                    "loinc_code": row[7] or "",
                    "provider": row[8] or "",
                    "notes": row[9] or ""
                })
            
            # Calculate trends for numeric values
            for test_name_key, test_results in test_groups.items():
                test_groups[test_name_key] = self._add_trend_analysis(test_results)
            
            return json.dumps({
                "total_found": len(results),
                "unique_tests": len(test_groups),
                "test_results": test_groups,
                "summary": self._generate_lab_summary(test_groups)
            }, indent=2)
            
        except Exception as e:
            logger.error(f"Error in get_lab_results: {e}")
            return f"Error retrieving lab results: {str(e)}"
    
    async def get_vitals(self, date_from: str = None, date_to: str = None, 
                        vital_type: str = "all", limit: int = 100) -> str:
        """Get vital signs with trend analysis."""
        
        # Build query based on vital type
        if vital_type == "bp":
            query = """
                SELECT measurement_date, systolic_bp, diastolic_bp, notes
                FROM vitals 
                WHERE systolic_bp IS NOT NULL OR diastolic_bp IS NOT NULL
            """
        elif vital_type == "weight":
            query = """
                SELECT measurement_date, weight_kg, bmi, notes
                FROM vitals 
                WHERE weight_kg IS NOT NULL
            """
        elif vital_type == "height":
            query = """
                SELECT measurement_date, height_cm, notes
                FROM vitals 
                WHERE height_cm IS NOT NULL
            """
        elif vital_type == "heart_rate":
            query = """
                SELECT measurement_date, heart_rate, notes
                FROM vitals 
                WHERE heart_rate IS NOT NULL
            """
        else:  # all vitals
            query = """
                SELECT measurement_date, measurement_time, height_cm, weight_kg, bmi,
                       systolic_bp, diastolic_bp, heart_rate, temperature_c, 
                       respiratory_rate, oxygen_saturation, notes
                FROM vitals
            """
        
        params = []
        additional_conditions = []
        
        if date_from:
            additional_conditions.append("measurement_date >= ?")
            params.append(date_from)
        
        if date_to:
            additional_conditions.append("measurement_date <= ?")
            params.append(date_to)
        
        if additional_conditions:
            if "WHERE" in query:
                query += " AND " + " AND ".join(additional_conditions)
            else:
                query += " WHERE " + " AND ".join(additional_conditions)
        
        query += " ORDER BY measurement_date DESC LIMIT ?"
        params.append(limit)
        
        try:
            results = self.conn.execute(query, params).fetchall()
            
            if not results:
                return "No vital signs found matching the criteria."
            
            # Format results based on vital type
            if vital_type == "bp":
                vitals = []
                for row in results:
                    if row[1] or row[2]:  # systolic or diastolic
                        vitals.append({
                            "date": str(row[0]),
                            "systolic": row[1],
                            "diastolic": row[2],
                            "bp_reading": f"{row[1] or '?'}/{row[2] or '?'}",
                            "category": self._categorize_blood_pressure(row[1], row[2]),
                            "notes": row[3] or ""
                        })
                
                # Add trend analysis for BP
                trends = self._analyze_bp_trends(vitals)
                
                return json.dumps({
                    "vital_type": "Blood Pressure",
                    "total_readings": len(vitals),
                    "readings": vitals,
                    "trends": trends
                }, indent=2)
            
            elif vital_type == "weight":
                vitals = []
                for row in results:
                    if row[1]:  # weight_kg
                        vitals.append({
                            "date": str(row[0]),
                            "weight_kg": row[1],
                            "weight_lbs": round(row[1] * 2.20462, 1),
                            "bmi": row[2],
                            "notes": row[3] or ""
                        })
                
                trends = self._analyze_weight_trends(vitals)
                
                return json.dumps({
                    "vital_type": "Weight",
                    "total_readings": len(vitals),
                    "readings": vitals,
                    "trends": trends
                }, indent=2)
            
            else:  # all vitals
                vitals = []
                for row in results:
                    vital_entry = {
                        "date": str(row[0]),
                        "time": str(row[1]) if row[1] else None,
                    }
                    
                    # Add non-null vital measurements
                    if row[2]: vital_entry["height_cm"] = row[2]
                    if row[3]: vital_entry["weight_kg"] = row[3]
                    if row[4]: vital_entry["bmi"] = row[4]
                    if row[5] or row[6]: 
                        vital_entry["blood_pressure"] = f"{row[5] or '?'}/{row[6] or '?'}"
                        vital_entry["bp_category"] = self._categorize_blood_pressure(row[5], row[6])
                    if row[7]: vital_entry["heart_rate"] = row[7]
                    if row[8]: vital_entry["temperature_c"] = row[8]
                    if row[9]: vital_entry["respiratory_rate"] = row[9]
                    if row[10]: vital_entry["oxygen_saturation"] = row[10]
                    if row[11]: vital_entry["notes"] = row[11]
                    
                    vitals.append(vital_entry)
                
                return json.dumps({
                    "vital_type": "All Vitals",
                    "total_readings": len(vitals),
                    "readings": vitals
                }, indent=2)
            
        except Exception as e:
            logger.error(f"Error in get_vitals: {e}")
            return f"Error retrieving vital signs: {str(e)}"
    
    async def get_conditions(self, status: str = "all", condition_name: str = None) -> str:
        """Get medical conditions and problems."""
        
        query = """
            SELECT problem_name, icd10_code, snomed_code, onset_date, 
                   resolution_date, status, severity, notes
            FROM problems
        """
        params = []
        conditions = []
        
        if status != "all":
            conditions.append("LOWER(status) = ?")
            params.append(status.lower())
        
        if condition_name:
            conditions.append("LOWER(problem_name) LIKE ?")
            params.append(f"%{condition_name.lower()}%")
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY onset_date DESC"
        
        try:
            results = self.conn.execute(query, params).fetchall()
            
            if not results:
                return "No medical conditions found matching the criteria."
            
            conditions_list = []
            for row in results:
                condition = {
                    "condition": row[0],
                    "icd10_code": row[1] or "",
                    "snomed_code": row[2] or "",
                    "onset_date": str(row[3]) if row[3] else None,
                    "resolution_date": str(row[4]) if row[4] else None,
                    "status": row[5] or "Unknown",
                    "severity": row[6] or "",
                    "duration": self._calculate_condition_duration(row[3], row[4]),
                    "notes": row[7] or ""
                }
                conditions_list.append(condition)
            
            # Categorize conditions
            active_conditions = [c for c in conditions_list if c["status"].lower() == "active"]
            resolved_conditions = [c for c in conditions_list if c["status"].lower() == "resolved"]
            
            return json.dumps({
                "total_conditions": len(conditions_list),
                "active_conditions": len(active_conditions),
                "resolved_conditions": len(resolved_conditions),
                "conditions": conditions_list,
                "summary": {
                    "most_recent": conditions_list[0] if conditions_list else None,
                    "chronic_conditions": [c for c in active_conditions if self._is_chronic_condition(c)]
                }
            }, indent=2)
            
        except Exception as e:
            logger.error(f"Error in get_conditions: {e}")
            return f"Error retrieving conditions: {str(e)}"
    
    async def get_health_summary(self, include_trends: bool = True) -> str:
        """Generate comprehensive health summary."""
        
        try:
            summary = {
                "generated_at": datetime.now().isoformat(),
                "overview": {},
                "latest_data": {},
                "key_metrics": {},
                "alerts": []
            }
            
            # Get record counts
            summary["overview"] = await self._get_record_counts()
            
            # Get latest data from each category
            summary["latest_data"] = {
                "latest_lab_result": await self._get_latest_lab_result(),
                "latest_vital_signs": await self._get_latest_vital_signs(),
                "active_medications": await self._get_active_medication_count(),
                "active_conditions": await self._get_active_condition_count()
            }
            
            # Get key health metrics
            if include_trends:
                summary["key_metrics"] = await self._get_key_health_metrics()
            
            # Generate health alerts
            summary["alerts"] = await self._generate_health_alerts()
            
            return json.dumps(summary, indent=2)
            
        except Exception as e:
            logger.error(f"Error in get_health_summary: {e}")
            return f"Error generating health summary: {str(e)}"
    
    # Helper methods
    
    def _add_trend_analysis(self, test_results: List[Dict]) -> List[Dict]:
        """Add trend analysis to test results."""
        if len(test_results) < 2:
            return test_results
        
        # Try to extract numeric values for trend analysis
        numeric_values = []
        for result in test_results:
            try:
                # Extract numeric part from result_value
                value_str = str(result["value"]).strip()
                if value_str and value_str.replace(".", "").replace("-", "").isdigit():
                    numeric_values.append((result["date"], float(value_str)))
            except (ValueError, TypeError):
                continue
        
        if len(numeric_values) >= 2:
            # Sort by date
            numeric_values.sort(key=lambda x: x[0])
            
            # Calculate trend
            latest_value = numeric_values[-1][1]
            previous_value = numeric_values[-2][1]
            change = latest_value - previous_value
            percent_change = (change / previous_value * 100) if previous_value != 0 else 0
            
            # Add trend info to the most recent result
            for result in test_results:
                if result["date"] == numeric_values[-1][0]:
                    result["trend"] = {
                        "direction": "increasing" if change > 0 else "decreasing" if change < 0 else "stable",
                        "change": round(change, 2),
                        "percent_change": round(percent_change, 1)
                    }
                    break
        
        return test_results
    
    def _generate_lab_summary(self, test_groups: Dict) -> Dict:
        """Generate summary of lab results."""
        summary = {
            "total_tests": len(test_groups),
            "abnormal_results": 0,
            "recent_tests": []
        }
        
        for test_name, results in test_groups.items():
            for result in results:
                if result["abnormal_flag"] and result["abnormal_flag"] != "Normal":
                    summary["abnormal_results"] += 1
                
                # Add to recent tests (within last 30 days)
                try:
                    result_date = datetime.strptime(result["date"], "%Y-%m-%d")
                    if (datetime.now() - result_date).days <= 30:
                        summary["recent_tests"].append({
                            "test": test_name,
                            "date": result["date"],
                            "value": result["value"],
                            "abnormal": result["abnormal_flag"] != "Normal"
                        })
                except (ValueError, TypeError):
                    continue
        
        return summary
    
    def _categorize_blood_pressure(self, systolic: Optional[int], diastolic: Optional[int]) -> str:
        """Categorize blood pressure reading."""
        if not systolic or not diastolic:
            return "Incomplete reading"
        
        if systolic < 120 and diastolic < 80:
            return "Normal"
        elif systolic < 130 and diastolic < 80:
            return "Elevated"
        elif systolic < 140 or diastolic < 90:
            return "Stage 1 Hypertension"
        elif systolic < 180 or diastolic < 120:
            return "Stage 2 Hypertension"
        else:
            return "Hypertensive Crisis"
    
    def _analyze_bp_trends(self, bp_readings: List[Dict]) -> Dict:
        """Analyze blood pressure trends."""
        if len(bp_readings) < 2:
            return {"trend": "Insufficient data"}
        
        # Get numeric BP values
        systolic_values = [r["systolic"] for r in bp_readings if r["systolic"]]
        diastolic_values = [r["diastolic"] for r in bp_readings if r["diastolic"]]
        
        trends = {}
        
        if len(systolic_values) >= 2:
            recent_avg = sum(systolic_values[:3]) / min(3, len(systolic_values))
            older_avg = sum(systolic_values[-3:]) / min(3, len(systolic_values[-3:]))
            trends["systolic_trend"] = "improving" if recent_avg < older_avg else "worsening" if recent_avg > older_avg else "stable"
        
        if len(diastolic_values) >= 2:
            recent_avg = sum(diastolic_values[:3]) / min(3, len(diastolic_values))
            older_avg = sum(diastolic_values[-3:]) / min(3, len(diastolic_values[-3:]))
            trends["diastolic_trend"] = "improving" if recent_avg < older_avg else "worsening" if recent_avg > older_avg else "stable"
        
        return trends
    
    def _analyze_weight_trends(self, weight_readings: List[Dict]) -> Dict:
        """Analyze weight trends."""
        if len(weight_readings) < 2:
            return {"trend": "Insufficient data"}
        
        weights = [r["weight_kg"] for r in weight_readings if r["weight_kg"]]
        
        if len(weights) >= 2:
            recent_weight = weights[0]
            older_weight = weights[-1]
            change = recent_weight - older_weight
            
            return {
                "overall_change_kg": round(change, 1),
                "overall_change_lbs": round(change * 2.20462, 1),
                "trend": "weight_gain" if change > 1 else "weight_loss" if change < -1 else "stable"
            }
        
        return {"trend": "Insufficient data"}
    
    def _calculate_condition_duration(self, onset_date: Optional[date], resolution_date: Optional[date]) -> Optional[str]:
        """Calculate duration of a medical condition."""
        if not onset_date:
            return None
        
        end_date = resolution_date or date.today()
        duration = end_date - onset_date
        
        if duration.days < 30:
            return f"{duration.days} days"
        elif duration.days < 365:
            return f"{duration.days // 30} months"
        else:
            years = duration.days // 365
            months = (duration.days % 365) // 30
            return f"{years} years, {months} months"
    
    def _is_chronic_condition(self, condition: Dict) -> bool:
        """Determine if a condition is chronic."""
        chronic_keywords = [
            "diabetes", "hypertension", "asthma", "copd", "arthritis", 
            "depression", "anxiety", "chronic", "syndrome"
        ]
        
        condition_name = condition["condition"].lower()
        return any(keyword in condition_name for keyword in chronic_keywords)
    
    async def _get_record_counts(self) -> Dict:
        """Get record counts for all tables."""
        counts = {}
        tables = ["medications", "results", "vitals", "problems", "procedures", "immunizations"]
        
        for table in tables:
            try:
                count = self.conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                counts[table] = count
            except Exception:
                counts[table] = 0
        
        return counts
    
    async def _get_latest_lab_result(self) -> Optional[Dict]:
        """Get the most recent lab result."""
        try:
            result = self.conn.execute("""
                SELECT test_name, test_date, result_value, unit 
                FROM results 
                WHERE test_date IS NOT NULL 
                ORDER BY test_date DESC 
                LIMIT 1
            """).fetchone()
            
            if result:
                return {
                    "test": result[0],
                    "date": str(result[1]),
                    "value": result[2],
                    "unit": result[3]
                }
        except Exception:
            pass
        
        return None
    
    async def _get_latest_vital_signs(self) -> Optional[Dict]:
        """Get the most recent vital signs."""
        try:
            result = self.conn.execute("""
                SELECT measurement_date, systolic_bp, diastolic_bp, weight_kg 
                FROM vitals 
                WHERE measurement_date IS NOT NULL 
                ORDER BY measurement_date DESC 
                LIMIT 1
            """).fetchone()
            
            if result:
                vital = {"date": str(result[0])}
                if result[1] and result[2]:
                    vital["blood_pressure"] = f"{result[1]}/{result[2]}"
                if result[3]:
                    vital["weight_kg"] = result[3]
                return vital
        except Exception:
            pass
        
        return None
    
    async def _get_active_medication_count(self) -> int:
        """Get count of active medications."""
        try:
            count = self.conn.execute("""
                SELECT COUNT(*) FROM medications 
                WHERE LOWER(status) = 'active'
            """).fetchone()[0]
            return count
        except Exception:
            return 0
    
    async def _get_active_condition_count(self) -> int:
        """Get count of active conditions."""
        try:
            count = self.conn.execute("""
                SELECT COUNT(*) FROM problems 
                WHERE LOWER(status) = 'active'
            """).fetchone()[0]
            return count
        except Exception:
            return 0
    
    async def _get_key_health_metrics(self) -> Dict:
        """Get key health metrics with trends."""
        metrics = {}
        
        # Latest BMI
        try:
            bmi_result = self.conn.execute("""
                SELECT bmi, measurement_date FROM vitals 
                WHERE bmi IS NOT NULL 
                ORDER BY measurement_date DESC 
                LIMIT 1
            """).fetchone()
            if bmi_result:
                metrics["latest_bmi"] = {
                    "value": bmi_result[0],
                    "date": str(bmi_result[1]),
                    "category": self._categorize_bmi(bmi_result[0])
                }
        except Exception:
            pass
        
        # Blood pressure trend
        try:
            bp_results = self.conn.execute("""
                SELECT systolic_bp, diastolic_bp, measurement_date FROM vitals 
                WHERE systolic_bp IS NOT NULL AND diastolic_bp IS NOT NULL 
                ORDER BY measurement_date DESC 
                LIMIT 5
            """).fetchall()
            
            if bp_results:
                latest_bp = bp_results[0]
                metrics["blood_pressure"] = {
                    "latest": f"{latest_bp[0]}/{latest_bp[1]}",
                    "date": str(latest_bp[2]),
                    "category": self._categorize_blood_pressure(latest_bp[0], latest_bp[1])
                }
        except Exception:
            pass
        
        return metrics
    
    async def _generate_health_alerts(self) -> List[Dict]:
        """Generate health alerts based on data analysis."""
        alerts = []
        
        # Check for abnormal recent lab results
        try:
            abnormal_results = self.conn.execute("""
                SELECT test_name, test_date, result_value, abnormal_flag 
                FROM results 
                WHERE abnormal_flag IS NOT NULL 
                AND abnormal_flag != 'Normal' 
                AND test_date > date('now', '-30 days')
                ORDER BY test_date DESC
            """).fetchall()
            
            for result in abnormal_results:
                alerts.append({
                    "type": "abnormal_lab_result",
                    "message": f"Abnormal {result[0]}: {result[2]} ({result[3]})",
                    "date": str(result[1]),
                    "severity": "medium"
                })
        except Exception:
            pass
        
        # Check for missing recent vitals
        try:
            latest_vital = self.conn.execute("""
                SELECT MAX(measurement_date) FROM vitals
            """).fetchone()[0]
            
            if latest_vital:
                days_since = (datetime.now().date() - datetime.strptime(str(latest_vital), "%Y-%m-%d").date()).days
                if days_since > 90:
                    alerts.append({
                        "type": "missing_vitals",
                        "message": f"No vital signs recorded in {days_since} days",
                        "severity": "low"
                    })
        except Exception:
            pass
        
        return alerts[:10]  # Limit to 10 alerts
    
    def _categorize_bmi(self, bmi: float) -> str:
        """Categorize BMI value."""
        if bmi < 18.5:
            return "Underweight"
        elif bmi < 25:
            return "Normal weight"
        elif bmi < 30:
            return "Overweight"
        else:
            return "Obese"