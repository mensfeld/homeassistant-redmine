"""The Redmine integration."""

from __future__ import annotations

import logging

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import RedmineApiError, RedmineAuthError, RedmineClient
from .const import (
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
    DOMAIN,
    SERVICE_CREATE_ISSUE,
)

_LOGGER = logging.getLogger(__name__)

# Service schema
SERVICE_CREATE_ISSUE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_SUBJECT): cv.string,
        vol.Optional(ATTR_PROJECT_ID): cv.string,
        vol.Optional(ATTR_DESCRIPTION): cv.string,
        vol.Optional(ATTR_TRACKER_ID): cv.positive_int,
        vol.Optional(ATTR_PRIORITY_ID): cv.positive_int,
    }
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Redmine from a config entry."""
    session = async_get_clientsession(hass)

    client = RedmineClient(
        session=session,
        redmine_url=entry.data[CONF_REDMINE_URL],
        api_key=entry.data[CONF_API_KEY],
    )

    # Store client and config in hass.data
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "client": client,
        "config": entry.data,
    }

    # Register the service
    async def async_create_issue(call: ServiceCall) -> None:
        """Handle the create_issue service call."""
        # Get the first (and only) config entry
        entry_data = next(iter(hass.data[DOMAIN].values()))
        client: RedmineClient = entry_data["client"]
        config = entry_data["config"]

        # Get parameters with defaults from config
        project_id = call.data.get(ATTR_PROJECT_ID, config[CONF_DEFAULT_PROJECT_ID])
        subject = call.data[ATTR_SUBJECT]
        tracker_id = call.data.get(ATTR_TRACKER_ID, config[CONF_DEFAULT_TRACKER_ID])
        description = call.data.get(ATTR_DESCRIPTION)
        priority_id = call.data.get(ATTR_PRIORITY_ID, DEFAULT_PRIORITY_ID)

        try:
            result = await client.create_issue(
                project_id=project_id,
                subject=subject,
                tracker_id=tracker_id,
                description=description,
                priority_id=priority_id,
            )
            issue_id = result.get("issue", {}).get("id")
            _LOGGER.info("Created Redmine issue #%s: %s", issue_id, subject)
        except RedmineAuthError as err:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="auth_error",
            ) from err
        except RedmineApiError as err:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="api_error",
                translation_placeholders={"error": str(err)},
            ) from err

    # Only register service once
    if not hass.services.has_service(DOMAIN, SERVICE_CREATE_ISSUE):
        hass.services.async_register(
            DOMAIN,
            SERVICE_CREATE_ISSUE,
            async_create_issue,
            schema=SERVICE_CREATE_ISSUE_SCHEMA,
        )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    hass.data[DOMAIN].pop(entry.entry_id)

    # If no more entries, remove the service
    if not hass.data[DOMAIN]:
        hass.services.async_remove(DOMAIN, SERVICE_CREATE_ISSUE)
        hass.data.pop(DOMAIN)

    return True
