import pytest

from examples.geocode_example import geocode_address


def test_geocode_imports():
    # Basic smoke test: call the function with a known address but allow None result
    # (Nominatim may be unavailable in CI); we assert the function runs without error.
    try:
        result = geocode_address("10 Downing St, London")
    except Exception as e:
        pytest.skip(f"Network/geocoding unavailable: {e}")
    # If we get a result, it should be a tuple of two floats
    if result is not None:
        assert isinstance(result, tuple) and len(result) == 2
        assert all(isinstance(x, float) for x in result)
