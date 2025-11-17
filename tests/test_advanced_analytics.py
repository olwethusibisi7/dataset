"""Advanced analytics test suite."""
import pytest
import pandas as pd
import numpy as np
from advanced_analytics import RecruitmentAnalytics

def test_analytics_initialization(sample_data, analytics):
    """Test that RecruitmentAnalytics initializes correctly."""
    assert isinstance(analytics.data, pd.DataFrame)
    assert not analytics.data.empty
    assert hasattr(analytics, 'model')

def test_feature_engineering(analytics):
    """Test feature engineering process."""
    features = analytics.prepare_features()
    
    assert isinstance(features, pd.DataFrame)
    assert not features.empty
    assert 'experience_years' in features.columns
    assert 'education_level' in features.columns

def test_model_training(analytics):
    """Test model training process."""
    X, y = analytics.prepare_training_data()
    analytics.train_model(X, y)
    
    assert hasattr(analytics.model, 'predict')
    assert hasattr(analytics.model, 'feature_importances_')

def test_success_prediction(analytics):
    """Test candidate success prediction."""
    predictions = analytics.predict_success_probability(
        analytics.prepare_features()
    )
    
    assert isinstance(predictions, np.ndarray)
    assert all(0 <= p <= 1 for p in predictions)

def test_feature_importance(analytics):
    """Test feature importance analysis."""
    importance = analytics.get_feature_importance()
    
    assert isinstance(importance, pd.Series)
    assert not importance.empty
    assert all(importance >= 0)

def test_time_to_hire_prediction(analytics):
    """Test time-to-hire prediction."""
    predictions = analytics.predict_time_to_hire()
    
    assert isinstance(predictions, pd.Series)
    assert all(predictions > 0)

def test_source_roi_calculation(analytics):
    """Test recruitment source ROI calculation."""
    roi_data = analytics.calculate_source_roi()
    
    assert isinstance(roi_data, pd.DataFrame)
    assert 'source' in roi_data.columns
    assert 'roi' in roi_data.columns

def test_attrition_risk_prediction(analytics):
    """Test attrition risk prediction."""
    risk_scores = analytics.predict_attrition_risk()
    
    assert isinstance(risk_scores, np.ndarray)
    assert all(0 <= score <= 1 for score in risk_scores)

def test_skill_gap_analysis(analytics):
    """Test skill gap analysis."""
    gaps = analytics.analyze_skill_gaps()
    
    assert isinstance(gaps, pd.DataFrame)
    assert 'skill' in gaps.columns
    assert 'gap_score' in gaps.columns

def test_recruitment_forecasting(analytics):
    """Test recruitment demand forecasting."""
    forecast = analytics.forecast_recruitment_demand()
    
    assert isinstance(forecast, pd.DataFrame)
    assert 'date' in forecast.columns
    assert 'predicted_demand' in forecast.columns