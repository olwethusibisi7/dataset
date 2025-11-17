import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
from recruitment_functions import (
    load_recruitment_data,
    create_application_funnel,
    create_source_effectiveness,
    analyze_experience_education,
    analyze_skills_demand,
    create_sample_data,
    create_experience_distribution,
    create_education_pie_chart,
    create_skills_wordcloud,
    create_application_calendar,
    create_department_location_heatmap,
    create_time_series_analysis
)

# Page config
st.set_page_config(
    page_title="Isazi Consulting Recruitment Dashboard",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stMetric {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .stMetric:hover {
        background-color: #e9ecef;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize database
create_sample_data()

# Title and description
st.title("📊 Isazi Consulting Recruitment Dashboard")
st.markdown("""
    Track recruitment metrics, analyze candidate pipelines, and optimize hiring processes.
    Filter data using the sidebar controls.
""")

# Sidebar filters
with st.sidebar:
    st.header("Filters")
    
    # Date range selector
    st.subheader("Date Range")
    date_range = st.date_input(
        "Select period",
        value=(datetime.now() - timedelta(days=180), datetime.now())
    )
    
    # Load initial data for department filter
    initial_data = load_recruitment_data()
    if not initial_data.empty:
        departments = ["All"] + sorted(initial_data['department'].unique().tolist())
        department = st.selectbox("Department", departments)
        
        locations = ["All"] + sorted(initial_data['location'].unique().tolist())
        location = st.selectbox("Location", locations)
    else:
        department = "All"
        location = "All"

# Load filtered data
data = load_recruitment_data(date_range=date_range)
if not data.empty:
    if department != "All":
        data = data[data['department'] == department]
    if location != "All":
        data = data[data['location'] == location]

    # Top metrics
    st.header("Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Applications",
            len(data),
            f"{len(data) - len(initial_data)}"
        )
    
    with col2:
        hires = len(data[data['application_status'] == 'Hired'])
        conversion = round((hires / len(data) * 100), 2) if len(data) > 0 else 0
        st.metric("Conversion Rate", f"{conversion}%")
    
    with col3:
        avg_exp = round(data['years_experience'].mean(), 1)
        st.metric("Avg. Experience", f"{avg_exp} years")
    
    with col4:
        time_to_hire = round(random.uniform(20, 45), 1)  # Placeholder
        st.metric("Avg. Time to Hire", f"{time_to_hire} days")

    # Main visualizations
    st.header("Recruitment Pipeline Analysis")
    
    # Two-column layout for main charts
    col1, col2 = st.columns(2)
    
    with col1:
        funnel_fig = create_application_funnel(data)
        if funnel_fig is not None:
            st.plotly_chart(funnel_fig, use_container_width=True)
            
    with col2:
        source_fig, source_metrics = create_source_effectiveness(data, department)
        if source_fig is not None:
            st.plotly_chart(source_fig, use_container_width=True)

    # Skills analysis
    st.header("Skills Analysis")
    
    # Two-column layout for skills visualizations
    skills_col1, skills_col2 = st.columns(2)
    
    with skills_col1:
        skills_fig = analyze_skills_demand(data)
        if skills_fig is not None:
            st.plotly_chart(skills_fig, use_container_width=True)
    
    with skills_col2:
        wordcloud_fig = create_skills_wordcloud(data)
        if wordcloud_fig is not None:
            st.pyplot(wordcloud_fig)

    # Experience and Education Analysis
    st.header("Experience and Education Analysis")
    
    exp_col1, exp_col2 = st.columns(2)
    
    with exp_col1:
        exp_dist_fig = create_experience_distribution(data)
        if exp_dist_fig is not None:
            st.pyplot(exp_dist_fig)
    
    with exp_col2:
        edu_pie_fig = create_education_pie_chart(data)
        if edu_pie_fig is not None:
            st.pyplot(edu_pie_fig)

    # Application Trends
    st.header("Application Trends")
    
    # Calendar heatmap
    calendar_fig = create_application_calendar(data)
    if calendar_fig is not None:
        st.pyplot(calendar_fig)
    
    # Time series analysis
    timeseries_fig = create_time_series_analysis(data)
    if timeseries_fig is not None:
        st.pyplot(timeseries_fig)

    # Department and Location Analysis
    st.header("Department and Location Analysis")
    
    heatmap_fig = create_department_location_heatmap(data)
    if heatmap_fig is not None:
        st.pyplot(heatmap_fig)

    # Detailed qualification analysis
    st.header("Candidate Qualifications")
    qual_data = analyze_experience_education(data)
    if not qual_data.empty:
        st.dataframe(qual_data, use_container_width=True)

    # Download section
    st.header("Export Data")
    csv = data.to_csv(index=False)
    st.download_button(
        "Download Full Report (CSV)",
        csv,
        file_name=f'isazi_recruitment_data_{datetime.now().strftime("%Y%m%d")}.csv',
        mime='text/csv'
    )

else:
    st.error("No recruitment data available. Please check database connection or run sample data creation.")