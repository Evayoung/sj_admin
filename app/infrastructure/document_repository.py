"""Document repository — CRUD and calculations for proposals, quotations, invoices, and receipts."""

from __future__ import annotations

from datetime import datetime
from typing import Any
import uuid

from app.infrastructure.supabase_client import get_service_client, has_supabase


# In-memory document storage fallback populated with initial live test records
_LOCAL_DOCUMENTS: dict[str, dict] = {}


def _init_default_documents():
    if _LOCAL_DOCUMENTS:
        return

    # 1. Quotation: QTN-2026-0042
    qtn_items = get_official_sample_items()
    qtn_total = sum(float(it["quantity"]) * float(it["unit_price"]) for it in qtn_items)
    qtn_id = "doc-qtn-2026-0042"
    _LOCAL_DOCUMENTS[qtn_id] = {
        "id": qtn_id,
        "kind": "quotation",
        "document_number": "QTN-2026-0042",
        "customer_name": "Chief Meshell",
        "customer_phone": "09029952120",
        "customer_email": "meshell@sjinteriors.ng",
        "title": "Comprehensive 3-Bedroom Apartment Furnishing & Window Dressing",
        "subtitle": "SJ Interiors • Deco and Beddings Supply",
        "notes": "Full comprehensive cost quotation covering 6 divisions: living room drapery, bedroom blackout curtains, window blinds, luxury bedding, turnkey kitchenware, and installation.",
        "terms": "• Quotation validity: 14 business days from issuance date.\n• 70% commitment deposit required before procurement and tailoring commences; balance due upon delivery/installation.\n• All items supplied remain the quality standard of SJ Interior Deco & Beddings.",
        "status": "sent",
        "total_amount": qtn_total,
        "amount_paid": 0,
        "balance_due": qtn_total,
        "currency": "NGN",
        "access_token": "token-qtn-meshell-2026",
        "view_count": 2,
        "viewed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "created_at": datetime.now().isoformat(),
        "document_items": qtn_items,
        "comments": [
            {
                "id": "c1",
                "author": "Chief Meshell",
                "message": "Please ensure the living room bronze pole matches the gold wall sconces.",
                "created_at": "Today at 2:15 PM",
            }
        ],
    }

    # 2. Proposal: PRO-2026-0018
    pro_items = [
        {"category_group": "1. SITTING ROOM CURTAINS (3 WINDOWS ESTIMATION)", "description": "Custom Double Pleated Drapes", "specification": "Luxury velvet drapes with sheer lining", "quantity": 12, "unit_price": 15000, "unit_label": "₦15,000.00"},
        {"category_group": "3. INTERIOR DECOR & BLINDS", "description": "Motorized Zebra Blinds", "specification": "Smart motorized zebra blinds with remote", "quantity": 4, "unit_price": 45000, "unit_label": "₦45,000.00"},
        {"category_group": "4. BEDROOM & BEDDING", "description": "Hotel Suite King Bedding Bundle", "specification": "400TC Egyptian cotton duvet, sheets & 4 pillows", "quantity": 2, "unit_price": 85000, "unit_label": "₦85,000.00"},
        {"category_group": "6. LOGISTICS & WORKMANSHIP", "description": "Turnkey Staging & Installation", "specification": "Complete space setup and mounting", "quantity": 1, "unit_price": 50000, "unit_label": "₦50,000.00"},
    ]
    pro_total = sum(float(it["quantity"]) * float(it["unit_price"]) for it in pro_items)
    pro_id = "doc-pro-2026-0018"
    _LOCAL_DOCUMENTS[pro_id] = {
        "id": pro_id,
        "kind": "proposal",
        "document_number": "PRO-2026-0018",
        "customer_name": "Chief Meshell",
        "customer_phone": "09029952120",
        "customer_email": "meshell@sjinteriors.ng",
        "title": "Turnkey Penthouse Interior Styling & Luxury Staging Proposal",
        "subtitle": "SJ Interiors • Bespoke Design Proposal",
        "notes": "Concept design and execution plan for luxury penthouse shortlet property.",
        "terms": "Valid for 30 calendar days. Design scope verification required before fabrication.",
        "status": "sent",
        "total_amount": pro_total,
        "amount_paid": 0,
        "balance_due": pro_total,
        "currency": "NGN",
        "access_token": "token-pro-meshell-2026",
        "view_count": 1,
        "viewed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "created_at": datetime.now().isoformat(),
        "document_items": pro_items,
        "comments": [],
    }

    # 3. Invoice: INV-2026-0105
    inv_items = [
        {"category_group": "1. SITTING ROOM CURTAINS (3 WINDOWS ESTIMATION)", "description": "Custom Eyelet Drapes (Living Room)", "specification": "Heavyweight jacquard drapes with bronze hardware", "quantity": 18, "unit_price": 6500, "unit_label": "₦6,500.00"},
        {"category_group": "2. BEDROOM CURTAINS", "description": "Blackout Curtains (Master Bed)", "specification": "100% Light-block drapes with rings", "quantity": 16, "unit_price": 4500, "unit_label": "₦4,500.00"},
        {"category_group": "4. BEDROOM & BEDDING", "description": "400TC Luxury White Duvet Set (6x6)", "specification": "King size hotel collection with 4 pillowcases", "quantity": 2, "unit_price": 38000, "unit_label": "₦38,000.00"},
        {"category_group": "6. LOGISTICS & WORKMANSHIP", "description": "Delivery & Mounting Labor", "specification": "On-site installation at client residence", "quantity": 1, "unit_price": 25000, "unit_label": "₦25,000.00"},
    ]
    inv_total = sum(float(it["quantity"]) * float(it["unit_price"]) for it in inv_items)
    inv_id = "doc-inv-2026-0105"
    _LOCAL_DOCUMENTS[inv_id] = {
        "id": inv_id,
        "kind": "invoice",
        "document_number": "INV-2026-0105",
        "customer_name": "Chief Meshell",
        "customer_phone": "09029952120",
        "customer_email": "meshell@sjinteriors.ng",
        "title": "Official Invoice for Living Room & Master Bedroom Furnishing",
        "subtitle": "SJ Interiors • Official Commercial Invoice",
        "notes": "Please transfer 70% commitment deposit or full payment to account details provided.",
        "terms": "Payment due within 7 days. Account: SJ Interior Deco & Beddings / 08026022672 / GTBank.",
        "status": "sent",
        "total_amount": inv_total,
        "amount_paid": 0,
        "balance_due": inv_total,
        "currency": "NGN",
        "access_token": "token-inv-meshell-2026",
        "view_count": 4,
        "viewed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "created_at": datetime.now().isoformat(),
        "document_items": inv_items,
        "comments": [],
        "payment_claimed": False,
    }

    # 4. Receipt: REC-2026-0088
    rec_items = [
        {"category_group": "1. SITTING ROOM CURTAINS (3 WINDOWS ESTIMATION)", "description": "Custom Eyelet Drapes (Living Room)", "specification": "Heavyweight jacquard drapes with bronze hardware", "quantity": 18, "unit_price": 6500, "unit_label": "₦6,500.00"},
        {"category_group": "2. BEDROOM CURTAINS", "description": "Blackout Curtains (Master Bed)", "specification": "100% Light-block drapes with rings", "quantity": 16, "unit_price": 4500, "unit_label": "₦4,500.00"},
        {"category_group": "4. BEDROOM & BEDDING", "description": "400TC Luxury White Duvet Set (6x6)", "specification": "King size hotel collection with 4 pillowcases", "quantity": 2, "unit_price": 38000, "unit_label": "₦38,000.00"},
        {"category_group": "6. LOGISTICS & WORKMANSHIP", "description": "Delivery & Mounting Labor", "specification": "On-site installation at client residence", "quantity": 1, "unit_price": 25000, "unit_label": "₦25,000.00"},
    ]
    rec_total = sum(float(it["quantity"]) * float(it["unit_price"]) for it in rec_items)
    rec_id = "doc-rec-2026-0088"
    _LOCAL_DOCUMENTS[rec_id] = {
        "id": rec_id,
        "kind": "receipt",
        "document_number": "REC-2026-0088",
        "customer_name": "Chief Meshell",
        "customer_phone": "09029952120",
        "customer_email": "meshell@sjinteriors.ng",
        "title": "Payment Receipt for Living Room & Master Bedroom Furnishing",
        "subtitle": "SJ Interiors • Official Payment Receipt",
        "notes": "Payment received via Bank Transfer. Reference: GTB/TRF/982173. Date: Feb 19, 2026.",
        "terms": "Thank you for your payment! Goods supplied and services rendered remain the high standard of SJ Interior Deco & Beddings.",
        "status": "paid",
        "total_amount": rec_total,
        "amount_paid": rec_total,
        "balance_due": 0.0,
        "payment_method": "Bank Transfer",
        "payment_reference": "GTB/TRF/982173",
        "payment_date": datetime.now().strftime("%b %d, %Y"),
        "related_invoice_id": inv_id,
        "currency": "NGN",
        "access_token": "token-rec-meshell-2026",
        "view_count": 3,
        "viewed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "created_at": datetime.now().isoformat(),
        "document_items": rec_items,
        "comments": [],
    }


def generate_document_number(kind: str = "proposal") -> str:
    """Generate sequential or timestamped document number, e.g. QTN-2026-4821, REC-2026-4821."""
    prefix_map = {
        "proposal": "PRO",
        "quotation": "QTN",
        "invoice": "INV",
        "receipt": "REC",
    }
    prefix = prefix_map.get(kind.lower(), "DOC")
    year = datetime.now().year
    rand_seq = f"{int(datetime.now().strftime('%m%d%H%M')) % 9000 + 1000}"
    return f"{prefix}-{year}-{rand_seq}"


def get_all_documents(kind: str = "", status: str = "") -> list[dict]:
    """Fetch all documents, optionally filtered by kind and status."""
    _init_default_documents()
    if has_supabase():
        client = get_service_client()
        if client:
            try:
                query = client.table("documents").select("*, document_items(*)")
                if kind and kind != "all":
                    query = query.eq("kind", kind)
                if status and status != "all":
                    query = query.eq("status", status)
                result = query.order("created_at", desc=True).execute()
                return getattr(result, "data", []) or []
            except Exception as e:
                print(f"Supabase fetch documents fallback: {e}")

    docs = list(_LOCAL_DOCUMENTS.values())
    if kind and kind != "all":
        docs = [d for d in docs if d.get("kind") == kind]
    if status and status != "all":
        docs = [d for d in docs if d.get("status") == status]
    return sorted(docs, key=lambda d: d.get("created_at", ""), reverse=True)


def get_document_by_id(doc_id: str) -> dict | None:
    """Fetch a single document with its items by ID."""
    _init_default_documents()
    if has_supabase():
        client = get_service_client()
        if client:
            try:
                result = client.table("documents").select("*, document_items(*)").eq("id", doc_id).execute()
                rows = getattr(result, "data", [])
                if rows:
                    return rows[0]
            except Exception:
                pass

    return _LOCAL_DOCUMENTS.get(doc_id)


def get_document_by_token(token: str) -> dict | None:
    """Fetch document for client portal by access token."""
    _init_default_documents()
    if has_supabase():
        client = get_service_client()
        if client:
            try:
                result = client.table("documents").select("*, document_items(*)").eq("access_token", token).execute()
                rows = getattr(result, "data", [])
                if rows:
                    return rows[0]
            except Exception:
                pass

    for d in _LOCAL_DOCUMENTS.values():
        if d.get("access_token") == token:
            return d
    return None



def record_document_view(token: str) -> dict | None:
    """Track client visits to document portal."""
    doc = get_document_by_token(token)
    if not doc:
        return None

    views = int(doc.get("view_count") or 0) + 1
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    doc["view_count"] = views
    doc["viewed_at"] = now_str
    if doc.get("status") in ["draft", "sent"]:
        doc["status"] = "viewed"

    if has_supabase():
        client = get_service_client()
        if client:
            try:
                update_data = {
                    "view_count": views,
                    "viewed_at": now_str,
                }
                if doc.get("status") == "viewed":
                    update_data["status"] = "viewed"
                client.table("documents").update(update_data).eq("id", doc["id"]).execute()
            except Exception:
                pass
    return doc


def record_client_decision(token: str, decision: str, notes: str = "") -> dict | None:
    """Record client acceptance, rejection, or revision request."""
    doc = get_document_by_token(token)
    if not doc:
        return None

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    norm_decision = decision.lower().strip()
    if norm_decision in {"accepted", "approved"}:
        new_status = "accepted"
    elif norm_decision in {"declined", "rejected"}:
        new_status = "declined"
    else:
        new_status = "revision_requested"

    doc["client_decision"] = norm_decision
    doc["client_decision_at"] = now_str
    doc["client_notes"] = notes
    doc["status"] = new_status


    if has_supabase():
        client = get_service_client()
        if client:
            try:
                update_data = {
                    "client_decision": decision,
                    "client_decision_at": now_str,
                    "client_notes": notes,
                    "status": new_status,
                }
                client.table("documents").update(update_data).eq("id", doc["id"]).execute()
            except Exception:
                pass
    return doc


def add_document_comment(token: str, author_name: str, message: str) -> dict | None:
    """Add a question or comment to the document thread."""
    doc = get_document_by_token(token)
    if not doc:
        return None

    comments = doc.get("comments") or []
    if isinstance(comments, str):
        import json
        try: comments = json.loads(comments)
        except Exception: comments = []

    new_entry = {
        "id": str(uuid.uuid4())[:8],
        "author": author_name.strip() or "Client",
        "message": message.strip(),
        "created_at": datetime.now().strftime("%b %d, %Y %I:%M %p"),
    }
    comments.append(new_entry)
    doc["comments"] = comments

    if has_supabase():
        client = get_service_client()
        if client:
            try:
                client.table("documents").update({"comments": comments}).eq("id", doc["id"]).execute()
            except Exception:
                pass
    return doc


def record_client_payment_claim(token: str, payment_method: str = "Bank Transfer", payment_reference: str = "", notes: str = "") -> dict | None:
    """Record that client submitted a payment confirmation claim on their invoice."""
    doc = get_document_by_token(token)
    if not doc:
        return None

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    doc["payment_claimed"] = True
    doc["payment_method"] = payment_method
    doc["payment_reference"] = payment_reference
    doc["client_notes"] = f"Payment confirmation claimed on {now_str}. Ref: {payment_reference}. Notes: {notes}"
    doc["status"] = "payment_pending"

    if has_supabase():
        client = get_service_client()
        if client:
            try:
                update_data = {
                    "payment_claimed": True,
                    "payment_method": payment_method,
                    "payment_reference": payment_reference,
                    "client_notes": doc["client_notes"],
                    "status": "payment_pending",
                }
                client.table("documents").update(update_data).eq("id", doc["id"]).execute()
            except Exception:
                pass
    return doc


def convert_invoice_to_receipt(invoice_id: str, amount_paid: float | None = None, payment_method: str = "Bank Transfer", payment_reference: str = "") -> dict | None:
    """Generate an official receipt from a confirmed invoice and mark invoice as paid."""
    invoice = get_document_by_id(invoice_id)
    if not invoice:
        return None

    tot = float(invoice.get("total_amount") or 0)
    paid = float(amount_paid) if amount_paid is not None else tot
    balance = max(0.0, tot - paid)
    now_str = datetime.now().strftime("%b %d, %Y")

    receipt_data = {
        "kind": "receipt",
        "document_number": generate_document_number("receipt"),
        "customer_name": invoice.get("customer_name", "Valued Client"),
        "customer_phone": invoice.get("customer_phone", ""),
        "customer_email": invoice.get("customer_email", ""),
        "title": f"Payment Receipt for {invoice.get('title', 'Interior Furnishing')}",
        "terms": "Thank you for your payment! Goods supplied and services rendered remain the high standard of SJ Interior Deco & Beddings.",
        "notes": f"Payment received via {payment_method}. Reference: {payment_reference or 'N/A'}. Date: {now_str}.",
        "status": "paid" if balance == 0 else "partially_paid",
        "total_amount": tot,
        "amount_paid": paid,
        "balance_due": balance,
        "payment_method": payment_method,
        "payment_reference": payment_reference,
        "payment_date": now_str,
        "related_invoice_id": invoice_id,
        "currency": invoice.get("currency", "NGN"),
    }

    # Extract invoice items
    items = invoice.get("document_items", []) or []
    receipt_items = [
        {
            "category_group": it.get("category_group", ""),
            "description": it.get("description", "Item"),
            "specification": it.get("specification", ""),
            "quantity": float(it.get("quantity", 1)),
            "unit_price": float(it.get("unit_price", 0)),
            "unit_label": it.get("unit_label", ""),
        }
        for it in items
    ]

    receipt = create_document(receipt_data, items=receipt_items)

    # Mark original invoice as paid
    update_document_status(invoice_id, "paid")
    return receipt


def create_document(doc_data: dict, items: list[dict] | None = None) -> dict | None:
    """Create a document and associated line items."""
    _init_default_documents()

    if not doc_data.get("document_number"):
        doc_data["document_number"] = generate_document_number(doc_data.get("kind", "proposal"))
    if not doc_data.get("access_token"):
        doc_data["access_token"] = str(uuid.uuid4())

    items = items or []
    total_amount = sum(float(it.get("quantity", 1)) * float(it.get("unit_price", 0)) for it in items)
    doc_data["total_amount"] = total_amount

    raw_id = doc_data.get("id")
    if not raw_id or raw_id.startswith("doc-"):
        doc_id = str(uuid.uuid4())
    else:
        doc_id = raw_id
    doc_data["id"] = doc_id
    doc_data["created_at"] = doc_data.get("created_at") or datetime.now().isoformat()
    doc_data["document_items"] = items
    doc_data.setdefault("view_count", 0)
    doc_data.setdefault("comments", [])

    # Save to local store
    _LOCAL_DOCUMENTS[doc_id] = doc_data

    # Save to Supabase if available
    if has_supabase():
        client = get_service_client()
        if client:
            try:
                db_data = {k: v for k, v in doc_data.items() if k != "document_items"}
                res = client.table("documents").insert(db_data).execute()
                rows = getattr(res, "data", [])
                if rows:
                    real_id = rows[0]["id"]
                    for idx, item in enumerate(items):
                        item_data = {
                            "document_id": real_id,
                            "description": item.get("description", "Item"),
                            "quantity": float(item.get("quantity", 1)),
                            "unit_price": float(item.get("unit_price", 0)),
                            "sort_order": idx + 1,
                            "category_group": item.get("category_group", ""),
                            "specification": item.get("specification", ""),
                            "unit_label": item.get("unit_label", ""),
                        }
                        client.table("document_items").insert(item_data).execute()
            except Exception as e:
                print(f"Supabase create document fallback: {e}")

    return _LOCAL_DOCUMENTS[doc_id]


def update_document(doc_id: str, doc_data: dict, items: list[dict] | None = None) -> dict | None:
    """Update document header and replace line items if provided."""
    _init_default_documents()
    existing = get_document_by_id(doc_id)
    if not existing:
        return create_document(doc_data, items=items)

    if items is not None:
        total_amount = sum(float(it.get("quantity", 1)) * float(it.get("unit_price", 0)) for it in items)
        doc_data["total_amount"] = total_amount
        existing["document_items"] = items

    for k, v in doc_data.items():
        existing[k] = v

    _LOCAL_DOCUMENTS[doc_id] = existing

    if has_supabase():
        client = get_service_client()
        if client:
            try:
                db_data = {k: v for k, v in doc_data.items() if k != "document_items"}
                client.table("documents").update(db_data).eq("id", doc_id).execute()
                if items is not None:
                    client.table("document_items").delete().eq("document_id", doc_id).execute()
                    for idx, item in enumerate(items):
                        item_data = {
                            "document_id": doc_id,
                            "description": item.get("description", "Item"),
                            "quantity": float(item.get("quantity", 1)),
                            "unit_price": float(item.get("unit_price", 0)),
                            "sort_order": idx + 1,
                            "category_group": item.get("category_group", ""),
                            "specification": item.get("specification", ""),
                            "unit_label": item.get("unit_label", ""),
                        }
                        client.table("document_items").insert(item_data).execute()
            except Exception as e:
                print(f"Supabase update document fallback: {e}")

    return _LOCAL_DOCUMENTS[doc_id]


def delete_document(doc_id: str) -> bool:
    """Delete a document and its cascade items."""
    _init_default_documents()
    if doc_id in _LOCAL_DOCUMENTS:
        del _LOCAL_DOCUMENTS[doc_id]

    if has_supabase():
        client = get_service_client()
        if client:
            try:
                client.table("documents").delete().eq("id", doc_id).execute()
            except Exception:
                pass
    return True


def update_document_status(doc_id: str, status: str) -> dict | None:
    """Quick update of document status."""
    _init_default_documents()
    doc = get_document_by_id(doc_id)
    if doc:
        doc["status"] = status
        _LOCAL_DOCUMENTS[doc_id] = doc

    if has_supabase():
        client = get_service_client()
        if client:
            try:
                client.table("documents").update({"status": status}).eq("id", doc_id).execute()
            except Exception:
                pass
    return doc


def get_official_sample_items() -> list[dict]:
    """Return default template line items matching the official SJ Interiors 6-category quotation sample."""
    return [

        # Division 1: SITTING ROOM CURTAINS (3 WINDOWS ESTIMATION)
        {"category_group": "1. SITTING ROOM CURTAINS (3 WINDOWS ESTIMATION)", "description": "Yards of Curtain", "specification": "18 Yards total @ ₦5,000 per yard", "quantity": 18, "unit_price": 5000, "unit_label": "₦5,000.00"},
        {"category_group": "1. SITTING ROOM CURTAINS (3 WINDOWS ESTIMATION)", "description": "Yards of Tape", "specification": "Curtain Pleating Tape (18 Yards @ ₦300/yd)", "quantity": 18, "unit_price": 300, "unit_label": "₦300.00"},
        {"category_group": "1. SITTING ROOM CURTAINS (3 WINDOWS ESTIMATION)", "description": "Yards of Inner Sheer", "specification": "Inner Sheer Fabric (9 Yards @ ₦2,100/yd)", "quantity": 9, "unit_price": 2100, "unit_label": "₦2,100.00"},
        {"category_group": "1. SITTING ROOM CURTAINS (3 WINDOWS ESTIMATION)", "description": "Bronze Pole", "specification": "Heavy Duty Bronze Rods (2 Units @ ₦13,500/unit)", "quantity": 2, "unit_price": 13500, "unit_label": "₦13,500.00"},
        {"category_group": "1. SITTING ROOM CURTAINS (3 WINDOWS ESTIMATION)", "description": "Extra Accessories", "specification": "Finials, Brackets & Wall Hardware (4 Sets @ ₦6,500/set)", "quantity": 4, "unit_price": 6500, "unit_label": "₦6,500.00"},
        {"category_group": "1. SITTING ROOM CURTAINS (3 WINDOWS ESTIMATION)", "description": "Pairs of Tie Back", "specification": "Decorative Holdbacks (3 Pairs @ ₦10,000/pair)", "quantity": 3, "unit_price": 10000, "unit_label": "₦10,000.00"},
        {"category_group": "1. SITTING ROOM CURTAINS (3 WINDOWS ESTIMATION)", "description": "Black Pole", "specification": "Secondary Black Curtain Pole (1.5 Rods @ ₦3,000/rod)", "quantity": 1.5, "unit_price": 3000, "unit_label": "₦3,000.00"},
        {"category_group": "1. SITTING ROOM CURTAINS (3 WINDOWS ESTIMATION)", "description": "Sewing & Tailoring", "specification": "Custom Stitching & Finishing Workmanship", "quantity": 1, "unit_price": 14000, "unit_label": "₦14,000.00"},

        # Division 2: BEDROOM CURTAINS
        {"category_group": "2. BEDROOM CURTAINS", "description": "Yards of Curtain", "specification": "Bedroom Curtain Fabric (24 Yards @ ₦3,500/yd)", "quantity": 24, "unit_price": 3500, "unit_label": "₦3,500.00"},
        {"category_group": "2. BEDROOM CURTAINS", "description": "Yards of Tape", "specification": "Bedroom Curtain Tape (24 Yards @ ₦300/yd)", "quantity": 24, "unit_price": 300, "unit_label": "₦300.00"},
        {"category_group": "2. BEDROOM CURTAINS", "description": "Curtain Rings", "specification": "Eyelet / Pole Rings (144 Pieces @ ₦130/pc)", "quantity": 144, "unit_price": 130, "unit_label": "₦130.00"},
        {"category_group": "2. BEDROOM CURTAINS", "description": "Inner Sheer Fabric", "specification": "Inner Lining Sheer (10 Yards @ ₦2,100/yd)", "quantity": 10, "unit_price": 2100, "unit_label": "₦2,100.00"},
        {"category_group": "2. BEDROOM CURTAINS", "description": "Black Pole", "specification": "Curtain Rods for Bedrooms (4 Units @ ₦3,000/unit)", "quantity": 4, "unit_price": 3000, "unit_label": "₦3,000.00"},
        {"category_group": "2. BEDROOM CURTAINS", "description": "Tie Backs", "specification": "Curtain Tie Backs (4 Pairs @ ₦10,000/pair)", "quantity": 4, "unit_price": 10000, "unit_label": "₦10,000.00"},
        {"category_group": "2. BEDROOM CURTAINS", "description": "Sewing & Tailoring", "specification": "Custom Bedroom Sewing Workmanship", "quantity": 1, "unit_price": 7000, "unit_label": "₦7,000.00"},

        # Division 3: INTERIOR DECOR & BLINDS
        {"category_group": "3. INTERIOR DECOR & BLINDS", "description": "Kitchen Window Blind", "specification": "Window Blind Fitting for Kitchen (1 Window)", "quantity": 1, "unit_price": 26000, "unit_label": "₦26,000.00"},
        {"category_group": "3. INTERIOR DECOR & BLINDS", "description": "Wall Frames", "specification": "Decorative Wall Art Framing Set", "quantity": 1, "unit_price": 50000, "unit_label": "₦50,000.00"},
        {"category_group": "3. INTERIOR DECOR & BLINDS", "description": "Chandeliers (2 Units)", "specification": "Living Room (₦40,000) + Dining Room (₦52,000)", "quantity": 2, "unit_price": 46000, "unit_label": "Var."},
        {"category_group": "3. INTERIOR DECOR & BLINDS", "description": "Indoor Decorative Plants", "specification": "Potted Plants (₦65,000 + ₦60,000 + ₦69,000)", "quantity": 3, "unit_price": 64666.67, "unit_label": "Var."},
        {"category_group": "3. INTERIOR DECOR & BLINDS", "description": "Decorative Wall Mirrors", "specification": "Wall Mirrors (₦25,000 + ₦35,000)", "quantity": 2, "unit_price": 30000, "unit_label": "Var."},
        {"category_group": "3. INTERIOR DECOR & BLINDS", "description": "Welcome Doormat", "specification": "Main Entrance Floor Mat", "quantity": 1, "unit_price": 15000, "unit_label": "₦15,000.00"},
        {"category_group": "3. INTERIOR DECOR & BLINDS", "description": "Room Mat", "specification": "Bedroom Accent Floor Mat", "quantity": 1, "unit_price": 14000, "unit_label": "₦14,000.00"},

        # Division 4: BEDROOM & BEDDING
        {"category_group": "4. BEDROOM & BEDDING", "description": "Mattress (6x6 Bed Size)", "specification": "King Size High-Density Mattress", "quantity": 1, "unit_price": 155000, "unit_label": "₦155,000.00"},
        {"category_group": "4. BEDROOM & BEDDING", "description": "Mattress (4x6 Bed Size)", "specification": "Double Size High-Density Mattress", "quantity": 1, "unit_price": 95000, "unit_label": "₦95,000.00"},
        {"category_group": "4. BEDROOM & BEDDING", "description": "Bedsheets (6x6 Bed Size)", "specification": "2 Sets @ ₦8,500 each", "quantity": 2, "unit_price": 8500, "unit_label": "₦8,500.00"},
        {"category_group": "4. BEDROOM & BEDDING", "description": "Bedsheets (4x6 Bed Size)", "specification": "2 Sets @ ₦7,000 each", "quantity": 2, "unit_price": 7000, "unit_label": "₦7,000.00"},
        {"category_group": "4. BEDROOM & BEDDING", "description": "White Duvet Set (6x6)", "specification": "6x6 King Size Luxury White Duvet Set", "quantity": 1, "unit_price": 35000, "unit_label": "₦35,000.00"},
        {"category_group": "4. BEDROOM & BEDDING", "description": "White Duvet Set (4x6)", "specification": "4x6 Double Size Luxury White Duvet Set", "quantity": 1, "unit_price": 30000, "unit_label": "₦30,000.00"},
        {"category_group": "4. BEDROOM & BEDDING", "description": "Duvet Set (6x6)", "specification": "6x6 King Size Patterned Duvet Set", "quantity": 1, "unit_price": 25000, "unit_label": "₦25,000.00"},
        {"category_group": "4. BEDROOM & BEDDING", "description": "Duvet Set (4x6)", "specification": "4x6 Double Size Patterned Duvet Set", "quantity": 1, "unit_price": 21000, "unit_label": "₦21,000.00"},
        {"category_group": "4. BEDROOM & BEDDING", "description": "Pillows", "specification": "Standard Comfort Pillows (4 Units @ ₦4,000/pillow)", "quantity": 4, "unit_price": 4000, "unit_label": "₦4,000.00"},

        # Division 5: KITCHENWARE & UTENSILS
        {"category_group": "5. KITCHENWARE & UTENSILS", "description": "Non-Stick Pot Set", "specification": "Premium Non-Stick Cookware Set", "quantity": 1, "unit_price": 160000, "unit_label": "₦160,000.00"},
        {"category_group": "5. KITCHENWARE & UTENSILS", "description": "Burner Stove", "specification": "Kitchen Burner Appliance", "quantity": 1, "unit_price": 160000, "unit_label": "₦160,000.00"},
        {"category_group": "5. KITCHENWARE & UTENSILS", "description": "Silver Spoon Set", "specification": "Complete Cutlery Set", "quantity": 1, "unit_price": 43000, "unit_label": "₦43,000.00"},
        {"category_group": "5. KITCHENWARE & UTENSILS", "description": "Serving Tray", "specification": "Kitchen Serving Tray", "quantity": 1, "unit_price": 9000, "unit_label": "₦9,000.00"},
        {"category_group": "5. KITCHENWARE & UTENSILS", "description": "Trash Can", "specification": "Kitchen Waste Bin", "quantity": 1, "unit_price": 60000, "unit_label": "₦60,000.00"},
        {"category_group": "5. KITCHENWARE & UTENSILS", "description": "Wine Glass Set (A)", "specification": "Glassware Set 1", "quantity": 1, "unit_price": 25000, "unit_label": "₦25,000.00"},
        {"category_group": "5. KITCHENWARE & UTENSILS", "description": "Water Glass Set", "specification": "Drinking Glassware Set", "quantity": 1, "unit_price": 23000, "unit_label": "₦23,000.00"},
        {"category_group": "5. KITCHENWARE & UTENSILS", "description": "Wine Glass Set (B)", "specification": "Glassware Set 2", "quantity": 1, "unit_price": 18000, "unit_label": "₦18,000.00"},
        {"category_group": "5. KITCHENWARE & UTENSILS", "description": "Set of Plates", "specification": "Complete Dinnerware Plate Set", "quantity": 1, "unit_price": 47000, "unit_label": "₦47,000.00"},
        {"category_group": "5. KITCHENWARE & UTENSILS", "description": "Kitchen Spoon & Knife Set", "specification": "Chef Utensil Set", "quantity": 1, "unit_price": 35000, "unit_label": "₦35,000.00"},
        {"category_group": "5. KITCHENWARE & UTENSILS", "description": "Water Dispenser", "specification": "Freestanding Water Dispenser", "quantity": 1, "unit_price": 160000, "unit_label": "₦160,000.00"},
        {"category_group": "5. KITCHENWARE & UTENSILS", "description": "Water Heater", "specification": "Kitchen Water Heater Unit", "quantity": 1, "unit_price": 40000, "unit_label": "₦40,000.00"},
        {"category_group": "5. KITCHENWARE & UTENSILS", "description": "Plate Rack", "specification": "Dish Drying & Storage Rack", "quantity": 1, "unit_price": 55000, "unit_label": "₦55,000.00"},
        {"category_group": "5. KITCHENWARE & UTENSILS", "description": "Kitchen Floor Mat", "specification": "Anti-Slip Mat", "quantity": 1, "unit_price": 12000, "unit_label": "₦12,000.00"},

        # Division 6: LOGISTICS & WORKMANSHIP
        {"category_group": "6. LOGISTICS & WORKMANSHIP", "description": "Logistics & Delivery", "specification": "Transportation & Delivery Fee", "quantity": 1, "unit_price": 20000, "unit_label": "₦20,000.00"},
        {"category_group": "6. LOGISTICS & WORKMANSHIP", "description": "Workmanship & Installation", "specification": "Assembly, Fitting & Installation Labor", "quantity": 1, "unit_price": 20000, "unit_label": "₦20,000.00"},
    ]

