"""Brand repository — operations for brand_config."""

from __future__ import annotations

from typing import Any

from app.infrastructure.supabase_client import get_service_client, has_supabase


def get_brand_config() -> dict:
    """Fetch all brand config as a dict."""
    if not has_supabase():
        return {}
    client = get_service_client()
    if not client:
        return {}
    try:
        result = client.table("brand_config").select("key,value").execute()
        rows = getattr(result, "data", [])
        return {row["key"]: row["value"] for row in rows if row.get("key")}
    except Exception:
        return {}


def update_brand_config(key: str, value: Any) -> bool:
    """Update or insert a brand config key."""
    if not has_supabase():
        return False
    client = get_service_client()
    if not client:
        return False
    try:
        # Try update first
        result = client.table("brand_config").update({"value": value}).eq("key", key).execute()
        if getattr(result, "data", []):
            return True
        # If no rows updated, insert
        result = client.table("brand_config").insert({"key": key, "value": value}).execute()
        return bool(getattr(result, "data", []))
    except Exception:
        return False
