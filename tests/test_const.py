"""Tests for the Redmine integration constants."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "custom_components"))

from redmine.const import (
    ATTR_DESCRIPTION,
    ATTR_PRIORITY_ID,
    ATTR_PROJECT_ID,
    ATTR_SUBJECT,
    ATTR_TRACKER_ID,
    CONF_API_KEY,
    CONF_DEFAULT_PROJECT_ID,
    CONF_DEFAULT_TRACKER_ID,
    CONF_REDMINE_URL,
    DEFAULT_PRIORITY_ID,
    DEFAULT_TRACKER_ID,
    DOMAIN,
    SERVICE_CREATE_ISSUE,
)


class TestConstants:
    """Tests for constants."""

    def test_domain(self):
        """Test domain constant."""
        assert DOMAIN == "redmine"

    def test_config_keys(self):
        """Test configuration key constants."""
        assert CONF_REDMINE_URL == "redmine_url"
        assert CONF_API_KEY == "api_key"
        assert CONF_DEFAULT_PROJECT_ID == "default_project_id"
        assert CONF_DEFAULT_TRACKER_ID == "default_tracker_id"

    def test_service_attributes(self):
        """Test service attribute constants."""
        assert ATTR_PROJECT_ID == "project_id"
        assert ATTR_SUBJECT == "subject"
        assert ATTR_DESCRIPTION == "description"
        assert ATTR_TRACKER_ID == "tracker_id"
        assert ATTR_PRIORITY_ID == "priority_id"

    def test_service_names(self):
        """Test service name constants."""
        assert SERVICE_CREATE_ISSUE == "create_issue"

    def test_default_values(self):
        """Test default value constants."""
        assert DEFAULT_TRACKER_ID == 1
        assert DEFAULT_PRIORITY_ID == 2
