"""Orders management page — two-panel workspace."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from fasthtml.common import A, Div, Form, H3, H5, Input, Label, Option, P, Select, Small, Span, Textarea
from faststrap import Badge, Button, Card, Col, Container, Icon, Row

from app.presentation.page_helpers import empty_state, filter_pill


def _format_date(date_str: str) -> str:
    if not date_str:
        return ""
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return dt.strftime("%b %d, %H:%M")
    except Exception:
        return str(date_str)[:10]


def orders_page(orders: list, active_status: str = "all", selected_fragment: Any = None) -> list:
    return [
        Div(
            Row(
                Col(
                    Card(
                        Div(
                            H3("Orders", cls="admin-section-title mb-0"),
                            Button(
                                Icon("plus", cls="me-1"), "New Order",
                                cls="btn btn-primary btn-sm",
                                hx_get="/orders/editor",
                                hx_target="#order-detail",
                                hx_swap="innerHTML",
                            ),
                            cls="d-flex align-items-center justify-content-between mb-3",
                        ),
                        _status_filter(active_status),
                        _orders_list(orders, active_status),
                        cls="p-3",
                    ),
                    lg=5, cols=12, cls="mb-3",
                ),
                Col(
                    Div(
                        selected_fragment or Card(
                            Div(
                                H3("Order Detail", cls="admin-section-title mb-0"),
                                cls="mb-3",
                            ),
                            Div(
                                P("Select an order to view details or click 'New Order' to create one.", cls="text-muted"),
                                cls="p-4 text-center",
                            ),
                            cls="p-3",
                        ),
                        id="order-detail",
                    ),
                    lg=7, cols=12, cls="mb-3",
                ),
                cls="g-3",
            ),
        ),
    ]


def _status_filter(active: str) -> Div:
    filters = [("all", "All"), ("processing", "Processing"), ("shipped", "Shipped"), ("delivered", "Delivered"), ("cancelled", "Cancelled")]
    items = []
    for value, label in filters:
        href = f"/orders?status={value}" if value != "all" else "/orders"
        items.append(filter_pill(label, href, active == value))
    return Div(*items, cls="admin-filter-bar mb-3")


def _orders_list(orders: list, status: str = "all") -> Div:
    if not orders:
        return Div(
            empty_state("No orders", "Orders will appear here once customers place them or you create them."),
            id="orders-list",
            hx_get=f"/orders/list?status={status}",
            hx_trigger="refreshList from:body",
            hx_swap="outerHTML",
        )

    items = []
    for item in orders:
        ord_status = item.get("status", "processing")
        status_cls = {"processing": "warning", "shipped": "info", "delivered": "success", "cancelled": "danger"}.get(ord_status, "secondary")

        items.append(
            A(
                Div(
                    Div(
                        Icon("cart", cls="me-2 text-primary"),
                        Div(
                            P(item.get("order_number", "N/A"), cls="fw-semibold mb-0"),
                            P(f'{item.get("customer_name", "")} · {_format_date(item.get("created_at", ""))}', cls="text-muted small mb-0"),
                            cls="flex-grow-1",
                        ),
                        cls="d-flex align-items-center flex-grow-1",
                    ),
                    Badge(ord_status.title(), variant=status_cls),
                    cls="d-flex align-items-center justify-content-between py-2",
                ),
                href="#",
                cls="text-decoration-none text-dark border-bottom",
                hx_get=f'/orders/detail?order_id={item.get("id", "")}',
                hx_target="#order-detail",
                hx_swap="innerHTML",
            )
        )
    return Div(
        *items,
        id="orders-list",
        hx_get=f"/orders/list?status={status}",
        hx_trigger="refreshList from:body",
        hx_swap="outerHTML",
    )


def order_editor_fragment(order: dict | None = None, customer_name: str = "", phone: str = "") -> Card:
    """Render manual order creation/edit form."""
    is_new = order is None
    title = "Create New Order" if is_new else f'Edit Order: {order.get("order_number", "")}'

    name = order.get("customer_name", "") if order else customer_name
    cust_phone = order.get("phone", "") if order else phone
    order_id = order.get("id", "") if order else ""
    order_num = order.get("order_number", "") if order else ""
    notes = order.get("notes", "") if order else ""
    status = order.get("status", "processing") if order else "processing"

    return Card(
        Div(
            H3(title, cls="admin-section-title mb-0"),
            Div(
                Button(
                    Span(Icon("trash", cls="me-1"), "Delete"),
                    cls="btn btn-outline-danger btn-sm",
                    hx_post="/orders/delete",
                    hx_vals=f'{{"id": "{order_id}"}}' if order_id else "",
                    hx_confirm="Delete this order?",
                    hx_target="#order-detail",
                    hx_swap="innerHTML",
                    hx_disabled_elt="this",
                ) if not is_new else "",
                cls="d-flex gap-2",
            ),
            cls="d-flex align-items-center justify-content-between mb-3",
        ),
        Div(id="order-detail-result"),
        Form(
            Input(type="hidden", name="id", value=order_id),
            Row(
                Div(
                    Label("Customer Name", fr="order-cust-name", cls="form-label fw-semibold small"),
                    Input(type="text", name="customer_name", id="order-cust-name", value=name,
                          required=True, cls="form-control", placeholder="e.g. Adebayo Olamide"),
                    cls="col-12 col-md-6 mb-3",
                ),
                Div(
                    Label("Customer Phone", fr="order-cust-phone", cls="form-label fw-semibold small"),
                    Input(type="tel", name="phone", id="order-cust-phone", value=cust_phone,
                          required=True, cls="form-control", placeholder="e.g. 08026022672"),
                    cls="col-12 col-md-6 mb-3",
                ),
            ),
            Div(
                Label("Order Items (Name × Qty — Price, one per line)", fr="order-items", cls="form-label fw-semibold small"),
                Textarea(
                    name="items_text", id="order-items", rows="4", cls="form-control",
                    placeholder="Signature Stripe Bedsheet Set × 2 — NGN 49,000\nSoft Sheer Curtain Pair × 1 — NGN 28,500"
                )(_format_items_for_textarea(order.get("items", [])) if order else ""),
                cls="mb-3",
            ),
            Row(
                Div(
                    Label("Status", fr="order-form-status", cls="form-label fw-semibold small"),
                    Select(
                        *[Option(s.title(), value=s, selected=s == status) for s in ["processing", "shipped", "delivered", "cancelled"]],
                        name="status", id="order-form-status", cls="form-select",
                    ),
                    cls="col-12 col-md-6 mb-3",
                ),
                Div(
                    Label("Order Number (auto if blank)", fr="order-num", cls="form-label fw-semibold small"),
                    Input(type="text", name="order_number", id="order-num", value=order_num,
                          cls="form-control", placeholder="e.g. SJ-2026-0001"),
                    cls="col-12 col-md-6 mb-3",
                ),
            ),
            Div(
                Label("Notes / Delivery Address", fr="order-notes", cls="form-label fw-semibold small"),
                Textarea(name="notes", id="order-notes", rows="2", cls="form-control",
                         placeholder="Delivery instructions, measurements, notes...")(notes),
                cls="mb-3",
            ),
            Button(
                Span(Icon("check2-circle", cls="me-1"), "Save Order"),
                type="submit", cls="btn btn-primary px-4",
                hx_post="/orders/save",
                hx_include="closest form",
                hx_target="#order-detail",
                hx_swap="innerHTML",
                hx_disabled_elt="this",
            ),
            action="/orders/save",
            method="post",
        ),
        cls="p-3 shadow-sm",
    )


def _format_items_for_textarea(items: list) -> str:
    lines = []
    for item in items:
        if isinstance(item, dict):
            lines.append(f"{item.get('name', 'Item')} × {item.get('quantity', 1)} — {item.get('price', '')}")
        elif isinstance(item, str):
            lines.append(item)
    return "\n".join(lines)


def order_detail_fragment(order: dict | None) -> Card:
    if not order:
        return Card(P("Order not found.", cls="text-muted"), cls="p-3")

    status = order.get("status", "processing")
    items = order.get("items", []) or []
    customer_phone = (order.get("phone", "") or "").replace("+", "").replace(" ", "").replace("-", "")
    order_num = order.get("order_number", "N/A")

    return Card(
        Div(
            H3(order_num, cls="admin-section-title mb-0"),
            Badge(status.title(), variant={"processing": "warning", "shipped": "info", "delivered": "success", "cancelled": "danger"}.get(status, "secondary"), cls="ms-2"),
            cls="d-flex align-items-center mb-3",
        ),
        Div(id="order-detail-result"),
        Div(
            P(f'Customer: {order.get("customer_name", "N/A")}', cls="mb-1 fw-semibold"),
            P(f'Phone: {order.get("phone", "N/A")}', cls="mb-1"),
            P(f'Created: {_format_date(order.get("created_at", ""))}', cls="mb-3 text-muted"),
            cls="mb-3",
        ),
        items and Div(
            H5("Ordered Items", cls="mb-2 fw-bold"),
            Div(*[
                P(
                    f'• {item.get("name", "Item")} × {item.get("quantity", 1)} — {item.get("price", "")}'
                    if isinstance(item, dict) else f'• {item}',
                    cls="mb-1 small"
                )
                for item in items
            ], cls="border rounded p-3 bg-light"),
            cls="mb-3",
        ),
        Div(
            H5("Update Status & Notes", cls="mb-2 fw-bold"),
            Form(
                Select(
                    *[Option(s.title(), value=s, selected=s == status) for s in ["processing", "shipped", "delivered", "cancelled"]],
                    name="status", id="order-status", cls="form-select form-select-sm mb-2",
                ),
                Textarea(name="notes", rows="2", cls="form-control form-control-sm mb-2", placeholder="Order notes...")(order.get("notes", "")),
                Input(type="hidden", name="id", value=order.get("id", "")),
                Button(
                    Span(Icon("check2", cls="me-1"), "Save Status"),
                    type="submit", cls="btn btn-primary btn-sm px-3 fw-semibold",
                    hx_post="/orders/status",
                    hx_include="closest form",
                    hx_target="#order-detail-result",
                    hx_swap="innerHTML",
                    hx_disabled_elt="this",
                ),
                action="/orders/status",
                method="post",
            ),
            cls="mb-4",
        ),
        Div(
            H5("Customer Communications", cls="mb-2 fw-bold"),
            Div(
                A(
                    Icon("whatsapp", cls="me-1"), "WhatsApp Notification",
                    href=f"https://wa.me/{customer_phone}?text=Hello%20{order.get('customer_name', '')},%20your%20order%20{order_num}%20is%20currently%20{status.upper()}.",
                    target="_blank", rel="noreferrer",
                    cls="btn btn-outline-success btn-sm flex-fill",
                ) if customer_phone else "",
                A(
                    Icon("pencil", cls="me-1"), "Edit Order",
                    hx_get=f'/orders/editor?order_id={order.get("id", "")}',
                    hx_target="#order-detail",
                    hx_swap="innerHTML",
                    cls="btn btn-outline-secondary btn-sm flex-fill",
                ),
                cls="d-flex flex-column flex-sm-row gap-2",
            ),
            cls="mb-2",
        ),
        order.get("notes") and Div(
            H5("Internal Notes", cls="mb-2 fw-bold"),
            P(order.get("notes"), cls="border rounded p-3 bg-light small"),
            cls="mb-3",
        ),
        cls="p-3 shadow-sm",
    )
