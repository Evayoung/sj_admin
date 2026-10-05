"""Dashboard overview page with real data and auto-refresh."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from fasthtml.common import A, Div, H2, H3, P, Span
from faststrap import Badge, Button, Card, Col, Container, Icon, Row

from app.presentation.page_helpers import summary_card


def _format_date(date_str: str) -> str:
    """Format ISO date to short form."""
    if not date_str:
        return ""
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return dt.strftime("%b %d, %H:%M")
    except Exception:
        return str(date_str)[:10]


def _status_badge(status: str) -> Span:
    """Status badge with color."""
    colors = {
        "new": "primary", "contacted": "info", "ordered": "success", "closed": "secondary",
        "processing": "warning", "shipped": "info", "delivered": "success", "cancelled": "danger",
    }
    return Badge(status.replace("_", " ").title(), variant=colors.get(status, "secondary"), cls="ms-1")


def _source_badge(source: str) -> Span:
    """Source badge for inquiries."""
    icons = {"whatsapp": "whatsapp", "contact_form": "envelope", "phone": "telephone", "services_page": "wrench"}
    icon = icons.get(source, "circle")
    return Span(Icon(icon, cls="me-1"), source.replace("_", " ").title(), cls="badge bg-light text-dark")


def metrics_row(data: dict) -> list:
    """Render metrics row (extracted for HTMX auto-refresh)."""
    return [
        Row(
            Col(summary_card("Products", str(data.get("products", 0)), "box-seam"), lg=3, md=6, cols=6, cls="mb-3"),
            Col(summary_card("Categories", str(data.get("categories", 0)), "tags"), lg=3, md=6, cols=6, cls="mb-3"),
            Col(summary_card("New Inquiries", str(data.get("inquiries", 0)), "inbox"), lg=3, md=6, cols=6, cls="mb-3"),
            Col(summary_card("Orders Active", str(data.get("orders", 0)), "cart"), lg=3, md=6, cols=6, cls="mb-3"),
            cls="g-3",
        ),
    ]


def dashboard_page(data: dict) -> list:
    """Render dashboard with real Supabase data."""
    recent_inquiries = data.get("recent_inquiries", [])
    recent_orders = data.get("recent_orders", [])

    return [
        # Metrics row with HTMX auto-refresh every 30s
        Div(
            *metrics_row(data),
            id="dashboard-metrics",
            hx_get="/dashboard/metrics",
            hx_trigger="every 30s",
            hx_swap="outerHTML",
        ),

        # Quick Actions
        Div(
            H3("Quick Actions", cls="admin-section-title"),
            Row(
                Col(
                    A(Icon("plus-circle", cls="me-2"), Span("Add Product"), href="/products?new=1", cls="btn btn-primary w-100 py-2 d-flex align-items-center justify-content-center text-truncate small fw-semibold"),
                    lg=3, md=6, cols=6, cls="mb-2",
                ),
                Col(
                    A(Icon("file-earmark-plus", cls="me-2"), Span("New Proposal"), href="/documents?kind=proposal&new=1", cls="btn btn-primary w-100 py-2 d-flex align-items-center justify-content-center text-truncate small fw-semibold"),
                    lg=3, md=6, cols=6, cls="mb-2",
                ),
                Col(
                    A(Icon("inbox", cls="me-2"), Span("View Inquiries"), href="/inquiries", cls="btn btn-outline-secondary w-100 py-2 d-flex align-items-center justify-content-center text-truncate small fw-semibold"),
                    lg=3, md=6, cols=6, cls="mb-2",
                ),
                Col(
                    A(Icon("gear", cls="me-2"), Span("Settings"), href="/settings", cls="btn btn-outline-secondary w-100 py-2 d-flex align-items-center justify-content-center text-truncate small fw-semibold"),
                    lg=3, md=6, cols=6, cls="mb-2",
                ),
                cls="g-2 mb-4",
            ),
        ),

        # Two-column recent activity
        Div(
            Row(
                # Recent Inquiries
                Col(
                    Card(
                        Div(
                            H3("Recent Inquiries", cls="admin-section-title mb-0"),
                            A("View All", href="/inquiries", cls="btn btn-sm btn-outline-primary rounded-pill px-3"),
                            cls="d-flex align-items-center justify-content-between mb-3",
                        ),
                        _inquiries_list(recent_inquiries),
                        cls="p-3",
                    ),
                    cls="mb-3",
                ),
                # Recent Orders
                Col(
                    Card(
                        Div(
                            H3("Recent Orders", cls="admin-section-title mb-0"),
                            A("View All", href="/orders", cls="btn btn-sm btn-outline-primary rounded-pill px-3"),
                            cls="d-flex align-items-center justify-content-between mb-3",
                        ),
                        _orders_list(recent_orders),
                        cls="p-3",
                    ),
                    cls="mb-3",
                ),
                cols=1, cols_lg=2, cls="g-3",
            ),
        ),

        # Summary stats row
        Div(
            Row(
                Col(
                    Card(
                        Div(
                            Icon("graph-up", cls="text-primary me-2"),
                            Span(f"{data.get('products', 0)} products across {data.get('categories', 0)} categories", cls="text-muted"),
                            cls="d-flex align-items-center",
                            style="border-bottom: 1px solid #e9ecef; padding-bottom: 0.5rem;",
                        ),
                        Div(
                            Icon("wrench", cls="text-primary me-2"),
                            Span(f"{data.get('services', 0)} services available for inquiry", cls="text-muted"),
                            cls="d-flex align-items-center mt-4",
                            style="border-bottom: 1px solid #e9ecef; padding-bottom: 0.5rem;",
                        ),
                        cls="p-3",
                    ),
                    cls="mb-3",
                ),
                Col(
                    Card(
                        Div(
                            Icon("whatsapp", cls="me-2", style="color: #25D366"),
                            Span("WhatsApp ordering is active", cls="text-muted"),
                            cls="d-flex align-items-center",
                        ),
                        Div(
                            Icon("check-circle", cls="text-success me-2"),
                            Span("Public site is live and accepting inquiries", cls="text-muted"),
                            cls="d-flex align-items-center mt-3",
                            
                        ),
                        cls="p-3",
                    ),
                    cls="mb-3",
                ),
                cols=1, cols_lg=2, cls="g-3",
            ),
        ),

        # Recent Sister Administrator Activity
        Div(
            Card(
                Div(
                    Div(
                        H3("Sister Activity Log", cls="admin-section-title mb-0"),
                        P("Real-time record of operations performed by the two sister owners.", cls="text-muted small mb-0"),
                    ),
                    A("Full Audit Trail →", href="/audit-trail", cls="btn btn-outline-primary btn-sm fw-semibold"),
                    cls="d-flex justify-content-between align-items-center mb-3 pb-3 border-bottom",
                ),
                _activity_list(data.get("recent_activity", [])),
                cls="p-4 border-0 shadow-sm",
            ),
            cls="mb-4",
        ),
    ]


def _activity_list(activity: list) -> Div:
    if not activity:
        return Div(
            Icon("clock-history", cls="text-muted mb-2", size="2rem"),
            P("No activity logged yet", cls="text-muted mb-0"),
            P("Actions by Mercy or Christianah will appear here.", cls="text-muted small"),
            cls="text-center py-4",
        )
    from app.presentation.pages.audit import _action_badge, _actor_pill
    rows = []
    for item in activity:
        rows.append(
            Div(
                Div(
                    _actor_pill(item.get("actor_name", "Admin"), item.get("actor_email", "")),
                    Span(item.get("details", ""), cls="ms-3 small fw-medium text-dark flex-grow-1"),
                    cls="d-flex align-items-center flex-grow-1 mb-1 mb-md-0",
                ),
                Div(
                    _action_badge(item.get("action", "")),
                    Span(item.get("created_at", "")[11:16], cls="ms-2 font-monospace text-muted small"),
                    cls="d-flex align-items-center ms-md-3",
                ),
                cls="d-flex flex-column flex-md-row align-items-start align-items-md-center justify-content-between py-2 border-bottom",
            )
        )
    return Div(*rows)


def _inquiries_list(inquiries: list) -> Div:
    """Render recent inquiries list."""
    if not inquiries:
        return Div(
            Icon("inbox", cls="text-muted mb-2", size="2rem"),
            P("No inquiries yet", cls="text-muted mb-0"),
            P("Inquiries from the public site will appear here.", cls="text-muted small"),
            cls="text-center py-4",
        )

    items = []
    for item in inquiries:
        items.append(
            Div(
                Div(
                    P(item.get("customer_name", "Anonymous"), cls="fw-semibold mb-0 text-dark"),
                    Div(
                        _source_badge(item.get("source", "")),
                        _status_badge(item.get("status", "")),
                        cls="mt-1 d-flex flex-wrap gap-1 align-items-center",
                    ),
                    cls="flex-grow-1",
                ),
                Span(_format_date(item.get("created_at", "")), cls="text-muted small"),
                cls="d-flex flex-column flex-sm-row align-items-start align-items-sm-center justify-content-between py-2 border-bottom gap-1",
            )
        )
    return Div(*items)


def _orders_list(orders: list) -> Div:
    """Render recent orders list."""
    if not orders:
        return Div(
            Icon("cart", cls="text-muted mb-2", size="2rem"),
            P("No orders yet", cls="text-muted mb-0"),
            P("Orders will appear here once customers place them.", cls="text-muted small"),
            cls="text-center py-4",
        )

    items = []
    for item in orders:
        items.append(
            Div(
                Div(
                    P(item.get("order_number", "N/A"), cls="fw-semibold mb-0 text-dark"),
                    P(item.get("customer_name", ""), cls="text-muted small mb-1"),
                    _status_badge(item.get("status", "")),
                    cls="flex-grow-1",
                ),
                Span(_format_date(item.get("created_at", "")), cls="text-muted small"),
                cls="d-flex flex-column flex-sm-row align-items-start align-items-sm-center justify-content-between py-2 border-bottom gap-1",
            )
        )
    return Div(*items)
