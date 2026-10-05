"""Category repository — CRUD operations for categories."""

from __future__ import annotations

import uuid
from typing import Any

from app.infrastructure.supabase_client import get_service_client, has_supabase

_LOCAL_CATEGORIES: dict[str, dict] = {}


def get_all_categories() -> list[dict]:
    """Fetch all categories ordered by sort_order."""
    if has_supabase():
        client = get_service_client()
        if client:
            try:
                result = client.table("categories").select("*").order("sort_order").execute()
                return getattr(result, "data", [])
            except Exception:
                pass

    cats = list(_LOCAL_CATEGORIES.values())
    return sorted(cats, key=lambda c: c.get("sort_order", 0))


def get_category_by_id(category_id: str) -> dict | None:
    """Fetch a single category by ID."""
    if has_supabase():
        client = get_service_client()
        if client:
            try:
                result = client.table("categories").select("*").eq("id", category_id).execute()
                rows = getattr(result, "data", [])
                if rows:
                    return rows[0]
            except Exception:
                pass
    return _LOCAL_CATEGORIES.get(category_id)


def create_category(data: dict) -> dict | None:
    """Create a new category."""
    if has_supabase():
        client = get_service_client()
        if client:
            try:
                result = client.table("categories").insert(data).execute()
                rows = getattr(result, "data", [])
                if rows:
                    return rows[0]
            except Exception as e:
                print(f"Error creating category: {e}")

    item = dict(data)
    item["id"] = item.get("id") or str(uuid.uuid4())
    _LOCAL_CATEGORIES[item["id"]] = item
    return item


def update_category(category_id: str, data: dict) -> dict | None:
    """Update an existing category."""
    if has_supabase():
        client = get_service_client()
        if client:
            try:
                result = client.table("categories").update(data).eq("id", category_id).execute()
                rows = getattr(result, "data", [])
                if rows:
                    return rows[0]
            except Exception as e:
                print(f"Error updating category: {e}")

    if category_id in _LOCAL_CATEGORIES:
        _LOCAL_CATEGORIES[category_id].update(data)
        return _LOCAL_CATEGORIES[category_id]
    return None


def delete_category(category_id: str) -> bool:
    """Delete a category."""
    if has_supabase():
        client = get_service_client()
        if client:
            try:
                client.table("categories").delete().eq("id", category_id).execute()
                return True
            except Exception as e:
                print(f"Error deleting category: {e}")

    return _LOCAL_CATEGORIES.pop(category_id, None) is not None
