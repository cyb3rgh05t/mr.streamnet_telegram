"""Shared cache module for API routers"""

import time
from typing import Any, Dict, Optional

# Shared cache for cross-router data
_shared_cache: Dict[str, Dict[str, Any]] = {
    "total_members": {"value": 0, "timestamp": 0},
}

# Cache TTL in seconds (5 minutes for member count)
MEMBER_CACHE_TTL = 300


def set_total_members(count: int):
    """Update the cached total member count"""
    _shared_cache["total_members"] = {
        "value": count,
        "timestamp": time.time(),
    }


def get_total_members() -> int:
    """Get the cached total member count"""
    cached = _shared_cache.get("total_members", {})
    return cached.get("value", 0)


def get_total_members_age() -> float:
    """Get how old the cached member count is in seconds"""
    cached = _shared_cache.get("total_members", {})
    timestamp = cached.get("timestamp", 0)
    if timestamp == 0:
        return float("inf")
    return time.time() - timestamp


def is_member_cache_valid() -> bool:
    """Check if the member cache is still valid"""
    return get_total_members_age() < MEMBER_CACHE_TTL
