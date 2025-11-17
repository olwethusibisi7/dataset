import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import accuracy_score, mean_squared_error
from prophet import Prophet
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

class RecruitmentAnalytics:
    def __init__(self, data):
        self.data = data
        self.label_encoders = {}
        self._preprocess_data()
        
    def _preprocess_data(self):
        """Preprocess data for modeling"""
        # Create label encoders for categorical variables
        categorical_cols = ['department', 'source', 'education_level', 'application_status']
        
        for col in categorical_cols:
            if col in self.data.columns:
                self.label_encoders[col] = LabelEncoder()
                self.data[f'{col}_encoded'] = self.label_encoders[col].fit_transform(self.data[col])
        
        # Convert dates to datetime if not already
        date_cols = ['apply_date', 'interview_date', 'hire_date']
        for col in date_cols:
            if col in self.data.columns:
                self.data[col] = pd.to_datetime(self.data[col])
                
        # Calculate time to hire
        if 'apply_date' in self.data.columns and 'hire_date' in self.data.columns:
            self.data['time_to_hire'] = (self.data['hire_date'] - self.data['apply_date']).dt.days
            
    def train_hire_prediction_model(self):
        """Train model to predict hiring probability"""
        # Prepare features
        feature_cols = [
            'years_experience', 
            'department_encoded',
            'source_encoded',
            'education_level_encoded'
        ]
        
        X = self.data[feature_cols].fillna(-1)
        y = (self.data['application_status'] == 'Hired').astype(int)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train model
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Get predictions and accuracy
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        # Get feature importance
        importance_df = pd.DataFrame({
            'feature': feature_cols,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=True)
        
        return {
            'model': model,
            'accuracy': accuracy,
            'feature_importance': importance_df
        }
        
    def predict_time_to_hire(self):
        """Train model to predict time to hire"""
        # Prepare features
        feature_cols = [
            'years_experience', 
            'department_encoded',
            'source_encoded',
            'education_level_encoded'
        ]
        
        # Filter rows with valid time_to_hire
        mask = self.data['time_to_hire'].notna()
        X = self.data.loc[mask, feature_cols].fillna(-1)
        y = self.data.loc[mask, 'time_to_hire']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train model
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Get predictions and RMSE
        y_pred = model.predict(X_test)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        
        return {
            'model': model,
            'rmse': rmse
        }
        
    def forecast_applications(self, periods=90):
        """Forecast application volume using Prophet"""
        # Prepare data for Prophet
        df = self.data.copy()
        df['ds'] = df['apply_date']
        df['y'] = 1  # Count each application
        
        # Aggregate by date
        df = df.groupby('ds').count()['y'].reset_index()
        
        # Train Prophet model
        model = Prophet(yearly_seasonality=True, weekly_seasonality=True)
        model.fit(df)
        
        # Make forecast
        future = model.make_future_dataframe(periods=periods)
        forecast = model.predict(future)
        
        # Create visualization
        fig = go.Figure()
        
        # Add actual values
        fig.add_trace(go.Scatter(
            x=df['ds'],
            y=df['y'],
            name='Actual',
            mode='markers+lines'
        ))
        
        # Add forecast
        fig.add_trace(go.Scatter(
            x=forecast['ds'],
            y=forecast['yhat'],
            name='Forecast',
            mode='lines',
            line=dict(dash='dash')
        ))
        
        # Add confidence intervals
        fig.add_trace(go.Scatter(
            x=forecast['ds'],
            y=forecast['yhat_upper'],
            fill=None,
            mode='lines',
            line=dict(color='rgba(0,100,80,0.2)'),
            name='Upper Bound'
        ))
        
        fig.add_trace(go.Scatter(
            x=forecast['ds'],
            y=forecast['yhat_lower'],
            fill='tonexty',
            mode='lines',
            line=dict(color='rgba(0,100,80,0.2)'),
            name='Lower Bound'
        ))
        
        fig.update_layout(
            title='Application Volume Forecast',
            xaxis_title='Date',
            yaxis_title='Number of Applications'
        )
        
        return {
            'forecast': forecast,
            'figure': fig
        }
        
    def analyze_skill_trends(self):
        """Analyze trends in required skills over time"""
        # Prepare skill trend data
        skill_data = self.data.copy()
        skill_data['month'] = skill_data['apply_date'].dt.to_period('M')
        
        # Count skills per month
        skill_counts = skill_data.groupby(['month', 'required_skills']).size().reset_index(name='count')
        
        # Create visualization
        fig = px.line(
            skill_counts,
            x='month',
            y='count',
            color='required_skills',
            title='Skill Demand Trends'
        )
        
        return {
            'data': skill_counts,
            'figure': fig
        }
        
    def perform_cohort_analysis(self):
        """Perform cohort analysis of candidates"""
        # Create cohorts based on application month
        cohort_data = self.data.copy()
        cohort_data['cohort'] = cohort_data['apply_date'].dt.to_period('M')
        
        # Calculate success metrics for each cohort
        cohort_stats = cohort_data.groupby('cohort').agg({
            'candidate_id': 'count',
            'application_status': lambda x: (x == 'Hired').mean(),
            'time_to_hire': 'mean'
        }).round(2)
        
        cohort_stats.columns = ['Total Applications', 'Hire Rate', 'Avg Time to Hire']
        
        # Create visualization
        fig = go.Figure(data=[
            go.Scatter(
                x=cohort_stats.index.astype(str),
                y=cohort_stats['Hire Rate'],
                mode='lines+markers',
                name='Hire Rate'
            ),
            go.Bar(
                x=cohort_stats.index.astype(str),
                y=cohort_stats['Total Applications'],
                name='Total Applications',
                yaxis='y2'
            )
        ])
        
        fig.update_layout(
            title='Cohort Analysis: Applications and Hire Rate',
            yaxis=dict(title='Hire Rate'),
            yaxis2=dict(title='Total Applications', overlaying='y', side='right')
        )
        
        return {
            'cohort_stats': cohort_stats,
            'figure': fig
        }
        
    def generate_candidate_insights(self, candidate_id):
        """Generate insights for a specific candidate"""
        # Get candidate data
        candidate = self.data[self.data['candidate_id'] == candidate_id].iloc[0]
        
        # Prepare features for prediction
        features = pd.DataFrame({
            'years_experience': [candidate['years_experience']],
            'department_encoded': [self.label_encoders['department'].transform([candidate['department']])[0]],
            'source_encoded': [self.label_encoders['source'].transform([candidate['source']])[0]],
            'education_level_encoded': [self.label_encoders['education_level'].transform([candidate['education_level']])[0]]
        })
        
        # Get predictions
        hire_prob = self.train_hire_prediction_model()['model'].predict_proba(features)[0][1]
        time_to_hire = self.predict_time_to_hire()['model'].predict(features)[0]
        
        # Calculate experience percentile
        exp_percentile = (
            self.data['years_experience'] <= candidate['years_experience']
        ).mean() * 100
        
        # Calculate skills match
        required_skills = set(str(candidate['required_skills']).split(','))
        candidate_skills = set(str(candidate['skills']).split(','))
        skills_match = len(required_skills.intersection(candidate_skills)) / len(required_skills) * 100
        
        return {
            'hire_probability': round(hire_prob * 100, 1),
            'estimated_time_to_hire': round(time_to_hire, 1),
            'experience_percentile': exp_percentile,
            'skills_match': round(skills_match, 1)
        }