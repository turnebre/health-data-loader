import pandas as pd
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataTransformer:
    """Transform and clean extracted health data."""
    
    def __init__(self):
        pass
    
    def clean_text(self, text: Optional[str]) -> Optional[str]:
        """Clean and normalize text fields."""
        if not text or pd.isna(text):
            return None
        
        # Convert to string if not already
        text = str(text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove common HTML entities
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&nbsp;', ' ')
        
        return text.strip() if text.strip() else None
    
    def standardize_date(self, date_str: Optional[str]) -> Optional[str]:
        """Standardize date format."""
        if not date_str:
            return None
        
        # Already in YYYY-MM-DD format
        if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
            return date_str
        
        # Handle various other formats
        date_patterns = [
            ('%Y%m%d', r'^\d{8}$'),
            ('%m/%d/%Y', r'^\d{1,2}/\d{1,2}/\d{4}$'),
            ('%m-%d-%Y', r'^\d{1,2}-\d{1,2}-\d{4}$'),
            ('%Y/%m/%d', r'^\d{4}/\d{1,2}/\d{1,2}$'),
        ]
        
        for pattern, regex in date_patterns:
            if re.match(regex, date_str):
                try:
                    return datetime.strptime(date_str, pattern).strftime('%Y-%m-%d')
                except ValueError:
                    continue
        
        logger.warning(f"Could not parse date: {date_str}")
        return date_str
    
    def extract_numeric_value(self, value_str: Optional[str]) -> Optional[float]:
        """Extract numeric value from string."""
        if not value_str:
            return None
        
        # Remove non-numeric characters except decimal point and minus
        numeric_str = re.sub(r'[^\d.-]', '', str(value_str))
        
        try:
            return float(numeric_str) if numeric_str else None
        except ValueError:
            return None
    
    def transform_medications(self, medications: List[Dict[str, Any]]) -> pd.DataFrame:
        """Transform medications data."""
        if not medications:
            return pd.DataFrame()
        
        df = pd.DataFrame(medications)
        
        # Clean text fields
        text_fields = ['medication_name', 'dosage', 'frequency', 'route', 'status', 'prescriber', 'instructions']
        for field in text_fields:
            if field in df.columns:
                df[field] = df[field].apply(self.clean_text)
        
        # Standardize dates
        date_fields = ['start_date', 'end_date']
        for field in date_fields:
            if field in df.columns:
                df[field] = df[field].apply(self.standardize_date)
        
        # Fill missing values
        df = df.fillna('')
        
        logger.info(f"Transformed {len(df)} medication records")
        return df
    
    def transform_allergies(self, allergies: List[Dict[str, Any]]) -> pd.DataFrame:
        """Transform allergies data."""
        if not allergies:
            return pd.DataFrame()
        
        df = pd.DataFrame(allergies)
        
        # Clean text fields
        text_fields = ['allergen', 'reaction', 'severity', 'status', 'notes']
        for field in text_fields:
            if field in df.columns:
                df[field] = df[field].apply(self.clean_text)
        
        # Standardize dates
        if 'onset_date' in df.columns:
            df['onset_date'] = df['onset_date'].apply(self.standardize_date)
        
        # Standardize severity levels
        if 'severity' in df.columns:
            severity_mapping = {
                'mild': 'Mild',
                'moderate': 'Moderate', 
                'severe': 'Severe',
                'critical': 'Critical'
            }
            df['severity'] = df['severity'].str.lower().map(severity_mapping).fillna(df['severity'])
        
        df = df.fillna('')
        
        logger.info(f"Transformed {len(df)} allergy records")
        return df
    
    def transform_problems(self, problems: List[Dict[str, Any]]) -> pd.DataFrame:
        """Transform problems/diagnoses data."""
        if not problems:
            return pd.DataFrame()
        
        df = pd.DataFrame(problems)
        
        # Clean text fields
        text_fields = ['problem_name', 'severity', 'status', 'notes']
        for field in text_fields:
            if field in df.columns:
                df[field] = df[field].apply(self.clean_text)
        
        # Standardize dates
        date_fields = ['onset_date', 'resolution_date']
        for field in date_fields:
            if field in df.columns:
                df[field] = df[field].apply(self.standardize_date)
        
        df = df.fillna('')
        
        logger.info(f"Transformed {len(df)} problem records")
        return df
    
    def transform_procedures(self, procedures: List[Dict[str, Any]]) -> pd.DataFrame:
        """Transform procedures data."""
        if not procedures:
            return pd.DataFrame()
        
        df = pd.DataFrame(procedures)
        
        # Clean text fields
        text_fields = ['procedure_name', 'provider', 'location', 'status', 'notes']
        for field in text_fields:
            if field in df.columns:
                df[field] = df[field].apply(self.clean_text)
        
        # Standardize dates
        if 'procedure_date' in df.columns:
            df['procedure_date'] = df['procedure_date'].apply(self.standardize_date)
        
        df = df.fillna('')
        
        logger.info(f"Transformed {len(df)} procedure records")
        return df
    
    def transform_results(self, results: List[Dict[str, Any]]) -> pd.DataFrame:
        """Transform lab results data."""
        if not results:
            return pd.DataFrame()
        
        df = pd.DataFrame(results)
        
        # Clean text fields
        text_fields = ['test_name', 'unit', 'reference_range', 'abnormal_flag', 'status', 'provider', 'notes']
        for field in text_fields:
            if field in df.columns:
                df[field] = df[field].apply(self.clean_text)
        
        # Standardize dates
        if 'test_date' in df.columns:
            df['test_date'] = df['test_date'].apply(self.standardize_date)
        
        # Clean result values
        if 'result_value' in df.columns:
            df['result_value'] = df['result_value'].apply(self.clean_text)
        
        df = df.fillna('')
        
        logger.info(f"Transformed {len(df)} lab result records")
        return df
    
    def transform_vitals(self, vitals: List[Dict[str, Any]]) -> pd.DataFrame:
        """Transform vitals data."""
        if not vitals:
            return pd.DataFrame()
        
        # Group vitals by date to combine measurements from same visit
        vitals_by_date = {}
        for vital in vitals:
            date = vital.get('measurement_date')
            if date:
                if date not in vitals_by_date:
                    vitals_by_date[date] = {'measurement_date': date}
                vitals_by_date[date].update(vital)
        
        df = pd.DataFrame(list(vitals_by_date.values()))
        
        # Standardize dates
        if 'measurement_date' in df.columns:
            df['measurement_date'] = df['measurement_date'].apply(self.standardize_date)
        
        # Convert numeric fields
        numeric_fields = ['height_cm', 'weight_kg', 'bmi', 'systolic_bp', 'diastolic_bp', 
                         'heart_rate', 'temperature_c', 'respiratory_rate', 'oxygen_saturation']
        
        for field in numeric_fields:
            if field in df.columns:
                df[field] = df[field].apply(self.extract_numeric_value)
        
        # Calculate BMI if height and weight are available
        if 'height_cm' in df.columns and 'weight_kg' in df.columns and 'bmi' not in df.columns:
            df['bmi'] = df.apply(
                lambda row: round(row['weight_kg'] / ((row['height_cm']/100) ** 2), 1) 
                if pd.notna(row['weight_kg']) and pd.notna(row['height_cm']) and row['height_cm'] > 0 
                else None, axis=1
            )
        
        df = df.fillna('')
        
        logger.info(f"Transformed {len(df)} vital sign records")
        return df
    
    def transform_immunizations(self, immunizations: List[Dict[str, Any]]) -> pd.DataFrame:
        """Transform immunizations data."""
        if not immunizations:
            return pd.DataFrame()
        
        df = pd.DataFrame(immunizations)
        
        # Clean text fields
        text_fields = ['vaccine_name', 'lot_number', 'manufacturer', 'route', 'site', 'provider', 'notes']
        for field in text_fields:
            if field in df.columns:
                df[field] = df[field].apply(self.clean_text)
        
        # Standardize dates
        if 'administration_date' in df.columns:
            df['administration_date'] = df['administration_date'].apply(self.standardize_date)
        
        df = df.fillna('')
        
        logger.info(f"Transformed {len(df)} immunization records")
        return df
    
    def transform_all_data(self, parsed_data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, pd.DataFrame]:
        """Transform all parsed data sections."""
        transformed_data = {}
        
        if 'medications' in parsed_data:
            transformed_data['medications'] = self.transform_medications(parsed_data['medications'])
        
        if 'allergies' in parsed_data:
            transformed_data['allergies'] = self.transform_allergies(parsed_data['allergies'])
        
        if 'problems' in parsed_data:
            transformed_data['problems'] = self.transform_problems(parsed_data['problems'])
        
        if 'procedures' in parsed_data:
            transformed_data['procedures'] = self.transform_procedures(parsed_data['procedures'])
        
        if 'results' in parsed_data:
            transformed_data['results'] = self.transform_results(parsed_data['results'])
        
        if 'vitals' in parsed_data:
            transformed_data['vitals'] = self.transform_vitals(parsed_data['vitals'])
        
        if 'immunizations' in parsed_data:
            transformed_data['immunizations'] = self.transform_immunizations(parsed_data['immunizations'])
        
        return transformed_data