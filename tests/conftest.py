"""Pytest configuration for Redmine integration tests."""

import pytest


@pytest.fixture
def mock_redmine_config():
    """Return a mock Redmine configuration."""
    return {
        "redmine_url": "https://redmine.example.com",
        "api_key": "test_api_key_12345",
        "default_project_id": "test-project",
        "default_tracker_id": 1,
    }
