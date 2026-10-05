"""Inquiries management page — two-panel workspace."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from fasthtml.common import A, Div, Form, H3, H5, Input, Option, P, Select, Small, Span, Textarea
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


def inquiries_page(inquiries: list, active_status: str = "all") -> list:
    return [
        Div(
            Row(
                Col(
                    Card(
                        Div(
                            H3("Inquiries", cls="admin-section-title mb-0"),
                            cls="mb-3",
                        ),
                        _status_filter(active_status),
                        _inquiries_list(inquiries),
                        cls="p-2",
                    ),
                    lg=5, span=12, cls="mb-3",
                ),
                Col(
                    Div(
                        Card(
                            Div(
                                H3("Inquiry Detail", cls="admin-section-title mb-0"),
                                cls="mb-3",
                            ),
                            Div(
                                P("Select an inquiry to view details.", cls="text-muted"),
                                cls="p-4 text-center",
                            ),
                            cls="p-3",
                        ),
                        id="inquiry-detail",
                    ),
                    lg=7, span=12, cls="mb-3",
                ),
                cls="g-3",
            ),
        ),
    ]


def _status_filter(active: str) -> Div:
    filters = [("all", "All"), ("new", "New"), ("contacted", "Contacted"), ("ordered", "Ordered"), ("closed", "Closed")]
    items = []
    for value, label in filters:
        href = f"/inquiries?status={value}" if value != "all" else "/inquiries"
        items.append(filter_pill(label, href, active == value))
    return Div(*items, cls="admin-filter-bar mb-3 p-1")


def _inquiries_list(inquiries: list) -> Div:
    if not inquiries:
        return empty_state("No inquiries", "Inquiries from the public site will appear here.")

    items = []
    for item in inquiries:
        source_icons = {"whatsapp": "whatsapp", "contact_form": "envelope", "phone": "telephone", "services_page": "wrench"}
        source = item.get("source", "")
        status = item.get("status", "new")
        status_cls = {"new": "primary", "contacted": "info", "ordered": "success", "closed": "secondary"}.get(status, "secondary")

        items.append(
            A(
                Div(
                    Div(
                        Icon(source_icons.get(source, "circle"), cls="me-2 text-primary"),
                        Div(
                            P(item.get("customer_name", "Anonymous"), cls="fw-semibold mb-0"),
                            P(f'{source.replace("_", " ").title()} · {_format_date(item.get("created_at", ""))}', cls="text-muted small mb-0"),
                            cls="flex-grow-1",
                        ),
                        cls="d-flex align-items-center flex-grow-1",
                    ),
                    Badge(status.title(), variant=status_cls),
                    cls="d-flex align-items-center justify-content-between p-2 bg-light ",
                    style="border-bottom: 1px solid #e9ecef; padding-bottom: 0.5rem;",
                ),
                href="#",
                cls="text-decoration-none text-dark border-bottom",
                hx_get=f'/inquiries/detail?inquiry_id={item.get("id", "")}',
                hx_target="#inquiry-detail",
                hx_swap="innerHTML",
            )
        )
    return Div(*items)


def inquiry_detail_fragment(inquiry: dict | None) -> Card:
    if not inquiry:
        return Card(P("Inquiry not found.", cls="text-muted"), cls="p-3")

    status = inquiry.get("status", "new")
    source = inquiry.get("source", "")
    services = inquiry.get("selected_services", []) or []
    customer_phone = (inquiry.get("phone", "") or "").replace("+", "").replace(" ", "").replace("-", "")

    return Card(
        Div(
            H3(inquiry.get("customer_name", "Anonymous"), cls="admin-section-title mb-0"),
            Badge(source.replace("_", " ").title(), variant="info", cls="ms-2"),
            cls="d-flex align-items-center mb-3",
        ),
        Div(id="inquiry-detail-result"),
        Div(
            P(f'Phone: {inquiry.get("phone", "N/A")}', cls="mb-1 fw-semibold"),
            P(f'Email: {inquiry.get("email", "N/A")}', cls="mb-1"),
            P(f'Source: {source.replace("_", " ").title()}', cls="mb-1"),
            P(f'Date: {_format_date(inquiry.get("created_at", ""))}', cls="mb-3 text-muted"),
            cls="mb-3",
        ),
        Div(
            H5("Customer Message / Project Scope", cls="mb-2"),
            P(inquiry.get("message", "No message"), cls="border rounded p-3 bg-light"),
            cls="mb-3",
        ),
        services and Div(
            H5("Selected Service Divisions", cls="mb-2 fw-bold"),
            Div(*[Badge(svc.replace("_", " ").title(), variant="light", cls="me-1 mb-1 text-dark border p-2") for svc in services]),
            cls="mb-3",
        ),
        inquiry.get("service_inquiry") and Div(
            Div(
                Icon("stars", cls="me-2 text-warning fs-5"),
                Div(
                    P("Rich Service Request Lead", cls="fw-bold mb-0 text-dark small"),
                    Small("Customer submitted project scope through the interactive public service planner.", cls="text-muted"),
                ),
                cls="d-flex align-items-center p-3 bg-light rounded-3 border border-warning mb-3",
            ),
        ),
        Div(
            H5("Update Status & Notes", cls="mb-2 fw-bold"),
            Form(
                Select(
                    *[Option(s.title(), value=s, selected=s == status) for s in ["new", "contacted", "ordered", "closed"]],
                    name="status", id="inquiry-status", cls="form-select form-select-sm mb-2",
                ),
                Textarea(name="notes", rows="2", cls="form-control form-control-sm mb-2", placeholder="Internal follow-up notes...")(inquiry.get("notes", "")),
                Input(type="hidden", name="id", value=inquiry.get("id", "")),
                Button(
                    Span(Icon("check2", cls="me-1"), "Save Status"),
                    type="submit", cls="btn btn-primary btn-sm px-3 fw-semibold",
                    hx_post="/inquiries/status",
                    hx_include="closest form",
                    hx_target="#inquiry-detail-result",
                    hx_swap="innerHTML",
                    hx_disabled_elt="this",
                ),
                action="/inquiries/status",
                method="post",
            ),
            cls="mb-4",
        ),
        Div(
            H5("Lead Conversion Actions", cls="mb-2 fw-bold"),
            Div(
                A(
                    Icon("file-earmark-plus", cls="me-1"), "Generate Official Quotation",
                    href=f"/documents?kind=quotation&inquiry_id={inquiry.get('id', '')}",
                    cls="btn btn-primary btn-sm flex-fill fw-bold",
                ),
                A(
                    Icon("whatsapp", cls="me-1"), "WhatsApp Chat",
                    href=f"https://wa.me/{customer_phone}?text=Hello%20{inquiry.get('customer_name', '')},%20this%20is%20SJ%20Interiors%20regarding%20your%20service%20inquiry.",
                    target="_blank", rel="noreferrer",
                    cls="btn btn-success btn-sm flex-fill fw-semibold text-white",
                ) if customer_phone else "",
                A(
                    Icon("cart-plus", cls="me-1"), "Create Order",
                    href=f"/orders?new=1&inquiry_id={inquiry.get('id', '')}",
                    cls="btn btn-outline-secondary btn-sm flex-fill",
                ),
                cls="d-flex flex-column flex-sm-row gap-2",
            ),
            cls="mb-2",
        ),
        cls="p-3 shadow-sm",
    )
