"""Supabase client singleton for SJ Interiors Admin."""

from __future__ import annotations

import logging
import re
from functools import lru_cache

from app.config import settings

logger = logging.getLogger(__name__)


def _normalize_supabase_url(raw_url: str) -> str:
    """Normalize raw URL string to a valid Supabase HTTPS REST endpoint."""
    if not raw_url:
        return ""
    url = raw_url.strip()
    if url.startswith("postgresql://") or url.startswith("postgres://"):
        # Extract project reference, e.g. postgres.zekxadnuciejhfmsgytf:...
        match = re.search(r"postgres(?:ql)?://(?:postgres\.)?([a-z0-9]+):", url)
        if match:
            ref = match.group(1)
            return f"https://{ref}.supabase.co"
    return url.rstrip("/")


@lru_cache(maxsize=1)
def get_service_client():
    """Return a singleton Supabase service-role client or None if not configured."""
    url = _normalize_supabase_url(settings.supabase_url)
    key = settings.supabase_service_key
    if not url or not key:
        logger.debug("Supabase credentials not configured.")
        return None
    try:
        from supabase import create_client
        return create_client(url, key)
    except ImportError:
        logger.warning("Supabase package not installed. Run `pip install supabase`.")
        return None
    except Exception as exc:
        logger.error("Failed to initialize Supabase client: %s", exc)
        return None


def has_supabase() -> bool:
    """Check if Supabase client can be initialized."""
    return get_service_client() is not None

