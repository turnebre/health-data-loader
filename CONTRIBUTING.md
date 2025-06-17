# Contributing to Health Data Pipeline

Thank you for your interest in contributing to this health data pipeline project!

## 🚀 Quick Start for Developers

### 1. Clone the Repository
```bash
git clone <repository-url>
cd health-data-loader
```

### 2. Set Up Development Environment
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Prepare Test Data
- Place your C-CDA XML health data files in the `health_data/` directory
- The pipeline supports files exported from most healthcare providers
- See `health_data/README.md` for details on obtaining health data

### 4. Test the Pipeline
```bash
# Run with your health data
python health_pipeline.py health_data/your_file.xml --summary

# Run with debug logging
python health_pipeline.py health_data/your_file.xml --log-level DEBUG
```

## 🔒 Privacy & Security Guidelines

### Critical Privacy Rules
- **NEVER commit health data files** (`.xml`, `.pdf`, `.duckdb`)
- The `.gitignore` file protects against accidental commits
- Only commit code improvements, never actual health data
- Test with your own data, but don't include it in commits

### Safe Development Practices
- Use synthetic or anonymized test data when sharing examples
- If reporting bugs, redact all personal information
- Be mindful of log files that might contain sensitive data

## 🧪 Testing

### Manual Testing
1. Test with different C-CDA XML file formats
2. Verify data extraction accuracy by spot-checking results
3. Test error handling with invalid/corrupted files
4. Check database schema and data types

### Code Quality
- Follow PEP 8 Python style guidelines
- Add type hints where appropriate
- Include docstrings for new functions/classes
- Test edge cases and error conditions

## 📁 Project Structure

```
health-data-loader/
├── README.md              # Main documentation
├── CONTRIBUTING.md        # This file
├── requirements.txt       # Python dependencies
├── .gitignore            # Excludes sensitive data
├── health_pipeline.py    # Main pipeline script
├── xml_parser.py         # C-CDA XML parsing
├── data_transformers.py  # Data cleaning/transformation
├── database.py           # Database schema
├── simple_loader.py      # Data loading utilities
├── data_loader.py        # Alternative loader (legacy)
└── health_data/          # Where users place their data
    ├── README.md         # Instructions for users
    └── .gitkeep          # Preserves directory structure
```

## 🐛 Reporting Issues

When reporting bugs or requesting features:

1. **Check existing issues** first
2. **Use descriptive titles** (e.g., "XML parsing fails for Kaiser Permanente exports")
3. **Include system information**:
   - Python version
   - Operating system
   - DuckDB version
   - Pipeline version/commit
4. **Provide minimal reproduction steps**
5. **Redact all personal health information** from logs/examples

### Bug Report Template
```
**Description**: Brief description of the issue

**Steps to Reproduce**:
1. Run pipeline with...
2. Expected behavior...
3. Actual behavior...

**Environment**:
- OS: macOS/Windows/Linux
- Python version: 
- DuckDB version:

**Logs** (redacted):
```

## 💡 Feature Requests

We welcome suggestions for:
- Support for additional health data formats
- New data analysis features
- Performance improvements
- Database schema enhancements
- Additional export formats

## 🔧 Development Areas

### Current Priorities
- **HL7 FHIR support**: Adding parser for FHIR JSON/XML
- **Data visualization**: Built-in health data charts
- **Performance optimization**: Faster processing of large files
- **Additional healthcare providers**: Testing with more C-CDA variants

### Code Architecture
- **Modular design**: Each component (parser, transformer, loader) is separate
- **Database-agnostic**: Easy to swap DuckDB for PostgreSQL/SQLite
- **Extensible**: Adding new health data sections is straightforward

## 📋 Pull Request Process

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature-name`
3. **Make your changes** with appropriate tests
4. **Ensure no health data is included** in your commits
5. **Update documentation** if needed
6. **Submit pull request** with clear description

### PR Requirements
- [ ] Code follows project style guidelines
- [ ] No sensitive health data included
- [ ] Documentation updated (if applicable)
- [ ] Manual testing completed
- [ ] Descriptive commit messages

## 🤝 Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Protect privacy and sensitive information
- Help newcomers learn the codebase
- Follow security best practices

## 📞 Getting Help

- **Issues**: For bugs and feature requests
- **Discussions**: For questions and general discussion
- **Documentation**: Check README.md and code comments

## 🎯 Vision

This project aims to empower individuals to:
- Own and control their health data
- Gain insights from their medical history
- Maintain privacy through local processing
- Contribute to open-source healthcare tools

Thank you for contributing to better health data tools! 🏥✨