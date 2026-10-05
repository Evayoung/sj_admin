"""Order management routes."""

from __future__ import annotations

from typing import Any
from fasthtml.common import HttpHeader
from starlette.responses import JSONResponse

try:
    from ..infrastructure.inquiry_repository import get_inquiry_by_id
    from ..infrastructure.order_repository import (
        create_order,
        delete_order,
        get_all_orders,
        get_order_by_id,
        update_order,
        update_order_status,
    )
    from ..presentation.page_helpers import oob_alert, toast_fragment
    from ..presentation.pages.orders import (
        _orders_list,
        order_detail_fragment,
        order_editor_fragment,
        orders_page,
    )
    from ..presentation.shell import page_frame
except ImportError:
    from app.infrastructure.inquiry_repository import get_inquiry_by_id
    from app.infrastructure.order_repository import (
        create_order,
        delete_order,
        get_all_orders,
        get_order_by_id,
        update_order,
        update_order_status,
    )
    from app.presentation.page_helpers import oob_alert, toast_fragment
    from app.presentation.pages.orders import (
        _orders_list,
        order_detail_fragment,
        order_editor_fragment,
        orders_page,
    )
    from app.presentation.shell import page_frame


def register_order_routes(app: Any) -> None:

    @app.get("/orders")
    def orders_list(status: str = "all", inquiry_id: str = "", new: int = 0):
        orders = get_all_orders(status)
        editor = None
        if new or inquiry_id:
            inquiry = get_inquiry_by_id(inquiry_id) if inquiry_id else None
            cust_name = inquiry.get("customer_name", "") if inquiry else ""
            phone = inquiry.get("phone", "") if inquiry else ""
            editor = order_editor_fragment(None, customer_name=cust_name, phone=phone)
        page_content = orders_page(orders, status, selected_fragment=editor)
        return page_frame(*page_content, current="/orders", title="Orders")

    @app.get("/orders/list")
    def orders_list_fragment(status: str = "all"):
        """HTMX: return updated orders list fragment."""
        orders = get_all_orders(status)
        return _orders_list(orders, status)

    @app.get("/orders/detail")
    def order_detail(order_id: str = ""):
        """HTMX: return order detail."""
        order = None
        if order_id:
            order = get_order_by_id(order_id)
        return order_detail_fragment(order)

    @app.get("/orders/editor")
    def order_editor(order_id: str = "", inquiry_id: str = ""):
        """HTMX: return order create/edit form."""
        order = None
        cust_name = ""
        phone = ""
        if order_id:
            order = get_order_by_id(order_id)
        elif inquiry_id:
            inquiry = get_inquiry_by_id(inquiry_id)
            if inquiry:
                cust_name = inquiry.get("customer_name", "")
                phone = inquiry.get("phone", "")
        return order_editor_fragment(order, customer_name=cust_name, phone=phone)

    @app.post("/orders/save")
    def order_save(
        req=None,
        session=None,
        id: str = "",
        customer_name: str = "",
        phone: str = "",
        items_text: str = "",
        status: str = "processing",
        order_number: str = "",
        notes: str = "",
    ):
        """HTMX: save order (create or update)."""
        # Parse items_text
        items = []
        for line in items_text.splitlines():
            line_str = line.strip()
            if line_str:
                items.append(line_str)

        data = {
            "customer_name": customer_name,
            "phone": phone,
            "items": items,
            "status": status,
            "notes": notes,
        }
        if order_number:
            data["order_number"] = order_number

        from app.infrastructure.audit_repository import log_activity

        if id:
            result = update_order(id, data)
            if result:
                log_activity(req, session, "UPDATE_ORDER", "order", str(id), f"Updated order {order_number or id} for {customer_name}")
        else:
            result = create_order(data)
            if result:
                log_activity(req, session, "CREATE_ORDER", "order", str(result.get("order_number", result.get("id"))), f"Created order {result.get('order_number')} for {customer_name}")

        if result:
            return order_detail_fragment(result), toast_fragment("Order saved successfully.", variant="success"), HttpHeader("HX-Trigger", "refreshList")
        return oob_alert("Failed to save order.", variant="danger", target="order-detail-result"), toast_fragment("Failed to save order.", variant="danger")

    @app.post("/orders/delete")
    def order_delete(req=None, session=None, id: str = ""):
        """HTMX: delete order."""
        if not id:
            return JSONResponse({"error": "Missing id"}, status_code=400)
        from app.infrastructure.audit_repository import log_activity
        success = delete_order(id)
        if success:
            log_activity(req, session, "DELETE_ORDER", "order", str(id), f"Deleted order {id}")
            return order_detail_fragment(None), toast_fragment("Order deleted successfully.", variant="success"), HttpHeader("HX-Trigger", "refreshList")
        return oob_alert("Failed to delete order.", variant="danger", target="order-detail-result"), toast_fragment("Failed to delete order.", variant="danger")

    @app.post("/orders/status")
    def order_status_update(req=None, session=None, id: str = "", status: str = "", notes: str = ""):
        """HTMX: update order status."""
        if not id or not status:
            return oob_alert("Missing parameters.", variant="danger", target="order-detail-result"), toast_fragment("Missing parameters.", variant="danger")
        from app.infrastructure.audit_repository import log_activity
        result = update_order_status(id, status, notes)
        if result:
            log_activity(req, session, "UPDATE_ORDER_STATUS", "order", str(id), f"Updated order {id} status to {status.upper()}" + (f": {notes}" if notes else ""))
            return oob_alert(f"Order status updated to {status.upper()}.", variant="success", target="order-detail-result"), toast_fragment(f"Order status updated to {status.upper()}.", variant="success"), HttpHeader("HX-Trigger", "refreshList")
        return oob_alert("Failed to update status.", variant="danger", target="order-detail-result"), toast_fragment("Failed to update status.", variant="danger")
