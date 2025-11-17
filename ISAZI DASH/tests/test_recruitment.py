import pytest
from recruitment_functions import (
    load_recruitment_data,
    create_sample_data,
    ensure_db_exists
)

def test_database_initialization():
    """Test that database can be initialized with tables."""
    ensure_db_exists()
    # Should not raise any exceptions

def test_sample_data_creation():
    """Test sample data creation."""
    create_sample_data(force=True)
    df = load_recruitment_data()
    assert not df.empty, "Data frame should not be empty after sample data creation"
    assert len(df) > 0, "Should have at least some rows"

def test_load_recruitment_data():
    """Test data loading functionality."""
    df = load_recruitment_data()
    assert not df.empty, "Should be able to load data"
    assert 'application_status' in df.columns, "Should have status column"
    assert 'department' in df.columns, "Should have department column"