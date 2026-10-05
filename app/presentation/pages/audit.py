"""Audit trail presentation page for SJ Interiors Admin.

Displays a chronological log of all actions performed by the two sister owners:
- Fatima vs Zainab
- Action types (Create, Update, Delete, Payment, Auth, Settings)
- Targets, human-readable summaries, timestamps, and IP origins
"""

from __future__ import annotations

from typing import Any
from fasthtml.common import A, Button, Div, H3, H4, P, Small, Span, Table, Tbody, Td, Th, Thead, Tr
from faststrap import Badge, Card, Col, Icon, Row

from app.presentation.page_helpers import empty_state, filter_pill


def _action_badge(action: str) -> Span:
    act = action.upper()
    if act in {"CREATE_PRODUCT", "CREATE_DOCUMENT", "CREATE_ORDER", "CREATE_CATEGORY", "CREATE_SERVICE", "LOGIN_SUCCESS", "GENERATE_RECEIPT"}:
        variant = "success"
    elif act in {"UPDATE_PRODUCT", "UPDATE_DOCUMENT", "UPDATE_ORDER_STATUS", "UPDATE_SETTINGS", "UPDATE_CATEGORY", "UPDATE_SERVICE", "UPDATE_SISTER_PROFILE"}:
        variant = "warning"
    elif act in {"DELETE_PRODUCT", "DELETE_DOCUMENT", "DELETE_ORDER", "DELETE_CATEGORY", "DELETE_SERVICE", "DELETE_MEDIA", "LOGIN_FAILED"}:
        variant = "danger"
    elif act in {"PASSWORD_RESET", "PASSWORD_RESET_REQUESTED", "UPLOAD_MEDIA"}:
        variant = "primary"
    else:
        variant = "secondary"

    return Badge(act.replace("_", " "), variant=variant, cls="fw-semibold font-monospace small")


def _actor_pill(actor_name: str, actor_email: str) -> Div:
    combined = (actor_name + " " + actor_email).lower()
    is_mercy = "mercy" in combined or "alademercy" in combined or "fatima" in combined
    is_christianah = "christianah" in combined or "christiana" in combined or "zainab" in combined
    
    if is_mercy:
        bg = "#f3e8ff"
        color = "#6b21a8"
        label = "Mercy"
    elif is_christianah:
        bg = "#fef3c7"
        color = "#b45309"
        label = "Christianah"
    else:
        bg = "#f1f5f9"
        color = "#334155"
        label = actor_name or "Admin"

    return Div(
        Span(label[:1].upper(), cls="rounded-circle text-white fw-bold d-inline-flex align-items-center justify-content-center me-2",
             style=f"width: 24px; height: 24px; background-color: {color}; font-size: 0.75rem;"),
        Div(
            Span(label, cls="fw-bold d-block", style=f"color: {color}; font-size: 0.82rem; line-height: 1.1;"),
            Small(actor_email or "alademercy93@gmail.com", cls="text-muted", style="font-size: 0.72rem;"),
        ),
        cls="d-flex align-items-center py-1 px-2 rounded-3",
        style=f"background-color: {bg}; border: 1px solid rgba(0,0,0,0.05); display: inline-flex;",
    )


def audit_trail_page(logs: list[dict[str, Any]], active_actor: str = "all", active_action: str = "all") -> list:
    """Render audit trail activity log page."""
    # Filter pills
    actor_filters = [
        filter_pill("All Sisters", "/audit-trail", active_actor == "all"),
        filter_pill("Mercy", "/audit-trail?actor=Mercy", active_actor.lower() in ("mercy", "fatima")),
        filter_pill("Christianah", "/audit-trail?actor=Christianah", active_actor.lower() in ("christianah", "zainab")),
    ]

    action_filters = [
        filter_pill("All Actions", f"/audit-trail?actor={active_actor}" if active_actor != "all" else "/audit-trail", active_action == "all"),
        filter_pill("Catalog & Stock", f"/audit-trail?action=product&actor={active_actor}", active_action == "product"),
        filter_pill("Documents & Invoices", f"/audit-trail?action=document&actor={active_actor}", active_action == "document"),
        filter_pill("Orders", f"/audit-trail?action=order&actor={active_actor}", active_action == "order"),
        filter_pill("Security & Auth", f"/audit-trail?action=auth&actor={active_actor}", active_action == "auth"),
    ]

    if not logs:
        content = empty_state("No Activity Logged Yet", "Actions performed by Mercy or Christianah will appear here automatically.")
    else:
        rows = []
        for log in logs:
            action = log.get("action", "")
            actor_name = log.get("actor_name", "Admin")
            actor_email = log.get("actor_email", "")
            target_type = log.get("target_type", "")
            target_id = log.get("target_id", "")
            details = log.get("details", "")
            ip = log.get("ip_address", "127.0.0.1")
            ts = log.get("created_at", "")[:19].replace("T", " ")

            rows.append(
                Tr(
                    Td(
                        Small(ts, cls="font-monospace text-muted d-block", style="font-size: 0.75rem; white-space: nowrap;"),
                        Small(f"IP: {ip}", cls="text-muted d-block", style="font-size: 0.68rem;"),
                        style="vertical-align: middle; width: 14%;",
                    ),
                    Td(
                        _actor_pill(actor_name, actor_email),
                        style="vertical-align: middle; width: 22%;",
                    ),
                    Td(
                        _action_badge(action),
                        style="vertical-align: middle; width: 16%;",
                    ),
                    Td(
                        P(details, cls="mb-0 text-dark small fw-medium", style="font-size: 0.85rem;"),
                        Small(f"Target: {target_type.title()} · {target_id}", cls="text-muted", style="font-size: 0.72rem;") if target_id else "",
                        style="vertical-align: middle; width: 48%;",
                    ),
                    cls="border-bottom",
                )
            )

        content = Div(
            Table(
                Thead(
                    Tr(
                        Th("Timestamp & Origin", cls="small fw-bold text-muted border-0 py-2", style="font-size: 0.78rem;"),
                        Th("Administrator (Sister)", cls="small fw-bold text-muted border-0 py-2", style="font-size: 0.78rem;"),
                        Th("Action Taken", cls="small fw-bold text-muted border-0 py-2", style="font-size: 0.78rem;"),
                        Th("Details & Modification Summary", cls="small fw-bold text-muted border-0 py-2", style="font-size: 0.78rem;"),
                        cls="bg-light border-bottom",
                    ),
                ),
                Tbody(*rows),
                cls="table table-hover align-middle mb-0",
            ),
            cls="table-responsive rounded-3 border",
        )

    return [
        Div(
            Card(
                Div(
                    Div(
                        H3("System Audit Trail", cls="h5 fw-bold mb-1 text-dark"),
                        P("Detailed chronological record of every administrative action performed across the store.", cls="text-muted small mb-0"),
                    ),
                    Badge(f"{len(logs)} Events Recorded", variant="primary", cls="px-3 py-2"),
                    cls="d-flex flex-wrap justify-content-between align-items-center gap-2 mb-3 pb-3 border-bottom",
                ),
                Div(
                    Div(
                        Span("Filter by Sister:", cls="small fw-bold text-muted me-2"),
                        *actor_filters,
                        cls="d-flex flex-wrap align-items-center gap-1 mb-2 mb-md-0",
                    ),
                    Div(
                        Span("Category:", cls="small fw-bold text-muted me-2"),
                        *action_filters,
                        cls="d-flex flex-wrap align-items-center gap-1",
                    ),
                    cls="d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-2 mb-4 p-3 bg-light rounded-3 border",
                ),
                content,
                cls="p-4 border-0 shadow-sm",
            ),
            cls="mb-4",
        )
    ]
