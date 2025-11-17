import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import plotly.graph_objects as go
from advanced_analytics import RecruitmentAnalytics
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

# Page config with dark theme
st.set_page_config(
    page_title="Isazi Consulting Advanced Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme
st.markdown("""
    <style>
    .main {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    .stMetric {
        background-color: #262730;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .stMetric:hover {
        background-color: #1E1F25;
    }
    .stPlotlyChart {
        background-color: #262730;
        border-radius: 0.5rem;
        padding: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'analytics' not in st.session_state:
    st.session_state['analytics'] = None

# Initialize database
create_sample_data()

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Select Page",
    ["Dashboard Overview", "Predictive Analytics", "Trend Analysis", "Candidate Insights"]
)

# Filters in sidebar
st.sidebar.header("Filters")
date_range = st.sidebar.date_input(
    "Date Range",
    value=(datetime.now() - timedelta(days=180), datetime.now())
)

# Load data
data = load_recruitment_data()
if not data.empty:
    # Initialize analytics if not done
    if st.session_state['analytics'] is None:
        st.session_state['analytics'] = RecruitmentAnalytics(data)
    
    departments = ["All"] + sorted(data['department'].unique().tolist())
    department = st.sidebar.selectbox("Department", departments)
    
    if department != "All":
        data = data[data['department'] == department]

    if page == "Dashboard Overview":
        st.title("📊 Isazi Consulting Analytics Dashboard")
        
        # Key Metrics Row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Applications",
                len(data),
                f"{len(data) - len(data[data['apply_date'] < date_range[0]])}",
            )
        
        with col2:
            hires = len(data[data['application_status'] == 'Hired'])
            conv_rate = round((hires / len(data) * 100), 2) if len(data) > 0 else 0
            st.metric("Conversion Rate", f"{conv_rate}%")
        
        with col3:
            avg_exp = round(data['years_experience'].mean(), 1)
            st.metric("Avg. Experience", f"{avg_exp} years")
        
        with col4:
            top_source = data['source'].mode()[0] if not data['source'].mode().empty else "N/A"
            st.metric("Top Source", top_source)

        # Main visualizations
        st.header("Recruitment Pipeline")
        col1, col2 = st.columns(2)
        
        with col1:
            funnel_fig = create_application_funnel(data)
            if funnel_fig is not None:
                st.plotly_chart(funnel_fig, use_container_width=True)
        
        with col2:
            source_fig, _ = create_source_effectiveness(data)
            if source_fig is not None:
                st.plotly_chart(source_fig, use_container_width=True)

    elif page == "Predictive Analytics":
        st.title("🔮 Predictive Analytics")
        
        # Train models if needed
        with st.spinner("Training predictive models..."):
            hire_pred = st.session_state['analytics'].train_hire_prediction_model()
            time_pred = st.session_state['analytics'].predict_time_to_hire()
        
        # Model Performance Metrics
        st.header("Model Performance")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Hire Prediction Accuracy", f"{round(hire_pred['accuracy'] * 100, 2)}%")
        with col2:
            st.metric("Time-to-Hire RMSE", f"{round(time_pred['rmse'], 2)} days")
        
        # Feature Importance
        st.header("Feature Importance")
        importance_df = hire_pred['feature_importance']
        
        fig = go.Figure(go.Bar(
            x=importance_df['importance'],
            y=importance_df['feature'],
            orientation='h'
        ))
        fig.update_layout(title="Feature Importance in Hire Prediction")
        st.plotly_chart(fig, use_container_width=True)
        
        # Application Volume Forecast
        st.header("Application Volume Forecast")
        with st.spinner("Generating forecast..."):
            forecast = st.session_state['analytics'].forecast_applications(periods=90)
            st.plotly_chart(forecast['figure'], use_container_width=True)

    elif page == "Trend Analysis":
        st.title("📈 Trend Analysis")
        
        # Skill Trends
        st.header("Skill Trends")
        with st.spinner("Analyzing skill trends..."):
            skill_trends = st.session_state['analytics'].analyze_skill_trends()
            st.plotly_chart(skill_trends['figure'], use_container_width=True)
        
        # Cohort Analysis
        st.header("Cohort Analysis")
        with st.spinner("Performing cohort analysis..."):
            cohort_analysis = st.session_state['analytics'].perform_cohort_analysis()
            st.plotly_chart(cohort_analysis['figure'], use_container_width=True)
            
            st.dataframe(cohort_analysis['cohort_stats'], use_container_width=True)

    elif page == "Candidate Insights":
        st.title("👥 Candidate Insights")
        
        # Candidate selector
        candidates = sorted(data['candidate_id'].unique())
        selected_candidate = st.selectbox("Select Candidate", candidates)
        
        if selected_candidate:
            with st.spinner("Generating insights..."):
                insights = st.session_state['analytics'].generate_candidate_insights(selected_candidate)
                
                if insights:
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric(
                            "Hire Probability",
                            f"{insights['hire_probability']}%"
                        )
                    
                    with col2:
                        st.metric(
                            "Estimated Time to Hire",
                            f"{insights['estimated_time_to_hire']} days"
                        )
                    
                    with col3:
                        st.metric(
                            "Experience Percentile",
                            f"{round(insights['experience_percentile'], 1)}%"
                        )
                    
                    # Skills match visualization
                    st.header("Skills Match Analysis")
                    fig = go.Figure(go.Indicator(
                        mode = "gauge+number",
                        value = insights['skills_match'],
                        title = {'text': "Skills Match"},
                        domain = {'x': [0, 1], 'y': [0, 1]},
                        gauge = {
                            'axis': {'range': [0, 100]},
                            'bar': {'color': "darkblue"},
                            'steps': [
                                {'range': [0, 50], 'color': "lightgray"},
                                {'range': [50, 75], 'color': "gray"},
                                {'range': [75, 100], 'color': "darkgray"}
                            ]
                        }
                    ))
                    st.plotly_chart(fig, use_container_width=True)

else:
    st.error("No recruitment data available. Please check database connection or run sample data creation.")