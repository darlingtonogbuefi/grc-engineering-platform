"""
GRC Engineering Platform
Mapping Package

Responsible for translating validated evidence into
framework controls.

Pipeline

Evidence
    |
    v
ControlMapper
    |
    v
Framework Mapper
    |
    v
Scoring Engine
"""

from .control_mapper import (
    ControlMapper,
    ControlMapping,
    MappingResult,
)

__all__ = [
    "ControlMapper",
    "ControlMapping",
    "MappingResult",
]
