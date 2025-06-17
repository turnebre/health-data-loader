# Health Data Directory

This directory is where you should place your C-CDA XML health data files for processing.

## Supported File Types

- **C-CDA XML files** (`.xml`) - Primary format exported from healthcare providers
- **PDF files** (`.pdf`) - Human-readable versions (not processed, kept for reference)
- **XSL stylesheets** (`.xsl`) - For viewing XML files in browsers

## Example File Structure

```
health_data/
├── README.md                           # This file
├── .gitkeep                           # Keeps directory in Git
├── Document_XML/                      # XML files subdirectory
│   ├── your_health_export.xml         # Your C-CDA file
│   └── continuity_of_care.xml         # Additional exports
├── your_health_summary.pdf            # Human-readable version
└── stylesheet.xsl                     # Optional: for browser viewing
```

## Getting Your Health Data

1. **Request C-CDA Export** from your doctor's office or hospital
   - Ask for "C-CDA XML export" or "Consolidated Clinical Document Architecture file"
   - Common file names include: `*AmbulatorySummary*.xml`, `*ContinuityOfCare*.xml`

2. **Save Files Here** - Place your XML files in this directory or the `Document_XML/` subdirectory

3. **Run Pipeline** - Use the health pipeline to process your data:
   ```bash
   python health_pipeline.py health_data/your_file.xml --summary
   ```

## Privacy & Security

⚠️ **IMPORTANT**: 
- These files contain your Personal Health Information (PHI)
- The `.gitignore` file ensures health data files are NEVER committed to Git
- Keep these files secure and back them up safely
- Only share the codebase, never the actual health data files

## File Formats Supported

- **C-CDA XML**: Primary format for health data exchange
- **HL7 FHIR**: Future support planned
- **Blue Button**: May work if exported as C-CDA format

## Troubleshooting

If the pipeline can't find your file:
- Check the file path is correct
- Ensure the file has a `.xml` extension
- Verify the file is a valid C-CDA document (opens in text editor and contains XML)
- Try using absolute path: `python health_pipeline.py /full/path/to/your/file.xml`