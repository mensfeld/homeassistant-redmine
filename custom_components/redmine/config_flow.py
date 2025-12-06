"""Config flow for Redmine integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .api import RedmineAuthError, RedmineClient, RedmineConnectionError
from .const import (
    CONF_API_KEY,
    CONF_DEFAULT_PRIORITY_ID,
    CONF_DEFAULT_PROJECT_ID,
    CONF_DEFAULT_TRACKER_ID,
    CONF_REDMINE_URL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_REDMINE_URL): str,
        vol.Required(CONF_API_KEY): str,
    }
)


class RedmineConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Redmine."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._redmine_url: str | None = None
        self._api_key: str | None = None
        self._client: RedmineClient | None = None
        self._projects: list[dict] = []
        self._priorities: list[dict] = []
        self._trackers: list[dict] = []

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the initial step - URL and API key."""
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
                # Store credentials for next step
                self._redmine_url = redmine_url
                self._api_key = user_input[CONF_API_KEY]
                self._client = client

                # Fetch projects, priorities, and trackers
                try:
                    self._projects = await client.get_projects()
                    self._priorities = await client.get_priorities()
                    self._trackers = await client.get_trackers()
                except RedmineConnectionError as err:
                    _LOGGER.error("Failed to fetch options: %s", err)
                    errors["base"] = "cannot_fetch_options"

            if not errors:
                return await self.async_step_options()

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    async def async_step_options(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the options step - select defaults."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Set unique ID to prevent duplicate entries
            await self.async_set_unique_id(self._redmine_url)
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=f"Redmine ({self._redmine_url})",
                data={
                    CONF_REDMINE_URL: self._redmine_url,
                    CONF_API_KEY: self._api_key,
                    CONF_DEFAULT_PROJECT_ID: user_input[CONF_DEFAULT_PROJECT_ID],
                    CONF_DEFAULT_TRACKER_ID: int(user_input[CONF_DEFAULT_TRACKER_ID]),
                    CONF_DEFAULT_PRIORITY_ID: int(user_input[CONF_DEFAULT_PRIORITY_ID]),
                },
            )

        # Build options for dropdowns
        project_options = [
            SelectOptionDict(value=p["identifier"], label=p["name"]) for p in self._projects
        ]
        tracker_options = [
            SelectOptionDict(value=str(t["id"]), label=t["name"]) for t in self._trackers
        ]
        priority_options = [
            SelectOptionDict(value=str(p["id"]), label=p["name"]) for p in self._priorities
        ]

        # Find default priority (marked as is_default in Redmine)
        default_priority = next(
            (str(p["id"]) for p in self._priorities if p.get("is_default")),
            str(self._priorities[0]["id"]) if self._priorities else "2",
        )

        # Build dynamic schema with selectors
        options_schema = vol.Schema(
            {
                vol.Required(CONF_DEFAULT_PROJECT_ID): SelectSelector(
                    SelectSelectorConfig(
                        options=project_options,
                        mode=SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Required(
                    CONF_DEFAULT_TRACKER_ID,
                    default=str(self._trackers[0]["id"]) if self._trackers else "1",
                ): SelectSelector(
                    SelectSelectorConfig(
                        options=tracker_options,
                        mode=SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Required(
                    CONF_DEFAULT_PRIORITY_ID,
                    default=default_priority,
                ): SelectSelector(
                    SelectSelectorConfig(
                        options=priority_options,
                        mode=SelectSelectorMode.DROPDOWN,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="options",
            data_schema=options_schema,
            errors=errors,
        )
