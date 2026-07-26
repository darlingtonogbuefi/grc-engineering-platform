"""
Custom exceptions used throughout the GRC Engineering Platform.
"""


class GRCError(Exception):
    """Base exception for the platform."""


#
# Configuration
#

class ConfigurationError(GRCError):
    """Raised when configuration is invalid."""


class TenantConfigurationError(ConfigurationError):
    """Invalid tenant configuration."""


class FrameworkConfigurationError(ConfigurationError):
    """Invalid framework configuration."""


class CollectorConfigurationError(ConfigurationError):
    """Invalid collector configuration."""


#
# Validation
#

class ValidationError(GRCError):
    """Base validation error."""


class SchemaValidationError(ValidationError):
    """JSON schema validation failed."""


class EvidenceValidationError(ValidationError):
    """Evidence failed validation."""


class FrameworkValidationError(ValidationError):
    """Framework failed validation."""


#
# Collection
#

class CollectorError(GRCError):
    """Collector execution failed."""


class AuthenticationError(CollectorError):
    """Authentication failed."""


class ConnectionError(CollectorError):
    """Unable to connect to external system."""


class RateLimitError(CollectorError):
    """External API rate limit exceeded."""


#
# Parsing
#

class ParserError(GRCError):
    """Parser failed."""


class YAMLParseError(ParserError):
    """Invalid YAML."""


class JSONParseError(ParserError):
    """Invalid JSON."""


#
# Reporting
#

class ReportingError(GRCError):
    """Report generation failed."""


class ExportError(ReportingError):
    """Export operation failed."""


#
# Scoring
#

class ScoringError(GRCError):
    """Scoring engine failure."""


class RiskCalculationError(ScoringError):
    """Risk calculation failure."""
