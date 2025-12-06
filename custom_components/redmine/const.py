"""Constants for the Redmine integration."""

from typing import Final

DOMAIN: Final = "redmine"

# Configuration keys
CONF_REDMINE_URL: Final = "redmine_url"
CONF_API_KEY: Final = "api_key"
CONF_DEFAULT_PROJECT_ID: Final = "default_project_id"
CONF_DEFAULT_TRACKER_ID: Final = "default_tracker_id"

# Service attributes
ATTR_PROJECT_ID: Final = "project_id"
ATTR_SUBJECT: Final = "subject"
ATTR_DESCRIPTION: Final = "description"
ATTR_TRACKER_ID: Final = "tracker_id"
ATTR_PRIORITY_ID: Final = "priority_id"

# Service names
SERVICE_CREATE_ISSUE: Final = "create_issue"

# Default values
DEFAULT_TRACKER_ID: Final = 1
DEFAULT_PRIORITY_ID: Final = 2
