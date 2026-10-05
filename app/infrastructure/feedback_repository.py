"""Feedback & complaints repository for SJ Interiors.

Handles:
1. Public reviews and testimonials with 1-click publishing to storefront.
2. Client complaints and service tickets with status resolution workflow and audit logging.
"""

from __future__ import annotations

import time
import uuid
from typing import Any

from app.infrastructure.supabase_client import get_service_client, has_supabase

# In-memory storage for feedback & complaints (fallback and fast local dev)
_LOCAL_FEEDBACK: list[dict[str, Any]] = [
    {
        "id": "fb-2026-001",
        "created_at": "2026-09-28T14:30:00Z",
        "kind": "review",
        "customer_name": "Mrs. Folashade Adeyemi",
        "customer_phone": "08026022672",
        "customer_email": "folashade@example.com",
        "rating": 5,
        "project_category": "Living Room Curtains & Sheers",
        "location_tag": "GRA Ilorin",
        "message": "The luxury pleated curtains completely elevated our parlor! Mercy and the team arrived on time for measurements and installation was flawless.",
        "order_ref": "REC-2026-0088",
        "complaint_type": "",
        "urgency": "normal",
        "status": "published",
        "is_published": True,
        "assigned_to": "Mercy",
        "resolution_notes": "Client sent video of completed parlor. Highly satisfied.",
        "resolved_at": "2026-09-28T16:00:00Z",
    },
    {
        "id": "fb-2026-002",
        "created_at": "2026-10-01T11:15:00Z",
        "kind": "review",
        "customer_name": "Dr. Tunde Balogun",
        "customer_phone": "08033112244",
        "customer_email": "tunde.balogun@example.com",
        "rating": 5,
        "project_category": "Bespoke Hotel Bedding Sets",
        "location_tag": "Fate Road, Ilorin",
        "message": "Top quality cotton duvet sets. The finishing is crisp and hotel-grade. Christianah kept us updated throughout the bulk production.",
        "order_ref": "INV-2026-0105",
        "complaint_type": "",
        "urgency": "normal",
        "status": "published",
        "is_published": True,
        "assigned_to": "Christianah",
        "resolution_notes": "Delivered 12 duvet sets to guesthouse.",
        "resolved_at": "2026-10-01T12:00:00Z",
    },
    {
        "id": "fb-2026-003",
        "created_at": "2026-10-04T09:45:00Z",
        "kind": "complaint",
        "customer_name": "Alhaji Ibrahim Sani",
        "customer_phone": "08182233445",
        "customer_email": "i.sani@example.com",
        "rating": 0,
        "project_category": "Dining Room Roman Blinds",
        "location_tag": "Tanke, Ilorin",
        "message": "The left side blind pull cord feels slightly stiff after initial installation yesterday. Kindly send a technician to adjust the track.",
        "order_ref": "INV-2026-0112",
        "complaint_type": "Installation Support",
        "urgency": "urgent",
        "status": "investigating",
        "is_published": False,
        "assigned_to": "Mercy",
        "resolution_notes": "Installer scheduled to visit Tanke premises on Tuesday morning.",
        "resolved_at": "",
    },
]


def create_feedback(data: dict[str, Any]) -> dict[str, Any]:
    """Record a new review or complaint from public or admin."""
    fb_id = f"fb-2026-{uuid.uuid4().hex[:6]}"
    now_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    kind = data.get("kind", "review").lower()
    is_review = kind == "review"

    entry: dict[str, Any] = {
        "id": fb_id,
        "created_at": now_iso,
        "kind": kind,
        "customer_name": str(data.get("customer_name") or "Valued Client").strip(),
        "customer_phone": str(data.get("customer_phone") or "").strip(),
        "customer_email": str(data.get("customer_email") or "").strip(),
        "rating": int(data.get("rating") or 5) if is_review else 0,
        "project_category": str(data.get("project_category") or "General Interior Furnishing").strip(),
        "location_tag": str(data.get("location_tag") or "Ilorin, Kwara State").strip(),
        "message": str(data.get("message") or "").strip(),
        "order_ref": str(data.get("order_ref") or "").strip(),
        "complaint_type": str(data.get("complaint_type") or ("Review" if is_review else "General Inquiry")).strip(),
        "urgency": str(data.get("urgency") or "normal").strip(),
        "status": "pending" if is_review else "open",
        "is_published": False,
        "assigned_to": str(data.get("assigned_to") or ""),
        "resolution_notes": "",
        "resolved_at": "",
    }

    _LOCAL_FEEDBACK.insert(0, entry)

    if has_supabase():
        client = get_service_client()
        if client:
            try:
                client.table("client_feedback").insert(entry).execute()
            except Exception:
                pass

    return entry


def get_all_feedback(kind: str = "all", status: str = "all") -> list[dict[str, Any]]:
    """Retrieve feedback filtered by kind ('all', 'review', 'complaint') and status."""
    if has_supabase():
        client = get_service_client()
        if client:
            try:
                q = client.table("client_feedback").select("*").order("created_at", desc=True)
                if kind != "all":
                    q = q.eq("kind", kind)
                if status != "all":
                    q = q.eq("status", status)
                res = q.execute()
                data = getattr(res, "data", [])
                if data:
                    return data
            except Exception:
                pass

    # In-memory filter
    results = _LOCAL_FEEDBACK
    if kind != "all":
        results = [fb for fb in results if fb.get("kind") == kind]
    if status != "all":
        results = [fb for fb in results if fb.get("status") == status]
    return sorted(results, key=lambda x: x.get("created_at", ""), reverse=True)


def get_feedback_by_id(fb_id: str) -> dict[str, Any] | None:
    """Find a feedback item by ID."""
    for fb in _LOCAL_FEEDBACK:
        if fb.get("id") == fb_id:
            return fb
    if has_supabase():
        client = get_service_client()
        if client:
            try:
                res = client.table("client_feedback").select("*").eq("id", fb_id).execute()
                rows = getattr(res, "data", [])
                if rows:
                    return rows[0]
            except Exception:
                pass
    return None


def toggle_publish_testimonial(fb_id: str) -> dict[str, Any] | None:
    """Toggle publication status of a review for public storefront display."""
    target = None
    for fb in _LOCAL_FEEDBACK:
        if fb.get("id") == fb_id and fb.get("kind") == "review":
            current = fb.get("is_published", False)
            fb["is_published"] = not current
            fb["status"] = "published" if fb["is_published"] else "pending"
            target = fb
            break

    if has_supabase() and target:
        client = get_service_client()
        if client:
            try:
                client.table("client_feedback").update({
                    "is_published": target["is_published"],
                    "status": target["status"],
                }).eq("id", fb_id).execute()
            except Exception:
                pass

    return target


def update_complaint_status(
    fb_id: str,
    status: str,
    resolution_notes: str = "",
    assigned_to: str = "",
) -> dict[str, Any] | None:
    """Update complaint status (open, investigating, resolved) with sister notes."""
    target = None
    now_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    for fb in _LOCAL_FEEDBACK:
        if fb.get("id") == fb_id:
            fb["status"] = status
            if resolution_notes:
                fb["resolution_notes"] = resolution_notes
            if assigned_to:
                fb["assigned_to"] = assigned_to
            if status == "resolved":
                fb["resolved_at"] = now_iso
            target = fb
            break

    if has_supabase() and target:
        client = get_service_client()
        if client:
            try:
                updates: dict[str, Any] = {"status": status}
                if resolution_notes:
                    updates["resolution_notes"] = resolution_notes
                if assigned_to:
                    updates["assigned_to"] = assigned_to
                if status == "resolved":
                    updates["resolved_at"] = now_iso
                client.table("client_feedback").update(updates).eq("id", fb_id).execute()
            except Exception:
                pass

    return target


def get_published_testimonials() -> list[dict[str, Any]]:
    """Get all approved published reviews formatted for the storefront testimonials carousel."""
    reviews = [
        fb for fb in _LOCAL_FEEDBACK
        if fb.get("kind") == "review" and fb.get("is_published", False)
    ]
    if has_supabase():
        client = get_service_client()
        if client:
            try:
                res = client.table("client_feedback").select("*").eq("kind", "review").eq("is_published", True).order("created_at", desc=True).execute()
                rows = getattr(res, "data", [])
                if rows:
                    reviews = rows
            except Exception:
                pass

    formatted = []
    for r in reviews:
        formatted.append({
            "name": r.get("customer_name") or "Valued Client",
            "role": f"{r.get('location_tag', 'Kwara State')} · {r.get('project_category', 'Interior Styling')}",
            "text": r.get("message", ""),
            "rating": r.get("rating", 5),
        })
    return formatted
