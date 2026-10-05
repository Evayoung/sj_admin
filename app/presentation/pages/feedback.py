"""Feedback & Complaints management page — 1-Click Review Publishing & Complaint Resolution."""

from __future__ import annotations

from typing import Any

from fasthtml.common import (
    A, Button as HButton, Div, Form, H3, H4, H5, Input, Label, Option, P,
    Select, Small, Span, Table, Tbody, Td, Textarea, Th, Thead, Tr,
)
from faststrap import Badge, Button, Card, Col, Container, Icon, Row

from app.presentation.page_helpers import empty_state, filter_pill


def _rating_stars(rating: int) -> Span:
    """Render 5-star rating visual."""
    stars = []
    for i in range(1, 6):
        if i <= rating:
            stars.append(Icon("star-fill", cls="text-warning me-1 small"))
        else:
            stars.append(Icon("star", cls="text-muted me-1 small opacity-50"))
    return Span(*stars, cls="d-inline-flex align-items-center")


def _urgency_badge(urgency: str) -> Span:
    urg = (urgency or "normal").lower()
    if urg == "urgent":
        return Badge("Urgent", variant="danger", cls="fw-bold")
    if urg == "priority":
        return Badge("Priority", variant="warning", cls="fw-bold")
    return Badge("Normal", variant="secondary", cls="fw-normal")


def _status_badge(status: str, is_review: bool = False) -> Span:
    st = (status or "").lower()
    if is_review:
        if st == "published":
            return Badge(Icon("globe", cls="me-1"), "Live on Website", variant="success", cls="fw-bold")
        return Badge(Icon("clock", cls="me-1"), "Pending Approval", variant="secondary")
    
    if st == "resolved":
        return Badge(Icon("check2-circle", cls="me-1"), "Resolved", variant="success", cls="fw-bold")
    if st == "investigating":
        return Badge(Icon("hourglass-split", cls="me-1"), "Investigating", variant="warning", cls="fw-bold")
    return Badge(Icon("exclamation-circle", cls="me-1"), "Open Ticket", variant="danger", cls="fw-bold")


def feedback_row_fragment(fb: dict[str, Any]) -> Tr:
    """Render a single table row for review or complaint (used in full page and HTMX update)."""
    fb_id = fb.get("id", "")
    kind = fb.get("kind", "review")
    is_rev = kind == "review"
    is_pub = fb.get("is_published", False)
    status = fb.get("status", "open")
    created = fb.get("created_at", "")[:10]

    if is_rev:
        action_btn = Button(
            Icon("globe", cls="me-1") if not is_pub else Icon("eye-slash", cls="me-1"),
            "Unpublish" if is_pub else "Publish to Site",
            cls="btn btn-sm " + ("btn-outline-secondary" if is_pub else "btn-success fw-bold"),
            hx_post=f"/feedback/toggle-publish/{fb_id}",
            hx_target=f"#fb-row-{fb_id}",
            hx_swap="outerHTML",
        )
    else:
        action_btn = Button(
            Icon("wrench", cls="me-1"),
            "Resolve Issue",
            type="button",
            cls="btn btn-sm btn-outline-primary fw-semibold",
            **{"data-bs-toggle": "modal", "data-bs-target": f"#resolve-modal-{fb_id}"},
        )

    return Tr(
        Td(
            Span(
                "REVIEW" if is_rev else "COMPLAINT",
                cls="badge fw-bold small",
                style="background-color: rgba(110, 69, 201, 0.12); color: #6E45C9; border: 1px solid rgba(110, 69, 201, 0.25);" if is_rev else "background-color: #c8607d; color: #ffffff;"
            ),
            Div(Small(created, cls="text-muted d-block mt-1 font-monospace")),
            style="width: 12%; vertical-align: middle;",
        ),
        Td(
            H5(fb.get("customer_name", "Client"), cls="fw-bold mb-1 text-dark h6"),
            Div(
                Small(Icon("telephone", cls="me-1 text-muted"), fb.get("customer_phone") or "No phone", cls="text-muted me-3"),
                Small(Icon("geo-alt", cls="me-1 text-muted"), fb.get("location_tag") or "Ilorin", cls="text-muted"),
                cls="d-flex flex-wrap align-items-center",
            ),
            (Div(Small(Icon("receipt", cls="me-1 text-primary"), f"Ref: {fb.get('order_ref')}", cls="badge bg-light text-primary border mt-1")) if fb.get("order_ref") else ""),
            style="width: 25%; vertical-align: middle;",
        ),
        Td(
            (Div(_rating_stars(fb.get("rating", 5)), cls="mb-1") if is_rev else Div(_urgency_badge(fb.get("urgency", "normal")), Span(f" · {fb.get('complaint_type', 'General')}", cls="small text-muted fw-semibold ms-1"), cls="mb-1")),
            P(fb.get("message", ""), cls="small text-secondary mb-1"),
            (Div(Small(Icon("check-circle-fill", cls="me-1 text-success"), f"Resolution: {fb.get('resolution_notes')}", cls="text-success fw-semibold small")) if fb.get("resolution_notes") else ""),
            style="width: 38%; vertical-align: middle;",
        ),
        Td(
            _status_badge(status, is_review=is_rev),
            (Div(Small(f"Assigned: {fb.get('assigned_to')}", cls="text-muted d-block mt-1 small")) if fb.get("assigned_to") else ""),
            style="width: 13%; vertical-align: middle;",
        ),
        Td(
            action_btn,
            style="width: 12%; text-align: end; vertical-align: middle;",
        ),
        id=f"fb-row-{fb_id}",
    )


def feedback_page(items: list[dict[str, Any]], active_filter: str = "all") -> list:
    """Render full feedback & complaint management workspace."""
    total = len(items)
    reviews_count = sum(1 for f in items if f.get("kind") == "review")
    published_count = sum(1 for f in items if f.get("kind") == "review" and f.get("is_published"))
    complaints_count = sum(1 for f in items if f.get("kind") == "complaint")
    open_complaints = sum(1 for f in items if f.get("kind") == "complaint" and f.get("status") in ("open", "investigating"))

    # Modals for resolving complaints
    resolve_modals = []
    for f in items:
        if f.get("kind") == "complaint":
            f_id = f.get("id")
            modal = Div(
                Div(
                    Div(
                        Div(
                            H5(Icon("wrench", cls="me-2 text-primary"), f"Resolve Complaint: {f.get('customer_name')}", cls="modal-title fw-bold"),
                            HButton("×", type="button", cls="btn-close", **{"data-bs-dismiss": "modal"}),
                            cls="modal-header",
                        ),
                        Form(
                            Div(
                                P(f"Issue: {f.get('message')}", cls="small text-muted p-2 bg-light rounded-2 border mb-3"),
                                Div(
                                    Label("Assign Resolution To Sister:", cls="form-label small fw-bold"),
                                    Select(
                                        Option("Mercy Olorundare", value="Mercy", selected=f.get("assigned_to") == "Mercy"),
                                        Option("Christianah Alade", value="Christianah", selected=f.get("assigned_to") == "Christianah"),
                                        name="assigned_to", cls="form-select form-select-sm mb-3",
                                    ),
                                ),
                                Div(
                                    Label("Ticket Status:", cls="form-label small fw-bold"),
                                    Select(
                                        Option("Open (Pending Review)", value="open", selected=f.get("status") == "open"),
                                        Option("Investigating / In Progress", value="investigating", selected=f.get("status") == "investigating"),
                                        Option("Resolved & Closed", value="resolved", selected=f.get("status") == "resolved"),
                                        name="status", cls="form-select form-select-sm mb-3",
                                    ),
                                ),
                                Div(
                                    Label("Internal Sister Resolution Notes:", cls="form-label small fw-bold"),
                                    Textarea(
                                        f.get("resolution_notes") or "",
                                        name="notes", rows="3",
                                        placeholder="e.g. Visited customer home on Oct 6, adjusted track tension, customer approved.",
                                        cls="form-control form-control-sm mb-2",
                                    ),
                                ),
                                cls="modal-body",
                            ),
                            Div(
                                HButton("Cancel", type="button", cls="btn btn-outline-secondary btn-sm", **{"data-bs-dismiss": "modal"}),
                                HButton(
                                    Icon("check-circle-fill", cls="me-1"), "Save & Update Ticket",
                                    type="submit", cls="btn btn-primary btn-sm fw-bold",
                                    hx_post=f"/feedback/resolve/{f_id}",
                                    hx_target=f"#fb-row-{f_id}",
                                    hx_swap="outerHTML",
                                ),
                                cls="modal-footer",
                            ),
                            action=f"/feedback/resolve/{f_id}",
                            method="post",
                        ),
                        cls="modal-content",
                    ),
                    cls="modal-dialog modal-dialog-centered",
                ),
                id=f"resolve-modal-{f_id}", cls="modal fade", tabindex="-1", aria_hidden="true",
            )
            resolve_modals.append(modal)

    # Filtered table rows
    filtered = items
    if active_filter == "reviews":
        filtered = [f for f in items if f.get("kind") == "review"]
    elif active_filter == "complaints":
        filtered = [f for f in items if f.get("kind") == "complaint"]
    elif active_filter == "open_complaints":
        filtered = [f for f in items if f.get("kind") == "complaint" and f.get("status") in ("open", "investigating")]

    rows = [feedback_row_fragment(fb) for fb in filtered]

    return [
        *resolve_modals,
        # Metric Strip
        Row(
            Col(
                Card(
                    Div(
                        Div(Icon("star-fill", cls="text-warning h4 mb-0 me-3"), cls="p-2 bg-light rounded-circle"),
                        Div(
                            Small("Live Testimonials", cls="text-muted d-block small fw-bold text-uppercase"),
                            H4(f"{published_count} Published", cls="fw-bold mb-0 text-dark"),
                            Small(f"of {reviews_count} total client reviews", cls="text-muted small"),
                        ),
                        cls="d-flex align-items-center",
                    ),
                    cls="p-3 border-0 shadow-sm rounded-3 mb-3",
                ),
                span=12, md=4,
            ),
            Col(
                Card(
                    Div(
                        Div(Icon("exclamation-triangle", cls="text-danger h4 mb-0 me-3"), cls="p-2 bg-light rounded-circle"),
                        Div(
                            Small("Open Complaints", cls="text-muted d-block small fw-bold text-uppercase"),
                            H4(f"{open_complaints} Open", cls="fw-bold mb-0 text-danger"),
                            Small(f"of {complaints_count} total logged tickets", cls="text-muted small"),
                        ),
                        cls="d-flex align-items-center",
                    ),
                    cls="p-3 border-0 shadow-sm rounded-3 mb-3",
                ),
                span=12, md=4,
            ),
            Col(
                Card(
                    Div(
                        Div(Icon("link-45deg", cls="text-primary h4 mb-0 me-3"), cls="p-2 bg-light rounded-circle"),
                        Div(
                            Small("Public Client Link", cls="text-muted d-block small fw-bold text-uppercase"),
                            H4("Feedback Portal", cls="fw-bold mb-0 text-dark"),
                            A("Visit /feedback →", href="/feedback", target="_blank", cls="small text-primary text-decoration-none fw-semibold"),
                        ),
                        cls="d-flex align-items-center",
                    ),
                    cls="p-3 border-0 shadow-sm rounded-3 mb-3",
                ),
                span=12, md=4,
            ),
            cls="g-3 mb-2",
        ),
        # Filter Bar & Table
        Card(
            Div(
                Div(
                    H3("Client Feedback & Resolution Workspace", cls="h5 fw-bold text-dark mb-1"),
                    P("Review public client testimonials for 1-click website publishing, and resolve incoming service complaints.", cls="small text-muted mb-0"),
                    cls="mb-3 mb-md-0",
                ),
                Div(
                    filter_pill("All Submissions", "/feedback", active_filter == "all"),
                    filter_pill("Reviews Only", "/feedback?filter=reviews", active_filter == "reviews"),
                    filter_pill(f"Open Issues ({open_complaints})", "/feedback?filter=open_complaints", active_filter == "open_complaints"),
                    filter_pill("All Complaints", "/feedback?filter=complaints", active_filter == "complaints"),
                    cls="d-flex flex-wrap gap-2 align-items-center",
                ),
                cls="d-flex flex-column flex-md-row justify-content-between align-items-md-center p-3 border-bottom",
            ),
            Div(
                Table(
                    Thead(
                        Tr(
                            Th("TYPE & DATE", style="font-size: 0.75rem; letter-spacing: 0.05em; color: #6b7280;"),
                            Th("CLIENT & REFERENCE", style="font-size: 0.75rem; letter-spacing: 0.05em; color: #6b7280;"),
                            Th("FEEDBACK DETAILS", style="font-size: 0.75rem; letter-spacing: 0.05em; color: #6b7280;"),
                            Th("STATUS", style="font-size: 0.75rem; letter-spacing: 0.05em; color: #6b7280;"),
                            Th("ACTION", cls="text-end", style="font-size: 0.75rem; letter-spacing: 0.05em; color: #6b7280;"),
                            style="background-color: #f8fafc; border-bottom: 2px solid #e2e8f0;",
                        ),
                    ),
                    Tbody(*rows) if rows else Tbody(
                        Tr(
                            Td(
                                empty_state(
                                    "No Feedback Submissions Found",
                                    "When customers leave reviews or submit service inquiries through the public /feedback portal, they will appear here.",
                                    icon="chat-square-quote",
                                ),
                                colspan=5,
                                cls="py-5 text-center",
                            )
                        )
                    ),
                    cls="table table-hover align-middle mb-0",
                ),
                cls="table-responsive",
            ),
            cls="border-0 shadow-sm rounded-4 overflow-hidden mb-5 bg-white",
        ),
    ]
