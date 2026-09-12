import os
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)


# ============================================================
# STYLES
# ============================================================

styles = getSampleStyleSheet()

TITLE_STYLE = ParagraphStyle(
    "ReportTitle",
    parent=styles["Title"],
    fontName="Helvetica-Bold",
    fontSize=17,
    leading=21,
    alignment=TA_CENTER,
    spaceAfter=10,
)

SECTION_STYLE = ParagraphStyle(
    "Section",
    parent=styles["Heading2"],
    fontName="Helvetica-Bold",
    fontSize=11,
    leading=14,
    spaceBefore=8,
    spaceAfter=6,
)

NORMAL_STYLE = ParagraphStyle(
    "NormalReport",
    parent=styles["BodyText"],
    fontName="Helvetica",
    fontSize=8.5,
    leading=11,
    spaceAfter=3,
)

SMALL_STYLE = ParagraphStyle(
    "SmallReport",
    parent=styles["BodyText"],
    fontName="Helvetica",
    fontSize=7.5,
    leading=9.5,
)

TABLE_HEADER_STYLE = ParagraphStyle(
    "TableHeader",
    parent=styles["BodyText"],
    fontName="Helvetica-Bold",
    fontSize=7.2,
    leading=9,
    alignment=TA_CENTER,
)

TABLE_CELL_STYLE = ParagraphStyle(
    "TableCell",
    parent=styles["BodyText"],
    fontName="Helvetica",
    fontSize=6.8,
    leading=8.5,
    alignment=TA_LEFT,
)

TABLE_CELL_CENTER_STYLE = ParagraphStyle(
    "TableCellCenter",
    parent=TABLE_CELL_STYLE,
    alignment=TA_CENTER,
)

NOTE_STYLE = ParagraphStyle(
    "Note",
    parent=styles["BodyText"],
    fontName="Helvetica",
    fontSize=7.5,
    leading=10,
    spaceBefore=5,
)


# ============================================================
# HELPERS
# ============================================================

def _safe(value):
    if value is None:
        return "—"

    text = str(value).strip()

    if not text:
        return "—"

    return text


def _paragraph(value, style=TABLE_CELL_STYLE):
    """
    Convert any value into a ReportLab Paragraph.

    This is important because raw strings do not wrap
    reliably inside narrow table cells.
    """
    text = _safe(value)

    # Basic HTML escaping for ReportLab Paragraph.
    text = (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )

    return Paragraph(text, style)


def _status_paragraph(status):
    return _paragraph(
        status.replace("_", " "),
        TABLE_CELL_CENTER_STYLE,
    )


def _get_results(report):
    results = report.get("results", [])

    if isinstance(results, list):
        return results

    return []


def _get_product(report):
    product = report.get("product", {})

    if isinstance(product, dict):
        return product

    return {}


# ============================================================
# PRODUCT DETAILS TABLE
# ============================================================

def _build_product_table(product):

    rows = [
        [
            _paragraph("Field", TABLE_HEADER_STYLE),
            _paragraph("Value", TABLE_HEADER_STYLE),
        ]
    ]

    fields = [
        ("Commodity name", product.get("commodity_name")),
        ("Manufacturer", product.get("manufacturer")),
        ("Packer", product.get("packer")),
        ("Importer", product.get("importer")),
        ("Country of origin", product.get("country_of_origin")),
        ("Net quantity", product.get("net_quantity")),
        ("Unit", product.get("unit")),
        ("MRP", product.get("mrp")),
        ("Manufacture date", product.get("manufacture_date")),
        ("Packing date", product.get("packing_date")),
        ("Best before", product.get("best_before")),
        ("Use by", product.get("use_by")),
        ("Consumer care", product.get("consumer_care")),
        ("Unit sale price", product.get("unit_sale_price")),
        ("Package type", product.get("package_type")),
    ]

    for field, value in fields:
        rows.append(
            [
                _paragraph(field, TABLE_CELL_STYLE),
                _paragraph(value, TABLE_CELL_STYLE),
            ]
        )

    table = Table(
        rows,
        colWidths=[50 * mm, 130 * mm],
        repeatRows=1,
        hAlign="LEFT",
    )

    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E8E8E8")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )

    return table


# ============================================================
# COMPLIANCE RESULTS TABLE
# ============================================================

def _build_results_table(results):

    rows = [
        [
            _paragraph("Rule", TABLE_HEADER_STYLE),
            _paragraph("Requirement", TABLE_HEADER_STYLE),
            _paragraph("Status", TABLE_HEADER_STYLE),
            _paragraph("Reason", TABLE_HEADER_STYLE),
        ]
    ]

    for result in results:

        rule_id = result.get("rule_id", "")
        requirement = result.get(
            "requirement",
            result.get("description", "")
        )
        status = result.get("status", "")
        reason = result.get("reason", "")

        rows.append(
            [
                _paragraph(rule_id, TABLE_CELL_CENTER_STYLE),
                _paragraph(requirement, TABLE_CELL_STYLE),
                _status_paragraph(status),
                _paragraph(reason, TABLE_CELL_STYLE),
            ]
        )

    # A4 printable width:
    #
    # A4 width ≈ 210 mm
    # margins = 15 mm each
    # usable width = 180 mm
    #
    # Give Reason the largest area because it contains
    # the longest text.

    table = Table(
        rows,
        colWidths=[
            13 * mm,   # Rule
            52 * mm,   # Requirement
            25 * mm,   # Status
            90 * mm,   # Reason
        ],
        repeatRows=1,
        hAlign="LEFT",
    )

    table.setStyle(
        TableStyle(
            [
                # Header
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#D9E2F3"),
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.black,
                ),

                # Grid
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    colors.grey,
                ),

                # Alignment
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),

                (
                    "ALIGN",
                    (0, 0),
                    (0, -1),
                    "CENTER",
                ),

                (
                    "ALIGN",
                    (2, 0),
                    (2, -1),
                    "CENTER",
                ),

                # Padding
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
            ]
        )
    )

    return table


# ============================================================
# FOOTER
# ============================================================

def _add_page_number(canvas, document):

    canvas.saveState()

    page_number = canvas.getPageNumber()

    canvas.setFont("Helvetica", 7)

    canvas.drawCentredString(
        A4[0] / 2,
        8 * mm,
        f"Page {page_number}",
    )

    canvas.restoreState()


# ============================================================
# MAIN PDF GENERATOR
# ============================================================

def generate_pdf(report, output_path, image_path=None):

    # ReportLab requires a string path, not pathlib.WindowsPath
    output_path = str(output_path)

    os.makedirs(
        os.path.dirname(output_path),
        exist_ok=True,
    )

    document = SimpleDocTemplate(
        output_path,
        pagesize=A4,

        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,

        title="Legal Metrology Compliance Report",
        author="Packaged Commodity Compliance System",
    )

    story = []

    # ========================================================
    # TITLE
    # ========================================================

    story.append(
        Paragraph(
            "Packaged Commodity Compliance Report",
            TITLE_STYLE,
        )
    )

    report_id = report.get("report_id", "—")

    story.append(
        Paragraph(
            f"<b>Report ID:</b> {_safe(report_id)}",
            NORMAL_STYLE,
        )
    )

    generated_at = report.get("generated_at")

    story.append(
        Paragraph(
            f"<b>Generated:</b> {_safe(generated_at)}",
            NORMAL_STYLE,
        )
    )

    story.append(Spacer(1, 5))

    # ========================================================
    # OVERALL STATUS
    # ========================================================

    story.append(
        Paragraph(
            "Overall Compliance Status",
            SECTION_STYLE,
        )
    )

    overall_status = report.get(
        "overall_status",
        "MANUAL_REVIEW",
    )

    counts = report.get("counts", {})

    summary_data = [
        [
            _paragraph("Overall status", TABLE_HEADER_STYLE),
            _paragraph("PASS", TABLE_HEADER_STYLE),
            _paragraph("NON-COMPLIANT", TABLE_HEADER_STYLE),
            _paragraph("MANUAL REVIEW", TABLE_HEADER_STYLE),
            _paragraph("NOT APPLICABLE", TABLE_HEADER_STYLE),
        ],
        [
            _paragraph(
                overall_status.replace("_", " "),
                TABLE_CELL_CENTER_STYLE,
            ),
            _paragraph(
                counts.get("PASS", 0),
                TABLE_CELL_CENTER_STYLE,
            ),
            _paragraph(
                counts.get("NON_COMPLIANT", 0),
                TABLE_CELL_CENTER_STYLE,
            ),
            _paragraph(
                counts.get("MANUAL_REVIEW", 0),
                TABLE_CELL_CENTER_STYLE,
            ),
            _paragraph(
                counts.get("NOT_APPLICABLE", 0),
                TABLE_CELL_CENTER_STYLE,
            ),
        ],
    ]

    summary_table = Table(
        summary_data,
        colWidths=[
            35 * mm,
            30 * mm,
            35 * mm,
            40 * mm,
            40 * mm,
        ],
        repeatRows=1,
    )

    summary_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#E8E8E8"),
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    colors.grey,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "ALIGN",
                    (0, 0),
                    (-1, -1),
                    "CENTER",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
            ]
        )
    )

    story.append(summary_table)

    # ========================================================
    # PRODUCT DETAILS
    # ========================================================

    story.append(
        Paragraph(
            "Extracted Product Details",
            SECTION_STYLE,
        )
    )

    product = _get_product(report)

    story.append(
        _build_product_table(product)
    )

    # ========================================================
    # COMPLIANCE CHECKS
    # ========================================================

    story.append(
        Paragraph(
            "Compliance Checks",
            SECTION_STYLE,
        )
    )

    results = _get_results(report)

    if results:

        story.append(
            _build_results_table(results)
        )

    else:

        story.append(
            Paragraph(
                "No compliance results were available.",
                NORMAL_STYLE,
            )
        )

    # ========================================================
    # MANUAL REVIEW NOTE
    # ========================================================

    if overall_status == "MANUAL_REVIEW":

        story.append(
            Spacer(1, 6)
        )

        story.append(
            Paragraph(
                "<b>Important:</b> MANUAL_REVIEW means the automated "
                "pipeline did not have sufficient evidence to establish "
                "compliance for one or more checks. It is intentionally "
                "not treated as a compliance failure without validation.",
                NOTE_STYLE,
            )
        )

    # ========================================================
    # SOURCE IMAGE
    # ========================================================

    source_image = report.get("source_image")

    if source_image:

        story.append(
            Paragraph(
                f"<b>Source image:</b> {_safe(source_image)}",
                SMALL_STYLE,
            )
        )

    # ========================================================
    # BUILD
    # ========================================================

    document.build(
        story,
        onFirstPage=_add_page_number,
        onLaterPages=_add_page_number,
    )


# ============================================================
# BACKWARD-COMPATIBLE ALIAS
# ============================================================

def create_pdf(report, output_path):
    """
    Compatibility wrapper in case the existing pipeline
    calls create_pdf().
    """
    return generate_pdf(
        report,
        output_path,
    )