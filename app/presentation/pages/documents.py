"""Document management page (Proposals, Quotations, Invoices) — two-panel workspace & client portal."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from urllib.parse import quote

from fasthtml.common import (
    A, Button as HButton, Div, Form, H1, H2, H3, H4, H5, Hr, Img, Input, Label, Option, P,
    Script, Select, Small, Span, Table, Tbody, Td, Textarea, Th, Thead, Title, Tr, Ul, Li,
)
from faststrap import Badge, Button, Card, Col, Container, Icon, Row

from app.config import settings
from app.presentation.page_helpers import empty_state, filter_pill


def _format_date(date_str: str) -> str:
    if not date_str:
        return ""
    try:
        dt = datetime.fromisoformat(str(date_str).replace("Z", "+00:00"))
        return dt.strftime("%b %d, %Y")
    except Exception:
        return str(date_str)[:10]


def _format_currency(amount: float | int | str, currency: str = "NGN") -> str:
    try:
        val = float(amount or 0)
        return f"{currency} {val:,.2f}"
    except Exception:
        return f"{currency} {amount}"


def _kind_badge(kind: str) -> Span:
    kind_colors = {
        "proposal": "primary",
        "quotation": "warning",
        "invoice": "success",
        "receipt": "dark",
    }
    return Badge(kind.title(), variant=kind_colors.get(kind.lower(), "secondary"), cls="me-1")


def _status_badge(status: str) -> Span:
    status_colors = {
        "draft": "secondary",
        "sent": "info",
        "viewed": "primary",
        "accepted": "success",
        "declined": "danger",
        "paid": "success",
        "partially_paid": "warning",
        "payment_pending": "warning",
        "expired": "dark",
    }
    return Badge(status.replace("_", " ").title(), variant=status_colors.get(status.lower(), "secondary"))


def documents_page(documents: list, active_kind: str = "all", active_status: str = "all", selected_fragment: Any = None) -> list:
    """Render documents management workspace."""
    return [
        Div(
            Row(
                # Left List Panel
                Col(
                    Card(
                        Div(
                            H3("Business Documents", cls="admin-section-title mb-0"),
                            Div(
                                Button(
                                    Icon("receipt", cls="me-1"), "Quick Receipt",
                                    cls="btn btn-success btn-sm fw-bold",
                                    hx_get="/documents/quick-receipt-form",
                                    hx_target="#document-editor",
                                    hx_swap="innerHTML",
                                    hx_disabled_elt="this",
                                ),
                                Button(
                                    Icon("plus", cls="me-1"), "New Doc",
                                    cls="btn btn-primary btn-sm",
                                    hx_get="/documents/editor?new=1",
                                    hx_target="#document-editor",
                                    hx_swap="innerHTML",
                                    hx_disabled_elt="this",
                                ),
                                cls="d-flex gap-2",
                            ),
                            cls="d-flex align-items-center justify-content-between mb-3",
                        ),
                        _kind_filter(active_kind),
                        _documents_list(documents, active_kind, active_status),
                        cls="p-3",
                    ),
                    lg=5, span=12, cls="mb-3",
                ),
                # Right Editor Panel
                Col(
                    Div(
                        selected_fragment or Card(
                            Div(
                                H3("Document Workspace", cls="admin-section-title mb-0"),
                                cls="mb-3",
                            ),
                            Div(
                                Icon("file-earmark-text", size="3rem", cls="text-muted mb-3"),
                                P("Select a document to edit, or create a new proposal, quotation, invoice, or receipt.", cls="text-muted"),
                                Div(
                                    Button(
                                        "Proposal",
                                        cls="btn bg-normal btn-sm flex-fill",
                                        hx_get="/documents/editor?kind=proposal",
                                        hx_target="#document-editor",
                                        hx_swap="innerHTML",
                                    ),
                                    Button(
                                        "Quotation",
                                        cls="btn bg-normal btn-sm flex-fill",
                                        hx_get="/documents/editor?kind=quotation",
                                        hx_target="#document-editor",
                                        hx_swap="innerHTML",
                                    ),
                                    Button(
                                        "Invoice",
                                        cls="btn bg-normal btn-sm flex-fill",
                                        hx_get="/documents/editor?kind=invoice",
                                        hx_target="#document-editor",
                                        hx_swap="innerHTML",
                                    ),
                                    Button(
                                        "Receipt",
                                        cls="btn bg-normal btn-sm flex-fill",
                                        hx_get="/documents/editor?kind=receipt",
                                        hx_target="#document-editor",
                                        hx_swap="innerHTML",
                                    ),
                                    cls="d-flex flex-column flex-sm-row gap-2 justify-content-center",
                                ),
                                cls="p-4 text-center",
                            ),
                            cls="p-3",
                        ),
                        id="document-editor",
                    ),
                    lg=7, span=12, cls="mb-3",
                ),
                cls="g-3",
            ),
        ),
    ]


def _kind_filter(active: str) -> Div:
    filters = [
        ("all", "All"),
        ("proposal", "Proposals"),
        ("quotation", "Quotations"),
        ("invoice", "Invoices"),
        ("receipt", "Receipts"),
    ]
    items = []
    for val, label in filters:
        items.append(filter_pill(label, f"/documents?kind={val}" if val != "all" else "/documents", active == val))
    return Div(*items, cls="admin-filter-bar mb-3")


def _documents_list(documents: list, kind: str = "all", status: str = "all") -> Div:
    if not documents:
        return Div(
            empty_state("No documents found", "Click 'New Doc' to create your first proposal, quote, or invoice."),
            id="documents-list",
            hx_get=f"/documents/list?kind={kind}&status={status}",
            hx_trigger="refreshList from:body",
            hx_swap="outerHTML",
        )

    items = []
    for doc in documents:
        doc_id = doc.get("id", "")
        doc_num = doc.get("document_number", "DOC")
        doc_kind = doc.get("kind", "proposal")
        doc_status = doc.get("status", "draft")
        cust_name = doc.get("customer_name", "Client")
        total = doc.get("total_amount", 0)
        currency = doc.get("currency", "NGN")
        date_str = _format_date(doc.get("created_at", ""))

        items.append(
            A(
                Div(
                    Div(
                        Icon("file-earmark-text", cls="me-2 text-primary"),
                        Div(
                            P(f"{doc_num} — {cust_name}", cls="fw-semibold mb-0"),
                            P(f"{doc.get('title', 'Document')} · {date_str}", cls="text-muted small mb-0"),
                            cls="flex-grow-1",
                        ),
                        cls="d-flex align-items-center flex-grow-1",
                    ),
                    Div(
                        P(_format_currency(total, currency), cls="fw-bold mb-0 text-end small"),
                        Div(_kind_badge(doc_kind), _status_badge(doc_status), cls="mt-1 text-end"),
                        cls="ms-2",
                    ),
                    cls="d-flex align-items-center justify-content-between py-2",
                ),
                href="#",
                cls="text-decoration-none text-dark border-bottom",
                hx_get=f"/documents/editor?doc_id={doc_id}",
                hx_target="#document-editor",
                hx_swap="innerHTML",
            )
        )
    return Div(
        *items,
        id="documents-list",
        hx_get=f"/documents/list?kind={kind}&status={status}",
        hx_trigger="refreshList from:body",
        hx_swap="outerHTML",
    )


def document_editor_fragment(doc: dict | None = None, kind: str = "quotation", inquiry: dict | None = None) -> Card:
    """Render comprehensive document editor form with line items builder."""
    is_new = doc is None
    doc_id = doc.get("id", "") if doc else ""
    doc_kind = doc.get("kind", kind) if doc else kind
    doc_num = doc.get("document_number", "") if doc else ""
    cust_name = doc.get("customer_name", "") if doc else (inquiry.get("customer_name", "") if inquiry else "")
    cust_phone = doc.get("customer_phone", "") if doc else (inquiry.get("phone", "") if inquiry else "")
    cust_email = doc.get("customer_email", "") if doc else (inquiry.get("email", "") if inquiry else "")
    title = doc.get("title", f"Interior Decoration & Furnishing for {cust_name or 'Client'}") if doc else f"Interior Decoration & Furnishing for {cust_name or 'Client'}"
    subtitle = doc.get("subtitle", "SJ Interiors — Deco and Beddings Supply") if doc else "SJ Interiors — Deco and Beddings Supply"
    notes = doc.get("notes", "Prices include standard delivery within Kwara State. Custom curtain measurements will be verified prior to stitching.") if doc else "Prices include standard delivery within Kwara State. Custom curtain measurements will be verified prior to stitching."
    terms = doc.get("terms", "70% advance payment required to commence production; 30% balance payable upon delivery/installation.") if doc else "70% advance payment required to commence production; 30% balance payable upon delivery/installation."
    status = doc.get("status", "draft") if doc else "draft"
    currency = doc.get("currency", "NGN") if doc else "NGN"
    access_token = doc.get("access_token", "") if doc else ""
    inquiry_id = doc.get("inquiry_id", "") if doc else (inquiry.get("id", "") if inquiry else "")

    items = doc.get("document_items", []) if doc else []
    if not items and inquiry:
        # Pre-fill line items from inquiry
        for svc in (inquiry.get("selected_services", []) or []):
            items.append({"description": f"{svc.replace('-', ' ').title()} Package", "quantity": 1, "unit_price": 0})
    if not items:
        items = [{"description": "Curtain & Blind Custom Styling (Living Room)", "quantity": 1, "unit_price": 45000}]

    amount_paid = float(doc.get("amount_paid", 0) if doc else 0)
    balance_due = float(doc.get("balance_due", 0) if doc else 0)
    payment_method = doc.get("payment_method", "Bank Transfer") if doc else "Bank Transfer"
    payment_ref = doc.get("payment_reference", "") if doc else ""

    token_url = f"/documents/preview/{access_token}" if access_token else "#"
    pdf_url = f"/documents/pdf/{doc_id}" if doc_id else "#"

    # WhatsApp share message (Personalized thank-you message for receipts)
    clean_phone = cust_phone.replace("+", "").replace(" ", "").replace("-", "")
    if doc_kind == "receipt":
        paid_val = _format_currency(amount_paid or (doc.get("total_amount", 0) if doc else 0), currency)
        wa_msg = quote(
            f"Dear {cust_name},\n\n"
            f"Thank you for choosing SJ Interior Deco and Beddings.\n\n"
            f"We have received your payment of {paid_val} for '{title}'.\n"
            f"Your official payment receipt ({doc_num or 'REC-Draft'}) is ready.\n\n"
            f"View & Download Your Official Receipt:\n"
            f"{settings.public_site_url}{token_url}\n\n"
            f"Thank you for your patronage and trusting us to transform your space."
        )
    else:
        wa_msg = quote(f"Hello {cust_name}, here is your official {doc_kind.upper()} ({doc_num or 'Draft'}) from SJ Interiors: {settings.public_site_url}{token_url}")

    return Card(
        Div(
            Div(
                H3(f"{'Edit' if not is_new else 'New'} {doc_kind.title()}: {doc_num or 'Draft'}", cls="admin-section-title mb-0"),
                _status_badge(status) if not is_new else Badge("New", variant="primary"),
                cls="d-flex align-items-center gap-2",
            ),
            Div(
                Button("Load Official Template", cls="btn btn-outline-info btn-sm",
                       hx_get="/documents/editor?template=official",
                       hx_target="#document-editor",
                       hx_swap="innerHTML",
                       title="Pre-populate with 6-division official quotation items") if is_new else "",
                Button("Delete", cls="btn btn-outline-danger btn-sm",
                       hx_post="/documents/delete",
                       hx_vals=f'{{"id": "{doc_id}"}}' if doc_id else "",
                       hx_confirm="Are you sure you want to delete this document?",
                       hx_target="#document-editor",
                       hx_swap="innerHTML") if not is_new else "",
                cls="d-flex gap-2",
            ),
            cls="d-flex flex-column flex-sm-row align-items-sm-center justify-content-between gap-2 mb-3",
        ),
        Div(id="document-save-result"),
        Form(
            Input(type="hidden", name="id", value=doc_id),
            Input(type="hidden", name="inquiry_id", value=inquiry_id),
            Row(
                Div(
                    Label("Document Type", fr="doc-kind", cls="form-label small fw-bold"),
                    Select(
                        Option("Proposal", value="proposal", selected=doc_kind == "proposal"),
                        Option("Quotation", value="quotation", selected=doc_kind == "quotation"),
                        Option("Invoice", value="invoice", selected=doc_kind == "invoice"),
                        Option("Receipt", value="receipt", selected=doc_kind == "receipt"),
                        name="kind", id="doc-kind", cls="form-select form-select-sm",
                    ),
                    cls="col-md-4 mb-3",
                ),
                Div(
                    Label("Document Number", fr="doc-number", cls="form-label small fw-bold"),
                    Input(type="text", name="document_number", id="doc-number", value=doc_num,
                          cls="form-control form-control-sm", placeholder="auto-generated"),
                    cls="col-md-4 mb-3",
                ),
                Div(
                    Label("Status", fr="doc-status", cls="form-label small fw-bold"),
                    Select(
                        Option("Draft", value="draft", selected=status == "draft"),
                        Option("Sent", value="sent", selected=status == "sent"),
                        Option("Viewed", value="viewed", selected=status == "viewed"),
                        Option("Accepted", value="accepted", selected=status == "accepted"),
                        Option("Revision Requested", value="revision_requested", selected=status == "revision_requested"),
                        Option("Payment Pending", value="payment_pending", selected=status == "payment_pending"),
                        Option("Paid (Full)", value="paid", selected=status == "paid"),
                        Option("Partially Paid", value="partially_paid", selected=status == "partially_paid"),
                        Option("Declined", value="declined", selected=status == "declined"),
                        name="status", id="doc-status", cls="form-select form-select-sm",
                    ),
                    cls="col-md-4 mb-3",
                ),
            ),
            Row(
                Div(
                    Label("Customer Name", fr="doc-cust-name", cls="form-label small fw-bold"),
                    Input(type="text", name="customer_name", id="doc-cust-name", value=cust_name,
                          required=True, cls="form-control form-control-sm", placeholder="e.g. Mrs. Funke Adeyemi"),
                    cls="col-md-4 mb-3",
                ),
                Div(
                    Label("Customer Phone", fr="doc-cust-phone", cls="form-label small fw-bold"),
                    Input(type="tel", name="customer_phone", id="doc-cust-phone", value=cust_phone,
                          required=True, cls="form-control form-control-sm", placeholder="e.g. 08026022672"),
                    cls="col-md-4 mb-3",
                ),
                Div(
                    Label("Customer Email", fr="doc-cust-email", cls="form-label small fw-bold"),
                    Input(type="email", name="customer_email", id="doc-cust-email", value=cust_email,
                          cls="form-control form-control-sm", placeholder="e.g. client@example.com"),
                    cls="col-md-4 mb-3",
                ),
            ),
            Div(
                Label("Document Title / Project Scope", fr="doc-title", cls="form-label small fw-bold"),
                Input(type="text", name="title", id="doc-title", value=title,
                      required=True, cls="form-control form-control-sm", placeholder="e.g. Window Dressing & Full Interior Furnishing"),
                cls="mb-3",
            ),
            (Row(
                Div(
                    Label("Payment Method", fr="doc-pay-method", cls="form-label small fw-bold"),
                    Select(
                        Option("Bank Transfer", value="Bank Transfer", selected=payment_method == "Bank Transfer"),
                        Option("Cash", value="Cash", selected=payment_method == "Cash"),
                        Option("POS Terminal", value="POS Terminal", selected=payment_method == "POS Terminal"),
                        Option("Online Card Payment", value="Online Card Payment", selected=payment_method == "Online Card Payment"),
                        name="payment_method", id="doc-pay-method", cls="form-select form-select-sm",
                    ),
                    cls="col-md-4 mb-3",
                ),
                Div(
                    Label("Amount Paid (₦)", fr="doc-pay-amount", cls="form-label small fw-bold"),
                    Input(type="number", name="amount_paid", id="doc-pay-amount", value=str(amount_paid or ""),
                          step="100", min="0", cls="form-control form-control-sm", placeholder="e.g. 150000"),
                    cls="col-md-4 mb-3",
                ),
                Div(
                    Label("Payment Reference / Note", fr="doc-pay-ref", cls="form-label small fw-bold"),
                    Input(type="text", name="payment_reference", id="doc-pay-ref", value=payment_ref,
                          cls="form-control form-control-sm", placeholder="e.g. GTB/TRF/092837"),
                    cls="col-md-4 mb-3",
                ),
            ) if doc_kind == "receipt" else ""),
            Hr(cls="my-3"),
            Div(
                H5("Itemized Breakdown (Categorized Line Items)", cls="mb-0 fw-bold"),
                Small("Structure items by Division (e.g. 1. SITTING ROOM CURTAINS, 2. BEDROOM CURTAINS, etc.)", cls="text-muted"),
                cls="mb-3",
            ),
            Div(
                _render_items_editor_rows(items),
                id="document-items-container",
                cls="mb-3",
            ),
            Div(
                Button(
                    Icon("plus-circle", cls="me-1"), "Add Line Item",
                    type="button", cls="btn btn-outline-secondary btn-sm",
                    onclick="addDocumentItemRow();",
                ),
                cls="mb-3",
            ),
            Row(
                Div(
                    Label("Payment Terms / Conditions", fr="doc-terms", cls="form-label small fw-bold"),
                    Textarea(name="terms", id="doc-terms", rows="3", cls="form-control form-control-sm")(terms),
                    cls="col-12 col-md-6 mb-3",
                ),
                Div(
                    Label("Internal Notes / Delivery Info", fr="doc-notes", cls="form-label small fw-bold"),
                    Textarea(name="notes", id="doc-notes", rows="3", cls="form-control form-control-sm")(notes),
                    cls="col-12 col-md-6 mb-3",
                ),
            ),
            Div(
                Button(
                    Span(Icon("check2-circle", cls="me-1"), "Save Document"),
                    type="submit", cls="btn btn-primary px-4 me-2",
                    hx_post="/documents/save",
                    hx_include="closest form",
                    hx_target="#document-editor",
                    hx_swap="innerHTML",
                    hx_disabled_elt="this",
                ),
                (Button(
                    Span(Icon("receipt", cls="me-1"), "Confirm Payment & Generate Official Receipt"),
                    type="button", cls="btn btn-success btn-md fw-bold",
                    hx_post=f"/documents/generate-receipt/{doc_id}",
                    hx_confirm="Convert this invoice into an official confirmed payment receipt?",
                    hx_target="#document-editor",
                    hx_swap="innerHTML",
                    hx_disabled_elt="this",
                ) if (doc_kind == "invoice" and not is_new) else ""),
                cls="d-flex flex-wrap align-items-center gap-2 mb-3",
            ),
            action="/documents/save",
            method="post",
        ),
        (Div(
            Hr(cls="my-3"),
            H5("Client Dispatch & Portal Tools", cls="mb-3 fw-bold"),
            Div(
                A(
                    Icon("whatsapp", cls="me-1"), "Share Receipt on WhatsApp" if doc_kind == "receipt" else "Send to WhatsApp",
                    href=f"https://wa.me/{clean_phone}?text={wa_msg}",
                    target="_blank", rel="noreferrer",
                    cls="btn btn-success btn-sm flex-fill fw-bold",
                ) if clean_phone else "",
                A(
                    Icon("box-arrow-up-right", cls="me-1"), "Client Portal Link",
                    href=token_url, target="_blank", rel="noreferrer",
                    cls="btn btn-outline-primary btn-sm flex-fill",
                ),
                A(
                    Icon("printer", cls="me-1"), "Printable PDF",
                    href=pdf_url, target="_blank", rel="noreferrer",
                    cls="btn btn-outline-secondary btn-sm flex-fill",
                ),
                cls="d-flex flex-column flex-sm-row gap-2",
            ),
            cls="mt-3",
        ) if not is_new else ""),
        cls="p-3 shadow-sm",
    )


def _render_items_editor_rows(items: list[dict]) -> Div:
    header_row = Row(
        Div(Small("CATEGORY GROUP", cls="fw-bold text-muted"), cls="col-12 col-md-3 d-none d-md-block"),
        Div(Small("ITEM NAME", cls="fw-bold text-muted"), cls="col-12 col-md-3 d-none d-md-block"),
        Div(Small("SPECIFICATION / DETAILS", cls="fw-bold text-muted"), cls="col-12 col-md-2 d-none d-md-block"),
        Div(Small("QTY", cls="fw-bold text-muted"), cls="col-4 col-md-1 d-none d-md-block"),
        Div(Small("PRICE (₦)", cls="fw-bold text-muted"), cls="col-5 col-md-2 d-none d-md-block"),
        Div(cls="col-3 col-md-1 d-none d-md-block"),
        cls="mb-1 text-uppercase",
    )
    rows = [header_row]
    for idx, item in enumerate(items):
        cat_group = item.get("category_group", "")
        desc = item.get("description", "")
        spec = item.get("specification", "")
        qty = item.get("quantity", 1)
        price = item.get("unit_price", 0)
        rows.append(
            Row(
                Div(
                    Input(type="text", name="item_category[]", value=cat_group, placeholder="Category (e.g. 1. CURTAINS)", cls="form-control form-control-sm"),
                    cls="col-12 col-md-3 mb-2",
                ),
                Div(
                    Input(type="text", name="item_desc[]", value=desc, placeholder="Item name", required=True, cls="form-control form-control-sm"),
                    cls="col-12 col-md-3 mb-2",
                ),
                Div(
                    Input(type="text", name="item_spec[]", value=spec, placeholder="Spec / Estimation details", cls="form-control form-control-sm"),
                    cls="col-12 col-md-2 mb-2",
                ),
                Div(
                    Input(type="number", name="item_qty[]", value=str(qty), step="0.5", min="0.5", placeholder="Qty", required=True, cls="form-control form-control-sm"),
                    cls="col-4 col-md-1 mb-2",
                ),
                Div(
                    Input(type="number", name="item_price[]", value=str(price), step="100", min="0", placeholder="Price", required=True, cls="form-control form-control-sm"),
                    cls="col-5 col-md-2 mb-2",
                ),
                Div(
                    Button(Icon("x-lg"), type="button", cls="btn btn-outline-danger btn-sm w-100", onclick="this.closest('.row').remove();"),
                    cls="col-3 col-md-1 mb-2",
                ),
                cls="align-items-center g-2 doc-item-row",
            )
        )
    return Div(*rows)


def client_portal_page(doc: dict) -> tuple:
    """Public, branded mobile-first client portal matching the exact official SJ Interiors document design.
    Features:
    - Top sticky client bar with Copy Shareable Link and Download PDF (server-generated ReportLab PDF)
    - Mobile-first exact replica of the official 3-page plum (or green receipt) aesthetic
    - In-platform Accept and Decline modals with instant status update (no WhatsApp redirect required)
    - Invoice payment confirmation modal and receipt sharing
    """
    kind = doc.get("kind", "quotation").lower()
    kind_upper = kind.upper()
    if kind == "quotation":
        kind_title = "OFFICIAL COST QUOTATION"
    elif kind == "proposal":
        kind_title = "OFFICIAL PROJECT PROPOSAL"
    elif kind == "invoice":
        kind_title = "OFFICIAL INVOICE"
    elif kind == "receipt":
        kind_title = "OFFICIAL PAYMENT RECEIPT"
    else:
        kind_title = f"OFFICIAL {kind_upper}"

    doc_num = doc.get("document_number", f"SJ-{kind_upper[:3]}-2026-001")
    cust_name = doc.get("customer_name", "Valued Client")
    cust_phone = doc.get("customer_phone", "")
    cust_email = doc.get("customer_email", "")
    title = doc.get("title", "Window Dressing & Full Interior Furnishing")
    notes = doc.get("notes", "")
    terms = doc.get("terms", "")
    created = _format_date(doc.get("created_at", datetime.now().isoformat()))
    payment_date = doc.get("payment_date", "")
    total = float(doc.get("total_amount") or 0)
    amount_paid = float(doc.get("amount_paid") or 0)
    balance_due = float(doc.get("balance_due") or 0)
    payment_method = doc.get("payment_method", "Bank Transfer")
    payment_ref = doc.get("payment_reference", "")
    currency = doc.get("currency", "NGN")
    items = doc.get("document_items", []) or []
    status = doc.get("status", "sent")
    access_token = doc.get("access_token", "")
    payment_claimed = doc.get("payment_claimed", False)
    client_decision = doc.get("client_decision", "")
    client_decision_at = doc.get("client_decision_at", "")
    client_notes = doc.get("client_notes", "")
    comments = doc.get("comments", []) or []
    if isinstance(comments, str):
        import json
        try: comments = json.loads(comments)
        except Exception: comments = []

    # Group items by category_group
    grouped: dict[str, list[dict]] = {}
    for it in items:
        grp = it.get("category_group") or "1. GENERAL FURNISHING & SERVICES"
        if grp not in grouped:
            grouped[grp] = []
        grouped[grp].append(it)

    table_rows = []
    item_counter = 1
    for grp_name, grp_items in grouped.items():
        table_rows.append(
            Tr(
                Td(
                    grp_name.upper(),
                    colspan=6,
                    style="background-color: #fbeff6; color: #6b1d49; font-weight: 700; font-size: 0.82rem; padding: 0.55rem 0.8rem; border-top: 2px solid #e5c7d8; border-bottom: 2px solid #e5c7d8;",
                ),
                cls="category-header-row",
            )
        )
        for it in grp_items:
            q = float(it.get("quantity", 1))
            u = float(it.get("unit_price", 0))
            tot = q * u
            spec = it.get("specification", "")
            unit_str = it.get("unit_label") or f"{u:,.2f}"
            table_rows.append(
                Tr(
                    Td(str(item_counter), cls="text-center text-muted small", style="width: 5%; vertical-align: middle; font-size: 0.8rem;"),
                    Td(
                        P(it.get("description", "Item"), cls="fw-semibold mb-0 text-dark", style="font-size: 0.88rem;"),
                        style="width: 28%; vertical-align: middle;",
                    ),
                    Td(
                        P(spec or "-", cls="text-muted small mb-0", style="font-size: 0.8rem;"),
                        style="width: 35%; vertical-align: middle;",
                    ),
                    Td(f"{q:g}", cls="text-center fw-medium", style="width: 8%; vertical-align: middle; font-size: 0.85rem;"),
                    Td(unit_str, cls="text-end text-secondary small", style="width: 12%; vertical-align: middle; font-size: 0.82rem;"),
                    Td(f"{tot:,.2f}", cls="text-end fw-bold text-dark", style="width: 12%; vertical-align: middle; font-size: 0.88rem;"),
                    style="border-bottom: 1px solid #f0e6ed;",
                )
            )
            item_counter += 1

    # Comment cards
    comment_elements = [
        Div(
            Div(
                Span(c.get("author", "Client"), cls="fw-bold text-dark me-2 small"),
                Small(c.get("created_at", ""), cls="text-muted"),
                cls="d-flex justify-content-between mb-1",
            ),
            P(c.get("message", ""), cls="small text-secondary mb-0"),
            cls="p-2 bg-light rounded-2 mb-2 border",
        )
        for c in comments
    ]

    # ── Interactive In-Platform Decision Banner & Buttons ────────────────────
    is_decision_open = status in {"draft", "sent", "viewed"}
    
    if status == "accepted":
        decision_zone = Div(
            Div(
                Icon("check-circle-fill", size="1.5rem", cls="text-success me-3"),
                Div(
                    H5("Document Accepted & Confirmed", cls="fw-bold text-success mb-1"),
                    P(f"Thank you for your approval! This document was accepted on {client_decision_at or created}. Our team is processing your project.", cls="small text-secondary mb-0"),
                ),
                cls="d-flex align-items-center",
            ),
            style="background: #f0fdf4; border: 1.5px solid #86efac; border-radius: 0.5rem;",
            cls="p-3 mb-4 shadow-xs",
        )
    elif status == "declined":
        decision_zone = Div(
            Div(
                Icon("x-circle-fill", size="1.5rem", cls="text-danger me-3"),
                Div(
                    H5("Document Declined / Revision Requested", cls="fw-bold text-danger mb-1"),
                    P(f"Reason: {client_notes or 'Revision requested by client.'}", cls="small text-secondary mb-0"),
                ),
                cls="d-flex align-items-center",
            ),
            style="background: #fef2f2; border: 1.5px solid #fca5a5; border-radius: 0.5rem;",
            cls="p-3 mb-4 shadow-xs",
        )
    elif kind == "invoice" and payment_claimed:
        decision_zone = Div(
            Div(
                Icon("hourglass-split", size="1.5rem", cls="text-warning me-3"),
                Div(
                    H5("Payment Confirmation Submitted", cls="fw-bold text-dark mb-1"),
                    P(f"We received your payment notice ({payment_method} - Ref: {payment_ref or 'Provided'}). Admin verification is underway.", cls="small text-secondary mb-0"),
                ),
                cls="d-flex align-items-center",
            ),
            style="background: #fffbeb; border: 1.5px solid #fde68a; border-radius: 0.5rem;",
            cls="p-3 mb-4 shadow-xs",
        )
    elif kind in {"quotation", "proposal"} and is_decision_open:
        decision_zone = Div(
            Div(
                Div(
                    H5("Ready to Proceed with this Project?", cls="fw-bold text-dark mb-1"),
                    P("Confirm your acceptance directly on this portal or request adjustments. We will be notified instantly.", cls="small text-muted mb-0"),
                    cls="mb-3 mb-sm-0",
                ),
                Div(
                    Button(
                        Icon("check-circle-fill", cls="me-1"), "Accept & Confirm",
                        type="button", cls="btn btn-success fw-bold px-3 py-2",
                        **{"data-bs-toggle": "modal", "data-bs-target": "#accept-confirm-modal"},
                    ),
                    Button(
                        Icon("x-circle", cls="me-1"), "Decline / Request Revision",
                        type="button", cls="btn btn-outline-danger fw-semibold px-3 py-2",
                        **{"data-bs-toggle": "modal", "data-bs-target": "#decline-confirm-modal"},
                    ),
                    cls="d-flex flex-column flex-sm-row gap-2",
                ),
                cls="d-flex flex-column flex-sm-row justify-content-between align-items-sm-center",
            ),
            style="background: #fdfafc; border: 1.5px solid #e5c7d8; border-left: 5px solid #6b1d49; border-radius: 0.5rem;",
            cls="p-3 p-md-4 mb-4 shadow-xs",
        )
    elif kind == "invoice" and not payment_claimed:
        decision_zone = Div(
            Div(
                Div(
                    H5("Payment for this Invoice", cls="fw-bold text-dark mb-1"),
                    P("Please transfer to the official bank account below and click the button to confirm.", cls="small text-muted mb-0"),
                    cls="mb-3 mb-sm-0",
                ),
                Button(
                    Icon("check2-circle", cls="me-1"), "I Have Paid / Confirm Payment",
                    type="button", cls="btn btn-primary fw-bold px-3 py-2",
                    **{"data-bs-toggle": "modal", "data-bs-target": "#payment-confirm-modal"},
                ),
                cls="d-flex flex-column flex-sm-row justify-content-between align-items-sm-center",
            ),
            style="background: #f0f9ff; border: 1.5px solid #bae6fd; border-left: 5px solid #0284c7; border-radius: 0.5rem;",
            cls="p-3 p-md-4 mb-4 shadow-xs",
        )
    else:
        decision_zone = ""

    # ── In-Platform Accept Modal ──────────────────────────────────────────────
    accept_modal = Div(
        Div(
            Div(
                Div(
                    H5(Icon("check-circle-fill", cls="me-2 text-success"), f"Accept {kind.title()}?", cls="modal-title fw-bold"),
                    Button("×", type="button", cls="btn-close", **{"data-bs-dismiss": "modal", "aria-label": "Close"}),
                    cls="modal-header",
                ),
                Form(
                    Div(
                        P(f"You are confirming acceptance of {doc_num} for '{title}'. Total: ₦{total:,.2f}.", cls="text-muted small mb-3"),
                        Label("Add Note / Preferred Start Date (Optional):", cls="form-label small fw-bold"),
                        Textarea(name="notes", placeholder="e.g. Approved, ready to commence measurements...", rows="3", cls="form-control form-control-sm mb-2"),
                        Input(type="hidden", name="action", value="accepted"),
                        cls="modal-body",
                    ),
                    Div(
                        Button("Cancel", type="button", cls="btn btn-outline-secondary btn-sm", **{"data-bs-dismiss": "modal"}),
                        Button(Icon("check-circle-fill", cls="me-1"), "Confirm & Submit Acceptance",
                               type="submit", cls="btn btn-success btn-sm fw-bold px-3",
                               hx_post=f"/documents/respond/{access_token}",
                               hx_include="closest form",
                               hx_target="body",
                               hx_swap="outerHTML"),
                        cls="modal-footer",
                    ),
                    action=f"/documents/respond/{access_token}",
                    method="post",
                ),
                cls="modal-content",
            ),
            cls="modal-dialog modal-dialog-centered",
        ),
        id="accept-confirm-modal", cls="modal fade d-print-none", tabindex="-1",
        **{"aria-hidden": "true", "data-bs-focus-trap": "true"},
    )

    # ── In-Platform Decline Modal ─────────────────────────────────────────────
    decline_modal = Div(
        Div(
            Div(
                Div(
                    H5(Icon("x-circle", cls="me-2 text-danger"), f"Decline or Request Revision", cls="modal-title fw-bold text-danger"),
                    Button("×", type="button", cls="btn-close", **{"data-bs-dismiss": "modal", "aria-label": "Close"}),
                    cls="modal-header",
                ),
                Form(
                    Div(
                        P(f"Please tell us why you are declining or what adjustments you need on {doc_num}:", cls="text-muted small mb-3"),
                        Label("Reason / Adjustments Needed (Required):", cls="form-label small fw-bold"),
                        Textarea(name="notes", placeholder="e.g. Budget adjustment needed, please reduce bedroom scope, change fabric choice...", rows="4", cls="form-control form-control-sm mb-2", required=True),
                        Input(type="hidden", name="action", value="declined"),
                        cls="modal-body",
                    ),
                    Div(
                        Button("Cancel", type="button", cls="btn btn-outline-secondary btn-sm", **{"data-bs-dismiss": "modal"}),
                        Button(Icon("x-circle", cls="me-1"), "Submit Decision",
                               type="submit", cls="btn btn-danger btn-sm fw-bold px-3",
                               hx_post=f"/documents/respond/{access_token}",
                               hx_include="closest form",
                               hx_target="body",
                               hx_swap="outerHTML"),
                        cls="modal-footer",
                    ),
                    action=f"/documents/respond/{access_token}",
                    method="post",
                ),
                cls="modal-content",
            ),
            cls="modal-dialog modal-dialog-centered",
        ),
        id="decline-confirm-modal", cls="modal fade d-print-none", tabindex="-1",
        **{"aria-hidden": "true", "data-bs-focus-trap": "true"},
    )

    # ── Invoice Payment Modal ────────────────────────────────────────────────
    payment_confirm_modal = Div(
        Div(
            Div(
                Div(
                    H5(Icon("check2-circle", cls="me-2 text-primary"), "Submit Payment Details", cls="modal-title fw-bold"),
                    Button("×", type="button", cls="btn-close", **{"data-bs-dismiss": "modal", "aria-label": "Close"}),
                    cls="modal-header",
                ),
                Form(
                    Div(
                        P(f"Confirming payment for: {doc_num} — Total: ₦{total:,.2f}", cls="text-muted small mb-3"),
                        Div(
                            Label("Payment Method", cls="form-label small fw-bold"),
                            Select(
                                Option("Bank Transfer", value="Bank Transfer"),
                                Option("Cash", value="Cash"),
                                Option("POS Terminal", value="POS Terminal"),
                                Option("Online Card Payment", value="Online Card Payment"),
                                name="payment_method", cls="form-select form-select-sm mb-3",
                            ),
                        ),
                        Div(
                            Label("Payment Reference / Transaction ID", cls="form-label small fw-bold"),
                            Input(type="text", name="payment_reference", cls="form-control form-control-sm mb-3",
                                  placeholder="e.g. GTB/TRF/0927836 or Teller No.", required=True),
                        ),
                        Div(
                            Label("Additional Notes (Optional)", cls="form-label small fw-bold"),
                            Textarea(name="notes", cls="form-control form-control-sm mb-2", rows="2",
                                     placeholder="e.g. 70% commitment deposit transferred..."),
                        ),
                        cls="modal-body",
                    ),
                    Div(
                        Button("Cancel", type="button", cls="btn btn-outline-secondary btn-sm", **{"data-bs-dismiss": "modal"}),
                        Button(Icon("check-circle", cls="me-1"), "Submit Payment Confirmation",
                               type="submit", cls="btn btn-primary btn-sm fw-bold px-3",
                               hx_post=f"/documents/confirm-payment/{access_token}",
                               hx_include="closest form",
                               hx_target="body",
                               hx_swap="outerHTML"),
                        cls="modal-footer",
                    ),
                    action=f"/documents/confirm-payment/{access_token}",
                    method="post",
                ),
                cls="modal-content",
            ),
            cls="modal-dialog modal-dialog-centered",
        ),
        id="payment-confirm-modal", cls="modal fade d-print-none", tabindex="-1",
        **{"aria-hidden": "true", "data-bs-focus-trap": "true"},
    ) if kind == "invoice" else ""

    # JavaScript for 1-Click Copy Link
    copy_script = Script("""
        function copyShareLink(btn) {
            const url = window.location.href;
            navigator.clipboard.writeText(url).then(function() {
                const originalHtml = btn.innerHTML;
                btn.innerHTML = '<i class="bi bi-check2-circle me-1 text-success"></i> Link Copied!';
                btn.classList.remove('btn-outline-secondary');
                btn.classList.add('btn-light', 'text-success', 'border-success');
                setTimeout(function() {
                    btn.innerHTML = originalHtml;
                    btn.classList.remove('btn-light', 'text-success', 'border-success');
                    btn.classList.add('btn-outline-secondary');
                }, 2500);
            }).catch(function(err) {
                alert('Shareable URL: ' + url);
            });
        }
    """)

    return (
        Title(f"{kind_title} {doc_num} | SJ Interiors"),
        Div(
            copy_script,
            # Top Sticky Client Header Bar
            Div(
                Container(
                    Div(
                        Div(
                            Div(
                                Span("SJ", cls="badge bg-dark text-white me-2 fw-bold px-2 py-1", style="font-size: 0.9rem; background-color: #6b1d49 !important;"),
                                Div(
                                    P("SJ Interiors", cls="fw-bold mb-0 text-dark", style="font-size: 0.95rem; line-height: 1.1;"),
                                    Small(f"{kind_title} • {doc_num}", cls="text-muted small"),
                                ),
                                cls="d-flex align-items-center",
                            ),
                            cls="d-flex align-items-center",
                        ),
                        Div(
                            Button(
                                Icon("link-45deg", cls="me-1"), "Copy Link",
                                type="button", cls="btn btn-outline-secondary btn-sm fw-semibold",
                                onclick="copyShareLink(this);",
                                title="Copy shareable link for client",
                            ),
                            A(
                                Icon("download", cls="me-1"), "Download PDF",
                                href=f"/documents/pdf/{access_token}",
                                target="_blank",
                                cls="btn btn-primary btn-sm fw-bold px-3",
                                style="background-color: #6b1d49; border-color: #6b1d49;" if kind != "receipt" else "background-color: #1a7a3b; border-color: #1a7a3b;",
                                title="Download exact server-generated PDF",
                            ),
                            cls="d-flex align-items-center gap-2",
                        ),
                        cls="d-flex flex-wrap justify-content-between align-items-center gap-2",
                    ),
                    cls="py-2",
                ),
                cls="bg-white border-bottom sticky-top py-2 d-print-none shadow-xs",
                style="z-index: 1020;",
            ),
            # Modals
            accept_modal,
            decline_modal,
            payment_confirm_modal,
            # Main Document Container
            Container(
                Div(
                    # Interactive in-platform decision zone
                    decision_zone,
                    # Document Paper Sheet (matching sample invoice design)
                    Card(
                        # Subtle Watermark
                        Div(
                            "PAID" if (kind == "receipt" or status == "paid") else ("PROFORMA" if kind == "quotation" else ("INVOICE" if kind == "invoice" else "OFFICIAL")),
                            style="position: absolute; top: 40%; left: 50%; transform: translate(-50%, -50%) rotate(-32deg); font-size: 5.5rem; font-weight: 900; color: rgba(107, 29, 73, 0.035); pointer-events: none; user-select: none; z-index: 1; letter-spacing: 0.18em;",
                        ),
                        # 1. Company Header Lockup (Left Brand, Right Uppercase Doc Type & Ref)
                        Div(
                            Row(
                                Col(
                                    H1("SJ Interiors", cls="brand-title mb-0", style=f"color: {'#1a7a3b' if kind == 'receipt' else '#6b1d49'}; font-weight: 800; font-size: 1.85rem; letter-spacing: -0.02em;"),
                                    Div("Deco and Beddings", cls="brand-subtitle", style=f"color: {'#125428' if kind == 'receipt' else '#4a1232'}; font-weight: 600; font-size: 1.05rem; margin-bottom: 2px;"),
                                    Div("REDEFINING YOUR SPACE • SIMPLICITY. COMFORT. STYLE.", cls="brand-tagline", style="color: #b87d28; font-size: 0.72rem; font-weight: 700; letter-spacing: 0.08em;"),
                                    lg=6, cols=12,
                                ),
                                Col(
                                    Div(
                                        H2("PROFORMA INVOICE" if kind == "quotation" else kind_title, cls="fw-bold mb-2 text-dark", style="letter-spacing: 0.03em; font-size: 1.45rem;"),
                                        Div(
                                            Span("REFERENCE", cls="small fw-bold text-muted text-uppercase d-block", style="font-size: 0.68rem; letter-spacing: 0.06em;"),
                                            Span(doc_num, cls="fw-bold text-dark font-monospace", style="font-size: 0.95rem;"),
                                            cls="mb-1",
                                        ),
                                        Div(
                                            Span("DATE ISSUED", cls="small fw-bold text-muted text-uppercase d-block", style="font-size: 0.68rem; letter-spacing: 0.06em;"),
                                            Span(created, cls="fw-semibold text-dark small"),
                                        ),
                                        cls="text-start text-lg-end mt-2 mt-lg-0",
                                    ),
                                    lg=6, cols=12,
                                ),
                                cls="align-items-start g-3",
                            ),
                            # Solid Accent Line under header (matching sample invoice)
                            Div(style=f"height: 3px; background-color: {'#1a7a3b' if kind == 'receipt' else '#6b1d49'}; width: 100%; margin-top: 1rem; margin-bottom: 1.5rem; border-radius: 2px;"),
                            cls="pb-2",
                        ),
                        # 2. Two-Column Metadata Box (BILLED TO & SERVICE REQUESTED)
                        Div(
                            Row(
                                Col(
                                    Div(
                                        Span("BILLED TO", cls="small fw-bold text-uppercase d-block mb-1", style=f"color: {'#1a7a3b' if kind == 'receipt' else '#6b1d49'}; font-size: 0.72rem; letter-spacing: 0.06em;"),
                                        H5(cust_name, cls="fw-bold text-dark mb-1"),
                                        P(cust_email or "client@example.com", cls="small text-muted mb-0"),
                                        P(cust_phone or "Phone not specified", cls="small text-muted mb-0"),
                                        cls="p-3 bg-light rounded-3 border h-100",
                                    ),
                                    lg=6, cols=12,
                                ),
                                Col(
                                    Div(
                                        Span("SERVICE REQUESTED", cls="small fw-bold text-uppercase d-block mb-1", style=f"color: {'#1a7a3b' if kind == 'receipt' else '#6b1d49'}; font-size: 0.72rem; letter-spacing: 0.06em;"),
                                        H5(title, cls="fw-bold text-dark mb-1"),
                                        P("Valid for 14 days from date issued" if kind != "receipt" else f"Payment acknowledged via {payment_method}", cls="small text-muted mb-0"),
                                        cls="p-3 bg-light rounded-3 border h-100",
                                    ),
                                    lg=6, cols=12,
                                    cls="mt-2 mt-lg-0",
                                ),
                                cls="g-3 mb-4",
                            ),
                        ),
                        # 3. Itemized Table with Deep Brand Header
                        Div(
                            Table(
                                Thead(
                                    Tr(
                                        Th("ITEM", style=f"background-color: {'#1a7a3b' if kind == 'receipt' else '#6b1d49'}; color: #ffffff; border: none; font-size: 0.8rem; padding: 0.75rem 0.6rem; letter-spacing: 0.05em; width: 32%;"),
                                        Th("DETAILS", style=f"background-color: {'#1a7a3b' if kind == 'receipt' else '#6b1d49'}; color: #ffffff; border: none; font-size: 0.8rem; padding: 0.75rem 0.6rem; letter-spacing: 0.05em; width: 44%;"),
                                        Th("AMOUNT", cls="text-end", style=f"background-color: {'#1a7a3b' if kind == 'receipt' else '#6b1d49'}; color: #ffffff; border: none; font-size: 0.8rem; padding: 0.75rem 0.8rem; letter-spacing: 0.05em; width: 24%;"),
                                    ),
                                ),
                                Tbody(*table_rows),
                                cls="table table-hover mb-0 align-middle",
                                style="border: 1px solid #e2e8f0;",
                            ),
                            cls="table-responsive rounded-3 border overflow-hidden mb-4",
                        ),
                        # 4. Highlighted Investment Banner (matching sample invoice)
                        Div(
                            Div(
                                Span(
                                    "ESTIMATED INVESTMENT" if kind in {"proposal", "quotation"} else ("TOTAL AMOUNT" if kind == "invoice" else "TOTAL PAYMENT RECEIVED"),
                                    cls="fw-bold text-uppercase small",
                                    style=f"color: {'#1a7a3b' if kind == 'receipt' else '#6b1d49'}; letter-spacing: 0.05em;",
                                ),
                                H4(f"NGN {total:,.2f}", cls="fw-bold mb-0 text-dark", style="letter-spacing: -0.01em;") if kind != "receipt" else Div(
                                    Div(Span("Total: ", cls="text-muted small me-2"), Span(f"NGN {total:,.2f}", cls="fw-semibold text-dark me-3"), Span("Paid: ", cls="text-muted small me-2"), Span(f"NGN {amount_paid:,.2f}", cls="fw-bold text-success me-3"), Span("Balance: ", cls="text-muted small me-2"), Span(f"NGN {balance_due:,.2f}", cls="fw-bold text-dark"), cls="d-flex flex-wrap align-items-center justify-content-end"),
                                    cls="text-end",
                                ),
                                cls="d-flex flex-column flex-sm-row justify-content-between align-items-sm-center w-100 gap-2",
                            ),
                            style=f"background-color: {'#f0fdf4' if kind == 'receipt' else '#faf5f8'}; border: 1.5px solid {'#bbf7d0' if kind == 'receipt' else '#f3d5e5'}; padding: 1rem 1.25rem; border-radius: 0.5rem;",
                            cls="mb-4",
                        ),
                        # 5. Project Description Box (matching sample invoice)
                        Div(
                            P("PROJECT DESCRIPTION", cls="small fw-bold text-dark text-uppercase letter-spacing-1 mb-2", style="font-size: 0.75rem;"),
                            Div(
                                P(notes or title, cls="small text-secondary mb-0"),
                                cls="p-3 bg-light rounded-3 border",
                            ),
                            cls="mb-4",
                        ),
                        # 6. Terms & Notes with Sign-off (matching sample invoice)
                        Div(
                            P("TERMS & NOTES", cls="small fw-bold text-dark text-uppercase letter-spacing-1 mb-2", style="font-size: 0.75rem;"),
                            Ul(
                                Li(Small("This is an official project document based on the specifications above.", cls="text-secondary"), cls="mb-1"),
                                (Li(Small("70% commitment deposit required before fabric procurement and tailoring commences; balance due upon delivery/installation.", cls="text-secondary"), cls="mb-1") if kind != "receipt" else Li(Small("Payment received with thanks! Official receipt acknowledges fulfillment.", cls="text-secondary"), cls="mb-1")),
                                Li(Small("Official Account: Guaranty Trust Bank (GTBank) • 08026022672 • SJ Interior Deco and Beddings", cls="text-secondary fw-semibold"), cls="mb-1"),
                                Li(Small("This document is valid for 14 calendar days from the date issued above.", cls="text-secondary")),
                                cls="ps-3 mb-3",
                            ),
                            P("Thank you for reaching out to SJ Interiors.", cls="fw-bold text-dark small mb-0"),
                            cls="mb-4",
                        ),
                        # 7. Corporate Footer (matching sample invoice)
                        Div(
                            Row(
                                Col(
                                    Small("SJ Interior Deco and Beddings · Limca Junction Shopping Complex, Along Asa Dam Road, Ilorin, Kwara State · RC 9711335", cls="text-muted d-block"),
                                    Small("contact@sjinteriors.com · +234 802 602 2672 · +234 911 507 6282", cls="text-muted d-block"),
                                    lg=9, cols=12,
                                ),
                                Col(
                                    Small("Page 1 of 1", cls="text-muted text-start text-lg-end d-block fw-semibold"),
                                    lg=3, cols=12,
                                ),
                                cls="align-items-center g-2",
                            ),
                            cls="pt-3 border-top mt-4",
                        ),
                        cls="p-4 p-md-5 my-3 shadow-sm border-0 bg-white rounded-3 position-relative",
                        style="max-width: 960px; margin: 0 auto;",
                    ),
                    # 8. Interactive Comments / Thread
                    Div(
                        Card(
                            H4("Questions or Special Requests on this Document?", cls="h6 fw-bold text-dark mb-2"),
                            P("Have a question regarding measurements, fabric choices, or delivery timelines? Leave your note below:", cls="small text-muted mb-3"),
                            Div(*comment_elements, id="client-comments-thread", cls="mb-3") if comment_elements
                            else Div(P("No comments yet. Leave a note below if you have any questions.", cls="small text-muted fst-italic"), id="client-comments-thread", cls="mb-3"),
                            Form(
                                Input(type="hidden", name="token", value=access_token),
                                Row(
                                    Div(
                                        Input(type="text", name="author", placeholder="Your Name", required=True, cls="form-control form-control-sm"),
                                        cls="col-md-4 mb-2",
                                    ),
                                    Div(
                                        Input(type="text", name="message", placeholder="Type your question or request...", required=True, cls="form-control form-control-sm"),
                                        cls="col-md-6 mb-2",
                                    ),
                                    Div(
                                        Button("Send Comment", type="submit", cls="btn btn-primary btn-sm w-100 fw-bold",
                                               hx_post=f"/documents/comment/{access_token}",
                                               hx_target="#client-comments-thread",
                                               hx_swap="innerHTML"),
                                        cls="col-md-2 mb-2",
                                    ),
                                    cls="g-2",
                                ),
                                action=f"/documents/comment/{access_token}",
                                method="post",
                            ),
                            cls="p-4 border-0 shadow-sm bg-white rounded-3 mt-3",
                            style="max-width: 960px; margin: 0 auto;",
                        ),
                        cls="d-print-none mb-5",
                    ) if kind != "receipt" else "",
                    style="max-width: 960px; margin: 0 auto;",
                ),
                cls="py-3 px-2 px-sm-3",
            ),
            cls="client-portal-page min-vh-100 bg-light",
        ),
    )


def printable_document_view(doc: dict) -> tuple:
    """Printable invoice/quotation/receipt layout with auto-print."""
    portal = client_portal_page(doc)
    return (
        portal[0],  # Title
        portal[1],  # Body
        Script("window.addEventListener('DOMContentLoaded', function() { setTimeout(function() { window.print(); }, 400); });"),
    )



