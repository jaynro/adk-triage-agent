"""
Unit tests for the ADK Triage Agent
"""
import pytest
from src.main import main


def test_main_function_exists():
    """Test that the main function exists and is callable."""
    assert callable(main)


def test_main_runs_without_error():
    """Test that the main function runs without errors."""
    try:
        main()
        assert True
    except Exception as e:
        pytest.fail(f"main() raised {type(e).__name__} unexpectedly: {e}")


# Add more tests as your agent functionality grows
