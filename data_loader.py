import pandas as pd
from typing import Dict, Any
import logging
from database import HealthDatabase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataLoader:
    """Load transformed health data into DuckDB."""
    
    def __init__(self, db_path: str = "health_data.duckdb"):
        self.db = HealthDatabase(db_path)
        self.conn = self.db.get_connection()
    
    def clean_date_value(self, date_value):
        """Clean date value - return None for empty strings."""
        if not date_value or date_value == '' or pd.isna(date_value):
            return None
        return date_value
    
    def load_medications(self, df: pd.DataFrame) -> int:
        """Load medications data into database."""
        if df.empty:
            logger.info("No medications data to load")
            return 0
        
        # Clear existing data (for full refresh)
        self.conn.execute("DELETE FROM medications")
        
        # Insert new data
        records_inserted = 0
        for idx, row in df.iterrows():
            try:
                self.conn.execute("""
                    INSERT INTO medications (
                        id, medication_name, dosage, frequency, route, start_date, end_date,
                        status, prescriber, ndc_code, rxnorm_code, instructions
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, [
                    idx + 1,
                    row.get('medication_name', ''),
                    row.get('dosage', ''),
                    row.get('frequency', ''),
                    row.get('route', ''),
                    self.clean_date_value(row.get('start_date')),
                    self.clean_date_value(row.get('end_date')),
                    row.get('status', ''),
                    row.get('prescriber', ''),
                    row.get('ndc_code', ''),
                    row.get('rxnorm_code', ''),
                    row.get('instructions', '')
                ])
                records_inserted += 1
            except Exception as e:
                logger.error(f"Error inserting medication record: {e}")
        
        logger.info(f"Loaded {records_inserted} medication records")
        return records_inserted
    
    def load_allergies(self, df: pd.DataFrame) -> int:
        """Load allergies data into database."""
        if df.empty:
            logger.info("No allergies data to load")
            return 0
        
        self.conn.execute("DELETE FROM allergies")
        
        records_inserted = 0
        for _, row in df.iterrows():
            try:
                self.conn.execute("""
                    INSERT INTO allergies (
                        allergen, reaction, severity, onset_date, status, allergy_code, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, [
                    row.get('allergen', ''),
                    row.get('reaction', ''),
                    row.get('severity', ''),
                    self.clean_date_value(row.get('onset_date')),
                    row.get('status', ''),
                    row.get('allergy_code', ''),
                    row.get('notes', '')
                ])
                records_inserted += 1
            except Exception as e:
                logger.error(f"Error inserting allergy record: {e}")
        
        logger.info(f"Loaded {records_inserted} allergy records")
        return records_inserted
    
    def load_problems(self, df: pd.DataFrame) -> int:
        """Load problems data into database."""
        if df.empty:
            logger.info("No problems data to load")
            return 0
        
        self.conn.execute("DELETE FROM problems")
        
        records_inserted = 0
        for _, row in df.iterrows():
            try:
                self.conn.execute("""
                    INSERT INTO problems (
                        problem_name, icd10_code, snomed_code, onset_date, resolution_date,
                        status, severity, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, [
                    row.get('problem_name', ''),
                    row.get('icd10_code', ''),
                    row.get('snomed_code', ''),
                    self.clean_date_value(row.get('onset_date')),
                    self.clean_date_value(row.get('resolution_date')),
                    row.get('status', ''),
                    row.get('severity', ''),
                    row.get('notes', '')
                ])
                records_inserted += 1
            except Exception as e:
                logger.error(f"Error inserting problem record: {e}")
        
        logger.info(f"Loaded {records_inserted} problem records")
        return records_inserted
    
    def load_procedures(self, df: pd.DataFrame) -> int:
        """Load procedures data into database."""
        if df.empty:
            logger.info("No procedures data to load")
            return 0
        
        self.conn.execute("DELETE FROM procedures")
        
        records_inserted = 0
        for _, row in df.iterrows():
            try:
                self.conn.execute("""
                    INSERT INTO procedures (
                        procedure_name, procedure_date, cpt_code, snomed_code, provider,
                        location, status, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, [
                    row.get('procedure_name', ''),
                    self.clean_date_value(row.get('procedure_date')),
                    row.get('cpt_code', ''),
                    row.get('snomed_code', ''),
                    row.get('provider', ''),
                    row.get('location', ''),
                    row.get('status', ''),
                    row.get('notes', '')
                ])
                records_inserted += 1
            except Exception as e:
                logger.error(f"Error inserting procedure record: {e}")
        
        logger.info(f"Loaded {records_inserted} procedure records")
        return records_inserted
    
    def load_results(self, df: pd.DataFrame) -> int:
        """Load lab results data into database."""
        if df.empty:
            logger.info("No lab results data to load")
            return 0
        
        self.conn.execute("DELETE FROM results")
        
        records_inserted = 0
        for _, row in df.iterrows():
            try:
                self.conn.execute("""
                    INSERT INTO results (
                        test_name, test_date, result_value, unit, reference_range,
                        abnormal_flag, status, loinc_code, provider, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, [
                    row.get('test_name', ''),
                    self.clean_date_value(row.get('test_date')),
                    row.get('result_value', ''),
                    row.get('unit', ''),
                    row.get('reference_range', ''),
                    row.get('abnormal_flag', ''),
                    row.get('status', ''),
                    row.get('loinc_code', ''),
                    row.get('provider', ''),
                    row.get('notes', '')
                ])
                records_inserted += 1
            except Exception as e:
                logger.error(f"Error inserting lab result record: {e}")
        
        logger.info(f"Loaded {records_inserted} lab result records")
        return records_inserted
    
    def load_vitals(self, df: pd.DataFrame) -> int:
        """Load vitals data into database."""
        if df.empty:
            logger.info("No vitals data to load")
            return 0
        
        self.conn.execute("DELETE FROM vitals")
        
        records_inserted = 0
        for _, row in df.iterrows():
            try:
                self.conn.execute("""
                    INSERT INTO vitals (
                        measurement_date, measurement_time, height_cm, weight_kg, bmi,
                        systolic_bp, diastolic_bp, heart_rate, temperature_c,
                        respiratory_rate, oxygen_saturation, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, [
                    self.clean_date_value(row.get('measurement_date')),
                    row.get('measurement_time', None),
                    row.get('height_cm', None),
                    row.get('weight_kg', None),
                    row.get('bmi', None),
                    row.get('systolic_bp', None),
                    row.get('diastolic_bp', None),
                    row.get('heart_rate', None),
                    row.get('temperature_c', None),
                    row.get('respiratory_rate', None),
                    row.get('oxygen_saturation', None),
                    row.get('notes', '')
                ])
                records_inserted += 1
            except Exception as e:
                logger.error(f"Error inserting vitals record: {e}")
        
        logger.info(f"Loaded {records_inserted} vitals records")
        return records_inserted
    
    def load_immunizations(self, df: pd.DataFrame) -> int:
        """Load immunizations data into database."""
        if df.empty:
            logger.info("No immunizations data to load")
            return 0
        
        self.conn.execute("DELETE FROM immunizations")
        
        records_inserted = 0
        for _, row in df.iterrows():
            try:
                self.conn.execute("""
                    INSERT INTO immunizations (
                        vaccine_name, administration_date, lot_number, manufacturer,
                        route, site, cvx_code, provider, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, [
                    row.get('vaccine_name', ''),
                    self.clean_date_value(row.get('administration_date')),
                    row.get('lot_number', ''),
                    row.get('manufacturer', ''),
                    row.get('route', ''),
                    row.get('site', ''),
                    row.get('cvx_code', ''),
                    row.get('provider', ''),
                    row.get('notes', '')
                ])
                records_inserted += 1
            except Exception as e:
                logger.error(f"Error inserting immunization record: {e}")
        
        logger.info(f"Loaded {records_inserted} immunization records")
        return records_inserted
    
    def load_all_data(self, transformed_data: Dict[str, pd.DataFrame]) -> Dict[str, int]:
        """Load all transformed data into database."""
        load_results = {}
        
        if 'medications' in transformed_data:
            load_results['medications'] = self.load_medications(transformed_data['medications'])
        
        if 'allergies' in transformed_data:
            load_results['allergies'] = self.load_allergies(transformed_data['allergies'])
        
        if 'problems' in transformed_data:
            load_results['problems'] = self.load_problems(transformed_data['problems'])
        
        if 'procedures' in transformed_data:
            load_results['procedures'] = self.load_procedures(transformed_data['procedures'])
        
        if 'results' in transformed_data:
            load_results['results'] = self.load_results(transformed_data['results'])
        
        if 'vitals' in transformed_data:
            load_results['vitals'] = self.load_vitals(transformed_data['vitals'])
        
        if 'immunizations' in transformed_data:
            load_results['immunizations'] = self.load_immunizations(transformed_data['immunizations'])
        
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