import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
from recruitment_functions import (
    load_recruitment_data,
    create_application_funnel,
    create_source_effectiveness,
    analyze_experience_education,
    create_sample_data
)

# Ensure sample data exists (no-op if DB already populated)
create_sample_data()

st.set_page_config(page_title="Data Science Recruitment Dashboard", page_icon="📊", layout="wide")

st.title("📊 Data Science Recruitment Dashboard")
st.markdown("Interactive dashboard for Data Science recruitment metrics")

# Sidebar filters
with st.sidebar:
    st.header("Filters")
    date_range = st.date_input("Date Range", value=(datetime.now() - timedelta(days=180), datetime.now()))
    data = load_recruitment_data()
    if not data.empty:
        departments = ["All"] + sorted(data['department'].unique().tolist())
        department = st.selectbox("Department", departments)
    else:
        department = "All"

# Load and filter data
data = load_recruitment_data()
if not data.empty:
    if department != "All":
        data = data[data['department'] == department]

    # Layout
    col1, col2 = st.columns(2)
    with col1:
        funnel_fig = create_application_funnel(data)
        if funnel_fig is not None:
            st.plotly_chart(funnel_fig, use_container_width=True)
    with col2:
        source_fig, source_metrics = create_source_effectiveness(data, department_filter=department)
        if source_fig is not None:
            st.plotly_chart(source_fig, use_container_width=True)

    # Key metrics
    st.header("Key Recruitment Metrics")
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Total Applications", len(data))
    with m2:
        hires = len(data[data['application_status'] == 'Hired'])
        conv_rate = round((hires / len(data) * 100), 2) if len(data) > 0 else 0
        st.metric("Conversion Rate", f"{conv_rate}%")
    with m3:
        st.metric("Avg. Years Experience", round(data['years_experience'].mean(), 1))
    with m4:
        top_source = data['source'].mode()[0] if not data['source'].mode().empty else "N/A"
        st.metric("Top Recruitment Source", top_source)

    # Qualifications
    st.header("Candidate Qualifications")
    qual = analyze_experience_education(data)
    if not qual.empty:
        st.dataframe(qual)

    # Download
    csv = data.to_csv(index=False)
    st.download_button("Download CSV", csv, file_name='recruitment_data.csv', mime='text/csv')
else:
    st.error("No recruitment data available. Run the notebook cells or use the sample data creator.")
