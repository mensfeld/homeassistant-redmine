"""Redmine API client."""

from __future__ import annotations

import logging
from typing import Any

from aiohttp import ClientError, ClientResponseError, ClientSession

_LOGGER = logging.getLogger(__name__)


class RedmineApiError(Exception):
    """Base exception for Redmine API errors."""


class RedmineAuthError(RedmineApiError):
    """Authentication error."""


class RedmineConnectionError(RedmineApiError):
    """Connection error."""


class RedmineClient:
    """Async client for Redmine API."""

    def __init__(
        self,
        session: ClientSession,
        redmine_url: str,
        api_key: str,
    ) -> None:
        """Initialize the Redmine client.

        Args:
            session: aiohttp ClientSession from Home Assistant.
            redmine_url: Base URL of the Redmine instance.
            api_key: Redmine API key for authentication.
        """
        self._session = session
        self._base_url = redmine_url.rstrip("/")
        self._api_key = api_key

    @property
    def _headers(self) -> dict[str, str]:
        """Return headers for API requests."""
        return {
            "X-Redmine-API-Key": self._api_key,
            "Content-Type": "application/json",
        }

    async def validate_connection(self) -> bool:
        """Validate the connection and API key by fetching current user.

        Returns:
            True if connection is valid.

        Raises:
            RedmineAuthError: If authentication fails.
            RedmineConnectionError: If connection fails.
        """
        try:
            async with self._session.get(
                f"{self._base_url}/users/current.json",
                headers=self._headers,
                timeout=10,
            ) as response:
                if response.status == 401:
                    raise RedmineAuthError("Invalid API key")
                response.raise_for_status()
                return True
        except ClientResponseError as err:
            if err.status == 401:
                raise RedmineAuthError("Invalid API key") from err
            raise RedmineConnectionError(f"API error: {err.status}") from err
        except ClientError as err:
            raise RedmineConnectionError(f"Connection failed: {err}") from err

    async def create_issue(
        self,
        project_id: str,
        subject: str,
        tracker_id: int,
        description: str | None = None,
        priority_id: int | None = None,
    ) -> dict[str, Any]:
        """Create a new issue in Redmine.

        Args:
            project_id: Project identifier (string slug or numeric ID).
            subject: Issue subject/title.
            tracker_id: Tracker ID (e.g., 1 for Bug).
            description: Optional issue description.
            priority_id: Optional priority ID (e.g., 2 for Normal).

        Returns:
            Created issue data from Redmine API.

        Raises:
            RedmineApiError: If issue creation fails.
        """
        payload: dict[str, Any] = {
            "issue": {
                "project_id": project_id,
                "subject": subject,
                "tracker_id": tracker_id,
            }
        }

        if description:
            payload["issue"]["description"] = description
        if priority_id:
            payload["issue"]["priority_id"] = priority_id

        try:
            async with self._session.post(
                f"{self._base_url}/issues.json",
                headers=self._headers,
                json=payload,
                timeout=30,
            ) as response:
                if response.status == 401:
                    raise RedmineAuthError("Invalid API key")
                if response.status == 422:
                    error_data = await response.json()
                    errors = error_data.get("errors", ["Unknown validation error"])
                    raise RedmineApiError(f"Validation error: {', '.join(errors)}")
                response.raise_for_status()
                result = await response.json()
                _LOGGER.debug("Created issue: %s", result)
                return result
        except ClientResponseError as err:
            raise RedmineApiError(f"Failed to create issue: {err.status}") from err
        except ClientError as err:
            raise RedmineConnectionError(f"Connection failed: {err}") from err
