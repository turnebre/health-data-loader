import pandas as pd
from typing import Dict
import logging
from database import HealthDatabase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleDataLoader:
    """Load transformed health data into DuckDB using pandas."""
    
    def __init__(self, db_path: str = "health_data.duckdb"):
        self.db = HealthDatabase(db_path)
        self.conn = self.db.get_connection()
    
    def _get_table_schemas(self) -> Dict[str, list]:
        """Get the column names for each table."""
        return {
            'medications': ['id', 'medication_name', 'dosage', 'frequency', 'route', 'start_date', 'end_date', 'status', 'prescriber', 'ndc_code', 'rxnorm_code', 'instructions', 'created_at'],
            'allergies': ['id', 'allergen', 'reaction', 'severity', 'onset_date', 'status', 'allergy_code', 'notes', 'created_at'],
            'problems': ['id', 'problem_name', 'icd10_code', 'snomed_code', 'onset_date', 'resolution_date', 'status', 'severity', 'notes', 'created_at'],
            'procedures': ['id', 'procedure_name', 'procedure_date', 'cpt_code', 'snomed_code', 'provider', 'location', 'status', 'notes', 'created_at'],
            'results': ['id', 'test_name', 'test_date', 'result_value', 'unit', 'reference_range', 'abnormal_flag', 'status', 'loinc_code', 'provider', 'notes', 'created_at'],
            'vitals': ['id', 'measurement_date', 'measurement_time', 'height_cm', 'weight_kg', 'bmi', 'systolic_bp', 'diastolic_bp', 'heart_rate', 'temperature_c', 'respiratory_rate', 'oxygen_saturation', 'notes', 'created_at'],
            'immunizations': ['id', 'vaccine_name', 'administration_date', 'lot_number', 'manufacturer', 'route', 'site', 'cvx_code', 'provider', 'notes', 'created_at']
        }
    
    def load_all_data(self, transformed_data: Dict[str, pd.DataFrame]) -> Dict[str, int]:
        """Load all transformed data into database using pandas."""
        load_results = {}
        
        # Define table mappings
        table_mappings = {
            'medications': 'medications',
            'allergies': 'allergies', 
            'problems': 'problems',
            'procedures': 'procedures',
            'results': 'results',
            'vitals': 'vitals',
            'immunizations': 'immunizations'
        }
        
        # Get table schemas
        table_schemas = self._get_table_schemas()
        
        for data_type, table_name in table_mappings.items():
            if data_type in transformed_data and not transformed_data[data_type].empty:
                df = transformed_data[data_type].copy()
                
                # Add ID column
                df.insert(0, 'id', range(1, len(df) + 1))
                
                # Add created_at timestamp
                df['created_at'] = pd.Timestamp.now()
                
                # Ensure all required columns exist
                expected_columns = table_schemas.get(table_name, [])
                for col in expected_columns:
                    if col not in df.columns:
                        df[col] = None
                
                # Reorder columns to match table schema
                df = df[expected_columns]
                
                # Replace empty strings with None for date and numeric columns
                date_columns = [col for col in df.columns if 'date' in col.lower()]
                numeric_columns = ['height_cm', 'weight_kg', 'bmi', 'systolic_bp', 'diastolic_bp', 
                                 'heart_rate', 'temperature_c', 'respiratory_rate', 'oxygen_saturation']
                
                for col in date_columns + numeric_columns:
                    if col in df.columns:
                        df[col] = df[col].replace('', None)
                
                try:
                    # Clear existing data
                    self.conn.execute(f"DELETE FROM {table_name}")
                    
                    # Insert new data using pandas
                    self.conn.register('temp_df', df)
                    self.conn.execute(f"INSERT INTO {table_name} SELECT * FROM temp_df")
                    
                    load_results[data_type] = len(df)
                    logger.info(f"Loaded {len(df)} {data_type} records")
                    
                except Exception as e:
                    logger.error(f"Error loading {data_type}: {e}")
                    load_results[data_type] = 0
            else:
                load_results[data_type] = 0
                logger.info(f"No {data_type} data to load")
        
        return load_results
    
    def get_table_counts(self) -> Dict[str, int]:
        """Get record counts for all tables."""
        tables = ['medications', 'allergies', 'problems', 'procedures', 'results', 'vitals', 'immunizations']
        counts = {}
        
        for table in tables:
            try:
                result = self.conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
                counts[table] = result[0] if result else 0
            except Exception as e:
                logger.error(f"Error getting count for {table}: {e}")
                counts[table] = 0
        
        return counts
    
    def close(self):
        """Close database connection."""
        if self.db:
            self.db.close()