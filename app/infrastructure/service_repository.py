"""Service repository — CRUD operations for services."""

from __future__ import annotations

import uuid
from typing import Any

from app.infrastructure.supabase_client import get_service_client, has_supabase

_LOCAL_SERVICES: dict[str, dict] = {}


def get_all_services() -> list[dict]:
    """Fetch all services ordered by sort_order."""
    if has_supabase():
        client = get_service_client()
        if client:
            try:
                result = client.table("services").select("*").order("sort_order").execute()
                return getattr(result, "data", [])
            except Exception:
                pass

    services = list(_LOCAL_SERVICES.values())
    return sorted(services, key=lambda s: s.get("sort_order", 0))


def get_service_by_id(service_id: str) -> dict | None:
    """Fetch a single service by ID."""
    if has_supabase():
        client = get_service_client()
        if client:
            try:
                result = client.table("services").select("*").eq("id", service_id).execute()
                rows = getattr(result, "data", [])
                if rows:
                    return rows[0]
            except Exception:
                pass
    return _LOCAL_SERVICES.get(service_id)


def create_service(data: dict) -> dict | None:
    """Create a new service."""
    if has_supabase():
        client = get_service_client()
        if client:
            try:
                result = client.table("services").insert(data).execute()
                rows = getattr(result, "data", [])
                if rows:
                    return rows[0]
            except Exception as e:
                print(f"Error creating service: {e}")

    item = dict(data)
    item["id"] = item.get("id") or str(uuid.uuid4())
    _LOCAL_SERVICES[item["id"]] = item
    return item


def update_service(service_id: str, data: dict) -> dict | None:
    """Update an existing service."""
    if has_supabase():
        client = get_service_client()
        if client:
            try:
                result = client.table("services").update(data).eq("id", service_id).execute()
                rows = getattr(result, "data", [])
                if rows:
                    return rows[0]
            except Exception as e:
                print(f"Error updating service: {e}")

    if service_id in _LOCAL_SERVICES:
        _LOCAL_SERVICES[service_id].update(data)
        return _LOCAL_SERVICES[service_id]
    return None


def delete_service(service_id: str) -> bool:
    """Delete a service."""
    if has_supabase():
        client = get_service_client()
        if client:
            try:
                client.table("services").delete().eq("id", service_id).execute()
                return True
            except Exception as e:
                print(f"Error deleting service: {e}")

    return _LOCAL_SERVICES.pop(service_id, None) is not None
