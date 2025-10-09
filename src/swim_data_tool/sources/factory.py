"""Factory for creating swim data source instances."""

import os
from typing import Type

from swim_data_tool.sources.base import SwimDataSource


# Registry of available data sources
_SOURCES: dict[str, Type[SwimDataSource]] = {}


def register_source(name: str, source_class: Type[SwimDataSource]) -> None:
    """Register a data source implementation.
    
    Args:
        name: Source identifier (e.g., "usa_swimming", "maxpreps")
        source_class: Class implementing SwimDataSource
    """
    _SOURCES[name.lower()] = source_class


def get_source(source_name: str | None = None) -> SwimDataSource:
    """Get data source instance by name.
    
    Args:
        source_name: Source identifier (e.g., "usa_swimming", "maxpreps")
                    If None, uses DATA_SOURCE from environment or defaults to "usa_swimming"
    
    Returns:
        Instantiated SwimDataSource
    
    Raises:
        ValueError: If source_name is unknown
    """
    # Determine source name
    if source_name is None:
        source_name = os.getenv("DATA_SOURCE", "usa_swimming")
    
    source_name = source_name.lower()
    
    # Get source class
    if source_name not in _SOURCES:
        available = ", ".join(_SOURCES.keys())
        raise ValueError(
            f"Unknown data source: '{source_name}'. "
            f"Available sources: {available}"
        )
    
    source_class = _SOURCES[source_name]
    return source_class()


def list_sources() -> list[str]:
    """List all registered data sources.
    
    Returns:
        List of source identifiers
    """
    return sorted(_SOURCES.keys())


def get_source_info() -> dict[str, str]:
    """Get information about all registered sources.
    
    Returns:
        Dictionary mapping source identifier to source name
    """
    info = {}
    for source_id, source_class in _SOURCES.items():
        # Instantiate to get source_name property
        instance = source_class()
        info[source_id] = instance.source_name
    return info


# Auto-register sources on import
def _auto_register_sources() -> None:
    """Auto-register available data source implementations."""
    try:
        from swim_data_tool.sources.usa_swimming import USASwimmingSource
        register_source("usa_swimming", USASwimmingSource)
    except ImportError:
        pass  # USA Swimming source not available
    
    try:
        from swim_data_tool.sources.maxpreps import MaxPrepsSource
        register_source("maxpreps", MaxPrepsSource)
    except ImportError:
        pass  # MaxPreps source not available


# Register on module import
_auto_register_sources()


