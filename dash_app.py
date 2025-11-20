"""
Minimal Dash app wrapper that falls back to a sample CSV when DB credentials are missing.
- Reads MySQL if env vars present, otherwise uses `recruitment_data_sample.csv`.
- Lightweight layout showing application counts by status and source.
"""
import os
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")

SAMPLE_CSV = Path(__file__).with_name("recruitment_data_sample.csv")


def load_data():
    # If DB creds present, try to read from MySQL. Otherwise, use sample CSV.
    if DB_HOST and DB_USER and DB_PASS and DB_NAME:
        try:
            import sqlalchemy
            engine = sqlalchemy.create_engine(f"mysql+mysqlconnector://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}")
            df = pd.read_sql_table("applications", engine)
            return df
        except Exception as e:
            print("Failed to read from MySQL, falling back to sample CSV:", e)

    if SAMPLE_CSV.exists():
        df = pd.read_csv(SAMPLE_CSV, parse_dates=["application_date", "interview_date"], keep_default_na=False)
        return df

    # Fallback: empty dataframe with expected columns
    cols = [
        "candidate_id",
        "application_id",
        "job_posting_id",
        "application_date",
        "status",
        "source",
        "qualifications",
        "interview_date",
        "interview_score",
    ]
    return pd.DataFrame(columns=cols)


data = load_data()

# Build a minimal Dash app
from dash import Dash, html, dcc
import plotly.express as px

app = Dash(__name__)

status_counts = data["status"].fillna("Unknown").value_counts().reset_index()
status_counts.columns = ["status", "count"]

source_counts = data["source"].fillna("Unknown").value_counts().reset_index()
source_counts.columns = ["source", "count"]

fig_status = px.bar(status_counts, x="status", y="count", title="Applications by Status")
fig_source = px.bar(source_counts, x="source", y="count", title="Applications by Source")

app.layout = html.Div([
    html.H1("Recruitment Dashboard (Dash)") ,
    html.Div("Data source: MySQL if env provided else sample CSV"),
    dcc.Graph(figure=fig_status),
    dcc.Graph(figure=fig_source),
])

if __name__ == "__main__":
    app.run_server(debug=True, port=8050)
