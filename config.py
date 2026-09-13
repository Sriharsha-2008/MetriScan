from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

INPUT_DIR = BASE_DIR / "images"
OUTPUT_DIR = BASE_DIR / "output"

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# Minimum OCR confidence accepted by the pipeline.
OCR_MIN_CONFIDENCE = 0.25
# Keep weak OCR for layout/field recovery; do not delete it in OCR parser.
OCR_KEEP_CONFIDENCE = 0.40

# Geometry/search tuning for declaration association.
OCR_MAX_FIELD_VERTICAL_FACTOR = 6.0
OCR_MAX_FIELD_HORIZONTAL_FACTOR = 16.0
FIELD_ACCEPT_SCORE = 8.0
FIELD_VERIFY_SCORE = 4.5


# ============================================================
# DECLARATION LABELS
# ============================================================
#
# Keep these aliases specific.
# Do NOT use generic words such as "PER", "MFG", etc.
# because they occur naturally in unrelated package text.
#
DECLARATION_ALIASES = {

    "MRP": [
        "MRP",
        "MAXIMUM RETAIL PRICE",
        "MAX RETAIL PRICE",
        "MAX. RETAIL PRICE",
        "MAXIMUM RETAIL PRICE RS",
    ],

    "NET QTY": [
        "NET QTY",
        "NET QTY.",
        "NET QUANTITY",
        "NET WT",
        "NET WEIGHT",
        "NET VOL",
        "NET VOLUME",
    ],

    "MFD & USE BY": [
        "MFD & USE BY",
        "MFD & USE-BY",
        "MFD USE BY",
        "DATE OF MANUFACTURE",
        "MANUFACTURED ON",
        "PACKED ON",
        "PKD",
        "PKD.",
        "BEST BEFORE",
        "USE BY",
        "USE BY DATE",
        "BEST BEFORE DATE",
    ],

    "UNIT SALE PRICE": [
        "UNIT SALE PRICE",
        "UNIT SALE PRICE RS",
        "UNIT SALE PRICE:",
        "SALE PRICE PER",
        "UNIT PRICE",
        "PRICE PER UNIT",
    ],

    "PER PACK": [
        "PER PACK",
        "PRICE PER PACK",
    ],

    "CONSUMER CARE": [
        "CONSUMER CARE",
        "CUSTOMER CARE",
        "CONSUMER COMPLAINT",
        "CUSTOMER SERVICE",
        "TOLL FREE",
        "HELPLINE",
        "CONSUMER SERVICES",
    ],

    "MANUFACTURER": [
        "MANUFACTURED BY",
        "MANUFACTURER",
        "MFR",
        "MFG BY",
        "MFG. BY",
        "MFG & MKT BY",
        "MFG. & MKT. BY",
        "MANUFACTURED AND MARKETED BY",
    ],

    "PACKER": [
        "PACKED BY",
        "PACKER",
        "PACKED AND MARKETED BY",
        "PACKED & MARKETED BY",
    ],

    "IMPORTER": [
        "IMPORTED BY",
        "IMPORTER",
    ],

    "COUNTRY OF ORIGIN": [
        "COUNTRY OF ORIGIN",
        "MADE IN",
        "PRODUCT OF",
    ],
}


# ============================================================
# DATE PATTERNS
# ============================================================

DATE_PATTERNS = [

    # 12/08/2026
    r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",

    # 12/2026
    r"\b\d{1,2}[/-]\d{2,4}\b",

    # Compact month/year and common separators: 08.2026 / 08-2026
    r"\b\d{1,2}[.]\d{2,4}\b",

    # AUG 2026 / AUGUST 2026
    r"\b(?:JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)[A-Z]*[ .,-]+\d{2,4}\b",

    # BEST BEFORE 6 MONTHS / 30 DAYS
    r"\b\d{1,2}\s+(?:MONTH|MONTHS|DAYS|DAY)\b",
]


# ============================================================
# QUANTITY
# ============================================================

QUANTITY_PATTERN = (
    r"\b"
    r"\d+(?:\.\d+)?"
    r"\s*"
    r"(?:mg|g|kg|ml|l|litre|liter|litres|liters)"
    r"\b"
)


# ============================================================
# MRP
# ============================================================
#
# Deliberately strict.
#
# Examples accepted:
#   MRP 20
#   MRP ₹20
#   MRP Rs. 20
#   MRP INR 20.00
#
# Long licence numbers must not match.
#

MRP_PATTERN = (
    r"\b(?:MRP|MAX(?:IMUM)?\.?\s*RETAIL\s*PRICE)"
    r"\s*[:\-]?"
    r"\s*(?:₹|RS\.?|INR)?"
    r"\s*"
    r"(\d{1,5}(?:[.,]\d{1,2})?)"
)