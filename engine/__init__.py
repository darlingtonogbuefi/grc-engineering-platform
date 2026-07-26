"""
GRC Engineering Platform
========================

Core engine package.

Supports:

- CAF
- ISO 27001
- SOC 2
- GovAssure
- Cyber Essentials

This package provides the core runtime used for:

- Configuration loading
- Collector orchestration
- Evidence parsing
- Framework validation
- Control mapping
- Scoring
- Report generation
"""

from .version import (
    __author__,
    __license__,
    __title__,
    __version__,
)

__all__ = [
    "__title__",
    "__version__",
    "__author__",
    "__license__",
]
