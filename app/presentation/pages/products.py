"""Products management page — two-panel workspace."""

from __future__ import annotations

from typing import Any

from fasthtml.common import A, Div, Form, H3, Img, Input, Label, Option, P, Select, Textarea, Span
from faststrap import Badge, Button, Card, Col, Container, Icon, Row

from app.presentation.page_helpers import empty_state, filter_pill


def products_page(products: list, categories: list, active_category: str = "all", selected_fragment: Any = None) -> list:
    """Render products management page."""
    return [
        Div(
            Row(
                # List panel
                Col(
                    Card(
                        Div(
                            H3("Products", cls="admin-section-title mb-0"),
                            Button(
                                Icon("plus", cls="me-1"), "Add",
                                cls="btn btn-primary btn-sm",
                                hx_get="/products/editor",
                                hx_target="#product-editor",
                                hx_swap="innerHTML",
                            ),
                            cls="d-flex align-items-center justify-content-between mb-3",
                        ),
                        # Category filter
                        _category_filter(categories, active_category),
                        _products_list(products, active_category),
                        cls="p-3",
                    ),
                    lg=5, span=12, cls="mb-3",
                ),
                # Editor panel
                Col(
                    Div(
                        selected_fragment or Card(
                            Div(
                                H3("Product Editor", cls="admin-section-title mb-0"),
                                cls="mb-3",
                            ),
                            Div(
                                P("Select a product to edit, or click Add to create a new one.", cls="text-muted"),
                                cls="p-4 text-center",
                            ),
                            cls="p-3",
                        ),
                        id="product-editor",
                    ),
                    lg=7, span=12, cls="mb-3",
                ),
                cls="g-3",
            ),
        ),
    ]


def _category_filter(categories: list, active: str) -> Div:
    """Category filter pills."""
    items = [filter_pill("All", "/products", active == "all")]
    for cat in categories:
        slug = cat.get("slug", "")
        label = cat.get("label", "")
        items.append(
            filter_pill(label, f"/products?category={slug}",
                       active == slug)
        )
    return Div(*items, cls="admin-filter-bar mb-3")


def _products_list(products: list, category: str = "all") -> Div:
    """Render products list."""
    if not products:
        return Div(
            empty_state("No products", "Create your first product to get started."),
            id="products-list",
            hx_get=f"/products/list?category={category}",
            hx_trigger="refreshList from:body",
            hx_swap="outerHTML",
        )

    items = []
    for prod in products:
        stock_cls = {"in_stock": "success", "made_to_order": "warning", "discontinued": "danger"}.get(
            prod.get("stock_status", ""), "secondary"
        )
        items.append(
            A(
                Div(
                    Div(
                        Img(src=prod.get("image_url", ""), alt="", cls="rounded me-2",
                            style="width:40px;height:40px;object-fit:cover;") if prod.get("image_url") else "",
                        Div(
                            P(prod.get("name", ""), cls="fw-semibold mb-0"),
                            P(f'{prod.get("category_slug", "")} · {prod.get("price", "")}', cls="text-muted small mb-0"),
                            cls="flex-grow-1",
                        ),
                        cls="d-flex align-items-center flex-grow-1",
                    ),
                    Div(
                        Badge(prod.get("stock_status", "in_stock").replace("_", " ").title(), variant=stock_cls, cls="me-2"),
                        Badge("Featured", variant="warning") if prod.get("is_featured") else "",
                        cls="d-flex align-items-center",
                    ),
                    cls="d-flex align-items-center justify-content-between py-2",
                ),
                href="#",
                cls="text-decoration-none text-dark border-bottom",
                hx_get=f'/products/editor?product_id={prod.get("id", "")}',
                hx_target="#product-editor",
                hx_swap="innerHTML",
            )
        )
    return Div(
        *items,
        id="products-list",
        hx_get=f"/products/list?category={category}",
        hx_trigger="refreshList from:body",
        hx_swap="outerHTML",
    )


def product_editor_fragment(product: dict | None, categories: list) -> Card:
    """Render product editor form fragment for HTMX."""
    is_new = product is None
    title = "New Product" if is_new else f'Edit: {product.get("name", "")}'

    prod_id = product.get("id", "") if product else ""
    name = product.get("name", "") if product else ""
    slug = product.get("slug", "") if product else ""
    category_slug = product.get("category_slug", "") if product else ""
    price = product.get("price", "") if product else ""
    description = product.get("description", "") if product else ""
    highlight = product.get("highlight", "") if product else ""
    image_url = product.get("image_url", "") if product else ""
    stock_status = product.get("stock_status", "in_stock") if product else "in_stock"
    is_featured = product.get("is_featured", False) if product else False
    is_active = product.get("is_active", True) if product else True

    category_options = [Option("Select category", value="", selected=not category_slug)]
    for cat in categories:
        cat_slug = cat.get("slug", "")
        category_options.append(Option(cat.get("label", ""), value=cat_slug, selected=cat_slug == category_slug))

    stock_options = [
        Option("In Stock", value="in_stock", selected=stock_status == "in_stock"),
        Option("Made to Order", value="made_to_order", selected=stock_status == "made_to_order"),
        Option("Discontinued", value="discontinued", selected=stock_status == "discontinued"),
    ]

    return Card(
        Div(
            H3(title, cls="admin-section-title mb-0"),
            Div(
                Button(
                    Span(Icon("trash", cls="me-1"), "Delete"),
                    cls="btn btn-outline-danger btn-sm",
                    hx_post="/products/delete",
                    hx_vals=f'{{"id": "{prod_id}"}}' if prod_id else "",
                    hx_confirm="Are you sure you want to delete this product?",
                    hx_target="#product-editor",
                    hx_swap="innerHTML",
                    hx_disabled_elt="this",
                ) if not is_new else "",
                cls="d-flex gap-2",
            ),
            cls="d-flex align-items-center justify-content-between mb-3",
        ),
        Div(id="save-result"),
        Form(
            Input(type="hidden", name="id", value=prod_id),
            Div(
                Label("Product Name", fr="prod-name", cls="form-label fw-semibold small"),
                Input(type="text", name="name", id="prod-name", value=name,
                      required=True, cls="form-control", placeholder="e.g. Signature Stripe Bedsheet Set",
                      data_slug_source="true", data_slug_target="prod-slug"),
                cls="mb-3",
            ),
            Row(
                Div(
                    Label("Slug", fr="prod-slug", cls="form-label fw-semibold small"),
                    Input(type="text", name="slug", id="prod-slug", value=slug,
                          cls="form-control", placeholder="auto-generated-if-blank"),
                    cls="col-12 col-md-6 mb-3",
                ),
                Div(
                    Label("Category", fr="prod-category", cls="form-label fw-semibold small"),
                    Select(*category_options, name="category_slug", id="prod-category", cls="form-select"),
                    cls="col-12 col-md-6 mb-3",
                ),
            ),
            Row(
                Div(
                    Label("Price", fr="prod-price", cls="form-label fw-semibold small"),
                    Input(type="text", name="price", id="prod-price", value=price,
                          cls="form-control", placeholder="e.g. NGN 24,500"),
                    cls="col-12 col-md-6 mb-3",
                ),
                Div(
                    Label("Highlight / Badge", fr="prod-highlight", cls="form-label fw-semibold small"),
                    Input(type="text", name="highlight", id="prod-highlight", value=highlight,
                          cls="form-control", placeholder="e.g. Best Seller, New Arrival, Wholesale ready"),
                    cls="col-12 col-md-6 mb-3",
                ),
            ),
            Div(
                Label("Description", fr="prod-description", cls="form-label fw-semibold small"),
                Textarea(name="description", id="prod-description", rows="3",
                         cls="form-control", placeholder="Product description, dimensions, fabric details...")(description),
                cls="mb-3",
            ),
            Div(
                Label("Primary Cover Image URL", fr="prod-image", cls="form-label fw-semibold small"),
                Div(
                    Input(type="text", name="image_url", id="prod-image", value=image_url,
                          cls="form-control", placeholder="https://..."),
                    Button(Icon("images"), type="button", cls="btn btn-outline-secondary",
                           title="Select from Media Library",
                           data_bs_toggle="modal", data_bs_target="#mediaPickerModal",
                           onclick="window.currentMediaTarget = 'prod-image';"),
                    cls="input-group",
                ),
                cls="mb-3",
            ),
            Div(
                Label("Additional Gallery Images (comma or newline separated URLs)", fr="prod-images", cls="form-label fw-semibold small"),
                Textarea(name="images_raw", id="prod-images", rows="2", cls="form-control",
                         placeholder="https://... image 2\nhttps://... image 3")(
                    "\n".join(product.get("images", [])) if (product and isinstance(product.get("images"), list)) else ""
                ),
                cls="mb-3",
            ),
            Row(
                Div(
                    Label("Stock Status", fr="prod-stock", cls="form-label fw-semibold small"),
                    Select(*stock_options, name="stock_status", id="prod-stock", cls="form-select"),
                    cls="col-12 col-md-4 mb-3",
                ),
                Div(
                    Label("Featured on Home", cls="form-label fw-semibold small"),
                    Div(
                        Input(type="checkbox", name="is_featured", id="prod-featured",
                              cls="form-check-input", checked=is_featured),
                        Label("Show on Homepage", fr="prod-featured", cls="form-check-label ms-1"),
                        cls="form-check form-switch pt-1",
                    ),
                    cls="col-12 col-md-4 mb-3",
                ),
                Div(
                    Label("Visibility", cls="form-label fw-semibold small"),
                    Div(
                        Input(type="checkbox", name="is_active", id="prod-active",
                              cls="form-check-input", checked=is_active),
                        Label("Published & Active", fr="prod-active", cls="form-check-label ms-1"),
                        cls="form-check form-switch pt-1",
                    ),
                    cls="col-12 col-md-4 mb-3",
                ),
            ),
            Button(
                Span(Icon("check2-circle", cls="me-1"), "Save Product"),
                type="submit", cls="btn btn-primary px-4",
                hx_post="/products/save",
                hx_include="closest form",
                hx_target="#product-editor",
                hx_swap="innerHTML",
                hx_disabled_elt="this",
            ),
            action="/products/save",
            method="post",
        ),
        cls="p-3 shadow-sm",
    )
