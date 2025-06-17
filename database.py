import duckdb
from typing import Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HealthDatabase:
    def __init__(self, db_path: str = "health_data.duckdb"):
        """Initialize the health database connection."""
        self.db_path = db_path
        self.conn = duckdb.connect(db_path)
        self.create_tables()
    
    def create_tables(self):
        """Create all health data tables."""
        
        # Medications table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS medications (
                id INTEGER,
                medication_name VARCHAR,
                dosage VARCHAR,
                frequency VARCHAR,
                route VARCHAR,
                start_date DATE,
                end_date DATE,
                status VARCHAR,
                prescriber VARCHAR,
                ndc_code VARCHAR,
                rxnorm_code VARCHAR,
                instructions TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Allergies table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS allergies (
                id INTEGER,
                allergen VARCHAR,
                reaction VARCHAR,
                severity VARCHAR,
                onset_date DATE,
                status VARCHAR,
                allergy_code VARCHAR,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Problems/Diagnoses table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS problems (
                id INTEGER,
                problem_name VARCHAR,
                icd10_code VARCHAR,
                snomed_code VARCHAR,
                onset_date DATE,
                resolution_date DATE,
                status VARCHAR,
                severity VARCHAR,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Procedures table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS procedures (
                id INTEGER,
                procedure_name VARCHAR,
                procedure_date DATE,
                cpt_code VARCHAR,
                snomed_code VARCHAR,
                provider VARCHAR,
                location VARCHAR,
                status VARCHAR,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Lab Results table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER,
                test_name VARCHAR,
                test_date DATE,
                result_value VARCHAR,
                unit VARCHAR,
                reference_range VARCHAR,
                abnormal_flag VARCHAR,
                status VARCHAR,
                loinc_code VARCHAR,
                provider VARCHAR,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Vitals table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS vitals (
                id INTEGER,
                measurement_date DATE,
                measurement_time TIME,
                height_cm DECIMAL(8,2),
                weight_kg DECIMAL(8,2),
                bmi DECIMAL(8,2),
                systolic_bp INTEGER,
                diastolic_bp INTEGER,
                heart_rate INTEGER,
                temperature_c DECIMAL(4,1),
                respiratory_rate INTEGER,
                oxygen_saturation DECIMAL(5,2),
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Immunizations table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS immunizations (
                id INTEGER,
                vaccine_name VARCHAR,
                administration_date DATE,
                lot_number VARCHAR,
                manufacturer VARCHAR,
                route VARCHAR,
                site VARCHAR,
                cvx_code VARCHAR,
                provider VARCHAR,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Encounters table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS encounters (
                id INTEGER,
                encounter_date DATE,
                encounter_time TIME,
                encounter_type VARCHAR,
                provider VARCHAR,
                facility VARCHAR,
                department VARCHAR,
                chief_complaint TEXT,
                diagnosis TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Social History table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS social_history (
                id INTEGER,
                category VARCHAR,
                description TEXT,
                status VARCHAR,
                start_date DATE,
                end_date DATE,
                quantity VARCHAR,
                frequency VARCHAR,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Family History table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS family_history (
                id INTEGER,
                relationship VARCHAR,
                condition VARCHAR,
                age_at_diagnosis INTEGER,
                icd10_code VARCHAR,
                snomed_code VARCHAR,
                status VARCHAR,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Medical History table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS medical_history (
                id INTEGER,
                condition VARCHAR,
                onset_date DATE,
                resolution_date DATE,
                icd10_code VARCHAR,
                snomed_code VARCHAR,
                status VARCHAR,
                severity VARCHAR,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Care Plans/Goals table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS care_plans (
                id INTEGER,
                goal_description TEXT,
                target_date DATE,
                status VARCHAR,
                priority VARCHAR,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        logger.info("Database tables created successfully")
    
    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
    
    def get_connection(self):
        """Get the database connection."""
        return self.conn