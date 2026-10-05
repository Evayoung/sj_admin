"""Inquiry repository — operations for inquiries."""

from __future__ import annotations

from datetime import datetime
from typing import Any
import uuid

from app.infrastructure.supabase_client import get_service_client, has_supabase


_LOCAL_INQUIRIES: dict[str, dict] = {}


def _init_default_inquiries():
    if _LOCAL_INQUIRIES:
        return
    inq1 = "inq-meshell-2026-001"
    _LOCAL_INQUIRIES[inq1] = {
        "id": inq1,
        "customer_name": "Chief Meshell",
        "phone": "09029952120",
        "email": "meshell@sjinteriors.ng",
        "message": "Property Type: Duplex | Estimated Windows: 8 Windows | Location: Ilorin | Notes: Interested in full living room drape styling and bedroom blackout curtains.",
        "source": "services_page",
        "service_inquiry": True,
        "selected_services": [
            "sitting-room-curtains",
            "bedroom-curtains",
            "interior-decor-blinds",
            "luxury-bedding",
        ],
        "status": "new",
        "created_at": datetime.now().isoformat(),
    }
    inq2 = "inq-meshell-2026-002"
    _LOCAL_INQUIRIES[inq2] = {
        "id": inq2,
        "customer_name": "Mrs. Adebayo",
        "phone": "08026022672",
        "email": "adebayo@gmail.com",
        "message": "Need 4 sets of 400TC white duvets and king mattresses for our new guest rooms in GRA.",
        "source": "contact_form",
        "service_inquiry": False,
        "selected_services": [],
        "status": "contacted",
        "created_at": datetime.now().isoformat(),
    }


def get_all_inquiries(status: str = "") -> list[dict]:
    """Fetch all inquiries, optionally filtered by status."""
    _init_default_inquiries()
    if has_supabase():
        client = get_service_client()
        if client:
            try:
                query = client.table("inquiries").select("*")
                if status and status != "all":
                    query = query.eq("status", status)
                result = query.order("created_at", desc=True).execute()
                return getattr(result, "data", []) or []
            except Exception:
                pass

    inquiries = list(_LOCAL_INQUIRIES.values())
    if status and status != "all":
        inquiries = [i for i in inquiries if i.get("status") == status]
    return sorted(inquiries, key=lambda i: i.get("created_at", ""), reverse=True)


def get_inquiry_by_id(inquiry_id: str) -> dict | None:
    """Fetch a single inquiry by ID."""
    _init_default_inquiries()
    if has_supabase():
        client = get_service_client()
        if client:
            try:
                result = client.table("inquiries").select("*").eq("id", inquiry_id).execute()
                rows = getattr(result, "data", [])
                if rows:
                    return rows[0]
            except Exception:
                pass

    return _LOCAL_INQUIRIES.get(inquiry_id)


def update_inquiry_status(inquiry_id: str, status: str, notes: str = "") -> dict | None:
    """Update inquiry status and notes."""
    _init_default_inquiries()
    inquiry = get_inquiry_by_id(inquiry_id)
    if inquiry:
        inquiry["status"] = status
        if notes:
            inquiry["notes"] = notes
        _LOCAL_INQUIRIES[inquiry_id] = inquiry

    if has_supabase():
        client = get_service_client()
        if client:
            try:
                data = {"status": status}
                if notes:
                    data["notes"] = notes
                result = client.table("inquiries").update(data).eq("id", inquiry_id).execute()
                rows = getattr(result, "data", [])
                if rows:
                    return rows[0]
            except Exception:
                pass

    return _LOCAL_INQUIRIES.get(inquiry_id)

