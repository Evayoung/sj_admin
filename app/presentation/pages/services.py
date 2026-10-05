"""Services management page — two-panel workspace."""

from __future__ import annotations

from typing import Any

from fasthtml.common import A, Div, Form, H3, Img, Input, Label, P, Textarea, Span
from faststrap import Badge, Button, Card, Col, Container, Icon, Row

from app.presentation.page_helpers import empty_state


def services_page(services: list, selected_fragment: Any = None) -> list:
    """Render services management page."""
    return [
        Div(
            Row(
                # List panel
                Col(
                    Card(
                        Div(
                            H3("Services", cls="admin-section-title mb-0"),
                            Button(
                                Icon("plus", cls="me-1"), "Add",
                                cls="btn btn-primary btn-sm",
                                hx_get="/services/editor",
                                hx_target="#service-editor",
                                hx_swap="innerHTML",
                            ),
                            cls="d-flex align-items-center justify-content-between mb-3",
                        ),
                        _services_list(services),
                        cls="p-3",
                    ),
                    lg=5, span=12, cls="mb-3",
                ),
                # Editor panel
                Col(
                    Div(
                        selected_fragment or Card(
                            Div(
                                H3("Service Editor", cls="admin-section-title mb-0"),
                                cls="mb-3",
                            ),
                            Div(
                                P("Select a service to edit, or click Add to create a new one.", cls="text-muted"),
                                cls="p-4 text-center",
                            ),
                            cls="p-3",
                        ),
                        id="service-editor",
                    ),
                    lg=7, span=12, cls="mb-3",
                ),
                cls="g-3",
            ),
        ),
    ]


def _services_list(services: list) -> Div:
    """Render services list."""
    if not services:
        return Div(
            empty_state("No services", "Create your first service to get started."),
            id="services-list",
            hx_get="/services/list",
            hx_trigger="refreshList from:body",
            hx_swap="outerHTML",
        )

    items = []
    for svc in services:
        status_cls = "success" if svc.get("is_active", True) else "secondary"
        items.append(
            A(
                Div(
                    Div(
                        Icon(svc.get("icon", "wrench"), cls="me-2 text-primary"),
                        Div(
                            P(svc.get("title", ""), cls="fw-semibold mb-0"),
                            P(svc.get("summary", "")[:60] + "..." if len(svc.get("summary", "")) > 60 else svc.get("summary", ""), cls="text-muted small mb-0"),
                            cls="flex-grow-1",
                        ),
                        cls="d-flex align-items-center flex-grow-1",
                    ),
                    Div(
                        Badge("Active" if svc.get("is_active", True) else "Inactive", variant=status_cls, cls="me-2"),
                        Span(str(svc.get("sort_order", 0)), cls="text-muted small"),
                        cls="d-flex align-items-center",
                    ),
                    cls="d-flex align-items-center justify-content-between py-2",
                ),
                href="#",
                cls="text-decoration-none text-dark border-bottom",
                hx_get=f'/services/editor?service_id={svc.get("id", "")}',
                hx_target="#service-editor",
                hx_swap="innerHTML",
            )
        )
    return Div(
        *items,
        id="services-list",
        hx_get="/services/list",
        hx_trigger="refreshList from:body",
        hx_swap="outerHTML",
    )


def service_editor_fragment(service: dict | None) -> Card:
    """Render service editor form fragment for HTMX."""
    is_new = service is None
    title = "New Service" if is_new else f'Edit: {service.get("title", "")}'

    svc_id = service.get("id", "") if service else ""
    svc_title = service.get("title", "") if service else ""
    slug = service.get("slug", "") if service else ""
    summary = service.get("summary", "") if service else ""
    description = service.get("description", "") if service else ""
    icon = service.get("icon", "wrench") if service else "wrench"
    image_url = service.get("image_url", "") if service else ""
    sort_order = service.get("sort_order", 0) if service else 0
    is_active = service.get("is_active", True) if service else True

    return Card(
        Div(
            H3(title, cls="admin-section-title mb-0"),
            Div(
                Button(
                    Span(Icon("trash", cls="me-1"), "Delete"),
                    cls="btn btn-outline-danger btn-sm",
                    hx_post="/services/delete",
                    hx_vals=f'{{"id": "{svc_id}"}}' if svc_id else "",
                    hx_confirm="Delete this service?",
                    hx_target="#service-editor",
                    hx_swap="innerHTML",
                    hx_disabled_elt="this",
                ) if not is_new else "",
                cls="d-flex gap-2",
            ),
            cls="d-flex align-items-center justify-content-between mb-3",
        ),
        Div(id="save-result"),
        Form(
            Input(type="hidden", name="id", value=svc_id),
            Div(
                Label("Service Title", fr="svc-title", cls="form-label fw-semibold small"),
                Input(type="text", name="title", id="svc-title", value=svc_title,
                      required=True, cls="form-control", placeholder="e.g. Full House Curtain Design"),
                cls="mb-3",
            ),
            Row(
                Div(
                    Label("Slug", fr="svc-slug", cls="form-label fw-semibold small"),
                    Input(type="text", name="slug", id="svc-slug", value=slug,
                          cls="form-control", placeholder="auto-generated-if-blank"),
                    cls="col-12 col-md-6 mb-3",
                ),
                Div(
                    Label("Icon", fr="svc-icon", cls="form-label fw-semibold small"),
                    Input(type="text", name="icon", id="svc-icon", value=icon,
                          cls="form-control", placeholder="Bootstrap icon name (e.g. wrench, stars)"),
                    cls="col-12 col-md-6 mb-3",
                ),
            ),
            Div(
                Label("Summary", fr="svc-summary", cls="form-label fw-semibold small"),
                Textarea(name="summary", id="svc-summary", rows="2",
                         cls="form-control", placeholder="Brief summary of this service")(summary),
                cls="mb-3",
            ),
            Div(
                Label("Full Description", fr="svc-description", cls="form-label fw-semibold small"),
                Textarea(name="description", id="svc-description", rows="4",
                         cls="form-control", placeholder="Detailed description of this service")(description),
                cls="mb-3",
            ),
            Row(
                Div(
                    Label("Image URL", fr="svc-image", cls="form-label fw-semibold small"),
                    Div(
                        Input(type="text", name="image_url", id="svc-image", value=image_url,
                              cls="form-control", placeholder="https://..."),
                        Button(Icon("images"), type="button", cls="btn btn-outline-secondary",
                               title="Select from Media Library",
                               data_bs_toggle="modal", data_bs_target="#mediaPickerModal",
                               onclick="window.currentMediaTarget = 'svc-image';"),
                        cls="input-group",
                    ),
                    cls="col-12 col-md-6 mb-3",
                ),
                Div(
                    Label("Sort Order", fr="svc-sort", cls="form-label fw-semibold small"),
                    Input(type="number", name="sort_order", id="svc-sort", value=str(sort_order),
                          cls="form-control"),
                    cls="col-12 col-md-3 mb-3",
                ),
                Div(
                    Label("Status", cls="form-label fw-semibold small"),
                    Div(
                        Input(type="checkbox", name="is_active", id="svc-active",
                              cls="form-check-input", checked=is_active),
                        Label("Active", fr="svc-active", cls="form-check-label ms-1"),
                        cls="form-check form-switch pt-1",
                    ),
                    cls="col-12 col-md-3 mb-3",
                ),
            ),
            Button(
                Span(Icon("check2-circle", cls="me-1"), "Save Service"),
                type="submit", cls="btn btn-primary px-4",
                hx_post="/services/save",
                hx_include="closest form",
                hx_target="#service-editor",
                hx_swap="innerHTML",
                hx_disabled_elt="this",
            ),
            action="/services/save",
            method="post",
        ),
        cls="p-3 shadow-sm",
    )
