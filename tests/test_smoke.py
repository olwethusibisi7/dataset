import recruitment_functions as rf


def test_load_data_creates_and_loads():
    # Force creation of sample data so test is deterministic
    rf.create_sample_data(force=True)
    df = rf.load_recruitment_data()
    assert df is not None
    assert not df.empty
    # basic expected columns
    assert 'application_status' in df.columns
    assert 'candidate_id' in df.columns
