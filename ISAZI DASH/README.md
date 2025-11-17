# Isazi Consulting Recruitment Dashboard

An interactive dashboard for tracking and analyzing recruitment metrics at Isazi Consulting.

## Features

- Interactive recruitment pipeline visualization
- Source effectiveness analysis
- Skills demand tracking
- Experience and education level analysis
- Filterable by department and location
- Exportable reports

## Setup

1. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Initialize the database (automatic on first run):
```bash
python recruitment_functions.py
```

4. Run the dashboard:
```bash
streamlit run dashboard.py
```

The dashboard will be available at http://localhost:8501

## Development

- Run tests: `pytest tests/`
- Generate sample data: `python recruitment_functions.py`
- Edit `recruitment_functions.py` to modify data processing
- Edit `dashboard.py` to update the interface

## Project Structure

- `dashboard.py`: Main Streamlit application
- `recruitment_functions.py`: Core business logic and data processing
- `requirements.txt`: Python dependencies
- `tests/`: Test files
- `data/`: Sample data and database

## Notes

- The dashboard uses SQLite for data storage
- Sample data is automatically generated on first run
- For production, update the database connection in `recruitment_functions.py`