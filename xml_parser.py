from lxml import etree
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CCDAParser:
    """Parser for C-CDA XML documents."""
    
    def __init__(self, xml_file_path: str):
        self.xml_file_path = xml_file_path
        self.tree = None
        self.root = None
        self.namespaces = {
            'hl7': 'urn:hl7-org:v3',
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'sdtc': 'urn:hl7-org:sdtc'
        }
        self.parse_document()
    
    def parse_document(self):
        """Parse the XML document."""
        try:
            self.tree = etree.parse(self.xml_file_path)
            self.root = self.tree.getroot()
            logger.info(f"Successfully parsed XML document: {self.xml_file_path}")
        except Exception as e:
            logger.error(f"Error parsing XML document: {e}")
            raise
    
    def parse_date(self, date_str: Optional[str]) -> Optional[str]:
        """Parse HL7 date format to standard date."""
        if not date_str:
            return None
        
        # Remove timezone info and normalize
        date_str = re.sub(r'[-+]\d{4}$', '', date_str)
        
        if len(date_str) == 8:  # YYYYMMDD
            try:
                parsed_date = datetime.strptime(date_str, '%Y%m%d')
                return parsed_date.strftime('%Y-%m-%d')
            except ValueError:
                pass
        
        if len(date_str) >= 14:  # YYYYMMDDHHMMSS
            try:
                parsed_date = datetime.strptime(date_str[:14], '%Y%m%d%H%M%S')
                return parsed_date.strftime('%Y-%m-%d')
            except ValueError:
                pass
        
        return date_str
    
    def get_text_content(self, element) -> str:
        """Extract text content from element, handling nested elements."""
        if element is None:
            return ""
        
        text_parts = []
        if element.text:
            text_parts.append(element.text.strip())
        
        for child in element:
            if child.text:
                text_parts.append(child.text.strip())
            if child.tail:
                text_parts.append(child.tail.strip())
        
        return ' '.join(text_parts).strip()
    
    def find_section_by_title(self, title: str):
        """Find a section by its title."""
        sections = self.root.xpath(f"//hl7:section[hl7:title[text()='{title}']]", namespaces=self.namespaces)
        return sections[0] if sections else None
    
    def parse_medications(self) -> List[Dict[str, Any]]:
        """Parse medications section."""
        medications = []
        section = self.find_section_by_title("Medications")
        
        if section is None:
            logger.warning("Medications section not found")
            return medications
        
        entries = section.xpath(".//hl7:substanceAdministration", namespaces=self.namespaces)
        
        for entry in entries:
            med_data = {}
            
            # Medication name
            med_name_elem = entry.xpath(".//hl7:name", namespaces=self.namespaces)
            if med_name_elem:
                med_data['medication_name'] = self.get_text_content(med_name_elem[0])
            
            # Dosage and frequency
            dose_elem = entry.xpath(".//hl7:doseQuantity", namespaces=self.namespaces)
            if dose_elem:
                med_data['dosage'] = dose_elem[0].get('value', '')
            
            # Route
            route_elem = entry.xpath(".//hl7:routeCode", namespaces=self.namespaces)
            if route_elem:
                med_data['route'] = route_elem[0].get('displayName', '')
            
            # Start and end dates
            effective_time = entry.xpath(".//hl7:effectiveTime", namespaces=self.namespaces)
            for time_elem in effective_time:
                low_elem = time_elem.xpath(".//hl7:low", namespaces=self.namespaces)
                if low_elem:
                    med_data['start_date'] = self.parse_date(low_elem[0].get('value'))
                
                high_elem = time_elem.xpath(".//hl7:high", namespaces=self.namespaces)
                if high_elem:
                    med_data['end_date'] = self.parse_date(high_elem[0].get('value'))
            
            # Status
            status_elem = entry.xpath(".//hl7:statusCode", namespaces=self.namespaces)
            if status_elem:
                med_data['status'] = status_elem[0].get('code', '')
            
            if med_data:
                medications.append(med_data)
        
        logger.info(f"Parsed {len(medications)} medications")
        return medications
    
    def parse_allergies(self) -> List[Dict[str, Any]]:
        """Parse allergies section."""
        allergies = []
        section = self.find_section_by_title("Allergies")
        
        if section is None:
            logger.warning("Allergies section not found")
            return allergies
        
        entries = section.xpath(".//hl7:observation", namespaces=self.namespaces)
        
        for entry in entries:
            allergy_data = {}
            
            # Allergen name
            value_elem = entry.xpath(".//hl7:value", namespaces=self.namespaces)
            if value_elem:
                allergy_data['allergen'] = value_elem[0].get('displayName', '')
            
            # Reaction
            reaction_elem = entry.xpath(".//hl7:entryRelationship//hl7:value", namespaces=self.namespaces)
            if reaction_elem:
                allergy_data['reaction'] = reaction_elem[0].get('displayName', '')
            
            # Severity
            severity_elem = entry.xpath(".//hl7:entryRelationship[@typeCode='SUBJ']//hl7:value", namespaces=self.namespaces)
            if severity_elem:
                allergy_data['severity'] = severity_elem[0].get('displayName', '')
            
            # Status
            status_elem = entry.xpath(".//hl7:statusCode", namespaces=self.namespaces)
            if status_elem:
                allergy_data['status'] = status_elem[0].get('code', '')
            
            if allergy_data:
                allergies.append(allergy_data)
        
        logger.info(f"Parsed {len(allergies)} allergies")
        return allergies
    
    def parse_problems(self) -> List[Dict[str, Any]]:
        """Parse problems/diagnoses section."""
        problems = []
        section = self.find_section_by_title("Problems")
        
        if section is None:
            logger.warning("Problems section not found")
            return problems
        
        entries = section.xpath(".//hl7:observation", namespaces=self.namespaces)
        
        for entry in entries:
            problem_data = {}
            
            # Problem name
            value_elem = entry.xpath(".//hl7:value", namespaces=self.namespaces)
            if value_elem:
                problem_data['problem_name'] = value_elem[0].get('displayName', '')
                problem_data['icd10_code'] = value_elem[0].get('code', '')
            
            # Onset date
            effective_time = entry.xpath(".//hl7:effectiveTime//hl7:low", namespaces=self.namespaces)
            if effective_time:
                problem_data['onset_date'] = self.parse_date(effective_time[0].get('value'))
            
            # Status
            status_elem = entry.xpath(".//hl7:statusCode", namespaces=self.namespaces)
            if status_elem:
                problem_data['status'] = status_elem[0].get('code', '')
            
            if problem_data:
                problems.append(problem_data)
        
        logger.info(f"Parsed {len(problems)} problems")
        return problems
    
    def parse_procedures(self) -> List[Dict[str, Any]]:
        """Parse procedures section."""
        procedures = []
        section = self.find_section_by_title("Procedures")
        
        if section is None:
            logger.warning("Procedures section not found")
            return procedures
        
        entries = section.xpath(".//hl7:procedure", namespaces=self.namespaces)
        
        for entry in entries:
            procedure_data = {}
            
            # Procedure name
            code_elem = entry.xpath(".//hl7:code", namespaces=self.namespaces)
            if code_elem:
                procedure_data['procedure_name'] = code_elem[0].get('displayName', '')
                procedure_data['cpt_code'] = code_elem[0].get('code', '')
            
            # Procedure date
            effective_time = entry.xpath(".//hl7:effectiveTime", namespaces=self.namespaces)
            if effective_time:
                procedure_data['procedure_date'] = self.parse_date(effective_time[0].get('value'))
            
            # Status
            status_elem = entry.xpath(".//hl7:statusCode", namespaces=self.namespaces)
            if status_elem:
                procedure_data['status'] = status_elem[0].get('code', '')
            
            if procedure_data:
                procedures.append(procedure_data)
        
        logger.info(f"Parsed {len(procedures)} procedures")
        return procedures
    
    def parse_results(self) -> List[Dict[str, Any]]:
        """Parse lab results section."""
        results = []
        section = self.find_section_by_title("Results")
        
        if section is None:
            logger.warning("Results section not found")
            return results
        
        entries = section.xpath(".//hl7:observation", namespaces=self.namespaces)
        
        for entry in entries:
            result_data = {}
            
            # Test name
            code_elem = entry.xpath(".//hl7:code", namespaces=self.namespaces)
            if code_elem:
                result_data['test_name'] = code_elem[0].get('displayName', '')
                result_data['loinc_code'] = code_elem[0].get('code', '')
            
            # Result value
            value_elem = entry.xpath(".//hl7:value", namespaces=self.namespaces)
            if value_elem:
                result_data['result_value'] = value_elem[0].get('value', '')
                result_data['unit'] = value_elem[0].get('unit', '')
            
            # Test date
            effective_time = entry.xpath(".//hl7:effectiveTime", namespaces=self.namespaces)
            if effective_time:
                result_data['test_date'] = self.parse_date(effective_time[0].get('value'))
            
            # Reference range
            ref_range_elem = entry.xpath(".//hl7:referenceRange//hl7:text", namespaces=self.namespaces)
            if ref_range_elem:
                result_data['reference_range'] = self.get_text_content(ref_range_elem[0])
            
            if result_data:
                results.append(result_data)
        
        logger.info(f"Parsed {len(results)} lab results")
        return results
    
    def parse_vitals(self) -> List[Dict[str, Any]]:
        """Parse vitals section."""
        vitals = []
        section = self.find_section_by_title("Vitals")
        
        if section is None:
            logger.warning("Vitals section not found")
            return vitals
        
        entries = section.xpath(".//hl7:observation", namespaces=self.namespaces)
        
        for entry in entries:
            vital_data = {}
            
            # Measurement date
            effective_time = entry.xpath(".//hl7:effectiveTime", namespaces=self.namespaces)
            if effective_time:
                vital_data['measurement_date'] = self.parse_date(effective_time[0].get('value'))
            
            # Vital type and value
            code_elem = entry.xpath(".//hl7:code", namespaces=self.namespaces)
            value_elem = entry.xpath(".//hl7:value", namespaces=self.namespaces)
            
            if code_elem and value_elem:
                vital_type = code_elem[0].get('displayName', '').lower()
                vital_value = value_elem[0].get('value', '')
                
                if 'height' in vital_type:
                    vital_data['height_cm'] = vital_value
                elif 'weight' in vital_type:
                    vital_data['weight_kg'] = vital_value
                elif 'blood pressure' in vital_type or 'systolic' in vital_type:
                    vital_data['systolic_bp'] = vital_value
                elif 'diastolic' in vital_type:
                    vital_data['diastolic_bp'] = vital_value
                elif 'heart rate' in vital_type or 'pulse' in vital_type:
                    vital_data['heart_rate'] = vital_value
                elif 'temperature' in vital_type:
                    vital_data['temperature_c'] = vital_value
            
            if vital_data:
                vitals.append(vital_data)
        
        logger.info(f"Parsed {len(vitals)} vital measurements")
        return vitals
    
    def parse_immunizations(self) -> List[Dict[str, Any]]:
        """Parse immunizations section."""
        immunizations = []
        section = self.find_section_by_title("Immunizations")
        
        if section is None:
            logger.warning("Immunizations section not found")
            return immunizations
        
        entries = section.xpath(".//hl7:substanceAdministration", namespaces=self.namespaces)
        
        for entry in entries:
            imm_data = {}
            
            # Vaccine name
            code_elem = entry.xpath(".//hl7:code", namespaces=self.namespaces)
            if code_elem:
                imm_data['vaccine_name'] = code_elem[0].get('displayName', '')
                imm_data['cvx_code'] = code_elem[0].get('code', '')
            
            # Administration date
            effective_time = entry.xpath(".//hl7:effectiveTime", namespaces=self.namespaces)
            if effective_time:
                imm_data['administration_date'] = self.parse_date(effective_time[0].get('value'))
            
            # Route
            route_elem = entry.xpath(".//hl7:routeCode", namespaces=self.namespaces)
            if route_elem:
                imm_data['route'] = route_elem[0].get('displayName', '')
            
            if imm_data:
                immunizations.append(imm_data)
        
        logger.info(f"Parsed {len(immunizations)} immunizations")
        return immunizations
    
    def parse_all_sections(self) -> Dict[str, List[Dict[str, Any]]]:
        """Parse all supported sections."""
        return {
            'medications': self.parse_medications(),
            'allergies': self.parse_allergies(),
            'problems': self.parse_problems(),
            'procedures': self.parse_procedures(),
            'results': self.parse_results(),
            'vitals': self.parse_vitals(),
            'immunizations': self.parse_immunizations()
        }