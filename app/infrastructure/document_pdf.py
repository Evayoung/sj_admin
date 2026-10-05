"""Branded PDF generator for SJ Interiors official proposals, quotations, invoices, and receipts.

Adopts corporate Nigerian proforma/invoice design standard:
- Top header with brand left and uppercase doc type/reference/date right
- Solid brand accent divider line
- Translucent watermark
- Two-column BILLED TO & SERVICE REQUESTED block
- Dark brand header itemized table
- Highlighted ESTIMATED INVESTMENT banner
- Project description block
- Terms & notes with professional sign-off
- Corporate footer with registration and page numbers
"""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

BASE_DIR = Path(__file__).resolve().parents[2]
OUTPUT_DIR = Path("/tmp") if os.getenv("VERCEL") else BASE_DIR / "assets" / "generated"

# Brand Color Palette
PLUM = colors.HexColor("#6b1d49")
PLUM_DARK = colors.HexColor("#4a1232")
PLUM_LIGHT = colors.HexColor("#fbf5f8")
PLUM_ACCENT = colors.HexColor("#8a2760")
GOLD = colors.HexColor("#b87d28")
GOLD_LIGHT = colors.HexColor("#fff9ee")

GREEN = colors.HexColor("#1a7a3b")
GREEN_DARK = colors.HexColor("#125428")
GREEN_LIGHT = colors.HexColor("#f0fdf4")
GREEN_LINE = colors.HexColor("#ccebd7")

TEXT_DARK = colors.HexColor("#1e293b")
TEXT_MUTED = colors.HexColor("#64748b")
LINE_COLOR = colors.HexColor("#e2e8f0")
WHITE = colors.white


def _money(val: float | int | str) -> str:
    try:
        f = float(val or 0)
        return f"NGN {f:,.2f}"
    except (ValueError, TypeError):
        return "NGN 0.00"


def _styles(is_receipt: bool = False) -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    primary = GREEN if is_receipt else PLUM
    return {
        "header_title": ParagraphStyle("DocHdrTitle", parent=base["Heading1"], fontName="Helvetica-Bold", fontSize=16, leading=19, textColor=primary, alignment=0),
        "header_sub": ParagraphStyle("DocHdrSub", parent=base["BodyText"], fontName="Helvetica-Bold", fontSize=9, leading=11, textColor=primary, alignment=0),
        "header_tagline": ParagraphStyle("DocHdrTagline", parent=base["BodyText"], fontName="Helvetica-Bold", fontSize=6.5, leading=8.5, textColor=GOLD, alignment=0),
        
        "doc_type_title": ParagraphStyle("DocTypeTitle", parent=base["Heading1"], fontName="Helvetica-Bold", fontSize=15, leading=18, textColor=TEXT_DARK, alignment=2),
        "ref_label": ParagraphStyle("DocRefLbl", parent=base["BodyText"], fontName="Helvetica-Bold", fontSize=7, leading=9, textColor=TEXT_MUTED, alignment=2),
        "ref_val": ParagraphStyle("DocRefVal", parent=base["BodyText"], fontName="Helvetica-Bold", fontSize=9, leading=11, textColor=TEXT_DARK, alignment=2),
        "date_val": ParagraphStyle("DocDateVal", parent=base["BodyText"], fontName="Helvetica", fontSize=8, leading=10, textColor=TEXT_DARK, alignment=2),
        
        "meta_kicker": ParagraphStyle("DocMetaKicker", parent=base["BodyText"], fontName="Helvetica-Bold", fontSize=7.5, leading=10, textColor=primary),
        "meta_title": ParagraphStyle("DocMetaTitle", parent=base["BodyText"], fontName="Helvetica-Bold", fontSize=9.5, leading=12, textColor=TEXT_DARK),
        "meta_body": ParagraphStyle("DocMetaBody", parent=base["BodyText"], fontName="Helvetica", fontSize=7.8, leading=10.5, textColor=TEXT_MUTED),
        
        "table_hdr": ParagraphStyle("DocTblHdr", parent=base["BodyText"], fontName="Helvetica-Bold", fontSize=7.5, leading=9.5, textColor=WHITE),
        "table_hdr_right": ParagraphStyle("DocTblHdrR", parent=base["BodyText"], fontName="Helvetica-Bold", fontSize=7.5, leading=9.5, textColor=WHITE, alignment=2),
        "group_hdr": ParagraphStyle("DocGrpHdr", parent=base["BodyText"], fontName="Helvetica-Bold", fontSize=8, leading=10, textColor=primary),
        
        "item_desc": ParagraphStyle("DocItemDesc", parent=base["BodyText"], fontName="Helvetica-Bold", fontSize=8, leading=10.5, textColor=TEXT_DARK),
        "item_spec": ParagraphStyle("DocItemSpec", parent=base["BodyText"], fontName="Helvetica", fontSize=7.2, leading=9.5, textColor=TEXT_MUTED),
        "item_right": ParagraphStyle("DocItemRight", parent=base["BodyText"], fontName="Helvetica-Bold", fontSize=8, leading=10, textColor=TEXT_DARK, alignment=2),
        
        "total_banner_lbl": ParagraphStyle("DocTotLbl", parent=base["BodyText"], fontName="Helvetica-Bold", fontSize=8.5, leading=11, textColor=primary),
        "total_banner_val": ParagraphStyle("DocTotVal", parent=base["BodyText"], fontName="Helvetica-Bold", fontSize=12, leading=15, textColor=TEXT_DARK, alignment=2),
        
        "section_head": ParagraphStyle("DocSecHead", parent=base["Heading2"], fontName="Helvetica-Bold", fontSize=8, leading=10.5, textColor=TEXT_DARK),
        "desc_box": ParagraphStyle("DocDescBox", parent=base["BodyText"], fontName="Helvetica", fontSize=7.8, leading=11, textColor=TEXT_DARK),
        "terms_bullet": ParagraphStyle("DocTermsBullet", parent=base["BodyText"], fontName="Helvetica", fontSize=7.3, leading=10, textColor=TEXT_MUTED),
        "closing": ParagraphStyle("DocClosing", parent=base["BodyText"], fontName="Helvetica-Bold", fontSize=8, leading=10.5, textColor=TEXT_DARK),
    }


def _watermark_text(kind: str, status: str) -> str:
    if status in {"accepted", "paid"} or kind == "receipt":
        return "PAID"
    if kind == "quotation":
        return "PROFORMA"
    if kind == "invoice":
        return "INVOICE"
    return "OFFICIAL"


def _page_decorations(canvas, doc, is_receipt: bool = False, watermark: str | None = None):
    canvas.saveState()
    # Watermark
    if watermark:
        canvas.setFont("Helvetica-Bold", 46)
        canvas.setFillColor(colors.HexColor("#f8fafc" if not is_receipt else "#f0fdf4"))
        canvas.translate(A4[0] / 2, A4[1] / 2)
        canvas.rotate(32)
        canvas.drawCentredString(0, 0, watermark)
        canvas.rotate(-32)
        canvas.translate(-A4[0] / 2, -A4[1] / 2)

    # Bottom footer line & corporate details
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(TEXT_MUTED)
    footer_text = "SJ Interior Deco and Beddings · Limca Junction Shopping Complex, Along Asa Dam Road, Ilorin, Kwara State · RC 9711335"
    canvas.drawString(12 * mm, 8 * mm, footer_text)
    canvas.drawRightString(A4[0] - 12 * mm, 8 * mm, f"Page {doc.page} of 1")
    canvas.restoreState()


def build_document_pdf(doc: dict, brand_config: dict | None = None) -> Path:
    """Generate pixel-perfect official branded PDF matching sample invoice layout."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    kind = (doc.get("kind") or "quotation").lower()
    is_receipt = kind == "receipt"
    doc_num = doc.get("document_number") or "SJ-DOC-2026-001"
    output_path = OUTPUT_DIR / f"{doc_num}.pdf"

    primary_color = GREEN if is_receipt else PLUM
    tint_bg = GREEN_LIGHT if is_receipt else PLUM_LIGHT

    styles = _styles(is_receipt)
    pdf_doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=12 * mm,
        rightMargin=12 * mm,
        topMargin=10 * mm,
        bottomMargin=14 * mm,
    )

    story = []

    # 1. Top Header Lockup (Left Brand, Right Doc Type & Ref)
    kind_titles = {
        "quotation": "PROFORMA INVOICE",
        "proposal": "PROJECT PROPOSAL",
        "invoice": "OFFICIAL INVOICE",
        "receipt": "OFFICIAL PAYMENT RECEIPT",
    }
    doc_title = kind_titles.get(kind, "OFFICIAL DOCUMENT")
    doc_date = doc.get("created_at", "")[:10] or datetime.now().strftime("%Y-%m-%d")

    header_data = [
        [
            [
                Paragraph("SJ Interiors", styles["header_title"]),
                Paragraph("Deco and Beddings", styles["header_sub"]),
                Paragraph("REDEFINING YOUR SPACE • SIMPLICITY. COMFORT. STYLE.", styles["header_tagline"]),
            ],
            [
                Paragraph(doc_title, styles["doc_type_title"]),
                Paragraph("REFERENCE", styles["ref_label"]),
                Paragraph(doc_num, styles["ref_val"]),
                Paragraph("DATE ISSUED", styles["ref_label"]),
                Paragraph(doc_date, styles["date_val"]),
            ],
        ]
    ]
    header_table = Table(header_data, colWidths=[95 * mm, 91 * mm])
    header_table.setStyle(
        TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ])
    )
    story.append(header_table)

    # Solid accent divider line (matching sample PDF)
    accent_bar = Table([[""]], colWidths=[186 * mm], rowHeights=[2.5 * mm])
    accent_bar.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), primary_color),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ])
    )
    story.append(accent_bar)
    story.append(Spacer(1, 4 * mm))

    # 2. Two-Column Metadata Block (BILLED TO & SERVICE REQUESTED)
    cust_name = doc.get("customer_name") or "Valued Client"
    cust_phone = doc.get("customer_phone") or "N/A"
    cust_email = doc.get("customer_email") or "client@example.com"
    project_title = doc.get("title") or "Window Dressing & Full Interior Furnishing"
    validity_note = "Valid for 14 days from date issued" if not is_receipt else f"Payment acknowledged via {doc.get('payment_method', 'Bank Transfer')}"

    meta_data = [
        [
            [
                Paragraph("BILLED TO", styles["meta_kicker"]),
                Paragraph(cust_name, styles["meta_title"]),
                Paragraph(cust_email, styles["meta_body"]),
                Paragraph(cust_phone, styles["meta_body"]),
            ],
            [
                Paragraph("SERVICE REQUESTED", styles["meta_kicker"]),
                Paragraph(project_title, styles["meta_title"]),
                Paragraph(validity_note, styles["meta_body"]),
            ],
        ]
    ]
    meta_table = Table(meta_data, colWidths=[93 * mm, 93 * mm])
    meta_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ("BOX", (0, 0), (-1, -1), 0.5, LINE_COLOR),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, LINE_COLOR),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ])
    )
    story.append(meta_table)
    story.append(Spacer(1, 4 * mm))

    # 3. Categorized Line Items Table
    raw_items = doc.get("document_items", []) or []
    groups: dict[str, list[dict]] = {}
    for it in raw_items:
        grp = it.get("category_group") or "1. GENERAL FURNISHING & SERVICES"
        if grp not in groups:
            groups[grp] = []
        groups[grp].append(it)

    table_data = [
        [
            Paragraph("ITEM", styles["table_hdr"]),
            Paragraph("DETAILS", styles["table_hdr"]),
            Paragraph("AMOUNT", styles["table_hdr_right"]),
        ]
    ]

    grand_total = 0.0
    for grp_name, items in groups.items():
        table_data.append([
            Paragraph(grp_name.upper(), styles["group_hdr"]),
            Paragraph("", styles["group_hdr"]),
            Paragraph("", styles["group_hdr"]),
        ])
        for it in items:
            desc = it.get("description") or "Item"
            spec = it.get("specification") or ""
            qty = float(it.get("quantity") or 1)
            price = float(it.get("unit_price") or 0)
            line_tot = qty * price
            grand_total += line_tot

            details_p = [Paragraph(desc, styles["item_desc"])]
            if spec:
                details_p.append(Paragraph(spec, styles["item_spec"]))

            table_data.append([
                Paragraph(desc, styles["item_desc"]),
                details_p,
                Paragraph(_money(line_tot), styles["item_right"]),
            ])

    if len(table_data) == 1:
        # Fallback single line item if empty
        grand_total = float(doc.get("total_amount") or 0)
        table_data.append([
            Paragraph(project_title, styles["item_desc"]),
            Paragraph("Comprehensive interior decor & furnishing package", styles["item_spec"]),
            Paragraph(_money(grand_total), styles["item_right"]),
        ])

    items_table = Table(table_data, colWidths=[55 * mm, 85 * mm, 46 * mm])
    table_style_list = [
        ("BACKGROUND", (0, 0), (-1, 0), primary_color),
        ("BOX", (0, 0), (-1, -1), 0.5, LINE_COLOR),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, LINE_COLOR),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]
    items_table.setStyle(TableStyle(table_style_list))
    story.append(items_table)
    story.append(Spacer(1, 4 * mm))

    # 4. Highlighted Investment Banner
    inv_label = "ESTIMATED INVESTMENT" if kind in {"quotation", "proposal"} else ("TOTAL AMOUNT" if kind == "invoice" else "TOTAL PAYMENT RECEIVED")
    investment_data = [
        [
            Paragraph(inv_label, styles["total_banner_lbl"]),
            Paragraph(_money(grand_total), styles["total_banner_val"]),
        ]
    ]
    investment_table = Table(investment_data, colWidths=[93 * mm, 93 * mm])
    investment_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), tint_bg),
            ("BOX", (0, 0), (-1, -1), 1, primary_color),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ])
    )
    story.append(investment_table)
    story.append(Spacer(1, 4 * mm))

    # 5. Project Description Box (matching sample PDF)
    notes_text = doc.get("notes") or project_title
    desc_data = [
        [Paragraph("PROJECT DESCRIPTION", styles["section_head"])],
        [Paragraph(notes_text, styles["desc_box"])],
    ]
    desc_table = Table(desc_data, colWidths=[186 * mm])
    desc_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ("BOX", (0, 0), (-1, -1), 0.5, LINE_COLOR),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ])
    )
    story.append(desc_table)
    story.append(Spacer(1, 4 * mm))

    # 6. Terms & Notes with Sign-off (matching sample PDF)
    terms_elements = [
        Paragraph("TERMS & NOTES", styles["section_head"]),
        Paragraph("• This is an official project estimate based on the enquiry and specifications selected above.", styles["terms_bullet"]),
        Paragraph("• 70% commitment deposit required before fabric procurement and tailoring commences; balance due upon delivery.", styles["terms_bullet"]) if not is_receipt else Paragraph("• Payment received with thanks! Official receipt acknowledges fulfillment.", styles["terms_bullet"]),
        Paragraph("• Official Account: <b>Guaranty Trust Bank (GTBank) • 08026022672 • SJ Interior Deco and Beddings</b>", styles["terms_bullet"]),
        Paragraph("• This document is valid for 14 calendar days from the date issued above.", styles["terms_bullet"]),
        Spacer(1, 2 * mm),
        Paragraph("<b>Thank you for reaching out to SJ Interiors.</b>", styles["closing"]),
    ]
    story.append(KeepTogether(terms_elements))

    # Build PDF
    watermark_label = _watermark_text(kind, doc.get("status", "sent"))
    pdf_doc.build(
        story,
        onFirstPage=lambda c, d: _page_decorations(c, d, is_receipt=is_receipt, watermark=watermark_label),
        onLaterPages=lambda c, d: _page_decorations(c, d, is_receipt=is_receipt, watermark=watermark_label),
    )
    return output_path
