from pathlib import Path
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
import random
from datetime import datetime, timedelta
import logging
import os
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import calplot
import io
from matplotlib.figure import Figure
import calendar

# Load environment variables
load_dotenv()

# Set style for matplotlib
plt.style.use('seaborn')
sns.set_palette("husl")

logger = logging.getLogger(__name__)

# Database setup
HERE = Path(__file__).resolve().parent
DB_PATH = HERE / "isazi_recruitment.db"
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
    c.skills,
    j.title as job_title,
    j.department,
    j.location,
    j.salary_range
FROM applications a
JOIN candidates c ON a.candidate_id = c.candidate_id
JOIN job_postings j ON a.job_id = j.job_id
"""

def ensure_db_exists(engine=ENGINE):
    """Create tables if they do not exist."""
    create_tables_query = """
CREATE TABLE IF NOT EXISTS candidates (
    candidate_id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT,
    source TEXT,
    application_date DATE,
    years_experience INTEGER,
    education_level TEXT,
    skills TEXT,
    preferred_location TEXT
);

CREATE TABLE IF NOT EXISTS interviews (
    interview_id INTEGER PRIMARY KEY,
    candidate_id INTEGER,
    interview_date DATE,
    interview_stage TEXT,
    interviewer TEXT,
    status TEXT,
    feedback_score INTEGER,
    feedback_text TEXT,
    FOREIGN KEY (candidate_id) REFERENCES candidates(candidate_id)
);

CREATE TABLE IF NOT EXISTS job_postings (
    job_id INTEGER PRIMARY KEY,
    title TEXT,
    department TEXT,
    location TEXT,
    required_skills TEXT,
    posting_date DATE,
    status TEXT,
    salary_range TEXT,
    employment_type TEXT
);

CREATE TABLE IF NOT EXISTS applications (
    application_id INTEGER PRIMARY KEY,
    candidate_id INTEGER,
    job_id INTEGER,
    apply_date DATE,
    status TEXT,
    notes TEXT,
    FOREIGN KEY (candidate_id) REFERENCES candidates(candidate_id),
    FOREIGN KEY (job_id) REFERENCES job_postings(job_id)
);
"""
    with engine.connect() as conn:
        conn.execute(text(create_tables_query))
        conn.commit()

def random_date(start_date, end_date):
    """Return random datetime between start and end."""
    time_between = end_date - start_date
    days_between = max(1, time_between.days)
    random_days = random.randrange(days_between)
    return (start_date + timedelta(days=random_days)).date()

def create_sample_data(engine=ENGINE, force=False):
    """Populate sample data for Isazi Consulting."""
    ensure_db_exists(engine)

    # Check if data exists
    try:
        existing = pd.read_sql("SELECT count(1) as cnt FROM applications", engine)
        if not force and existing['cnt'].iloc[0] > 0:
            logger.info("Database already populated; skipping sample data creation.")
            return
    except Exception:
        pass

    start_date = datetime(2024, 1, 1)
    end_date = datetime(2025, 11, 1)
    
    # Isazi-specific data
    sources = ['LinkedIn', 'Isazi Website', 'Employee Referral', 'University Partnerships', 'Tech Events']
    education_levels = ["Bachelor's", "Master's", 'PhD', 'Honours']
    locations = ['Johannesburg', 'Cape Town', 'Remote', 'Pretoria', 'Durban']
    skills = ['Python', 'R', 'Machine Learning', 'Deep Learning', 'SQL', 'Data Visualization', 
             'Statistical Analysis', 'Natural Language Processing', 'Computer Vision']

    # Generate candidates
    candidates_data = []
    for i in range(100):
        candidate_skills = ', '.join(random.sample(skills, random.randint(3, 6)))
        candidates_data.append({
            'candidate_id': i + 1,
            'name': f'Candidate {i+1}',
            'email': f'candidate{i+1}@example.com',
            'source': random.choice(sources),
            'application_date': random_date(start_date, end_date),
            'years_experience': random.randint(0, 15),
            'education_level': random.choice(education_levels),
            'skills': candidate_skills,
            'preferred_location': random.choice(locations)
        })
    candidates_df = pd.DataFrame(candidates_data)

    # Job postings
    job_titles = ['Data Scientist', 'Senior Data Scientist', 'ML Engineer', 'Research Scientist',
                 'Data Analytics Consultant', 'AI Solutions Architect']
    departments = ['Research & Development', 'Consulting', 'Product Development', 'Solutions']
    salary_ranges = ['R30,000 - R45,000', 'R45,000 - R65,000', 'R65,000 - R85,000', 'R85,000+']

    job_postings_data = []
    for i in range(10):
        job_postings_data.append({
            'job_id': i + 1,
            'title': random.choice(job_titles),
            'department': random.choice(departments),
            'location': random.choice(locations),
            'required_skills': ', '.join(random.sample(skills, random.randint(4, 7))),
            'posting_date': random_date(start_date, end_date),
            'status': random.choice(['Open', 'Closed', 'On Hold']),
            'salary_range': random.choice(salary_ranges),
            'employment_type': random.choice(['Full-time', 'Contract', 'Part-time'])
        })
    job_postings_df = pd.DataFrame(job_postings_data)

    # Applications with Isazi's recruitment stages
    application_statuses = {
        'Applied': 0.25,
        'Technical Assessment': 0.20,
        'First Interview': 0.15,
        'Technical Interview': 0.15,
        'Final Interview': 0.10,
        'Offer Made': 0.05,
        'Hired': 0.05,
        'Rejected': 0.05
    }
    
    applications_data = []
    for candidate in candidates_data:
        num_applications = random.randint(1, 2)  # More focused applications
        for _ in range(num_applications):
            status = random.choices(list(application_statuses.keys()),
                                 weights=list(application_statuses.values()))[0]
            applications_data.append({
                'application_id': len(applications_data) + 1,
                'candidate_id': candidate['candidate_id'],
                'job_id': random.randint(1, 10),
                'apply_date': candidate['application_date'],
                'status': status,
                'notes': 'Sample application notes'
            })
    applications_df = pd.DataFrame(applications_data)

    # Write to DB
    candidates_df.to_sql('candidates', engine, if_exists='replace', index=False)
    job_postings_df.to_sql('job_postings', engine, if_exists='replace', index=False)
    applications_df.to_sql('applications', engine, if_exists='replace', index=False)
    logger.info('Sample data written to database')

def load_recruitment_data(engine=ENGINE, department=None, date_range=None):
    """Load recruitment data with optional filters."""
    try:
        query = BASE_JOIN_QUERY
        if department or date_range:
            conditions = []
            if department:
                conditions.append(f"j.department = '{department}'")
            if date_range:
                start_date, end_date = date_range
                conditions.append(f"a.apply_date BETWEEN '{start_date}' AND '{end_date}'")
            if conditions:
                query += " WHERE " + " AND ".join(conditions)

        df = pd.read_sql(query, engine)
        df.columns = [c.lower() for c in df.columns]
        if 'apply_date' in df.columns:
            df['apply_date'] = pd.to_datetime(df['apply_date'])
        return df
    except Exception as e:
        logger.error(f"Failed to load recruitment data: {e}")
        return pd.DataFrame()

def create_application_funnel(df: pd.DataFrame = None):
    """Create application funnel visualization."""
    if df is None:
        df = load_recruitment_data()
    if df.empty:
        return None

    funnel_data = df['application_status'].value_counts().reset_index()
    funnel_data.columns = ['stage', 'count']
    stage_order = ['Applied', 'Technical Assessment', 'First Interview', 
                   'Technical Interview', 'Final Interview', 'Offer Made', 
                   'Hired', 'Rejected']
    funnel_data['stage'] = pd.Categorical(funnel_data['stage'], 
                                        categories=stage_order, ordered=True)
    funnel_data = funnel_data.sort_values('stage')

    fig = go.Figure(go.Funnel(
        y=funnel_data['stage'],
        x=funnel_data['count'],
        textinfo='value+percent initial',
        marker=dict(color=['#1f77b4', '#2ca02c', '#ff7f0e', '#9467bd',
                          '#8c564b', '#e377c2', '#2ecc71', '#e74c3c'])
    ))
    fig.update_layout(
        title='Recruitment Pipeline',
        showlegend=False,
        height=500,
        font=dict(size=12)
    )
    return fig

def create_source_effectiveness(df: pd.DataFrame = None, department_filter: str = None):
    """Analyze recruitment source effectiveness."""
    if df is None:
        df = load_recruitment_data()
    if df.empty:
        return None, pd.DataFrame()
    if department_filter and department_filter != 'All':
        df = df[df['department'] == department_filter]

    grouped = df.groupby('source').agg({
        'application_id': 'count',
        'application_status': lambda x: (x == 'Hired').sum()
    }).reset_index()
    grouped.columns = ['source', 'total_applications', 'hires']
    grouped['conversion_rate'] = (grouped['hires'] / grouped['total_applications'] * 100).round(2)
    grouped = grouped.sort_values('conversion_rate', ascending=False)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name='Total Applications',
        x=grouped['source'],
        y=grouped['total_applications'],
        marker_color='#1f77b4'
    ))
    fig.add_trace(go.Bar(
        name='Hires',
        x=grouped['source'],
        y=grouped['hires'],
        marker_color='#2ecc71'
    ))
    
    fig.update_layout(
        title='Recruitment Source Effectiveness',
        barmode='group',
        height=400,
        xaxis_title='Source',
        yaxis_title='Count',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    return fig, grouped

def analyze_skills_demand(df: pd.DataFrame = None):
    """Analyze skills demand across applications."""
    if df is None:
        df = load_recruitment_data()
    if df.empty:
        return None

    # Split skills strings into lists and count occurrences
    all_skills = []
    for skills in df['skills'].dropna():
        all_skills.extend([s.strip() for s in skills.split(',')])
    
    skill_counts = pd.Series(all_skills).value_counts().head(10)
    
    fig = go.Figure(go.Bar(
        x=skill_counts.values,
        y=skill_counts.index,
        orientation='h',
        marker_color='#3498db'
    ))
    
    fig.update_layout(
        title='Top 10 Skills in Demand',
        xaxis_title='Number of Candidates',
        yaxis_title='Skill',
        height=400
    )
    
    return fig

def analyze_experience_education(df: pd.DataFrame = None):
    """Create experience vs education level analysis."""
    if df is None:
        df = load_recruitment_data()
    if df.empty:
        return pd.DataFrame()

    df['experience_range'] = pd.cut(
        df['years_experience'],
        bins=[-1, 2, 5, 8, float('inf')],
        labels=['0-2 years', '3-5 years', '6-8 years', '8+ years']
    )
    
    pivot = pd.pivot_table(
        df,
        index=['experience_range', 'education_level'],
        columns='application_status',
        values='application_id',
        aggfunc='count',
        fill_value=0
    ).reset_index()
    
    # Ensure all status columns exist
    for col in ['Applied', 'Technical Assessment', 'First Interview', 
                'Technical Interview', 'Final Interview', 'Offer Made', 
                'Hired', 'Rejected']:
        if col not in pivot.columns:
            pivot[col] = 0
            
    pivot['hire_rate'] = (
        pivot['Hired'] / 
        pivot[['Applied', 'Technical Assessment', 'First Interview',
               'Technical Interview', 'Final Interview', 'Offer Made',
               'Hired', 'Rejected']].sum(axis=1) * 100
    ).round(2)
    
    return pivot

def create_experience_distribution(df: pd.DataFrame = None):
    """Create experience distribution visualization using seaborn."""
    if df is None:
        df = load_recruitment_data()
    if df.empty:
        return None

    fig = Figure(figsize=(10, 6))
    ax = fig.add_subplot(111)
    
    sns.histplot(data=df, x='years_experience', bins=20, ax=ax)
    ax.set_title('Distribution of Years of Experience')
    ax.set_xlabel('Years of Experience')
    ax.set_ylabel('Number of Candidates')
    
    return fig

def create_education_pie_chart(df: pd.DataFrame = None):
    """Create education level distribution pie chart."""
    if df is None:
        df = load_recruitment_data()
    if df.empty:
        return None

    education_counts = df['education_level'].value_counts()
    
    fig = Figure(figsize=(10, 8))
    ax = fig.add_subplot(111)
    
    ax.pie(education_counts.values, labels=education_counts.index, autopct='%1.1f%%',
           startangle=90)
    ax.set_title('Distribution of Education Levels')
    
    return fig

def create_skills_wordcloud(df: pd.DataFrame = None):
    """Create a word cloud visualization of skills."""
    if df is None:
        df = load_recruitment_data()
    if df.empty:
        return None

    # Combine all skills into one text
    text = ' '.join(df['skills'].dropna())
    
    # Generate word cloud
    wordcloud = WordCloud(width=800, height=400, background_color='white',
                         max_words=100, contour_width=3, contour_color='steelblue')
    wordcloud.generate(text)
    
    # Create figure
    fig = Figure(figsize=(10, 5))
    ax = fig.add_subplot(111)
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    ax.set_title('Skills Word Cloud')
    
    return fig

def create_application_calendar(df: pd.DataFrame = None):
    """Create a calendar heatmap of applications."""
    if df is None:
        df = load_recruitment_data()
    if df.empty:
        return None

    # Count applications per day
    daily_counts = df.groupby('apply_date').size()
    
    fig = Figure(figsize=(16, 8))
    ax = fig.add_subplot(111)
    
    calplot.yearplot(daily_counts, year=2025, ax=ax, cmap='YlOrRd',
                    fillcolor='lightgrey', daylabels='MTWTFSS')
    ax.set_title('Application Activity Calendar (2025)')
    
    return fig

def create_department_location_heatmap(df: pd.DataFrame = None):
    """Create a heatmap of applications by department and location."""
    if df is None:
        df = load_recruitment_data()
    if df.empty:
        return None

    # Create cross-tabulation of department and location
    heatmap_data = pd.crosstab(df['department'], df['location'])
    
    fig = Figure(figsize=(12, 8))
    ax = fig.add_subplot(111)
    
    sns.heatmap(heatmap_data, annot=True, fmt='d', cmap='YlOrRd', ax=ax)
    ax.set_title('Applications by Department and Location')
    
    return fig

def create_time_series_analysis(df: pd.DataFrame = None):
    """Create time series analysis of applications."""
    if df is None:
        df = load_recruitment_data()
    if df.empty:
        return None

    # Group by date and count applications
    daily_apps = df.groupby('apply_date').size().reset_index()
    daily_apps.columns = ['date', 'applications']
    
    # Calculate 7-day moving average
    daily_apps['moving_avg'] = daily_apps['applications'].rolling(window=7).mean()
    
    fig = Figure(figsize=(12, 6))
    ax = fig.add_subplot(111)
    
    ax.plot(daily_apps['date'], daily_apps['applications'], 'b-', alpha=0.5, label='Daily')
    ax.plot(daily_apps['date'], daily_apps['moving_avg'], 'r-', label='7-day Moving Average')
    
    ax.set_title('Application Trends Over Time')
    ax.set_xlabel('Date')
    ax.set_ylabel('Number of Applications')
    ax.legend()
    ax.tick_params(axis='x', rotation=45)
    
    fig.tight_layout()
    return fig

if __name__ == '__main__':
    # Create sample data if running directly
    create_sample_data(force=False)
    df = load_recruitment_data()
    print('Rows loaded:', len(df))