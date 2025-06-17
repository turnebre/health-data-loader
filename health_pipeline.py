#!/usr/bin/env python3

import argparse
import logging
import sys
import os
from datetime import datetime

from xml_parser import CCDAParser
from data_transformers import DataTransformer
from simple_loader import SimpleDataLoader

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('health_pipeline.log')
    ]
)
logger = logging.getLogger(__name__)

class HealthDataPipeline:
    """Main health data processing pipeline."""
    
    def __init__(self, xml_file_path: str, db_path: str = "health_data.duckdb"):
        self.xml_file_path = xml_file_path
        self.db_path = db_path
        
        # Initialize components
        self.parser = None
        self.transformer = DataTransformer()
        self.loader = None
    
    def validate_input_file(self) -> bool:
        """Validate that the input XML file exists and is readable."""
        if not os.path.exists(self.xml_file_path):
            logger.error(f"XML file not found: {self.xml_file_path}")
            return False
        
        if not os.access(self.xml_file_path, os.R_OK):
            logger.error(f"Cannot read XML file: {self.xml_file_path}")
            return False
        
        # Check file size
        file_size = os.path.getsize(self.xml_file_path)
        logger.info(f"Input file size: {file_size:,} bytes")
        
        return True
    
    def run(self) -> bool:
        """Execute the complete health data pipeline."""
        try:
            logger.info("Starting health data pipeline")
            logger.info(f"Input XML file: {self.xml_file_path}")
            logger.info(f"Output database: {self.db_path}")
            
            # Step 1: Validate input
            if not self.validate_input_file():
                return False
            
            # Step 2: Parse XML
            logger.info("Step 1: Parsing XML document...")
            self.parser = CCDAParser(self.xml_file_path)
            parsed_data = self.parser.parse_all_sections()
            
            # Log parsing results
            for section, data in parsed_data.items():
                logger.info(f"Parsed {len(data)} records from {section} section")
            
            # Step 3: Transform data
            logger.info("Step 2: Transforming data...")
            transformed_data = self.transformer.transform_all_data(parsed_data)
            
            # Log transformation results
            for section, df in transformed_data.items():
                logger.info(f"Transformed {len(df)} {section} records")
            
            # Step 4: Load into database
            logger.info("Step 3: Loading data into database...")
            self.loader = SimpleDataLoader(self.db_path)
            load_results = self.loader.load_all_data(transformed_data)
            
            # Log loading results
            total_records = 0
            for section, count in load_results.items():
                logger.info(f"Loaded {count} {section} records")
                total_records += count
            
            logger.info(f"Pipeline completed successfully! Total records loaded: {total_records}")
            
            # Step 5: Verify data in database
            logger.info("Step 4: Verifying data in database...")
            table_counts = self.loader.get_table_counts()
            
            logger.info("Final database record counts:")
            for table, count in table_counts.items():
                logger.info(f"  {table}: {count:,} records")
            
            return True
            
        except Exception as e:
            logger.error(f"Pipeline failed with error: {e}")
            return False
        
        finally:
            # Clean up resources
            if self.loader:
                self.loader.close()
    
    def get_database_summary(self) -> dict:
        """Get a summary of the data in the database."""
        if not self.loader:
            self.loader = SimpleDataLoader(self.db_path)
        
        return self.loader.get_table_counts()

def main():
    """Main entry point for the health data pipeline."""
    parser = argparse.ArgumentParser(description='Health Data Pipeline - Extract and load C-CDA health data')
    
    parser.add_argument(
        'xml_file',
        help='Path to the C-CDA XML file to process'
    )
    
    parser.add_argument(
        '--database',
        '-d',
        default='health_data.duckdb',
        help='Path to DuckDB database file (default: health_data.duckdb)'
    )
    
    parser.add_argument(
        '--log-level',
        '-l',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Set logging level (default: INFO)'
    )
    
    parser.add_argument(
        '--summary',
        '-s',
        action='store_true',
        help='Show database summary after processing'
    )
    
    args = parser.parse_args()
    
    # Set logging level
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    # Create and run pipeline
    pipeline = HealthDataPipeline(args.xml_file, args.database)
    
    start_time = datetime.now()
    success = pipeline.run()
    end_time = datetime.now()
    
    # Show execution time
    duration = end_time - start_time
    logger.info(f"Pipeline execution time: {duration}")
    
    # Show summary if requested
    if args.summary and success:
        print("\n" + "="*50)
        print("DATABASE SUMMARY")
        print("="*50)
        summary = pipeline.get_database_summary()
        for table, count in summary.items():
            print(f"{table.capitalize()}: {count:,} records")
        print("="*50)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()