"""Dashboard route — overview with real Supabase data + auto-refresh."""

from __future__ import annotations

from typing import Any

from fasthtml.common import Div, Span

try:
    from ..infrastructure.supabase_client import get_service_client, has_supabase
    from ..presentation.shell import page_frame
    from ..presentation.pages.dashboard import dashboard_page, metrics_row
except ImportError:
    from app.infrastructure.supabase_client import get_service_client, has_supabase
    from app.presentation.shell import page_frame
    from app.presentation.pages.dashboard import dashboard_page, metrics_row


def register_dashboard_routes(app: Any) -> None:

    @app.get("/")
    def overview():
        data = _get_dashboard_data()
        return page_frame(*dashboard_page(data), current="/", title="Overview")

    @app.get("/dashboard/metrics")
    def dashboard_metrics():
        """HTMX auto-refresh endpoint — returns metrics row with its own polling wrapper."""
        data = _get_dashboard_data()
        return Div(
            *metrics_row(data),
            id="dashboard-metrics",
            hx_get="/dashboard/metrics",
            hx_trigger="every 30s",
            hx_swap="outerHTML",
        )


def _get_dashboard_data() -> dict:
    """Fetch all dashboard data from Supabase."""
    from app.infrastructure.audit_repository import get_recent_audit_logs
    result = {
        "products": 0,
        "inquiries": 0,
        "orders": 0,
        "categories": 0,
        "services": 0,
        "recent_inquiries": [],
        "recent_orders": [],
        "recent_activity": get_recent_audit_logs(limit=5),
    }

    if not has_supabase():
        return result

    client = get_service_client()
    if not client:
        return result

    try:
        # Counts — use count='exact' to avoid fetching full row data
        def _count(table: str, **filters):
            q = client.table(table).select("*", count="exact")
            for col, val in filters.items():
                q = q.eq(col, val)
            res = q.execute()
            return getattr(res, "count", None) or len(getattr(res, "data", []))

        result["products"] = _count("products")
        result["categories"] = _count("categories")
        result["services"] = _count("services")
        result["inquiries"] = _count("inquiries", status="new")
        result["orders"] = _count("orders", status="processing")

        # Recent inquiries (last 5)
        inquiries_data = getattr(
            client.table("inquiries")
            .select("id,customer_name,source,status,created_at")
            .order("created_at", desc=True)
            .limit(5)
            .execute(),
            "data", [],
        )
        result["recent_inquiries"] = inquiries_data

        # Recent orders (last 5)
        orders_data = getattr(
            client.table("orders")
            .select("id,order_number,customer_name,status,created_at")
            .order("created_at", desc=True)
            .limit(5)
            .execute(),
            "data", [],
        )
        result["recent_orders"] = orders_data

    except Exception:
        pass

    return result
