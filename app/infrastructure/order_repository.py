"""Order repository — operations for orders."""

from __future__ import annotations

from datetime import datetime
from typing import Any
import uuid

from app.infrastructure.supabase_client import get_service_client, has_supabase


_LOCAL_ORDERS: dict[str, dict] = {}


_DEFAULT_ORDER_ID = "550e8400-e29b-41d4-a716-446655440042"


def _init_default_orders():
    if _LOCAL_ORDERS:
        return
    _LOCAL_ORDERS[_DEFAULT_ORDER_ID] = {
        "id": _DEFAULT_ORDER_ID,
        "order_number": "SJ-2026-0042",
        "customer_name": "Chief Meshell",
        "phone": "09029952120",
        "items": [
            "2x 400TC Luxury White Duvet Set (6x6)",
            "1x Sitting Room Jacquard Bronze Curtain Package (3 Windows)",
            "4x Standard Hotel Cloud Comfort Pillows",
        ],
        "status": "processing",
        "total_amount": 165000,
        "notes": "Custom stitching completed. Delivery scheduled for Friday morning.",
        "created_at": datetime.now().isoformat(),
    }


def generate_order_number() -> str:
    """Generate sequential or timestamped order number, e.g. SJ-2026-0042."""
    year = datetime.now().year
    rand_seq = f"{int(datetime.now().strftime('%m%d%H%M')) % 9000 + 1000}"
    return f"SJ-{year}-{rand_seq}"


def get_all_orders(status: str = "") -> list[dict]:
    """Fetch all orders, optionally filtered by status."""
    _init_default_orders()
    if has_supabase():
        client = get_service_client()
        if client:
            try:
                query = client.table("orders").select("*")
                if status and status != "all":
                    query = query.eq("status", status)
                result = query.order("created_at", desc=True).execute()
                return getattr(result, "data", []) or []
            except Exception as exc:
                print(f"Supabase fetch orders fallback: {exc}")

    orders = list(_LOCAL_ORDERS.values())
    if status and status != "all":
        orders = [o for o in orders if o.get("status") == status]
    return sorted(orders, key=lambda o: o.get("created_at", ""), reverse=True)


def get_order_by_id(order_id: str) -> dict | None:
    """Fetch a single order by ID."""
    _init_default_orders()
    if has_supabase():
        client = get_service_client()
        if client:
            try:
                result = client.table("orders").select("*").eq("id", order_id).execute()
                rows = getattr(result, "data", [])
                if rows:
                    return rows[0]
            except Exception:
                pass

    return _LOCAL_ORDERS.get(order_id)


def create_order(data: dict) -> dict | None:
    """Create a new order."""
    _init_default_orders()
    if not data.get("order_number"):
        data["order_number"] = generate_order_number()

    # Always use valid UUID format for PostgreSQL uuid primary key compatibility
    raw_id = data.get("id")
    if not raw_id or raw_id.startswith("ord-"):
        ord_id = str(uuid.uuid4())
    else:
        ord_id = raw_id
    data["id"] = ord_id
    data["created_at"] = data.get("created_at") or datetime.now().isoformat()
    _LOCAL_ORDERS[ord_id] = data

    if has_supabase():
        client = get_service_client()
        if client:
            try:
                result = client.table("orders").insert(data).execute()
                rows = getattr(result, "data", [])
                if rows:
                    _LOCAL_ORDERS[ord_id] = rows[0]
                    return rows[0]
            except Exception as e:
                print(f"Supabase order insert fallback: {e}")

    return _LOCAL_ORDERS[ord_id]

def update_order(order_id: str, data: dict) -> dict | None:
    """Update an existing order."""
    _init_default_orders()
    existing = get_order_by_id(order_id)
    if existing:
        for k, v in data.items():
            existing[k] = v
        _LOCAL_ORDERS[order_id] = existing

    if has_supabase():
        client = get_service_client()
        if client:
            try:
                result = client.table("orders").update(data).eq("id", order_id).execute()
                rows = getattr(result, "data", [])
                if rows:
                    return rows[0]
            except Exception as e:
                print(f"Supabase update order fallback: {e}")

    return _LOCAL_ORDERS.get(order_id)


def delete_order(order_id: str) -> bool:
    """Delete an order."""
    _init_default_orders()
    if order_id in _LOCAL_ORDERS:
        del _LOCAL_ORDERS[order_id]
    if has_supabase():
        client = get_service_client()
        if client:
            try:
                client.table("orders").delete().eq("id", order_id).execute()
            except Exception:
                pass
    return True


def update_order_status(order_id: str, status: str, notes: str = "") -> dict | None:
    """Update order status and notes."""
    _init_default_orders()
    order = get_order_by_id(order_id)
    if order:
        order["status"] = status
        if notes:
            order["notes"] = notes
        _LOCAL_ORDERS[order_id] = order

    if has_supabase():
        client = get_service_client()
        if client:
            try:
                data = {"status": status}
                if notes:
                    data["notes"] = notes
                result = client.table("orders").update(data).eq("id", order_id).execute()
                rows = getattr(result, "data", [])
                if rows:
                    return rows[0]
            except Exception:
                pass

    return _LOCAL_ORDERS.get(order_id)

