# Data Science Recruitment Dashboard

This workspace contains a Jupyter notebook and a Streamlit dashboard for analyzing recruitment data (Data Science roles).

Files relevant to the dashboard:
- `recruitment_dashboard.ipynb` — Notebook with setup, data generation, and analysis sections.
- `recruitment_functions.py` — Module with DB setup, sample-data creator, data loading and plotting helpers.
- `dashboard.py` — Streamlit app that imports `recruitment_functions` and builds the interactive UI.
- `requirements.txt` — Python dependencies to install.

Quick start
1. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Initialize sample data (optional — the dashboard will call this automatically):

```bash
python -m recruitment_functions
```

4. Run the dashboard:

```bash
streamlit run dashboard.py
```

Run tests:

```bash
pytest -q
```

Notes
- The dashboard uses a local SQLite file `recruitment.db` stored in the same folder as `recruitment_functions.py`.
- For production, change `recruitment_functions.ENGINE` to a Postgres/MySQL connection string and remove the sample data creator call.
