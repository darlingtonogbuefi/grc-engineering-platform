"""
Collector exception hierarchy.

Provides standard exceptions used across
all evidence collectors.
"""


class CollectorException(Exception):
    """Base exception for collector failures."""

    pass


class CollectorError(CollectorException):
    """General collector execution failure."""

    pass


class AuthenticationError(CollectorException):
    """Authentication or credential failure."""

    pass


class ClientError(CollectorException):
    """API client communication failure."""

    pass


class RateLimitError(ClientError):
    """API rate limit exceeded."""

    pass


class EvidenceError(CollectorException):
    """Evidence creation or storage failure."""

    pass


class ValidationError(CollectorException):
    """Evidence validation failure."""

    pass


class ManifestError(CollectorException):
    """Collector manifest configuration failure."""

    pass


class ConfigurationError(CollectorException):
    """Invalid collector configuration."""

    pass
