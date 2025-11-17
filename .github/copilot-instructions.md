# AI Assistant Instructions for Data Science Dashboard Project

## Project Overview
This is a data science recruitment analytics project consisting of:
- A Streamlit dashboard for visualizing recruitment metrics
- Jupyter notebooks for analysis and data exploration
- Python modules for data processing and visualization
- Sample datasets for testing and development

## Key Components

### Core Architecture
- `dashboard.py`: Main Streamlit application entry point
- `recruitment_functions.py`: Core business logic and data processing
- SQLite database (`recruitment.db`) for data storage
- Sample datasets in CSV format for testing

### Data Flow
1. Data is stored in SQLite database with tables:
   - candidates
   - interviews
   - job_postings
   - applications
2. `recruitment_functions.py` handles:
   - Database connections via SQLAlchemy
   - Data loading and transformations
   - Visualization generation using Plotly
3. `dashboard.py` presents interactive UI with:
   - Application funnel visualization
   - Source effectiveness metrics
   - Key recruitment statistics
   - Qualification analysis

## Development Workflow

### Environment Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Database Initialization
- Database auto-initializes with sample data via `create_sample_data()`
- Tables are created if they don't exist using `ensure_db_exists()`
- Sample data generation can be forced with `create_sample_data(force=True)`

### Running the Application
1. Ensure virtual environment is activated
2. Run: `streamlit run dashboard.py`
3. Access dashboard at http://localhost:8501

### Testing
- Run tests with: `pytest -q`
- Test files located in `tests/` directory

## Project Patterns

### Data Processing
- Use pandas for data manipulation (`load_recruitment_data()`)
- Standardize column names to lowercase
- Parse dates using pandas datetime
- Handle empty DataFrames gracefully

### Visualization
- Use Plotly for interactive charts
- Standard chart types:
  - Funnel charts for application stages
  - Bar charts for source effectiveness
  - Pivot tables for qualification analysis

### Error Handling
- Functions return empty DataFrames or None on failure
- Logging used for error tracking
- Database operations wrapped in try-except blocks

## Key Files for Reference
- `recruitment_functions.py`: Check for database queries and data processing patterns
- `dashboard.py`: Review for Streamlit component structure
- `RECRUITMENT_README.md`: Additional setup instructions

## Integration Points
- SQLAlchemy for database operations
- Streamlit for web interface
- Plotly for visualization
- Pandas for data processing

Remember to maintain consistent error handling patterns and follow the established data processing flow when making changes.