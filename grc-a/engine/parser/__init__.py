"""
GRC Engineering Platform
Parser Package

Provides:

- YAML parsing
- JSON parsing
- Evidence normalisation
"""

from .evidence_parser import EvidenceParser
from .json_parser import JSONParser
from .yaml_parser import YAMLParser

__all__ = [
    "YAMLParser",
    "JSONParser",
    "EvidenceParser",
]
