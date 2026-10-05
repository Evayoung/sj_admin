"""Document management routes (proposals, quotations, invoices, receipts)."""

from __future__ import annotations

from typing import Any
from starlette.requests import Request
from starlette.responses import FileResponse, JSONResponse, RedirectResponse

try:
    from ..infrastructure.document_pdf import build_document_pdf
    from ..infrastructure.document_repository import (
        add_document_comment,
        convert_invoice_to_receipt,
        create_document,
        delete_document,
        get_all_documents,
        get_document_by_id,
        get_document_by_token,
        get_official_sample_items,
        record_client_decision,
        record_client_payment_claim,
        record_document_view,
        update_document,
        update_document_status,
    )
    from ..infrastructure.inquiry_repository import get_inquiry_by_id
    from ..presentation.pages.documents import (
        _documents_list,
        client_portal_page,
        document_editor_fragment,
        documents_page,
        printable_document_view,
    )
    from ..presentation.page_helpers import oob_alert, toast_fragment
    from ..presentation.shell import page_frame
except ImportError:
    from app.infrastructure.document_pdf import build_document_pdf
    from app.infrastructure.document_repository import (
        add_document_comment,
        convert_invoice_to_receipt,
        create_document,
        delete_document,
        get_all_documents,
        get_document_by_id,
        get_document_by_token,
        get_official_sample_items,
        record_client_decision,
        record_client_payment_claim,
        record_document_view,
        update_document,
        update_document_status,
    )
    from app.infrastructure.inquiry_repository import get_inquiry_by_id
    from app.presentation.pages.documents import (
        _documents_list,
        client_portal_page,
        document_editor_fragment,
        documents_page,
        printable_document_view,
    )
    from app.presentation.page_helpers import oob_alert, toast_fragment
    from app.presentation.shell import page_frame

from fasthtml.common import HttpHeader



def register_document_routes(app: Any) -> None:

    @app.get("/documents")
    def documents_view(kind: str = "all", status: str = "all", inquiry_id: str = "", new: int = 0):
        docs = get_all_documents(kind, status)
        editor = None
        if new or inquiry_id:
            inquiry = get_inquiry_by_id(inquiry_id) if inquiry_id else None
            editor = document_editor_fragment(None, kind=kind, inquiry=inquiry)
        return page_frame(*documents_page(docs, kind, status, selected_fragment=editor), current="/documents", title="Documents")

    @app.get("/documents/list")
    def documents_list_fragment(kind: str = "all", status: str = "all"):
        """HTMX: return updated documents list fragment."""
        docs = get_all_documents(kind, status)
        return _documents_list(docs, kind, status)

    @app.get("/documents/editor")
    def document_editor(doc_id: str = "", kind: str = "quotation", inquiry_id: str = "", template: str = ""):
        """HTMX: return document editor form."""
        doc = None
        inquiry = None
        if doc_id:
            doc = get_document_by_id(doc_id)
        elif template == "official":
            doc = {
                "kind": "quotation",
                "title": "Window Dressing & Full Interior Furnishing",
                "customer_name": "Valued Client",
                "customer_phone": "08026022672",
                "terms": "• Quotation validity: 14 business days from the date of issuance due to market fluctuations.\n• 70% commitment deposit required before procurement and tailoring commences; balance due upon delivery/installation.\n• All items supplied remain the quality standard of SJ Interior Deco & Beddings.",
                "notes": "Official comprehensive quotation covering window dressing, interior decor, luxury bedding, and complete apartment setup.",
                "document_items": get_official_sample_items(),
            }
        elif template == "receipt" or kind == "receipt":
            import random
            rec_seq = random.randint(100, 999)
            doc = {
                "kind": "receipt",
                "document_number": f"REC-2026-0{rec_seq}",
                "title": "Official Payment Receipt — Soft Furnishing & Bedding",
                "customer_name": "",
                "customer_phone": "",
                "customer_email": "",
                "status": "paid",
                "payment_method": "Bank Transfer",
                "payment_reference": "",
                "terms": "• Thank you for your payment and business with SJ Interior Deco & Beddings.\n• Goods received in good condition cannot be returned after 7 business days.\n• Please keep this receipt as proof of purchase and warranty for fitting accessories.",
                "notes": "Payment received in full. Production and tailoring scheduled per agreed timeline.",
                "document_items": [
                    {"category_group": "1. LIVING ROOM", "description": "Custom Drapery & Eyelet Pleated Curtains", "specification": "Custom drop length tailoring", "quantity": 1, "unit_price": 65000}
                ],
            }
        elif inquiry_id:
            inquiry = get_inquiry_by_id(inquiry_id)
            if inquiry:
                doc = {
                    "kind": "quotation",
                    "title": f"Interior Furnishing for {inquiry.get('customer_name', 'Client')}",
                    "customer_name": inquiry.get("customer_name", ""),
                    "customer_phone": inquiry.get("phone", ""),
                    "customer_email": inquiry.get("email", ""),
                    "notes": inquiry.get("message", ""),
                    "document_items": get_official_sample_items() if inquiry.get("service_inquiry") else [],
                }
        return document_editor_fragment(doc, kind=kind, inquiry=inquiry)

    @app.get("/documents/quick-receipt-form")
    def document_quick_receipt():
        """HTMX: rapid-entry walk-in / direct bank transfer receipt editor."""
        return document_editor(kind="receipt", template="receipt")


    @app.post("/documents/save")
    async def document_save(req: Request):
        """HTMX: save document and categorized line items from form."""
        form_data = await req.form()

        doc_id = form_data.get("id", "")
        kind = form_data.get("kind", "quotation")
        doc_number = form_data.get("document_number", "")
        customer_name = form_data.get("customer_name", "")
        customer_phone = form_data.get("customer_phone", "")
        customer_email = form_data.get("customer_email", "")
        title = form_data.get("title", "")
        terms = form_data.get("terms", "")
        notes = form_data.get("notes", "")
        status = form_data.get("status", "draft")
        inquiry_id = form_data.get("inquiry_id", "")

        # Receipt-specific payment fields
        amount_paid_raw = form_data.get("amount_paid", "")
        payment_method = form_data.get("payment_method", "Bank Transfer")
        payment_reference = form_data.get("payment_reference", "")

        # Extract line items arrays
        item_categories = form_data.getlist("item_category[]")
        item_descs = form_data.getlist("item_desc[]")
        item_specs = form_data.getlist("item_spec[]")
        item_qtys = form_data.getlist("item_qty[]")
        item_prices = form_data.getlist("item_price[]")

        items = []
        for i in range(len(item_descs)):
            desc = item_descs[i].strip() if item_descs[i] else ""
            if desc:
                cat = item_categories[i].strip() if i < len(item_categories) and item_categories[i] else ""
                spec = item_specs[i].strip() if i < len(item_specs) and item_specs[i] else ""
                qty = float(item_qtys[i]) if i < len(item_qtys) and item_qtys[i] else 1.0
                price = float(item_prices[i]) if i < len(item_prices) and item_prices[i] else 0.0
                items.append({
                    "category_group": cat,
                    "description": desc,
                    "specification": spec,
                    "quantity": qty,
                    "unit_price": price,
                })

        doc_data = {
            "kind": kind,
            "document_number": doc_number,
            "customer_name": customer_name,
            "customer_phone": customer_phone,
            "customer_email": customer_email,
            "title": title,
            "terms": terms,
            "notes": notes,
            "status": status,
        }
        if inquiry_id:
            doc_data["inquiry_id"] = inquiry_id

        # For receipts: compute and store payment amounts
        if kind == "receipt":
            total = sum(float(it.get("quantity", 1)) * float(it.get("unit_price", 0)) for it in items)
            try:
                amount_paid = float(amount_paid_raw) if amount_paid_raw else total
            except (ValueError, TypeError):
                amount_paid = total
            balance = max(0.0, total - amount_paid)
            doc_data["amount_paid"] = amount_paid
            doc_data["balance_due"] = balance
            doc_data["payment_method"] = payment_method
            doc_data["payment_reference"] = payment_reference
            from datetime import datetime as _dt
            doc_data["payment_date"] = _dt.now().strftime("%b %d, %Y")

        from app.infrastructure.audit_repository import log_activity
        session = req.scope.get("session", {})

        if doc_id:
            saved_doc = update_document(doc_id, doc_data, items=items)
            if saved_doc:
                log_activity(req, session, "UPDATE_DOCUMENT", "document", str(saved_doc.get("document_number", doc_id)), f"Updated {kind.title()} {saved_doc.get('document_number', doc_id)} for {customer_name}")
        else:
            saved_doc = create_document(doc_data, items=items)
            if saved_doc:
                log_activity(req, session, "CREATE_DOCUMENT", "document", str(saved_doc.get("document_number", "DOC")), f"Created {kind.title()} {saved_doc.get('document_number')} for {customer_name}")

        if saved_doc:
            return document_editor_fragment(saved_doc), toast_fragment("Document saved successfully.", variant="success"), HttpHeader("HX-Trigger", "refreshList")

        return oob_alert("Failed to save document. Please check database connection.", variant="danger", target="document-save-result"), toast_fragment("Failed to save document.", variant="danger")

    @app.post("/documents/delete")
    def document_delete(req: Request, id: str = ""):
        """HTMX: delete document."""
        if not id:
            return JSONResponse({"error": "Missing id"}, status_code=400)
        from app.infrastructure.audit_repository import log_activity
        session = req.scope.get("session", {})
        success = delete_document(id)
        if success:
            log_activity(req, session, "DELETE_DOCUMENT", "document", str(id), f"Deleted document {id}")
            return document_editor_fragment(None), toast_fragment("Document deleted successfully.", variant="success"), HttpHeader("HX-Trigger", "refreshList")
        return oob_alert("Failed to delete document.", variant="danger", target="document-save-result"), toast_fragment("Failed to delete document.", variant="danger")

    @app.post("/documents/status")
    def document_status_update(req: Request, id: str = "", status: str = ""):
        """HTMX: quick update status."""
        if not id or not status:
            return oob_alert("Missing parameters.", variant="danger", target="document-save-result"), toast_fragment("Missing parameters.", variant="danger")
        from app.infrastructure.audit_repository import log_activity
        session = req.scope.get("session", {})
        res = update_document_status(id, status)
        if res:
            log_activity(req, session, "UPDATE_DOCUMENT_STATUS", "document", str(id), f"Updated document {id} status to {status.upper()}")
            return oob_alert(f"Document status updated to {status.upper()}.", variant="success", target="document-save-result"), toast_fragment(f"Document status updated to {status.upper()}.", variant="success"), HttpHeader("HX-Trigger", "refreshList")
        return oob_alert("Failed to update status.", variant="danger", target="document-save-result"), toast_fragment("Failed to update status.", variant="danger")

    # Admin: 1-click invoice → receipt conversion
    @app.post("/documents/generate-receipt/{invoice_id}")
    async def document_generate_receipt(invoice_id: str, req: Request):
        """HTMX: convert a confirmed invoice into an official payment receipt."""
        form = await req.form()
        amount_paid_raw = form.get("amount_paid", "")
        pay_method = str(form.get("payment_method", "Bank Transfer"))
        pay_reference = str(form.get("payment_reference", ""))
        try:
            amount_paid = float(amount_paid_raw) if amount_paid_raw else None
        except (ValueError, TypeError):
            amount_paid = None
        receipt = convert_invoice_to_receipt(
            invoice_id,
            amount_paid=amount_paid,
            payment_method=pay_method,
            payment_reference=pay_reference,
        )
        if receipt:
            from app.infrastructure.audit_repository import log_activity
            session = req.scope.get("session", {})
            log_activity(req, session, "GENERATE_RECEIPT", "document", str(receipt.get("document_number", invoice_id)), f"Generated payment receipt {receipt.get('document_number')} from invoice {invoice_id}")
            return document_editor_fragment(receipt, kind="receipt"), toast_fragment("Official receipt generated successfully!", variant="success")
        return oob_alert("Failed to generate receipt. Check if invoice exists.", variant="danger", target="document-save-result"), toast_fragment("Failed to generate receipt.", variant="danger")

    # Public: client submits 'I Have Paid' from invoice portal
    @app.post("/documents/confirm-payment/{token}")
    def document_confirm_payment(token: str, payment_method: str = "Bank Transfer", payment_reference: str = "", notes: str = ""):
        """Public: client submits payment confirmation from invoice portal."""
        updated_doc = record_client_payment_claim(token, str(payment_method), str(payment_reference), str(notes))
        if not updated_doc:
            return page_frame("Document not found or link is invalid.", current="/documents", title="Invalid Link")
        return client_portal_page(updated_doc)

    # Public client portal with automated visit tracking
    @app.get("/documents/preview/{token}")
    def document_client_preview(token: str):
        tracked_doc = record_document_view(token)
        if not tracked_doc:
            return page_frame("Document not found or invalid link.", current="/documents", title="Document Not Found")
        return client_portal_page(tracked_doc)

    # In-Platform Client Decision Action (Accept / Decline / Revision Request)
    @app.post("/documents/respond/{token}")
    @app.post("/documents/decision/{token}")
    def document_client_respond(token: str, action: str = "accepted", decision: str = "", notes: str = "", comment: str = ""):
        """Public: Client confirms acceptance or declines with reason directly on the platform."""
        final_action = action or decision or "accepted"
        final_notes = notes or comment or ""
        updated_doc = record_client_decision(token, final_action, final_notes)
        if not updated_doc:
            return page_frame("Document not found or invalid link.", current="/documents", title="Invalid Link")
        return client_portal_page(updated_doc)

    # Client Comment Submission
    @app.post("/documents/comment/{token}")
    def document_client_comment(token: str, author: str = "Client", message: str = ""):
        clean_author = str(author or "Client").strip()
        clean_msg = str(message or "").strip()
        if not clean_msg:
            return oob_alert("Please enter a comment.", variant="warning")
        updated_doc = add_document_comment(token, clean_author, clean_msg)
        if not updated_doc:
            return oob_alert("Failed to post comment.", variant="danger")
        comments = updated_doc.get("comments") or []
        from fasthtml.common import Div, P, Small, Span
        elements = [
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
        return Div(*elements, id="client-comments-thread")


    # Exact server-generated PDF download (consistent on all devices)
    @app.get("/documents/pdf/{token}")
    @app.get("/documents/download/{token}")
    def document_download_pdf(token: str):
        """Download exact server-generated ReportLab PDF matching official SJ Interiors design."""
        doc = get_document_by_token(token) or get_document_by_id(token)
        if not doc:
            return JSONResponse({"error": "Document not found"}, status_code=404)
        pdf_path = build_document_pdf(doc)
        filename = f"{doc.get('document_number', 'SJ-Document')}.pdf"
        return FileResponse(
            str(pdf_path),
            media_type="application/pdf",
            filename=filename,
        )

    # Printable HTML view
    @app.get("/documents/print/{id}")
    def document_print_view(id: str):
        doc = get_document_by_id(id) or get_document_by_token(id)
        if not doc:
            return page_frame("Document not found.", current="/documents", title="Document Not Found")
        return printable_document_view(doc)


