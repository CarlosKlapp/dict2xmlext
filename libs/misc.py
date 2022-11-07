from typing import Any, Optional


def coalesce(*values: Any) -> Optional[Any]:
    """Return the first non-None value or None if all values are None"""
    return next((v for v in values if v is not None), None)
