# ISAZI Recruitment Analytics Dashboard

Interactive dashboard for visualizing recruitment metrics and analytics, built with Streamlit and Python.

## Quick Start

### Option 1: Run in Google Colab (Fastest)

1. Open one of these notebooks in Colab:
   - [`colab_run_dashboard_lightweight.ipynb`](colab_run_dashboard_lightweight.ipynb) (Recommended, faster setup)
   - [`colab_run_dashboard.ipynb`](colab_run_dashboard.ipynb) (Full version with heavy ML packages)

2. Run all cells in order. The last cell will print a public URL where you can view the dashboard.

### Option 2: Run Locally

1. Create conda environment:
```bash
conda create -n isazi-recruitment python=3.9
conda activate isazi-recruitment
```

2. Install dependencies:
```bash
# Core packages (required)
pip install streamlit pytest pandas numpy scikit-learn plotly xgboost

# Optional: Heavy packages for advanced analytics
pip install prophet shap optuna
```

3. Start the dashboard:
```bash
# Option A: Direct start
streamlit run dashboard.py

# Option B: Using helper script
./run_dashboard.sh
```

## Project Structure

- `dashboard.py` - Main Streamlit application
- `recruitment_functions.py` - Core data processing and visualization
- `advanced_analytics.py` - ML models and predictions
- Notebooks:
  - `recruitment_dashboard.ipynb` - Development notebook
  - `colab_run_dashboard.ipynb` - Full Colab runner (all packages)
  - `colab_run_dashboard_lightweight.ipynb` - Fast Colab runner

## Development

1. Run tests:
```bash
pytest tests/
pytest "ISAZI DASH/tests"  # Additional test folder
```

2. Create sample data:
```python
from recruitment_functions import create_sample_data
create_sample_data(force=True)  # Rebuilds the SQLite database
```

## Data Persistence

To persist data between Colab sessions:
1. Mount Google Drive in the notebook
2. Change the SQLite database path to your Drive
3. The data will remain after the Colab runtime ends

## Troubleshooting

1. Import errors:
   - Ensure you're in the correct conda environment
   - Check that all required packages are installed
   - Run `pip install -r requirements.txt`

2. Database errors:
   - Try recreating sample data: `create_sample_data(force=True)`
   - Check SQLite file permissions

3. Colab issues:
   - For "RAM exceeded" - Use lightweight notebook
   - For timeout - Reconnect and rerun failed cell

## Contributing

1. Fork the repository
2. Create a feature branch
3. Run tests before committing
4. Submit a pull request