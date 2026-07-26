"""
Azure API Client.

Handles Azure REST API communication
for evidence collection.
"""

from __future__ import annotations

from typing import Any, Dict, List
from pathlib import Path
import yaml
import logging

import requests

from collectors.base.client import BaseClient
from collectors.base.exceptions import ClientError


logger = logging.getLogger(__name__)


class AzureClient(BaseClient):
    """Azure REST API client."""

    BASE_URL = (
        "https://management.azure.com"
    )

    def __init__(
        self,
        authenticator,
        config: Dict[str, Any] | None = None,
    ):
        super().__init__(
            authenticator,
            config,
        )

        self.subscription_id = (
            self.config.get(
                "subscription_id"
            )
        )

        self.api_version = (
            self.config.get(
                "api_version",
                "2022-09-01",
            )
        )

        self.query_path = Path(
            self.config.get(
                "query_path",
                "collectors/azure/queries",
            )
        )

    def send(
        self,
        method: str,
        endpoint: str,
        token: str,
        **kwargs,
    ):
        """
        Execute Azure REST request.
        """

        url = (
            endpoint
            if endpoint.startswith("https://")
            else f"{self.BASE_URL}{endpoint}"
        )

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        try:
            return requests.request(
                method,
                url,
                headers=headers,
                timeout=self.timeout,
                **kwargs,
            )

        except requests.RequestException as exc:
            raise ClientError(
                "Azure API request failed"
            ) from exc

    def execute_query(
        self,
        query_name: str,
    ) -> List[Dict[str, Any]]:
        """
        Execute Azure query definition.
        """

        query = self.load_query(
            query_name
        )

        endpoint = query["endpoint"]

        response = self.get(
            endpoint
        )

        return response.get(
            "value",
            []
        )

    def load_query(
        self,
        query_name: str,
    ) -> Dict[str, Any]:
        """
        Load query YAML definition.
        """

        file = (
            self.query_path
            / f"{query_name}.yml"
        )

        if not file.exists():
            raise ClientError(
                f"Query not found: {query_name}"
            )

        with file.open() as stream:
            return yaml.safe_load(stream)

    def load_profile(
        self,
        profile: str,
    ) -> List[str]:
        """
        Load enabled queries from profile.
        """

        file = (
            Path(
                "collectors/azure/profiles"
            )
            / f"{profile}.yml"
        )

        if not file.exists():
            raise ClientError(
                f"Profile not found: {profile}"
            )

        with file.open() as stream:
            data = yaml.safe_load(stream)

        return data.get(
            "queries",
            [],
        )

    def paginate(
        self,
        response: Dict[str, Any],
    ):
        """
        Handle Azure nextLink pagination.
        """

        while response:

            yield from response.get(
                "value",
                [],
            )

            next_link = response.get(
                "nextLink"
            )

            if not next_link:
                break

            response = self.get(
                next_link
            )
