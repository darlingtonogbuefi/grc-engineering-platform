# collectors\azure\tests\mocks\mock_arm_client.py

"""
Mock Azure Resource Manager client.

Provides offline test behaviour for Azure collectors
without requiring live Azure authentication or API calls.
"""

from __future__ import annotations

from typing import Any


class MockARMClient:
    """
    Mock implementation of AzureClient.

    Used by unit tests to simulate Azure Resource Manager
    API responses.
    """

    def __init__(
        self,
        responses: dict[str, Any] | None = None,
    ) -> None:

        self.responses = responses or {}
        self.requests: list[str] = []

    def get_json(
        self,
        endpoint: str,
        token: str | None = None,
    ) -> dict[str, Any]:
        """
        Return mocked ARM response.

        Records requested endpoints for assertions.
        """

        self.requests.append(endpoint)

        return self.responses.get(
            endpoint,
            {"value": []},
        )

    def get_request_history(
        self,
    ) -> list[str]:
        """
        Return all requested endpoints.
        """

        return self.requests

    def set_response(
        self,
        endpoint: str,
        response: dict[str, Any],
    ) -> None:
        """
        Add or update mocked endpoint response.
        """

        self.responses[endpoint] = response
