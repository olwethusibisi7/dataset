"""Test suite for recruitment analytics dashboard."""
import pytest
import pandas as pd
from datetime import datetime, timedelta
from recruitment_functions import (
    create_sample_data, 
    load_recruitment_data,
    calculate_application_funnel,
    analyze_source_effectiveness,
    get_candidate_qualifications
)

def test_sample_data_creation():
    """Test that sample data is created with expected structure."""
    create_sample_data(force=True)
    data = load_recruitment_data()
    
    assert isinstance(data, pd.DataFrame)
    assert not data.empty
    required_cols = ['candidate_id', 'application_date', 'source', 'status']
    assert all(col in data.columns for col in required_cols)

def test_application_funnel():
    """Test application funnel calculation."""
    data = load_recruitment_data()
    funnel_data = calculate_application_funnel(data)
    
    assert isinstance(funnel_data, pd.DataFrame)
    assert 'stage' in funnel_data.columns
    assert 'count' in funnel_data.columns
    assert len(funnel_data) > 0
    assert funnel_data['count'].is_monotonic_decreasing

def test_source_effectiveness():
    """Test source effectiveness analysis."""
    data = load_recruitment_data()
    source_data = analyze_source_effectiveness(data)
    
    assert isinstance(source_data, pd.DataFrame)
    assert 'source' in source_data.columns
    assert 'success_rate' in source_data.columns
    assert all(0 <= rate <= 1 for rate in source_data['success_rate'])

def test_candidate_qualifications():
    """Test candidate qualifications analysis."""
    data = load_recruitment_data()
    qual_data = get_candidate_qualifications(data)
    
    assert isinstance(qual_data, pd.DataFrame)
    assert 'qualification' in qual_data.columns
    assert 'count' in qual_data.columns
    assert all(isinstance(count, (int, float)) for count in qual_data['count'])

def test_data_date_range():
    """Test that data falls within expected date range."""
    data = load_recruitment_data()
    
    assert pd.to_datetime(data['application_date']).min() >= datetime.now() - timedelta(days=365)
    assert pd.to_datetime(data['application_date']).max() <= datetime.now()

def test_source_categories():
    """Test that source categories are valid."""
    data = load_recruitment_data()
    valid_sources = {'LinkedIn', 'Indeed', 'Referral', 'Company Website', 'Other'}
    
    assert set(data['source'].unique()).issubset(valid_sources)

def test_status_transitions():
    """Test that status transitions are valid."""
    data = load_recruitment_data()
    valid_statuses = {
        'Applied',
        'Phone Screen',
        'Interview',
        'Offer',
        'Hired',
        'Rejected'
    }
    
    assert set(data['status'].unique()).issubset(valid_statuses)

def test_no_duplicate_applications():
    """Test that there are no duplicate applications."""
    data = load_recruitment_data()
    duplicates = data.duplicated(subset=['candidate_id', 'application_date'])
    
    assert not duplicates.any()

def test_data_types():
    """Test that data types are correct."""
    data = load_recruitment_data()
    
    assert pd.api.types.is_datetime64_any_dtype(pd.to_datetime(data['application_date']))
    assert pd.api.types.is_string_dtype(data['source'])
    assert pd.api.types.is_string_dtype(data['status'])
    assert pd.api.types.is_integer_dtype(data['candidate_id'])