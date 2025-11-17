"""Test configuration and fixtures."""
import pytest
import pandas as pd
from pathlib import Path
from recruitment_functions import create_sample_data, load_recruitment_data
from advanced_analytics import RecruitmentAnalytics

@pytest.fixture(scope="session")
def sample_data():
    """Create and load sample recruitment data."""
    create_sample_data(force=True)
    return load_recruitment_data()

@pytest.fixture(scope="session")
def analytics(sample_data):
    """Create RecruitmentAnalytics instance with sample data."""
    return RecruitmentAnalytics(sample_data)