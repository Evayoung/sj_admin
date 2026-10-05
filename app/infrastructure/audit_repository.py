"""Audit Trail repository for SJ Interiors Admin.

Tracks every significant action performed on the portal:
- Who did what (Fatima vs Zainab vs System)
- Action type (Create, Update, Delete, Payment, Auth, Settings)
- Target entity and human-readable details
- Timestamp and client IP
Persists to Supabase `audit_logs` table with full in-memory fallback.
"""

from __future__ import annotations

import time
import uuid
from collections import deque
from typing import Any

from app.infrastructure.supabase_client import get_service_client, has_supabase

# In-memory circular buffer of last 500 audit entries for instant querying & offline resilience
_LOCAL_AUDIT_LOGS: deque[dict[str, Any]] = deque(maxlen=500)


def _get_client_ip(req: Any) -> str:
    """Safely extract client IP from Starlette Request."""
    if not req:
        return "127.0.0.1"
    try:
        # Check reverse proxy headers first
        headers = getattr(req, "headers", {})
        forwarded = headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        real_ip = headers.get("x-real-ip")
        if real_ip:
            return real_ip.strip()
        client = getattr(req, "client", None)
        if client and hasattr(client, "host"):
            return client.host or "127.0.0.1"
    except Exception:
        pass
    return "127.0.0.1"


def log_activity(
    req: Any,
    session: dict[str, Any] | None,
    action: str,
    target_type: str,
    target_id: str = "",
    details: str = "",
    actor_override: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Record an audit trail log entry for an admin action."""
    session = session or {}
    actor_id = (actor_override.get("id") if actor_override else None) or session.get("admin_user_id") or session.get("admin_user") or "system"
    actor_name = (actor_override.get("name") if actor_override else None) or session.get("admin_user_name") or session.get("admin_user") or "System / Admin"
    actor_email = (actor_override.get("email") if actor_override else None) or session.get("admin_email") or "admin@sjinteriors.com"
    ip = _get_client_ip(req)
    now_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    entry: dict[str, Any] = {
        "id": str(uuid.uuid4()),
        "actor_id": str(actor_id),
        "actor_name": str(actor_name),
        "actor_email": str(actor_email),
        "action": str(action).upper(),
        "target_type": str(target_type).lower(),
        "target_id": str(target_id),
        "details": str(details),
        "ip_address": ip,
        "created_at": now_iso,
    }

    # Always prepend to local memory store
    _LOCAL_AUDIT_LOGS.appendleft(entry)

    # Persist to Supabase if connected
    if has_supabase():
        client = get_service_client()
        if client:
            try:
                client.table("audit_logs").insert(entry).execute()
            except Exception:
                pass

    return entry


def get_audit_logs(
    limit: int = 100,
    actor: str | None = None,
    action: str | None = None,
    target_type: str | None = None,
) -> list[dict[str, Any]]:
    """Retrieve audit logs with optional filters."""
    # Check Supabase first
    if has_supabase():
        client = get_service_client()
        if client:
            try:
                query = client.table("audit_logs").select("*").order("created_at", desc=True).limit(limit)
                if actor:
                    query = query.ilike("actor_name", f"%{actor}%")
                if action:
                    query = query.eq("action", action.upper())
                if target_type:
                    query = query.eq("target_type", target_type.lower())
                res = query.execute()
                data = getattr(res, "data", [])
                if data:
                    return data
            except Exception:
                pass

    # Filter local in-memory logs
    logs = list(_LOCAL_AUDIT_LOGS)
    if actor:
        actor_clean = actor.lower()
        logs = [e for e in logs if actor_clean in e.get("actor_name", "").lower() or actor_clean in e.get("actor_email", "").lower()]
    if action and action != "ALL":
        action_clean = action.upper()
        logs = [e for e in logs if e.get("action") == action_clean]
    if target_type and target_type != "all":
        tt_clean = target_type.lower()
        logs = [e for e in logs if e.get("target_type") == tt_clean]

    return logs[:limit]


def get_recent_audit_logs(limit: int = 5) -> list[dict[str, Any]]:
    """Get the N most recent activities for dashboard widgets."""
    return get_audit_logs(limit=limit)
