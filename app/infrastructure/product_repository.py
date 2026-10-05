"""Product repository — CRUD operations for products."""

from __future__ import annotations

import uuid
from typing import Any

from app.infrastructure.supabase_client import get_service_client, has_supabase

_LOCAL_PRODUCTS: dict[str, dict] = {}


def get_all_products(category_slug: str = "") -> list[dict]:
    """Fetch all products, optionally filtered by category."""
    if has_supabase():
        client = get_service_client()
        if client:
            try:
                query = client.table("products").select("*")
                if category_slug and category_slug != "all":
                    query = query.eq("category_slug", category_slug)
                result = query.order("created_at", desc=True).execute()
                return getattr(result, "data", [])
            except Exception:
                pass

    prods = list(_LOCAL_PRODUCTS.values())
    if category_slug and category_slug != "all":
        prods = [p for p in prods if p.get("category_slug") == category_slug]
    return sorted(prods, key=lambda p: p.get("created_at", ""), reverse=True)


def get_product_by_id(product_id: str) -> dict | None:
    """Fetch a single product by ID."""
    if has_supabase():
        client = get_service_client()
        if client:
            try:
                result = client.table("products").select("*").eq("id", product_id).execute()
                rows = getattr(result, "data", [])
                if rows:
                    return rows[0]
            except Exception:
                pass
    return _LOCAL_PRODUCTS.get(product_id)


def create_product(data: dict) -> dict | None:
    """Create a new product."""
    if has_supabase():
        client = get_service_client()
        if client:
            try:
                result = client.table("products").insert(data).execute()
                rows = getattr(result, "data", [])
                if rows:
                    return rows[0]
            except Exception as e:
                print(f"Error creating product: {e}")

    item = dict(data)
    item["id"] = item.get("id") or str(uuid.uuid4())
    _LOCAL_PRODUCTS[item["id"]] = item
    return item


def update_product(product_id: str, data: dict) -> dict | None:
    """Update an existing product."""
    if has_supabase():
        client = get_service_client()
        if client:
            try:
                result = client.table("products").update(data).eq("id", product_id).execute()
                rows = getattr(result, "data", [])
                if rows:
                    return rows[0]
            except Exception as e:
                print(f"Error updating product: {e}")

    if product_id in _LOCAL_PRODUCTS:
        _LOCAL_PRODUCTS[product_id].update(data)
        return _LOCAL_PRODUCTS[product_id]
    return None


def delete_product(product_id: str) -> bool:
    """Delete a product."""
    if has_supabase():
        client = get_service_client()
        if client:
            try:
                client.table("products").delete().eq("id", product_id).execute()
                return True
            except Exception as e:
                print(f"Error deleting product: {e}")

    return _LOCAL_PRODUCTS.pop(product_id, None) is not None
