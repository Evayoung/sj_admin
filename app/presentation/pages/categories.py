"""Categories management page — two-panel workspace."""

from __future__ import annotations

from typing import Any

from fasthtml.common import A, Div, Form, H3, Img, Input, Label, P, Select, Textarea, Span
from faststrap import Badge, Button, Card, Col, Container, Icon, Row

from app.presentation.page_helpers import empty_state, filter_pill


def categories_page(categories: list, selected_fragment: Any = None) -> list:
    """Render categories management page."""
    return [
        Div(
            Row(
                # List panel
                Col(
                    Card(
                        Div(
                            H3("Categories", cls="admin-section-title mb-0"),
                            Button(
                                Icon("plus", cls="me-1"), "Add",
                                cls="btn btn-primary btn-sm",
                                hx_get="/categories/editor",
                                hx_target="#category-editor",
                                hx_swap="innerHTML",
                            ),
                            cls="d-flex align-items-center justify-content-between mb-3",
                        ),
                        _categories_list(categories),
                        cls="p-3",
                    ),
                    lg=5, span=12, cls="mb-3",
                ),
                # Editor panel
                Col(
                    Div(
                        selected_fragment or Card(
                            Div(
                                H3("Category Editor", cls="admin-section-title mb-0"),
                                cls="mb-3",
                            ),
                            Div(
                                P("Select a category to edit, or click Add to create a new one.", cls="text-muted"),
                                cls="p-4 text-center",
                            ),
                            cls="p-3",
                        ),
                        id="category-editor",
                    ),
                    lg=7, span=12, cls="mb-3",
                ),
                cls="g-3",
            ),
        ),
    ]


def _categories_list(categories: list) -> Div:
    """Render categories list."""
    if not categories:
        return Div(
            empty_state("No categories", "Create your first category to get started."),
            id="categories-list",
            hx_get="/categories/list",
            hx_trigger="refreshList from:body",
            hx_swap="outerHTML",
        )

    items = []
    for cat in categories:
        status_cls = "success" if cat.get("is_active", True) else "secondary"
        items.append(
            A(
                Div(
                    Div(
                        Icon(cat.get("icon", "tag"), cls="me-2 text-primary"),
                        Div(
                            P(cat.get("label", ""), cls="fw-semibold mb-0"),
                            P(f'/{cat.get("slug", "")}', cls="text-muted small mb-0"),
                            cls="flex-grow-1",
                        ),
                        cls="d-flex align-items-center flex-grow-1",
                    ),
                    Div(
                        Badge("Active" if cat.get("is_active", True) else "Inactive", variant=status_cls, cls="me-2"),
                        Span(str(cat.get("sort_order", 0)), cls="text-muted small"),
                        cls="d-flex align-items-center",
                    ),
                    cls="d-flex align-items-center justify-content-between py-2",
                ),
                href="#",
                cls="text-decoration-none text-dark border-bottom",
                hx_get=f'/categories/editor?category_id={cat.get("id", "")}',
                hx_target="#category-editor",
                hx_swap="innerHTML",
            )
        )
    return Div(
        *items,
        id="categories-list",
        hx_get="/categories/list",
        hx_trigger="refreshList from:body",
        hx_swap="outerHTML",
    )


def category_editor_fragment(category: dict | None = None) -> Card:
    """Render category editor form fragment for HTMX."""
    is_new = category is None
    title = "New Category" if is_new else f'Edit: {category.get("label", "")}'

    cat_id = category.get("id", "") if category else ""
    label = category.get("label", "") if category else ""
    slug = category.get("slug", "") if category else ""
    description = category.get("description", "") if category else ""
    icon = category.get("icon", "tag") if category else "tag"
    image_url = category.get("image_url", "") if category else ""
    sort_order = category.get("sort_order", 0) if category else 0
    is_active = category.get("is_active", True) if category else True

    return Card(
        Div(
            H3(title, cls="admin-section-title mb-0"),
            Div(
                Button(
                    Span(Icon("trash", cls="me-1"), "Delete"),
                    cls="btn btn-outline-danger btn-sm",
                    hx_post="/categories/delete",
                    hx_vals=f'{{"id": "{cat_id}"}}' if cat_id else "",
                    hx_confirm="Are you sure you want to delete this category?",
                    hx_target="#category-editor",
                    hx_swap="innerHTML",
                    hx_disabled_elt="this",
                ) if not is_new else "",
                cls="d-flex gap-2",
            ),
            cls="d-flex align-items-center justify-content-between mb-3",
        ),
        Div(id="save-result"),
        Form(
            Input(type="hidden", name="id", value=cat_id),
            Div(
                Label("Label", fr="cat-label", cls="form-label fw-semibold small"),
                Input(type="text", name="label", id="cat-label", value=label,
                      required=True, cls="form-control", placeholder="e.g. Bedsheets",
                      data_slug_source="true", data_slug_target="cat-slug"),
                cls="mb-3",
            ),
            Div(
                Label("Slug", fr="cat-slug", cls="form-label fw-semibold small"),
                Input(type="text", name="slug", id="cat-slug", value=slug,
                      cls="form-control", placeholder="auto-generated-if-blank"),
                cls="mb-3",
            ),
            Div(
                Label("Description", fr="cat-description", cls="form-label fw-semibold small"),
                Textarea(name="description", id="cat-description", rows="2",
                         cls="form-control", placeholder="Brief description of this category")(description),
                cls="mb-3",
            ),
            Row(
                Div(
                    Label("Icon (Bootstrap icon name)", fr="cat-icon", cls="form-label fw-semibold small"),
                    Input(type="text", name="icon", id="cat-icon", value=icon,
                          cls="form-control", placeholder="e.g. stars, moon-stars, tag"),
                    cls="col-12 col-md-6 mb-3",
                ),
                Div(
                    Label("Image URL", fr="cat-image", cls="form-label fw-semibold small"),
                    Div(
                        Input(type="text", name="image_url", id="cat-image", value=image_url,
                              cls="form-control", placeholder="https://..."),
                        Button(Icon("images"), type="button", cls="btn btn-outline-secondary",
                               title="Select from Media Library",
                               data_bs_toggle="modal", data_bs_target="#mediaPickerModal",
                               onclick="window.currentMediaTarget = 'cat-image';"),
                        cls="input-group",
                    ),
                    cls="col-12 col-md-6 mb-3",
                ),
            ),
            Row(
                Div(
                    Label("Sort Order", fr="cat-sort", cls="form-label fw-semibold small"),
                    Input(type="number", name="sort_order", id="cat-sort", value=str(sort_order),
                          cls="form-control"),
                    cls="col-12 col-md-6 mb-3",
                ),
                Div(
                    Label("Status", cls="form-label fw-semibold small"),
                    Div(
                        Input(type="checkbox", name="is_active", id="cat-active",
                              cls="form-check-input", checked=is_active),
                        Label("Active", fr="cat-active", cls="form-check-label ms-1"),
                        cls="form-check form-switch pt-1",
                    ),
                    cls="col-12 col-md-6 mb-3",
                ),
            ),
            Button(
                Span(Icon("check2-circle", cls="me-1"), "Save Category"),
                type="submit", cls="btn btn-primary px-4",
                hx_post="/categories/save",
                hx_include="closest form",
                hx_target="#category-editor",
                hx_swap="innerHTML",
                hx_disabled_elt="this",
            ),
            action="/categories/save",
            method="post",
        ),
        cls="p-3 shadow-sm",
    )
