#collectors\entra\client.py

"""
Microsoft Graph API client.

Provides authenticated requests to the
Microsoft Graph API for Entra collectors.
"""

from __future__ import annotations

import logging
import time

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from collectors.base.client import BaseClient
from collectors.base.exceptions import (
    ClientError,
    RateLimitError,
)

logger = logging.getLogger(__name__)


class EntraClient(BaseClient):
    """Microsoft Graph API client."""

    BASE_URL = "https://graph.microsoft.com/v1.0"

    DEFAULT_RETRIES = 3
    DEFAULT_BACKOFF = 1.0

    def __init__(self, *args, **kwargs):
        """Initialize the Graph client."""
        super().__init__(*args, **kwargs)

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

        adapter = HTTPAdapter(max_retries=retry)

        self.session = requests.Session()
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def send(
        self,
        method: str,
        endpoint: str,
        token: str,
        **kwargs,
    ):
        """
        Execute a Microsoft Graph request.

        Handles authentication, retries,
        throttling, and error handling.
        """

        url = (
            endpoint
            if endpoint.startswith("http")
            else f"{self.BASE_URL}{endpoint}"
        )

        headers = kwargs.pop("headers", {})
        headers.update(
            {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        )

        logger.debug("%s %s", method.upper(), url)

        response = self.session.request(
            method=method,
            url=url,
            headers=headers,
            timeout=self.timeout,
            **kwargs,
        )

        #
        # Graph throttling
        #
        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After")

            if retry_after:
                try:
                    delay = int(retry_after)

                    logger.warning(
                        "Graph API throttled. "
                        "Retrying after %s seconds.",
                        delay,
                    )

                    time.sleep(delay)

                    response = self.session.request(
                        method=method,
                        url=url,
                        headers=headers,
                        timeout=self.timeout,
                        **kwargs,
                    )

                except ValueError:
                    pass

            if response.status_code == 429:
                raise RateLimitError(
                    "Microsoft Graph rate limit exceeded"
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
        token: str,
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
        token: str,
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
        token: str,
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
        token: str,
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
        token: str,
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
        token: str,
        **kwargs,
    ):
        """
        Execute a GET request and return JSON.
        """
        return self.get(
            endpoint,
            token,
            **kwargs,
        ).json()

    def get_all_pages(
        self,
        endpoint: str,
        token: str,
        **kwargs,
    ):
        """
        Retrieve all paginated results from
        Microsoft Graph.

        Returns:
            list: Combined items from every page.
        """

        items = []

        response = self.get(
            endpoint,
            token,
            **kwargs,
        ).json()

        while True:
            items.extend(response.get("value", []))

            next_link = response.get("@odata.nextLink")

            if not next_link:
                break

            logger.debug(
                "Fetching next Graph page: %s",
                next_link,
            )

            response = self.get(
                next_link,
                token,
            ).json()

        return items
