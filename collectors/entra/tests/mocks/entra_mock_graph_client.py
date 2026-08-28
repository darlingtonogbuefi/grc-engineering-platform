"""
Mock Microsoft Graph client.

Provides deterministic Microsoft Graph
responses for unit testing without
calling the live Microsoft Graph API.
"""

from __future__ import annotations

from collectors.entra.tests.mocks.mock_responses import (
    RESPONSES,
)


class MockResponse:
    """Mock HTTP response."""

    def __init__(self, data):
        self._data = data
        self.status_code = 200

    def json(self):
        """Return response JSON."""
        return self._data


class MockGraphClient:
    """Mock Microsoft Graph client."""

    BASE_URL = "https://graph.microsoft.com/v1.0"

    def get(
        self,
        endpoint,
        token=None,
        **kwargs,
    ):
        """
        Return a mock HTTP response.
        """

        return MockResponse(
            RESPONSES.get(
                endpoint,
                {"value": []},
            )
        )

    def get_json(
        self,
        endpoint,
        token=None,
        **kwargs,
    ):
        """
        Return mock JSON response.
        """

        return RESPONSES.get(
            endpoint,
            {"value": []},
        )

    def get_all_pages(
        self,
        endpoint,
        token=None,
        **kwargs,
    ):
        """
        Return mock paginated data.
        """

        response = RESPONSES.get(
            endpoint,
            {"value": []},
        )

        return response.get(
            "value",
            [],
        )
