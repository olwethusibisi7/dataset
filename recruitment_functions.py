from pathlib import Path
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
import random
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# Database setup
HERE = Path(__file__).resolve().parent
DB_PATH = HERE / "recruitment.db"
ENGINE = create_engine(f"sqlite:///{DB_PATH}")

# SQL query used by loader
BASE_JOIN_QUERY = """
SELECT 
    a.application_id,
    a.status as application_status,
    a.apply_date,
    c.candidate_id,
    c.source,
    c.years_experience,
    c.education_level,
    j.title as job_title,
    j.department,
    j.location
FROM applications a
JOIN candidates c ON a.candidate_id = c.candidate_id
JOIN job_postings j ON a.job_id = j.job_id
"""


def ensure_db_exists(engine=ENGINE):
    """Create tables if they do not exist (no-op if DB already populated)."""
    create_tables_query = """
CREATE TABLE IF NOT EXISTS candidates (
    candidate_id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT,
    source TEXT,
    application_date DATE,
    years_experience INTEGER,
    education_level TEXT
);

CREATE TABLE IF NOT EXISTS interviews (
    interview_id INTEGER PRIMARY KEY,
    candidate_id INTEGER,
    interview_date DATE,
    interview_stage TEXT,
    interviewer TEXT,
    status TEXT,
    feedback_score INTEGER,
    FOREIGN KEY (candidate_id) REFERENCES candidates(candidate_id)
);

CREATE TABLE IF NOT EXISTS job_postings (
    job_id INTEGER PRIMARY KEY,
    title TEXT,
    department TEXT,
    location TEXT,
    required_skills TEXT,
    posting_date DATE,
    status TEXT
);

CREATE TABLE IF NOT EXISTS applications (
    application_id INTEGER PRIMARY KEY,
    candidate_id INTEGER,
    job_id INTEGER,
    apply_date DATE,
    status TEXT,
    FOREIGN KEY (candidate_id) REFERENCES candidates(candidate_id),
    FOREIGN KEY (job_id) REFERENCES job_postings(job_id)
);
"""
    with engine.connect() as conn:
        # SQLite's default driver does not allow executing multiple
        # SQL statements in one execute() call. Split the DDL script
        # on semicolons and execute each non-empty statement separately.
        for stmt in create_tables_query.split(";"):
            stmt = stmt.strip()
            if not stmt:
                continue
            conn.execute(text(stmt))
        conn.commit()


def random_date(start_date, end_date):
    """Return random datetime between start and end (date-only)."""
    time_between = end_date - start_date
    days_between = max(1, time_between.days)
    random_days = random.randrange(days_between)
    return (start_date + timedelta(days=random_days)).date()


def create_sample_data(engine=ENGINE, force=False):
    """Populate sample data into the SQLite DB. If force=True, overwrite tables."""
    ensure_db_exists(engine)

    # Check whether applications table has rows
    try:
        existing = pd.read_sql("SELECT count(1) as cnt FROM applications", engine)
        if not force and existing['cnt'].iloc[0] > 0:
            logger.info("Database already populated; skipping sample data creation.")
            return
    except Exception:
        # If read fails, proceed to write sample data
        pass

    start_date = datetime(2024, 1, 1)
    end_date = datetime(2025, 11, 1)
    sources = ['LinkedIn', 'Company Website', 'Referral', 'Job Board', 'University Partnership']
    education_levels = ["Bachelor's", "Master's", 'PhD', 'Bootcamp']
    locations = ['Remote', 'New York', 'San Francisco', 'London', 'Singapore']

    # Generate candidates
    candidates_data = []
    for i in range(100):
        candidates_data.append({
            'candidate_id': i + 1,
            'name': f'Candidate {i+1}',
            'email': f'candidate{i+1}@example.com',
            'source': random.choice(sources),
            'application_date': random_date(start_date, end_date),
            'years_experience': random.randint(0, 15),
            'education_level': random.choice(education_levels)
        })
    candidates_df = pd.DataFrame(candidates_data)

    # Job postings
    job_titles = ['Data Scientist', 'Senior Data Scientist', 'ML Engineer', 'Data Science Manager']
    departments = ['Analytics', 'Research', 'Product', 'Engineering']

    job_postings_data = []
    for i in range(10):
        job_postings_data.append({
            'job_id': i + 1,
            'title': random.choice(job_titles),
            'department': random.choice(departments),
            'location': random.choice(locations),
            'required_skills': 'Python, SQL, Machine Learning',
            'posting_date': random_date(start_date, end_date),
            'status': random.choice(['Open', 'Closed', 'On Hold'])
        })
    job_postings_df = pd.DataFrame(job_postings_data)

    # Applications
    application_statuses = {
        'Applied': 0.3,
        'Screening': 0.2,
        'Interviewing': 0.2,
        'Offered': 0.1,
        'Hired': 0.1,
        'Rejected': 0.1
    }
    applications_data = []
    for candidate in candidates_data:
        num_applications = random.randint(1, 3)
        for _ in range(num_applications):
            status = random.choices(list(application_statuses.keys()), weights=list(application_statuses.values()))[0]
            applications_data.append({
                'application_id': len(applications_data) + 1,
                'candidate_id': candidate['candidate_id'],
                'job_id': random.randint(1, 10),
                'apply_date': candidate['application_date'],
                'status': status
            })
    applications_df = pd.DataFrame(applications_data)

    # Write to DB
    candidates_df.to_sql('candidates', engine, if_exists='replace', index=False)
    job_postings_df.to_sql('job_postings', engine, if_exists='replace', index=False)
    applications_df.to_sql('applications', engine, if_exists='replace', index=False)
    logger.info('Sample data written to database')


def load_recruitment_data(engine=ENGINE):
    """Load joined recruitment data as a pandas DataFrame."""
    try:
        df = pd.read_sql(BASE_JOIN_QUERY, engine)
        # Normalize column names
        df.columns = [c.lower() for c in df.columns]
        # Parse dates
        if 'apply_date' in df.columns:
            df['apply_date'] = pd.to_datetime(df['apply_date'])
        return df
    except Exception as e:
        logger.error(f"Failed to load recruitment data: {e}")
        return pd.DataFrame()


# Visualization helpers (return plotly objects)
import plotly.graph_objects as go
import plotly.express as px


def create_application_funnel(df: pd.DataFrame = None):
    """Return a Plotly funnel figure for the provided DataFrame. If df is None, it will be loaded."""
    if df is None:
        df = load_recruitment_data()
    if df.empty:
        return None

    funnel_data = df['application_status'].value_counts().reset_index()
    funnel_data.columns = ['stage', 'count']
    stage_order = ['Applied', 'Screening', 'Interviewing', 'Offered', 'Hired', 'Rejected']
    funnel_data['stage'] = pd.Categorical(funnel_data['stage'], categories=stage_order, ordered=True)
    funnel_data = funnel_data.sort_values('stage')

    fig = go.Figure(go.Funnel(
        y=funnel_data['stage'],
        x=funnel_data['count'],
        textinfo='value+percent initial'
    ))
    fig.update_layout(title='Application Funnel', showlegend=False, height=420)
    return fig

def calculate_application_funnel(df: pd.DataFrame = None):
    """Compatibility wrapper for older API/tests.

    Some tests expect a function named `calculate_application_funnel`.
    Delegate to `create_application_funnel` to preserve a single
    implementation point.
    """
    return create_application_funnel(df)

def create_source_effectiveness(df: pd.DataFrame = None, department_filter: str = None):
    """Return (fig, metrics_df) showing applications and hires by source."""
    if df is None:
        df = load_recruitment_data()
    if df.empty:
        return None, pd.DataFrame()
    if department_filter and department_filter != 'All':
        df = df[df['department'] == department_filter]

    grouped = df.groupby('source').agg({'application_id': 'count', 'application_status': lambda x: (x == 'Hired').sum()}).reset_index()
    grouped.columns = ['source', 'total_applications', 'hires']
    grouped['conversion_rate'] = (grouped['hires'] / grouped['total_applications'] * 100).round(2)
    grouped = grouped.sort_values('conversion_rate', ascending=False)

    fig = px.bar(grouped, x='source', y=['total_applications', 'hires'], barmode='group', title='Recruitment Source Effectiveness')
    return fig, grouped


def analyze_experience_education(df: pd.DataFrame = None):
    """Return pivot table of experience range x education level with hire rate."""
    if df is None:
        df = load_recruitment_data()
    if df.empty:
        return pd.DataFrame()

    df['experience_range'] = pd.cut(df['years_experience'], bins=[-1, 2, 5, 8, float('inf')], labels=['0-2 years', '3-5 years', '6-8 years', '8+ years'])
    pivot = pd.pivot_table(df, index=['experience_range', 'education_level'], columns='application_status', values='application_id', aggfunc='count', fill_value=0).reset_index()
    # Ensure columns exist for calculation
    for col in ['Applied', 'Screening', 'Interviewing', 'Offered', 'Hired', 'Rejected']:
        if col not in pivot.columns:
            pivot[col] = 0
    pivot['hire_rate'] = (pivot['Hired'] / pivot[['Applied', 'Screening', 'Interviewing', 'Offered', 'Hired', 'Rejected']].sum(axis=1) * 100).round(2)
    return pivot


if __name__ == '__main__':
    # Quick local run to create sample data if file executed directly
    create_sample_data(force=False)
    df = load_recruitment_data()
    print('Rows loaded:', len(df))
