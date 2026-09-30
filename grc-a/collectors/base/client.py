"""
Base API Client.
Provides common API behaviour for all evidence collectors.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Iterator, Optional
import logging
import time

from .exceptions import ClientError, RateLimitError

logger = logging.getLogger(__name__)


class BaseClient(ABC):
    """Common API client interface."""

    def __init__(self, authenticator, config: Optional[Dict[str, Any]] = None):
        self.authenticator = authenticator
        self.config = config or {}
        self.timeout = self.config.get("timeout", 60)
        self.max_retries = self.config.get("max_retries", 3)

    def request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        retries = 0

        while retries <= self.max_retries:
            try:
                token = self.authenticator.get_token()
                response = self.send(
                    method=method,
                    endpoint=endpoint,
                    token=token,
                    **kwargs,
                )
                return self.handle_response(response)

            except RateLimitError:
                retries += 1
                time.sleep(2 ** retries)

            except Exception as exc:
                retries += 1
                if retries > self.max_retries:
                    raise ClientError(endpoint) from exc

        raise ClientError("Maximum retries exceeded")

    @abstractmethod
    def send(self, method: str, endpoint: str, token: str, **kwargs):
        """Execute provider-specific API request."""
        pass

    def get(self, endpoint: str, **kwargs):
        return self.request("GET", endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs):
        return self.request("POST", endpoint, **kwargs)

    def handle_response(self, response):
        if response.status_code >= 400:
            raise ClientError(response.text)
        return response.json()

    def paginate(self, endpoint: str, **kwargs) -> Iterator[Dict[str, Any]]:
        response = self.get(endpoint, **kwargs)

        while response:
            yield response

            next_page = response.get("@odata.nextLink")

            if not next_page:
                break

            response = self.get(next_page)
