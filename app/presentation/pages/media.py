"""Media library page — grid gallery with upload."""

from __future__ import annotations

from typing import Any

from fasthtml.common import A, Div, Form, H3, Img, Input, P, Span
from faststrap import Badge, Button, Card, Col, Icon, Row

from app.infrastructure.media_repository import get_media_url
from app.presentation.page_helpers import empty_state


def media_page(files: list) -> list:
    """Render media library page."""
    return [
        # Upload section
        Div(
            Card(
                H3("Upload Media", cls="admin-section-title"),
                Form(
                    Div(
                        Input(type="file", name="file", id="media-file", cls="form-control",
                               accept="image/*", required=True),
                        cls="mb-3",
                    ),
                    Button(
                        Span(Icon("upload", cls="me-1"), "Upload to Storage"),
                        type="submit", cls="btn btn-primary px-4 fw-semibold",
                        hx_post="/media/upload",
                        hx_encoding="multipart/form-data",
                        hx_include="#media-file",
                        hx_target="#media-upload-result",
                        hx_swap="innerHTML",
                        hx_disabled_elt="this",
                    ),
                    Div(id="media-upload-result", cls="mt-2"),
                    action="/media/upload",
                    method="post",
                    enctype="multipart/form-data",
                ),
                cls="p-3 mb-4 shadow-sm",
            ),
        ),

        # Media grid
        Div(
            Card(
                Div(
                    Div(
                        H3("Media Library", cls="h5 fw-bold mb-1 text-dark"),
                        P("Browse and manage all uploaded high-resolution store assets and project photos.", cls="text-muted small mb-0"),
                    ),
                    Badge(f"{len(files)} Assets", variant="primary", cls="px-3 py-2"),
                    cls="d-flex flex-wrap justify-content-between align-items-center gap-2 mb-3 pb-3 border-bottom",
                ),
                _media_grid(files),
                cls="p-4 border-0 shadow-sm",
            ),
        ),
    ]


def _media_grid(files: list) -> Div:
    """Render media files as a grid."""
    if not files:
        return empty_state(
            "No media files",
            "Upload images to use in products, categories, and services.",
        )

    items = []
    for f in files:
        name = f.get("name", "")
        url = get_media_url(name) or f"/assets/{name}"
        card_id = "mc-" + "".join(c if c.isalnum() else "-" for c in name)
        items.append(
            Col(
                Card(
                    Div(
                        Img(
                            src=url,
                            alt=name,
                            cls="w-100 h-100 object-fit-cover rounded-top",
                            loading="lazy",
                            onerror="this.style.display='none';this.nextElementSibling.style.display='flex';",
                        ),
                        Div(
                            Icon("image", cls="text-muted", size="3rem"),
                            cls="d-none align-items-center justify-content-center w-100 h-100",
                        ),
                        cls="position-relative overflow-hidden",
                        style="height: 11rem; background: #f8f5fc;",
                    ),
                    Div(
                        P(name, cls="text-truncate small fw-semibold mb-2", title=name),
                        Div(
                            Button(
                                Icon("trash", size="0.8rem"),
                                cls="btn btn-outline-danger btn-sm",
                                title="Delete image",
                                hx_post="/media/delete",
                                hx_vals=f'{{"file_name": "{name}"}}',
                                hx_confirm=f"Delete {name}?",
                                hx_target=f"#{card_id}",
                                hx_swap="outerHTML",
                                hx_disabled_elt="this",
                            ),
                            Button(
                                Icon("copy", size="0.8rem"), " Copy URL",
                                type="button",
                                cls="btn btn-outline-primary btn-sm flex-grow-1",
                                title="Copy public URL",
                                onclick=f"navigator.clipboard.writeText('{url}');",
                            ),
                            cls="d-flex gap-1",
                        ),
                        cls="p-2",
                    ),
                    cls="border shadow-xs h-100",
                    body_cls="p-0",
                ),
                cols=6,
                md=4,
                lg=3,
                cls="mb-3",
                id=card_id,
            )
        )

    return Row(*items, cls="g-3")


def media_picker_modal_fragment(files: list) -> Div:
    """Render media grid inside a modal for inserting into input fields."""
    if not files:
        return empty_state("No media files", "Upload images in the Media section first.")

    items = []
    for f in files:
        name = f.get("name", "")
        url = get_media_url(name) or f"/assets/{name}"
        items.append(
            Div(
                Card(
                    Img(src=url, alt=name, style="height: 7rem; object-fit: cover;", cls="card-img-top"),
                    Div(
                        P(name, cls="text-truncate small mb-1", title=name),
                        Button(
                            "Select",
                            type="button",
                            cls="btn btn-sm btn-primary w-100",
                            onclick=f"window.selectMediaForTarget('{url}');",
                        ),
                        cls="p-2",
                    ),
                    cls="h-100 border shadow-none",
                    body_cls="p-0",
                ),
                cols=4,
                cls="mb-3",
            )
        )
    return Row(*items, cls="g-2")
