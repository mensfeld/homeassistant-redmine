"""Tests for the Redmine API client."""
import pytest
from aiohttp import ClientSession
from unittest.mock import AsyncMock, MagicMock, patch

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "custom_components"))

from redmine.api import (
    RedmineClient,
    RedmineApiError,
    RedmineAuthError,
    RedmineConnectionError,
)


@pytest.fixture
def mock_session():
    """Create a mock aiohttp session."""
    return MagicMock(spec=ClientSession)


@pytest.fixture
def redmine_client(mock_session):
    """Create a Redmine client with mock session."""
    return RedmineClient(
        session=mock_session,
        redmine_url="https://redmine.example.com",
        api_key="test_api_key",
    )


class TestRedmineClient:
    """Tests for RedmineClient."""

    def test_init(self, redmine_client):
        """Test client initialization."""
        assert redmine_client._base_url == "https://redmine.example.com"
        assert redmine_client._api_key == "test_api_key"

    def test_init_strips_trailing_slash(self, mock_session):
        """Test that trailing slash is removed from URL."""
        client = RedmineClient(
            session=mock_session,
            redmine_url="https://redmine.example.com/",
            api_key="test_api_key",
        )
        assert client._base_url == "https://redmine.example.com"

    def test_headers(self, redmine_client):
        """Test that headers are correctly set."""
        headers = redmine_client._headers
        assert headers["X-Redmine-API-Key"] == "test_api_key"
        assert headers["Content-Type"] == "application/json"

    @pytest.mark.asyncio
    async def test_validate_connection_success(self, redmine_client, mock_session):
        """Test successful connection validation."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.raise_for_status = MagicMock()

        mock_context = AsyncMock()
        mock_context.__aenter__.return_value = mock_response
        mock_session.get.return_value = mock_context

        result = await redmine_client.validate_connection()
        assert result is True

    @pytest.mark.asyncio
    async def test_validate_connection_auth_error(self, redmine_client, mock_session):
        """Test connection validation with invalid API key."""
        mock_response = AsyncMock()
        mock_response.status = 401

        mock_context = AsyncMock()
        mock_context.__aenter__.return_value = mock_response
        mock_session.get.return_value = mock_context

        with pytest.raises(RedmineAuthError, match="Invalid API key"):
            await redmine_client.validate_connection()

    @pytest.mark.asyncio
    async def test_create_issue_success(self, redmine_client, mock_session):
        """Test successful issue creation."""
        mock_response = AsyncMock()
        mock_response.status = 201
        mock_response.raise_for_status = MagicMock()
        mock_response.json = AsyncMock(
            return_value={"issue": {"id": 123, "subject": "Test Issue"}}
        )

        mock_context = AsyncMock()
        mock_context.__aenter__.return_value = mock_response
        mock_session.post.return_value = mock_context

        result = await redmine_client.create_issue(
            project_id="test-project",
            subject="Test Issue",
            tracker_id=1,
            description="Test description",
            priority_id=2,
        )

        assert result["issue"]["id"] == 123
        assert result["issue"]["subject"] == "Test Issue"

    @pytest.mark.asyncio
    async def test_create_issue_validation_error(self, redmine_client, mock_session):
        """Test issue creation with validation error."""
        mock_response = AsyncMock()
        mock_response.status = 422
        mock_response.json = AsyncMock(
            return_value={"errors": ["Project is invalid", "Subject is too short"]}
        )

        mock_context = AsyncMock()
        mock_context.__aenter__.return_value = mock_response
        mock_session.post.return_value = mock_context

        with pytest.raises(RedmineApiError, match="Validation error"):
            await redmine_client.create_issue(
                project_id="invalid-project",
                subject="X",
                tracker_id=1,
            )

    @pytest.mark.asyncio
    async def test_create_issue_auth_error(self, redmine_client, mock_session):
        """Test issue creation with auth error."""
        mock_response = AsyncMock()
        mock_response.status = 401

        mock_context = AsyncMock()
        mock_context.__aenter__.return_value = mock_response
        mock_session.post.return_value = mock_context

        with pytest.raises(RedmineAuthError, match="Invalid API key"):
            await redmine_client.create_issue(
                project_id="test-project",
                subject="Test Issue",
                tracker_id=1,
            )


class TestExceptions:
    """Tests for custom exceptions."""

    def test_redmine_api_error(self):
        """Test RedmineApiError exception."""
        error = RedmineApiError("Test error")
        assert str(error) == "Test error"
        assert isinstance(error, Exception)

    def test_redmine_auth_error(self):
        """Test RedmineAuthError exception."""
        error = RedmineAuthError("Auth failed")
        assert str(error) == "Auth failed"
        assert isinstance(error, RedmineApiError)

    def test_redmine_connection_error(self):
        """Test RedmineConnectionError exception."""
        error = RedmineConnectionError("Connection failed")
        assert str(error) == "Connection failed"
        assert isinstance(error, RedmineApiError)
