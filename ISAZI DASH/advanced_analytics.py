import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.metrics import classification_report, mean_squared_error, r2_score
from xgboost import XGBClassifier
import shap
import tensorflow as tf
from prophet import Prophet
import optuna
from scipy import stats
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class RecruitmentAnalytics:
    def __init__(self, df=None):
        self.df = df
        self.models = {}
        self.encoders = {}
        self.scaler = StandardScaler()
        
    def prepare_features(self, df):
        """Prepare features for modeling."""
        # Create label encoders for categorical variables
        categorical_cols = ['source', 'education_level', 'department', 'location']
        
        X = df.copy()
        for col in categorical_cols:
            if col not in self.encoders:
                self.encoders[col] = LabelEncoder()
                X[col] = self.encoders[col].fit_transform(X[col])
            else:
                X[col] = self.encoders[col].transform(X[col])
        
        # Extract features from skills
        X['skills_count'] = X['skills'].str.count(',') + 1
        
        # Create numeric features
        X['application_age'] = (datetime.now() - pd.to_datetime(X['apply_date'])).dt.days
        
        # Select features for modeling
        feature_cols = ['years_experience', 'skills_count', 'application_age'] + categorical_cols
        return X[feature_cols]

    def train_hire_prediction_model(self, df=None):
        """Train a model to predict hiring probability."""
        if df is not None:
            self.df = df
            
        # Prepare data
        X = self.prepare_features(self.df)
        y = (self.df['application_status'] == 'Hired').astype(int)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        model = XGBClassifier(use_label_encoder=False, eval_metric='logloss')
        model.fit(X_train_scaled, y_train)
        
        # Save model
        self.models['hire_prediction'] = model
        
        # Calculate SHAP values
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_test_scaled)
        
        # Create feature importance plot
        feature_importance = pd.DataFrame({
            'feature': X.columns,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        return {
            'model': model,
            'accuracy': model.score(X_test_scaled, y_test),
            'feature_importance': feature_importance,
            'shap_values': shap_values,
            'test_data': X_test_scaled
        }

    def predict_time_to_hire(self, df=None):
        """Predict time to hire for candidates."""
        if df is not None:
            self.df = df
            
        # Filter completed hires
        hired_df = self.df[self.df['application_status'] == 'Hired'].copy()
        
        # Calculate actual time to hire
        hired_df['time_to_hire'] = (pd.to_datetime(hired_df['apply_date']) - 
                                   hired_df.groupby('candidate_id')['apply_date'].transform('min')).dt.days
        
        # Prepare features
        X = self.prepare_features(hired_df)
        y = hired_df['time_to_hire']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train model
        model = GradientBoostingRegressor()
        model.fit(X_train, y_train)
        
        # Save model
        self.models['time_to_hire'] = model
        
        # Make predictions
        y_pred = model.predict(X_test)
        
        return {
            'model': model,
            'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
            'r2': r2_score(y_test, y_pred)
        }

    def forecast_applications(self, df=None, periods=30):
        """Forecast future application volumes using Prophet."""
        if df is not None:
            self.df = df
            
        # Prepare data for Prophet
        forecast_df = self.df.groupby('apply_date').size().reset_index()
        forecast_df.columns = ['ds', 'y']
        
        # Create and train model
        model = Prophet(yearly_seasonality=True, weekly_seasonality=True)
        model.fit(forecast_df)
        
        # Make forecast
        future = model.make_future_dataframe(periods=periods)
        forecast = model.predict(future)
        
        # Create visualization
        fig = go.Figure()
        
        # Actual values
        fig.add_trace(go.Scatter(
            x=forecast_df['ds'],
            y=forecast_df['y'],
            name='Actual',
            mode='markers+lines'
        ))
        
        # Forecasted values
        fig.add_trace(go.Scatter(
            x=forecast['ds'].tail(periods),
            y=forecast['yhat'].tail(periods),
            name='Forecast',
            mode='lines',
            line=dict(dash='dash')
        ))
        
        # Confidence intervals
        fig.add_trace(go.Scatter(
            x=forecast['ds'].tail(periods),
            y=forecast['yhat_upper'].tail(periods),
            fill=None,
            mode='lines',
            line_color='rgba(0,100,80,0.2)',
            name='Upper Bound'
        ))
        
        fig.add_trace(go.Scatter(
            x=forecast['ds'].tail(periods),
            y=forecast['yhat_lower'].tail(periods),
            fill='tonexty',
            mode='lines',
            line_color='rgba(0,100,80,0.2)',
            name='Lower Bound'
        ))
        
        fig.update_layout(
            title='Application Volume Forecast',
            xaxis_title='Date',
            yaxis_title='Number of Applications',
            hovermode='x unified'
        )
        
        return {
            'forecast': forecast,
            'figure': fig
        }

    def analyze_skill_trends(self, df=None):
        """Analyze trending skills over time."""
        if df is not None:
            self.df = df
            
        # Extract skills and dates
        skill_dates = []
        for _, row in self.df.iterrows():
            skills = [s.strip() for s in row['skills'].split(',')]
            for skill in skills:
                skill_dates.append({
                    'skill': skill,
                    'date': row['apply_date']
                })
        
        skill_trends = pd.DataFrame(skill_dates)
        
        # Calculate monthly skill frequencies
        skill_trends['month'] = pd.to_datetime(skill_trends['date']).dt.to_period('M')
        monthly_skills = skill_trends.groupby(['month', 'skill']).size().unstack(fill_value=0)
        
        # Calculate trend scores
        trend_scores = {}
        for skill in monthly_skills.columns:
            trend = monthly_skills[skill].values
            trend_scores[skill] = np.polyfit(range(len(trend)), trend, 1)[0]
        
        # Create visualization
        top_trends = pd.Series(trend_scores).sort_values(ascending=False).head(10)
        
        fig = go.Figure(data=[
            go.Bar(
                x=top_trends.index,
                y=top_trends.values,
                marker_color='lightblue'
            )
        ])
        
        fig.update_layout(
            title='Top 10 Trending Skills',
            xaxis_title='Skill',
            yaxis_title='Trend Score',
            xaxis_tickangle=-45
        )
        
        return {
            'trend_scores': trend_scores,
            'figure': fig
        }

    def perform_cohort_analysis(self, df=None):
        """Perform cohort analysis of candidates."""
        if df is not None:
            self.df = df
            
        # Create cohorts based on application month
        cohort_df = self.df.copy()
        cohort_df['Cohort'] = pd.to_datetime(cohort_df['apply_date']).dt.to_period('M')
        
        # Calculate conversion rates by cohort
        cohort_stats = cohort_df.groupby('Cohort').agg({
            'application_id': 'count',
            'application_status': lambda x: (x == 'Hired').sum()
        }).reset_index()
        
        cohort_stats.columns = ['Cohort', 'Total_Applications', 'Hires']
        cohort_stats['Conversion_Rate'] = (cohort_stats['Hires'] / cohort_stats['Total_Applications'] * 100).round(2)
        
        # Create visualization
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=cohort_stats['Cohort'].astype(str),
            y=cohort_stats['Conversion_Rate'],
            mode='lines+markers',
            name='Conversion Rate'
        ))
        
        fig.update_layout(
            title='Cohort Analysis: Conversion Rates Over Time',
            xaxis_title='Cohort (Month)',
            yaxis_title='Conversion Rate (%)',
            xaxis_tickangle=-45
        )
        
        return {
            'cohort_stats': cohort_stats,
            'figure': fig
        }

    def optimize_hiring_process(self, df=None):
        """Optimize hiring process using Optuna."""
        if df is not None:
            self.df = df
            
        def objective(trial):
            # Parameters to optimize
            params = {
                'max_depth': trial.suggest_int('max_depth', 3, 10),
                'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3),
                'n_estimators': trial.suggest_int('n_estimators', 50, 300),
                'min_child_weight': trial.suggest_int('min_child_weight', 1, 7),
                'subsample': trial.suggest_float('subsample', 0.6, 1.0),
                'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0)
            }
            
            # Prepare data
            X = self.prepare_features(self.df)
            y = (self.df['application_status'] == 'Hired').astype(int)
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
            
            # Train and evaluate model
            model = XGBClassifier(**params, use_label_encoder=False, eval_metric='logloss')
            model.fit(X_train, y_train)
            accuracy = model.score(X_test, y_test)
            
            return accuracy
        
        # Run optimization
        study = optuna.create_study(direction='maximize')
        study.optimize(objective, n_trials=50)
        
        return {
            'best_params': study.best_params,
            'best_accuracy': study.best_value
        }

    def generate_candidate_insights(self, candidate_id):
        """Generate detailed insights for a specific candidate."""
        if self.df is None:
            return None
            
        # Get candidate data
        candidate_data = self.df[self.df['candidate_id'] == candidate_id].iloc[0]
        
        # Prepare features for prediction
        X = self.prepare_features(pd.DataFrame([candidate_data]))
        X_scaled = self.scaler.transform(X)
        
        # Make predictions
        hire_prob = self.models.get('hire_prediction').predict_proba(X_scaled)[0][1]
        time_to_hire = self.models.get('time_to_hire').predict(X)[0]
        
        # Generate insights
        insights = {
            'candidate_id': candidate_id,
            'hire_probability': round(hire_prob * 100, 2),
            'estimated_time_to_hire': round(time_to_hire, 1),
            'experience_percentile': stats.percentileofscore(
                self.df['years_experience'], 
                candidate_data['years_experience']
            ),
            'skills_match': self._calculate_skills_match(candidate_data['skills'])
        }
        
        return insights

    def _calculate_skills_match(self, candidate_skills):
        """Calculate how well a candidate's skills match job requirements."""
        # Get all required skills from job postings
        all_required_skills = set()
        for skills in self.df['skills'].dropna():
            all_required_skills.update([s.strip() for s in skills.split(',')])
        
        # Calculate match percentage
        candidate_skill_list = set([s.strip() for s in candidate_skills.split(',')])
        match_percentage = len(candidate_skill_list.intersection(all_required_skills)) / len(all_required_skills) * 100
        
        return round(match_percentage, 2)