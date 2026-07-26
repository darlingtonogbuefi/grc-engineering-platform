"""
GRC Engineering Platform
Validation Package

Provides JSON Schema validation for:

- Evidence
- Controls
- Frameworks
- Collectors
- Tenants
- Reports
- Risks
"""

from .schema_validator import SchemaValidator

__all__ = [
    "SchemaValidator",
]
