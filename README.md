# Health Data Pipeline

A Python-based data pipeline for extracting, transforming, and loading personal health data from C-CDA (Consolidated Clinical Document Architecture) XML files into a local DuckDB database for analysis and querying.

## 🎯 Purpose & Goals

This project enables you to:
- **Extract** structured health data from C-CDA XML exports (common format from hospitals/clinics)
- **Transform** and clean the data for analysis
- **Load** data into a fast, local DuckDB database
- **Query** your complete health history using SQL
- **Analyze** trends in medications, lab results, vitals, and more
- **Maintain** complete control over your personal health data locally

## 📊 Supported Health Data Types

The pipeline extracts and stores:
- **Medications** - Current and historical prescriptions, dosages, dates
- **Allergies** - Known allergies and reactions
- **Problems/Diagnoses** - Medical conditions with ICD-10 codes
- **Procedures** - Medical procedures with CPT codes  
- **Lab Results** - Blood work, tests, and measurements with reference ranges
- **Vital Signs** - Blood pressure, weight, height, BMI, heart rate, temperature
- **Immunizations** - Vaccination history with dates and manufacturers

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Clone or download the project
cd health-data-loader

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Process Your Health Data

```bash
# Basic usage - process C-CDA XML file
python health_pipeline.py health_data/Document_XML/health_data.xml

# With summary and custom database location
python health_pipeline.py health_data/Document_XML/health_data.xml --database my_health.duckdb --summary

# With debug logging
python health_pipeline.py health_data/Document_XML/health_data.xml --log-level DEBUG --summary
```

### 3. Example Output
```
INFO:__main__:Pipeline completed successfully! Total records loaded: 695
==================================================
DATABASE SUMMARY
==================================================
Medications: 50 records
Allergies: 1 records  
Problems: 15 records
Procedures: 12 records
Results: 571 records
Vitals: 68 records
Immunizations: 46 records
==================================================
```

## 💾 Database Schema

### Medications Table
```sql
CREATE TABLE medications (
    id INTEGER,
    medication_name VARCHAR,    -- Drug name (e.g., "Lisinopril")
    dosage VARCHAR,            -- Dose amount (e.g., "10mg")
    frequency VARCHAR,         -- How often (e.g., "Daily")
    route VARCHAR,             -- How taken (e.g., "Oral")
    start_date DATE,           -- When started
    end_date DATE,             -- When stopped (if applicable)
    status VARCHAR,            -- Active, Discontinued, etc.
    prescriber VARCHAR,        -- Prescribing doctor
    ndc_code VARCHAR,          -- National Drug Code
    rxnorm_code VARCHAR,       -- RxNorm code
    instructions TEXT,         -- Special instructions
    created_at TIMESTAMP       -- When added to database
);
```

### Lab Results Table
```sql
CREATE TABLE results (
    id INTEGER,
    test_name VARCHAR,         -- Test name (e.g., "Hemoglobin A1c")
    test_date DATE,            -- When test was performed
    result_value VARCHAR,      -- Test result (e.g., "6.2")
    unit VARCHAR,              -- Units (e.g., "%", "mg/dL")
    reference_range VARCHAR,   -- Normal range (e.g., "4.0-6.0")
    abnormal_flag VARCHAR,     -- High, Low, Normal
    status VARCHAR,            -- Final, Preliminary, etc.
    loinc_code VARCHAR,        -- LOINC code
    provider VARCHAR,          -- Ordering provider
    notes TEXT,                -- Additional notes
    created_at TIMESTAMP
);
```

### Vitals Table
```sql
CREATE TABLE vitals (
    id INTEGER,
    measurement_date DATE,     -- Date of measurement
    measurement_time TIME,     -- Time of measurement
    height_cm DECIMAL(8,2),    -- Height in centimeters
    weight_kg DECIMAL(8,2),    -- Weight in kilograms
    bmi DECIMAL(8,2),          -- Body Mass Index
    systolic_bp INTEGER,       -- Systolic blood pressure
    diastolic_bp INTEGER,      -- Diastolic blood pressure
    heart_rate INTEGER,        -- Heart rate (BPM)
    temperature_c DECIMAL(4,1), -- Temperature in Celsius
    respiratory_rate INTEGER,   -- Breaths per minute
    oxygen_saturation DECIMAL(5,2), -- O2 saturation %
    notes TEXT,
    created_at TIMESTAMP
);
```

*Similar schemas exist for allergies, problems, procedures, and immunizations tables.*

## 🔍 Querying Your Health Data

### Connect to Database

#### Using DuckDB CLI
```bash
# Install DuckDB CLI if needed
# brew install duckdb  # On macOS
# Or download from https://duckdb.org

duckdb health_data.duckdb
```

#### Using Python
```python
import duckdb
import pandas as pd

# Connect to your health database
conn = duckdb.connect('health_data.duckdb')

# Query data
df = conn.execute("SELECT * FROM medications WHERE status = 'Active'").df()
print(df)
```

### Sample Queries

#### 1. Current Active Medications
```sql
SELECT medication_name, dosage, frequency, start_date
FROM medications 
WHERE status = 'Active' 
ORDER BY start_date DESC;
```

#### 2. Lab Results Trends (e.g., Cholesterol over time)
```sql
SELECT test_date, result_value, unit, reference_range
FROM results 
WHERE test_name LIKE '%Cholesterol%'
ORDER BY test_date DESC
LIMIT 10;
```

#### 3. Blood Pressure History
```sql
SELECT measurement_date, systolic_bp, diastolic_bp
FROM vitals 
WHERE systolic_bp IS NOT NULL 
ORDER BY measurement_date DESC;
```

#### 4. Recent Procedures
```sql
SELECT procedure_name, procedure_date, provider
FROM procedures 
ORDER BY procedure_date DESC
LIMIT 5;
```

#### 5. Abnormal Lab Results
```sql
SELECT test_name, test_date, result_value, unit, abnormal_flag
FROM results 
WHERE abnormal_flag IN ('High', 'Low', 'Critical')
ORDER BY test_date DESC;
```

#### 6. Vaccination History
```sql
SELECT vaccine_name, administration_date, manufacturer
FROM immunizations 
ORDER BY administration_date DESC;
```

### Advanced Analytics with Python

```python
import duckdb
import pandas as pd
import matplotlib.pyplot as plt

# Connect to database
conn = duckdb.connect('health_data.duckdb')

# Weight trend analysis
weight_data = conn.execute("""
    SELECT measurement_date, weight_kg 
    FROM vitals 
    WHERE weight_kg IS NOT NULL 
    ORDER BY measurement_date
""").df()

# Convert to datetime and plot
weight_data['measurement_date'] = pd.to_datetime(weight_data['measurement_date'])
plt.figure(figsize=(10, 6))
plt.plot(weight_data['measurement_date'], weight_data['weight_kg'])
plt.title('Weight Trend Over Time')
plt.xlabel('Date')
plt.ylabel('Weight (kg)')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Lab results summary
lab_summary = conn.execute("""
    SELECT test_name, COUNT(*) as test_count, 
           MIN(test_date) as first_test, 
           MAX(test_date) as latest_test
    FROM results 
    GROUP BY test_name 
    ORDER BY test_count DESC
""").df()

print("Lab Test Summary:")
print(lab_summary.head(10))
```

## 📥 Adding New Health Data

### 1. Export Data from Your Healthcare Provider
- Request C-CDA export from your doctor's office/hospital
- Common file names: `*AmbulatorySummary*.xml`, `*ContinuityOfCare*.xml`
- Save XML file to a known location

### 2. Process New Data
```bash
# Process new health data file
python health_pipeline.py new_health_export.xml --summary

# Use custom database name to keep separate
python health_pipeline.py new_data.xml --database health_2024.duckdb --summary
```

### 3. Data Update Strategy

**Option A: Full Refresh (Recommended)**
- The pipeline clears existing data and reloads everything
- Ensures data consistency
- Best for periodic updates (monthly/quarterly)

**Option B: Separate Databases**
- Process each export into a separate database
- Query across multiple databases if needed
- Useful for comparing data from different providers

### 4. Verify Data Quality
```bash
# Check processing logs
tail -f health_pipeline.log

# Validate record counts
python health_pipeline.py your_file.xml --summary --log-level DEBUG
```

## 🔧 Data Export & Integration

### Export to CSV
```python
import duckdb

conn = duckdb.connect('health_data.duckdb')

# Export all medications to CSV
conn.execute("COPY medications TO 'medications.csv' (HEADER, DELIMITER ',')");

# Export specific query results
conn.execute("""
    COPY (
        SELECT medication_name, start_date, status 
        FROM medications 
        WHERE status = 'Active'
    ) TO 'active_medications.csv' (HEADER, DELIMITER ',')
""");
```

### Export to JSON
```python
import json
import duckdb

conn = duckdb.connect('health_data.duckdb')

# Get data as Python objects
results = conn.execute("SELECT * FROM results ORDER BY test_date DESC LIMIT 50").fetchall()
columns = [desc[0] for desc in conn.description]

# Convert to list of dictionaries
data = [dict(zip(columns, row)) for row in results]

# Save as JSON
with open('recent_lab_results.json', 'w') as f:
    json.dump(data, f, indent=2, default=str)
```

## ⚠️ Troubleshooting

### Common Issues

1. **"XML file not found"**
   - Check file path is correct
   - Use absolute paths if relative paths fail
   - Ensure file has `.xml` extension

2. **"Parsing errors"**
   - Verify file is valid C-CDA XML
   - Check file isn't corrupted
   - Try with `--log-level DEBUG` for detailed error info

3. **"No data extracted"**
   - XML file may not contain expected sections
   - Check logs for section names found
   - Some exports may have different structure

4. **"Database connection errors"**
   - Ensure DuckDB is properly installed
   - Check file permissions in target directory
   - Try different database filename

### Log Files
- Pipeline logs: `health_pipeline.log`
- Contains detailed parsing and loading information
- Use for debugging issues

### Data Validation
```python
# Quick data quality check
import duckdb

conn = duckdb.connect('health_data.duckdb')

print("Data Overview:")
tables = ['medications', 'allergies', 'problems', 'procedures', 'results', 'vitals', 'immunizations']

for table in tables:
    count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    print(f"{table}: {count} records")

# Check for recent data
print("\\nMost recent records:")
print("Latest medication:", conn.execute("SELECT MAX(start_date) FROM medications").fetchone()[0])
print("Latest lab result:", conn.execute("SELECT MAX(test_date) FROM results").fetchone()[0])
print("Latest vital signs:", conn.execute("SELECT MAX(measurement_date) FROM vitals").fetchone()[0])
```

## 🔒 Privacy & Security

- **Local Storage**: All data stays on your computer
- **No Cloud**: No data sent to external services  
- **File Permissions**: Ensure database files have appropriate permissions
- **Backup**: Consider backing up your `.duckdb` files
- **Sharing**: Be cautious when sharing database files (contains PHI)

## 📁 Project Structure

```
health-data-loader/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── health_pipeline.py        # Main pipeline script
├── xml_parser.py            # C-CDA XML parsing logic
├── data_transformers.py     # Data cleaning and transformation
├── database.py              # Database schema and setup
├── simple_loader.py         # Data loading utilities
├── health_data.duckdb       # Your health database (created after first run)
├── health_pipeline.log      # Processing logs
├── venv/                    # Virtual environment (created by you)
└── health_data/             # Directory for your XML files
    └── Document_XML/
        └── your_health_data.xml
```

## 🆘 Support

If you encounter issues:
1. Check the log file: `health_pipeline.log`
2. Try running with debug logging: `--log-level DEBUG`
3. Verify your XML file is a valid C-CDA export
4. Ensure all dependencies are installed in virtual environment

---

**Disclaimer**: This tool is for personal health data management. Always consult healthcare professionals for medical decisions. Ensure compliance with relevant privacy regulations when handling health data.