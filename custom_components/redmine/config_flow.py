"""Config flow for Redmine integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import RedmineAuthError, RedmineClient, RedmineConnectionError
from .const import (
    CONF_API_KEY,
    CONF_DEFAULT_PROJECT_ID,
    CONF_DEFAULT_TRACKER_ID,
    CONF_REDMINE_URL,
    DEFAULT_TRACKER_ID,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_REDMINE_URL): str,
        vol.Required(CONF_API_KEY): str,
        vol.Required(CONF_DEFAULT_PROJECT_ID): str,
        vol.Optional(CONF_DEFAULT_TRACKER_ID, default=DEFAULT_TRACKER_ID): int,
    }
)


class RedmineConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Redmine."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Normalize URL (remove trailing slash, add http:// if missing)
            redmine_url = user_input[CONF_REDMINE_URL].rstrip("/")
            if not redmine_url.startswith(("http://", "https://")):
                redmine_url = f"http://{redmine_url}"

            # Validate the connection
            session = async_get_clientsession(self.hass)
            client = RedmineClient(
                session=session,
                redmine_url=redmine_url,
                api_key=user_input[CONF_API_KEY],
            )

            try:
                await client.validate_connection()
            except RedmineAuthError as err:
                _LOGGER.error("Authentication failed: %s", err)
                errors["api_key"] = "invalid_auth"
            except RedmineConnectionError as err:
                _LOGGER.error("Connection failed to %s: %s", redmine_url, err)
                errors["redmine_url"] = "cannot_connect"
            except Exception as err:
                _LOGGER.exception("Unexpected exception: %s", err)
                errors["base"] = "unknown"

            if not errors:
                # Set unique ID to prevent duplicate entries
                await self.async_set_unique_id(redmine_url)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"Redmine ({redmine_url})",
                    data={
                        CONF_REDMINE_URL: redmine_url,
                        CONF_API_KEY: user_input[CONF_API_KEY],
                        CONF_DEFAULT_PROJECT_ID: user_input[CONF_DEFAULT_PROJECT_ID],
                        CONF_DEFAULT_TRACKER_ID: user_input.get(
                            CONF_DEFAULT_TRACKER_ID, DEFAULT_TRACKER_ID
                        ),
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
