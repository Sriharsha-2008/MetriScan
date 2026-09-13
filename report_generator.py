"""MATRIScan PDF compliance report generator.

Generates a professional PDF from the existing OCR product data and the
existing compliance_engine.evaluate_compliance() result.
"""

from pathlib import Path
from datetime import datetime
from xml.sax.saxutils import escape
import hashlib

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, KeepTogether
)
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics


def _safe(value):
    if value is None or str(value).strip() == "":
        return "Not detected"
    return str(value)


def _status_label(status):
    return {
        "PASS": "PASS",
        "NON_COMPLIANT": "FAIL",
        "MANUAL_REVIEW": "NEEDS VERIFICATION",
        "NOT_APPLICABLE": "NOT APPLICABLE",
    }.get(str(status).upper(), str(status).upper() or "NEEDS VERIFICATION")


def _status_color(status):
    s = str(status).upper()
    if s == "PASS":
        return colors.HexColor("#16803A")
    if s == "NON_COMPLIANT":
        return colors.HexColor("#C62828")
    if s == "NOT_APPLICABLE":
        return colors.HexColor("#666666")
    return colors.HexColor("#C77700")


def _para(text, style):
    return Paragraph(escape(_safe(text)).replace("\n", "<br/>"), style)


def generate_compliance_report(
    image_path,
    product,
    declarations,
    compliance,
    ocr_records=None,
    output_path=None,
):
    """Create the PDF report and return its Path."""

    image_path = Path(image_path)
    ocr_records = ocr_records or []

    if output_path is None:
        output_path = Path("reports") / f"{image_path.stem}_compliance_report.pdf"
    else:
        output_path = Path(output_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    report_id = hashlib.sha1(
        f"{image_path.resolve()}|{datetime.now().isoformat()}".encode()
    ).hexdigest()[:10].upper()

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=14 * mm,
        leftMargin=14 * mm,
        topMargin=14 * mm,
        bottomMargin=14 * mm,
        title=f"MATRIScan Compliance Report - {image_path.stem}",
        author="MATRIScan",
    )

    styles = getSampleStyleSheet()
    title = ParagraphStyle(
        "MTitle", parent=styles["Title"], fontSize=22, leading=26,
        alignment=TA_CENTER, spaceAfter=3, textColor=colors.HexColor("#123B78")
    )
    subtitle = ParagraphStyle(
        "MSub", parent=styles["Normal"], fontSize=10, leading=14,
        alignment=TA_CENTER, textColor=colors.HexColor("#555555"), spaceAfter=10
    )
    h1 = ParagraphStyle(
        "MH1", parent=styles["Heading2"], fontSize=13, leading=16,
        textColor=colors.HexColor("#123B78"), spaceBefore=8, spaceAfter=6
    )
    body = ParagraphStyle(
        "MBody", parent=styles["BodyText"], fontSize=8.5, leading=11
    )
    small = ParagraphStyle(
        "MSmall", parent=body, fontSize=7.5, leading=9
    )
    tiny = ParagraphStyle(
        "MTiny", parent=body, fontSize=6.8, leading=8
    )
    center = ParagraphStyle(
        "MCenter", parent=small, alignment=TA_CENTER
    )

    story = []

    # Header
    story.append(Paragraph("MATRIScan", title))
    story.append(Paragraph(
        "Packaged Commodity Legal Metrology Compliance Report", subtitle
    ))

    meta = [
        [_para("Report ID", small), _para(report_id, small),
         _para("Report Date", small),
         _para(datetime.now().strftime("%d-%m-%Y %H:%M"), small)],
    ]
    meta_t = Table(meta, colWidths=[24*mm, 54*mm, 24*mm, 54*mm])
    meta_t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (0,-1), colors.HexColor("#EAF1FB")),
        ("BACKGROUND", (2,0), (2,-1), colors.HexColor("#EAF1FB")),
        ("GRID", (0,0), (-1,-1), 0.4, colors.HexColor("#C8D4E6")),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
        ("RIGHTPADDING", (0,0), (-1,-1), 6),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ]))
    story.append(meta_t)
    story.append(Spacer(1, 6))

    # Overall status
    overall = str(compliance.get("overall_status", "MANUAL_REVIEW"))
    overall_display = _status_label(overall)
    counts = compliance.get("counts", {}) or {}
    status_text = (
        f"Overall Assessment: {overall_display}    |    "
        f"PASS: {counts.get('PASS', 0)}    "
        f"FAIL: {counts.get('NON_COMPLIANT', 0)}    "
        f"NEEDS VERIFICATION: {counts.get('MANUAL_REVIEW', 0)}    "
        f"N/A: {counts.get('NOT_APPLICABLE', 0)}"
    )
    status_t = Table([[Paragraph(escape(status_text), body)]], colWidths=[156*mm])
    status_t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), _status_color(overall)),
        ("TEXTCOLOR", (0,0), (-1,-1), colors.white),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("BOX", (0,0), (-1,-1), 0.7, _status_color(overall)),
        ("TOPPADDING", (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
    ]))
    story.append(status_t)

    # Product image
    if image_path.exists():
        try:
            img = Image(str(image_path))
            max_w, max_h = 62*mm, 58*mm
            scale = min(max_w / img.imageWidth, max_h / img.imageHeight)
            img.drawWidth = img.imageWidth * scale
            img.drawHeight = img.imageHeight * scale
            image_table = Table(
                [[img, Paragraph(
                    "<b>Source Image</b><br/>"
                    + escape(image_path.name)
                    + "<br/><br/>The image used for OCR and automated screening.",
                    body
                )]],
                colWidths=[70*mm, 82*mm],
            )
            image_table.setStyle(TableStyle([
                ("BOX", (0,0), (-1,-1), 0.5, colors.HexColor("#D0D7E2")),
                ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
                ("ALIGN", (0,0), (0,0), "CENTER"),
                ("LEFTPADDING", (0,0), (-1,-1), 6),
                ("RIGHTPADDING", (0,0), (-1,-1), 6),
                ("TOPPADDING", (0,0), (-1,-1), 6),
                ("BOTTOMPADDING", (0,0), (-1,-1), 6),
            ]))
            story.append(Spacer(1, 7))
            story.append(image_table)
        except Exception:
            pass

    # Product details
    story.append(Paragraph("1. Product Details", h1))
    fields = [

        ("Manufacturer", product.get("manufacturer")),
        ("Packer", product.get("packer")),
        ("Importer", product.get("importer")),
        ("Country of Origin", product.get("country_of_origin")),
        ("Net Quantity", product.get("net_quantity")),
        ("Unit", product.get("unit")),
        ("MRP", product.get("mrp")),
        ("Manufacturing Date", product.get("manufacture_date")),
        ("Packing Date", product.get("packing_date")),
        ("Best Before", product.get("best_before")),
        ("Use By / Expiry", product.get("use_by")),
        ("Consumer Care", product.get("consumer_care")),
        ("Unit Sale Price", product.get("unit_sale_price")),
        ("Package Type", product.get("package_type")),
    ]
    product_rows = [[_para("Field", small), _para("Extracted Value", small)]]
    for k, v in fields:
        product_rows.append([_para(k, small), _para(v, small)])

    product_t = Table(product_rows, colWidths=[55*mm, 101*mm], repeatRows=1)
    product_t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#123B78")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("GRID", (0,0), (-1,-1), 0.35, colors.HexColor("#D4DAE3")),
        ("ROWBACKGROUNDS", (0,1), (-1,-1),
         [colors.white, colors.HexColor("#F7F9FC")]),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 5),
        ("RIGHTPADDING", (0,0), (-1,-1), 5),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]))
    story.append(product_t)

    # Declaration confidence
    story.append(Paragraph("2. OCR Declaration Evidence", h1))
    decl_rows = [[
        _para("Field", tiny), _para("Label", tiny),
        _para("Value", tiny), _para("Status", tiny),
        _para("Confidence", tiny)
    ]]
    for item in declarations or []:
        conf = item.get("confidence")
        conf_text = f"{float(conf):.3f}" if conf is not None else "—"
        decl_rows.append([
            _para(item.get("field"), tiny),
            _para(item.get("label"), tiny),
            _para(item.get("value"), tiny),
            _para(item.get("status"), tiny),
            _para(conf_text, center),
        ])
    if len(decl_rows) == 1:
        decl_rows.append([_para("—", tiny)] * 5)

    decl_t = Table(
        decl_rows,
        colWidths=[32*mm, 29*mm, 54*mm, 25*mm, 16*mm],
        repeatRows=1
    )
    decl_t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#123B78")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("GRID", (0,0), (-1,-1), 0.3, colors.HexColor("#D4DAE3")),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 3),
        ("RIGHTPADDING", (0,0), (-1,-1), 3),
        ("TOPPADDING", (0,0), (-1,-1), 3),
        ("BOTTOMPADDING", (0,0), (-1,-1), 3),
    ]))
    story.append(decl_t)

    # Rule-wise compliance
    story.append(Paragraph("3. Rule-wise Compliance Assessment", h1))
    rule_rows = [[
        _para("Rule", tiny),
        _para("Requirement / Legal Reference", tiny),
        _para("Status", tiny),
        _para("Reason / Evidence", tiny),
    ]]

    results = compliance.get("results", []) or []
    for r in results:
        status = r.get("status", "MANUAL_REVIEW")
        legal = r.get("legal_reference", "")
        req = r.get("requirement", "")
        reason = r.get("reason", "")
        evidence = r.get("evidence") or {}

        evidence_text = reason

        # LM002 may use commodity_name internally, but the user-facing
        # PDF must not display the commodity name/value.
        if evidence and str(r.get("rule_id", "")).upper() != "LM002":
            pieces = []
            for ek, ev in evidence.items():
                if ev is not None and str(ev).strip():
                    pieces.append(f"{ek}: {ev}")
            if pieces:
                evidence_text += " | " + " | ".join(pieces)

        rule_rows.append([
            _para(r.get("rule_id"), tiny),
            _para(f"{req}<br/><b>Legal reference:</b> {legal}", tiny),
            Paragraph(
                f'<font color="{_status_color(status).hexval()}">'
                f'<b>{escape(_status_label(status))}</b></font>',
                center
            ),
            _para(evidence_text, tiny),
        ])

    rule_t = Table(
        rule_rows,
        colWidths=[14*mm, 61*mm, 29*mm, 52*mm],
        repeatRows=1,
        splitByRow=1
    )
    rule_t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#123B78")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("GRID", (0,0), (-1,-1), 0.3, colors.HexColor("#D4DAE3")),
        ("ROWBACKGROUNDS", (0,1), (-1,-1),
         [colors.white, colors.HexColor("#F7F9FC")]),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("ALIGN", (0,0), (0,-1), "CENTER"),
        ("ALIGN", (2,1), (2,-1), "CENTER"),
        ("LEFTPADDING", (0,0), (-1,-1), 4),
        ("RIGHTPADDING", (0,0), (-1,-1), 4),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]))
    story.append(rule_t)

    # OCR summary
    story.append(Paragraph("4. OCR Summary", h1))
    confidences = [
        float(r.get("confidence", 0))
        for r in ocr_records
        if isinstance(r, dict) and r.get("confidence") is not None
    ]
    avg_conf = (sum(confidences) / len(confidences)) if confidences else 0
    low_count = sum(
        1 for r in ocr_records
        if isinstance(r, dict) and r.get("low_confidence")
    )
    ocr_rows = [
        [_para("OCR Records", small), _para(len(ocr_records), small)],
        [_para("Average OCR Confidence", small), _para(f"{avg_conf:.3f}", small)],
        [_para("Low-confidence OCR Records", small), _para(low_count, small)],
    ]
    ocr_t = Table(ocr_rows, colWidths=[70*mm, 86*mm])
    ocr_t.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.35, colors.HexColor("#D4DAE3")),
        ("ROWBACKGROUNDS", (0,0), (-1,-1),
         [colors.white, colors.HexColor("#F7F9FC")]),
        ("LEFTPADDING", (0,0), (-1,-1), 5),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]))
    story.append(ocr_t)

    # Disclaimer
    story.append(Spacer(1, 10))
    disclaimer = (
        "<b>Important:</b> This report is a preliminary automated screening "
        "generated from the supplied package image, OCR output, and configured "
        "compliance rules. Rules marked NEEDS VERIFICATION / manual review require "
        "human or calibrated visual verification. This report is not a legal "
        "certificate or a substitute for an authorised Legal Metrology inspection."
    )
    d_t = Table([[Paragraph(disclaimer, small)]], colWidths=[156*mm])
    d_t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#FFF7E6")),
        ("BOX", (0,0), (-1,-1), 0.5, colors.HexColor("#E2B75B")),
        ("LEFTPADDING", (0,0), (-1,-1), 7),
        ("RIGHTPADDING", (0,0), (-1,-1), 7),
        ("TOPPADDING", (0,0), (-1,-1), 7),
        ("BOTTOMPADDING", (0,0), (-1,-1), 7),
    ]))
    story.append(d_t)

    def footer(canvas, doc_obj):
        canvas.saveState()
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(colors.HexColor("#777777"))
        canvas.drawString(
            14*mm, 7*mm,
            f"MATRIScan • SIH26034 • Preliminary automated compliance screening • {report_id}"
        )
        canvas.drawRightString(
            A4[0] - 14*mm, 7*mm, f"Page {doc_obj.page}"
        )
        canvas.restoreState()

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return output_path
