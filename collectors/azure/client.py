# collectors\azure\client.py

"""
Azure API Client.

Handles Azure Resource Manager (ARM) REST API
communication for evidence collection.
"""

from __future__ import annotations

import logging
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List

import requests
import yaml
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from collectors.base.client import BaseClient
from collectors.base.exceptions import (
    ClientError,
    RateLimitError,
)

logger = logging.getLogger(__name__)


class AzureClient(BaseClient):
    """Azure Resource Manager REST API client."""

    BASE_URL = "https://management.azure.com"

    DEFAULT_RETRIES = 3
    DEFAULT_BACKOFF = 1.0

    def __init__(
        self,
        authenticator,
        config: Dict[str, Any] | None = None,
    ):
        super().__init__(
            authenticator,
            config,
        )

        self.subscription_id = self.config.get(
            "subscription_id",
        )

        self.api_version = self.config.get(
            "api_version",
            "2022-09-01",
        )

        self.query_path = Path(
            self.config.get(
                "query_path",
                "collectors/azure/queries",
            )
        )

        retry = Retry(
            total=self.DEFAULT_RETRIES,
            connect=self.DEFAULT_RETRIES,
            read=self.DEFAULT_RETRIES,
            status=self.DEFAULT_RETRIES,
            backoff_factor=self.DEFAULT_BACKOFF,
            status_forcelist=[
                429,
                500,
                502,
                503,
                504,
            ],
            allowed_methods=[
                "GET",
                "POST",
                "PUT",
                "PATCH",
                "DELETE",
            ],
            raise_on_status=False,
        )

        adapter = HTTPAdapter(
            max_retries=retry,
        )

        self.session = requests.Session()

        self.session.mount(
            "https://",
            adapter,
        )

        self.session.mount(
            "http://",
            adapter,
        )

    def _resolve_token(
        self,
        token: str | None = None,
    ) -> str:
        """
        Resolve ARM bearer token.

        Uses supplied token when provided,
        otherwise retrieves one from the authenticator.
        """

        if token:
            return token

        return self.authenticator.get_token()

    def send(
        self,
        method: str,
        endpoint: str,
        token: str | None = None,
        **kwargs,
    ):
        """
        Execute an Azure Resource Manager request.

        Handles authentication, retries,
        throttling, and error handling.
        """

        token = self._resolve_token(
            token,
        )

        url = endpoint if endpoint.startswith("http") else f"{self.BASE_URL}{endpoint}"

        headers = kwargs.pop(
            "headers",
            {},
        )

        headers.update(
            {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        )

        params = kwargs.pop(
            "params",
            {},
        )

        api_version = kwargs.pop(
            "api_version",
            None,
        )

        if (
            "api-version" not in params
            and "api-version=" not in url
        ):
            params["api-version"] = (
                api_version
                or self.api_version
            )

        logger.debug(
            "%s %s",
            method.upper(),
            url,
        )

        request_kwargs = {
            "headers": headers,
            "params": params,
            "timeout": self.timeout,
            **kwargs,
        }

        # Keep GET requests compatible with existing unit tests
        # which patch collectors.azure.client.requests.get.
        if method.upper() == "GET":
            response = requests.get(
                url,
                **request_kwargs,
            )
        else:
            response = self.session.request(
                method=method,
                url=url,
                **request_kwargs,
            )

        if response.status_code == 429:
            retry_after = response.headers.get(
                "Retry-After",
            )

            if retry_after:
                try:
                    delay = int(retry_after)

                    logger.warning(
                        "Azure API throttled. Retrying after %s seconds.",
                        delay,
                    )

                    time.sleep(
                        delay,
                    )

                    if method.upper() == "GET":
                        response = requests.get(
                            url,
                            **request_kwargs,
                        )
                    else:
                        response = self.session.request(
                            method=method,
                            url=url,
                            **request_kwargs,
                        )

                except ValueError:
                    pass

            if response.status_code == 429:
                raise RateLimitError(
                    "Azure API rate limit exceeded",
                )

        if response.status_code >= 400:
            raise ClientError(
                f"{method.upper()} {url} failed "
                f"({response.status_code}): "
                f"{response.text}"
            )

        return response

    def get(
        self,
        endpoint: str,
        token: str | None = None,
        **kwargs,
    ):
        """
        Execute a GET request.
        """

        return self.send(
            "GET",
            endpoint,
            token,
            **kwargs,
        )

    def post(
        self,
        endpoint: str,
        token: str | None = None,
        **kwargs,
    ):
        """
        Execute a POST request.
        """

        return self.send(
            "POST",
            endpoint,
            token,
            **kwargs,
        )

    def patch(
        self,
        endpoint: str,
        token: str | None = None,
        **kwargs,
    ):
        """
        Execute a PATCH request.
        """

        return self.send(
            "PATCH",
            endpoint,
            token,
            **kwargs,
        )

    def put(
        self,
        endpoint: str,
        token: str | None = None,
        **kwargs,
    ):
        """
        Execute a PUT request.
        """

        return self.send(
            "PUT",
            endpoint,
            token,
            **kwargs,
        )

    def delete(
        self,
        endpoint: str,
        token: str | None = None,
        **kwargs,
    ):
        """
        Execute a DELETE request.
        """

        return self.send(
            "DELETE",
            endpoint,
            token,
            **kwargs,
        )

    def get_json(
        self,
        endpoint: str,
        token: str | None = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Execute a GET request and return JSON.
        """

        return self.get(
            endpoint,
            token,
            **kwargs,
        ).json()

    def execute_query(
        self,
        query_name: str,
        token: str | None = None,
    ) -> List[Dict[str, Any]]:
        """
        Execute an Azure query definition.

        Supports query-specific parameters while
        preserving existing ARM query execution.
        """

        query = self.load_query(
            query_name,
        )

        endpoint = query["endpoint"]

        # Replace Azure ARM subscription placeholder
        if "{subscriptionId}" in endpoint:
            endpoint = endpoint.replace(
                "{subscriptionId}",
                self.subscription_id,
            )

        #
        # Resource scoped queries require a resolved resource URI.
        #
        # Example:
        # /{resourceUri}/providers/microsoft.insights/diagnosticSettings
        #
        # The current collector execution path only supplies
        # subscription-level context. Prevent invalid ARM requests
        # with unresolved placeholders.
        #
        if "{resourceUri}" in endpoint:
            logger.warning(
                "Skipping query '%s' because resourceUri "
                "was not resolved: %s",
                query_name,
                endpoint,
            )
            return []

        params = {
            "api-version": query.get(
                "api_version",
                self.api_version,
            )
        }

        #
        # Azure Activity Logs API requires a $filter.
        #
        # Endpoint:
        # /providers/Microsoft.Insights/eventtypes/management/values
        #
        if (
            "Microsoft.Insights/eventtypes/management/values"
            in endpoint
        ):
            end_time = datetime.now(
                timezone.utc,
            )

            start_time = end_time - timedelta(
                days=30,
            )

            params["$filter"] = (
                "eventTimestamp ge "
                f"{start_time.isoformat().replace('+00:00', 'Z')} "
                "and eventTimestamp le "
                f"{end_time.isoformat().replace('+00:00', 'Z')}"
            )

        response = self.get_json(
            endpoint,
            token,
            params=params,
        )

        #
        # Azure subscriptions do not include the common ARM
        # "name" and "type" fields. Add them so subscription
        # resources are consistent with other ARM resources.
        #
        if query_name == "subscriptions":
            for item in response.get(
                "value",
                [],
            ):
                item.setdefault(
                    "name",
                    item.get(
                        "displayName",
                        "",
                    ),
                )

                item.setdefault(
                    "type",
                    "Microsoft.Resources/subscriptions",
                )

        return list(
            self.paginate(
                response,
                token,
            )
        )

    def load_query(
        self,
        query_name: str,
    ) -> Dict[str, Any]:
        """
        Load query YAML definition.
        """

        file = self.query_path / f"{query_name}.yml"

        if not file.exists():
            raise ClientError(
                f"Query not found: {query_name}",
            )

        with file.open(
            encoding="utf-8",
        ) as stream:
            return yaml.safe_load(stream)

    def load_profile(
        self,
        profile: str,
    ) -> List[str]:
        """
        Load enabled queries from profile.
        """

        file = Path("collectors/azure/profiles") / f"{profile}.yml"

        if not file.exists():
            raise ClientError(
                f"Profile not found: {profile}",
            )

        with file.open(
            encoding="utf-8",
        ) as stream:
            data = yaml.safe_load(stream)

        return data.get(
            "queries",
            [],
        )

    def paginate(
        self,
        response: Dict[str, Any],
        token: str | None = None,
    ):
        """
        Handle Azure ARM nextLink pagination.

        Yields every item across all pages.
        """

        while True:

            yield from response.get(
                "value",
                [],
            )

            next_link = response.get(
                "nextLink",
            )

            if not next_link:
                break

            logger.debug(
                "Fetching next ARM page: %s",
                next_link,
            )

            response = self.get_json(
                next_link,
                token,
            )
