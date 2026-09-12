# field_extractor.py

import re


# ============================================================
# BASIC HELPERS
# ============================================================

def _clean_text(text):
    if not text:
        return ""

    text = str(text).strip()
    text = re.sub(r"\s+", " ", text)

    return text.strip(" :;,-")


def _get_text(record):
    if not isinstance(record, dict):
        return ""

    return _clean_text(record.get("text", ""))


def _get_confidence(record):
    try:
        return float(record.get("confidence", 0))
    except Exception:
        return 0.0


def _get_box(record):
    box = record.get("box", [])

    if not isinstance(box, (list, tuple)) or len(box) < 4:
        return [0, 0, 0, 0]

    try:
        return [
            float(box[0]),
            float(box[1]),
            float(box[2]),
            float(box[3]),
        ]
    except Exception:
        return [0, 0, 0, 0]


def _records_with_text(records):
    result = []

    for record in records or []:
        text = _get_text(record)

        if text:
            result.append(
                {
                    "text": text,
                    "confidence": _get_confidence(record),
                    "box": _get_box(record),
                }
            )

    return result


def _full_text(records):
    items = _records_with_text(records)

    return " ".join(
        item["text"]
        for item in items
    )


def _normalise_ocr_text(text):
    text = _clean_text(text)

    replacements = {
        "lndia": "India",
        "HCLDINGS": "HOLDINGS",
        "Hodings": "Holdings",
        "Hoitings": "Holdings",
        "Priiate": "Private",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text


# ============================================================
# GENERAL PATTERNS
# ============================================================

DECLARATION_LABEL_PATTERNS = [
    r"^\s*mrp\s*$",
    r"maximum\s+retail\s+price",
    r"unit\s+sale\s+price",
    r"net\s+qty",
    r"net\s+quantity",
    r"\bmfd\b",
    r"manufactur",
    r"packing\s+date",
    r"packed\s+on",
    r"best\s+before",
    r"use\s+by",
    r"expiry",
    r"batch\s*(no|number)",
    r"lot\s*(no|number)",
    r"date\s+of",
    r"no\.\s*of\s+serves",
    r"per\s+pack",
    r"ingredients",
    r"nutrition",
    r"nutritional",
]


CONTACT_PATTERNS = [
    r"consumer\s+care",
    r"consumer\s+service",
    r"consumer\s+services",
    r"customer\s+care",
    r"customer\s+service",
    r"customer\s+support",
    r"contact\s+us",
    r"complaint",
    r"feedback",
    r"queries",
    r"call\s+us",
    r"email\s+us",
]


LEGAL_PATTERNS = [
    r"fssai",
    r"licen[cs]e",
    r"lic\.?\s*no",
    r"gst",
    r"barcode",
    r"batch\s*no",
    r"lot\s*no",
    r"corporate\s+office",
    r"registered\s+office",
]


def _matches_any(text, patterns):
    low = text.lower()

    return any(
        re.search(
            pattern,
            low,
            re.I,
        )
        for pattern in patterns
    )


def _is_declaration_label(text):
    return _matches_any(
        text,
        DECLARATION_LABEL_PATTERNS,
    )


def _is_contact_or_legal(text):
    return (
        _matches_any(
            text,
            CONTACT_PATTERNS,
        )
        or
        _matches_any(
            text,
            LEGAL_PATTERNS,
        )
    )


def _looks_numeric_or_code(text):
    digits = len(
        re.findall(
            r"\d",
            text,
        )
    )

    letters = len(
        re.findall(
            r"[A-Za-z]",
            text,
        )
    )

    if digits >= 5 and digits > letters:
        return True

    if re.fullmatch(
        r"[\d\s./:#()\-]+",
        text,
    ):
        return True

    return False


def _looks_like_email(text):
    return bool(
        re.search(
            r"\b[A-Z0-9._%+\-]+"
            r"@[A-Z0-9.\-]+\.[A-Z]{2,}\b",
            text,
            re.I,
        )
    )


# ============================================================
# PHONE DETECTION
# ============================================================

def _find_toll_free_phone(text):
    """
    Handles Indian toll-free formats including:

        1800 22 4020
        1800-22-4020
        1800224020
        1800 123 4567
        1800-123-4567
    """

    patterns = [
        # Example: 1800 22 4020
        r"\b1800[\s\-]?\d{2}[\s\-]?\d{4}\b",

        # Example: 1800 123 4567
        r"\b1800[\s\-]?\d{3}[\s\-]?\d{4}\b",

        # Example: 1800 1234 567
        r"\b1800[\s\-]?\d{4}[\s\-]?\d{3}\b",

        # Example: 18001234567
        r"\b1800\d{7}\b",
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            text,
            re.I,
        )

        if match:
            return match.group(0)

    return None


def _looks_like_phone(text):
    return _find_toll_free_phone(text) is not None


# ============================================================
# COMPANY DETECTION
# ============================================================

COMPANY_SUFFIX_PATTERN = re.compile(
    r"\b("
    r"PVT\.?\s*LTD\.?"
    r"|PRIVATE\s+LIMITED"
    r"|LIMITED"
    r"|LTD\.?"
    r"|LLP"
    r"|INC\.?"
    r"|CORPORATION"
    r"|CORP\.?"
    r"|COMPANY"
    r")\b",
    re.I,
)


def _extract_company_from_text(text):
    text = _clean_text(text)

    if not text:
        return None

    if not COMPANY_SUFFIX_PATTERN.search(text):
        return None

    cleaned = re.sub(
        r"^(manufactured\s+by|"
        r"manufactured\s+for|"
        r"manufactured\s+at|"
        r"marketed\s+by|"
        r"packed\s+by|"
        r"imported\s+by|"
        r"manufacturer\s*:|"
        r"packer\s*:|"
        r"importer\s*:)\s*",
        "",
        text,
        flags=re.I,
    )

    cleaned = _clean_text(cleaned)

    words = cleaned.split()

    if len(words) < 2 or len(words) > 12:
        return None

    if _looks_numeric_or_code(cleaned):
        return None

    return cleaned.rstrip(".,:;")


# ============================================================
# MANUFACTURER
# ============================================================

def extract_manufacturer(records):
    items = _records_with_text(records)

    patterns = [
        r"manufacturer\s*[:\-]\s*(.+)",
        r"manufactured\s+by\s*[:\-]?\s*(.+)",
        r"manufactured\s+for\s*[:\-]?\s*(.+)",
        r"manufactured\s+at\s*[:\-]?\s*(.+)",
    ]

    for item in items:
        text = item["text"]

        for pattern in patterns:

            match = re.search(
                pattern,
                text,
                re.I,
            )

            if match:

                candidate = _clean_text(
                    match.group(1)
                )

                company = _extract_company_from_text(
                    candidate
                )

                if company:
                    return company

                if candidate:
                    return candidate.rstrip(
                        ".,:;"
                    )

    candidates = []

    for item in items:

        company = _extract_company_from_text(
            item["text"]
        )

        if not company:
            continue

        score = item["confidence"]

        if len(company.split()) >= 3:
            score += 0.10

        if re.search(
            r"PVT\.?\s*LTD|PRIVATE\s+LIMITED",
            company,
            re.I,
        ):
            score += 0.10

        candidates.append(
            (
                score,
                company,
            )
        )

    if candidates:

        candidates.sort(
            key=lambda x: x[0],
            reverse=True,
        )

        return candidates[0][1]

    return None


# ============================================================
# ADDRESS DETECTION
# ============================================================

ADDRESS_HINTS = [
    r"\broad\b",
    r"\bstreet\b",
    r"\bst\.\b",
    r"\blane\b",
    r"\bindustrial\b",
    r"\bindustrial\s+area\b",
    r"\bindustrial\s+estate\b",
    r"\bestate\b",
    r"\barea\b",
    r"\bplot\b",
    r"\bphase\b",
    r"\bsector\b",
    r"\bvillage\b",
    r"\bdistrict\b",
    r"\bcity\b",
    r"\btown\b",
    r"\bstate\b",
    r"\bnagar\b",
    r"\bcolony\b",
    r"\bpark\b",
    r"\bhighway\b",
    r"\bbypass\b",
    r"\bpin\b",
    r"\b\d{6}\b",
]


def _looks_like_address(text):
    if not text:
        return False

    if _looks_like_email(text):
        return False

    if _looks_like_phone(text):
        return False

    if _matches_any(
        text,
        [
            r"fssai",
            r"licen[cs]e",
            r"gst",
            r"barcode",
        ],
    ):
        return False

    if _matches_any(
        text,
        ADDRESS_HINTS,
    ):
        return True

    if text.count(",") >= 2:
        return True

    return False


def _collect_address_lines(
    items,
    start_index,
):
    address_parts = []

    for j in range(
        start_index,
        min(
            start_index + 5,
            len(items),
        ),
    ):

        text = items[j]["text"]

        if not text:
            continue

        if _looks_like_email(text):
            continue

        if _looks_like_phone(text):
            continue

        if re.search(
            r"^(consumer|customer|call|email)",
            text,
            re.I,
        ):
            break

        if _is_declaration_label(text):
            break

        if _matches_any(
            text,
            [
                r"fssai",
                r"licen[cs]e",
                r"gst",
                r"barcode",
            ],
        ):
            break

        address_parts.append(text)

    if not address_parts:
        return None

    address = ", ".join(
        address_parts
    )

    address = _clean_text(address)

    if len(address) < 8:
        return None

    return address


def _extract_address_after_patterns(
    items,
    patterns,
):
    for i, item in enumerate(items):

        text = item["text"]

        for pattern in patterns:

            match = re.search(
                pattern,
                text,
                re.I,
            )

            if not match:
                continue

            remainder = _clean_text(
                match.group(1)
            )

            if (
                remainder
                and
                _looks_like_address(
                    remainder
                )
            ):
                return remainder.rstrip(
                    ".,:;"
                )

            address = _collect_address_lines(
                items,
                i + 1,
            )

            if address:
                return address

    return None


def extract_manufacturing_address(records):
    items = _records_with_text(records)

    patterns = [
        r"manufactured\s+by\s*[:\-]?\s*(.*)",
        r"manufactured\s+at\s*[:\-]?\s*(.*)",
        r"manufacture\s+address\s*[:\-]?\s*(.*)",
        r"manufacturing\s+address\s*[:\-]?\s*(.*)",
    ]

    return _extract_address_after_patterns(
        items,
        patterns,
    )


# ============================================================
# PACKER
# ============================================================

def extract_packer(records):
    items = _records_with_text(records)

    patterns = [
        r"packer\s*[:\-]\s*(.+)",
        r"packed\s+by\s*[:\-]?\s*(.+)",
    ]

    for item in items:

        text = item["text"]

        for pattern in patterns:

            match = re.search(
                pattern,
                text,
                re.I,
            )

            if match:

                candidate = _clean_text(
                    match.group(1)
                )

                if candidate:
                    return candidate.rstrip(
                        ".,:;"
                    )

    return None


def extract_packer_address(records):
    items = _records_with_text(records)

    patterns = [
        r"packed\s+by\s*[:\-]?\s*(.*)",
        r"packer\s+address\s*[:\-]?\s*(.*)",
    ]

    return _extract_address_after_patterns(
        items,
        patterns,
    )


# ============================================================
# IMPORTER
# ============================================================

def extract_importer(records):
    items = _records_with_text(records)

    patterns = [
        r"importer\s*[:\-]\s*(.+)",
        r"imported\s+by\s*[:\-]?\s*(.+)",
    ]

    for item in items:

        text = item["text"]

        for pattern in patterns:

            match = re.search(
                pattern,
                text,
                re.I,
            )

            if match:

                candidate = _clean_text(
                    match.group(1)
                )

                if candidate:
                    return candidate.rstrip(
                        ".,:;"
                    )

    return None


def extract_importer_address(records):
    items = _records_with_text(records)

    patterns = [
        r"imported\s+by\s*[:\-]?\s*(.*)",
        r"importer\s+address\s*[:\-]?\s*(.*)",
    ]

    return _extract_address_after_patterns(
        items,
        patterns,
    )


# ============================================================
# IMPORT STATUS
# ============================================================

def extract_is_imported(records):

    items = _records_with_text(records)

    full_text = " ".join(
        item["text"]
        for item in items
    )

    # Explicit imported evidence.
    imported_patterns = [
        r"\bimported\s+by\b",
        r"\bimported\s+from\b",
        r"\bimported\b",
        r"\bcountry\s+of\s+origin\b",
        r"\bproduct\s+of\b",
    ]

    for pattern in imported_patterns:

        if re.search(
            pattern,
            full_text,
            re.I,
        ):
            return True

    # Explicit domestic evidence.
    domestic_patterns = [
        r"\bmade\s+in\s+india\b",
        r"\bmanufactured\s+in\s+india\b",
        r"\bproduced\s+in\s+india\b",
        r"\bpacked\s+in\s+india\b",
    ]

    for pattern in domestic_patterns:

        if re.search(
            pattern,
            full_text,
            re.I,
        ):
            return False

    return None


# ============================================================
# COUNTRY OF ORIGIN
# ============================================================

def extract_country_of_origin(records):
    items = _records_with_text(records)

    patterns = [
        r"country\s+of\s+origin\s*[:\-]?\s*(.+)",
        r"made\s+in\s*[:\-]?\s*(.+)",
        r"product\s+of\s*[:\-]?\s*(.+)",
    ]

    for item in items:

        text = item["text"]

        for pattern in patterns:

            match = re.search(
                pattern,
                text,
                re.I,
            )

            if match:

                value = _clean_text(
                    match.group(1)
                )

                if value:
                    return value.rstrip(
                        ".,:;"
                    )

    return None


# ============================================================
# COMMODITY NAME
# ============================================================

def _is_bad_commodity_candidate(text):
    low = text.lower()

    # Consumer-service/contact lines are NEVER
    # product names.
    bad_phrases = [
        r"consumer\s+care",
        r"consumer\s+service",
        r"consumer\s+services",
        r"customer\s+care",
        r"customer\s+service",
        r"customer\s+support",
        r"contact\s+us",
        r"call\s+us",
        r"email\s+us",
        r"feedback",
        r"queries",
        r"complaint",
        r"the\s+consumer",
    ]

    if _matches_any(
        low,
        bad_phrases,
    ):
        return True

    if _is_declaration_label(text):
        return True

    if _matches_any(
        low,
        LEGAL_PATTERNS,
    ):
        return True

    if _looks_like_email(text):
        return True

    if _looks_like_phone(text):
        return True

    if _looks_numeric_or_code(text):
        return True

    if re.search(
        r"https?://|www\.",
        text,
        re.I,
    ):
        return True

    return False


def _commodity_candidate_score(
    item,
    all_items,
):
    text = item["text"]
    confidence = item["confidence"]
    box = item["box"]

    if not text:
        return -1000

    if _is_bad_commodity_candidate(
        text
    ):
        return -1000

    if len(text) < 3:
        return -1000

    if len(text) > 80:
        return -1000

    words = text.split()

    if len(words) > 12:
        return -1000

    score = confidence * 2.0

    alpha_count = len(
        re.findall(
            r"[A-Za-z]",
            text,
        )
    )

    digit_count = len(
        re.findall(
            r"\d",
            text,
        )
    )

    if alpha_count >= 5:
        score += 0.4

    if digit_count == 0:
        score += 0.25

    if 2 <= len(words) <= 8:
        score += 0.5

    if (
        len(words) == 1
        and len(text) >= 4
    ):
        score += 0.2

    # Product name is usually near upper/middle
    # portion of the package.
    if all_items:

        ys = [
            x["box"][1]
            for x in all_items
            if x["box"]
        ]

        if ys:

            min_y = min(ys)
            max_y = max(ys)

            if max_y > min_y:

                relative_y = (
                    box[1] - min_y
                ) / (
                    max_y - min_y
                )

                if relative_y < 0.45:
                    score += 0.35

                if relative_y > 0.85:
                    score -= 0.25

    uppercase_letters = sum(
        1
        for c in text
        if c.isupper()
    )

    lowercase_letters = sum(
        1
        for c in text
        if c.islower()
    )

    if (
        uppercase_letters > 0
        and lowercase_letters == 0
    ):
        score += 0.25

    if "(" in text and ")" in text:
        score += 0.15

    if "-" in text:
        score += 0.10

    return score


def extract_commodity_name(records):

    items = _records_with_text(records)

    if not items:
        return None

    candidates = []

    for item in items:

        score = _commodity_candidate_score(
            item,
            items,
        )

        if score <= -100:
            continue

        candidates.append(
            (
                score,
                item["confidence"],
                item["text"],
            )
        )

    if not candidates:
        return None

    candidates.sort(
        key=lambda x: (
            x[0],
            x[1],
        ),
        reverse=True,
    )

    return _normalise_ocr_text(
        candidates[0][2]
    )


# ============================================================
# NET QUANTITY
# ============================================================

def _valid_quantity_number(number_text):

    try:
        value = float(
            number_text
            .replace(",", "")
            .strip()
        )
    except Exception:
        return False

    if value <= 0:
        return False

    if value > 100000:
        return False

    return True


def extract_net_quantity(records):

    items = _records_with_text(records)

    patterns = [
        r"net\s+qty\s*[:\-]?\s*"
        r"(\d+(?:\.\d+)?)\s*"
        r"(kg|g|mg|l|ml|cl|litre|liter|litres|liters)",

        r"net\s+quantity\s*[:\-]?\s*"
        r"(\d+(?:\.\d+)?)\s*"
        r"(kg|g|mg|l|ml|cl|litre|liter|litres|liters)",
    ]

    for item in items:

        text = item["text"]

        for pattern in patterns:

            match = re.search(
                pattern,
                text,
                re.I,
            )

            if match:

                number = match.group(1)
                unit = match.group(2)

                if _valid_quantity_number(
                    number
                ):
                    return (
                        number,
                        unit.lower(),
                    )

    for i, item in enumerate(items):

        if not re.search(
            r"net\s+(qty|quantity)",
            item["text"],
            re.I,
        ):
            continue

        nearby = " ".join(
            x["text"]
            for x in items[
                i:min(
                    i + 4,
                    len(items),
                )
            ]
        )

        match = re.search(
            r"net\s+(?:qty|quantity)"
            r"\s*[:\-]?\s*"
            r"(\d+(?:\.\d+)?)\s*"
            r"(kg|g|mg|l|ml|cl|litre|liter|litres|liters)",
            nearby,
            re.I,
        )

        if match:

            number = match.group(1)
            unit = match.group(2)

            if _valid_quantity_number(
                number
            ):
                return (
                    number,
                    unit.lower(),
                )

    return None, None


# ============================================================
# MRP
# ============================================================

def extract_mrp(records):

    items = _records_with_text(records)

    patterns = [
        r"\bmrp\s*"
        r"(?:rs\.?|₹|inr)?\s*"
        r"(\d{1,5}(?:\.\d{1,2})?)",

        r"maximum\s+retail\s+price\s*"
        r"(?:rs\.?|₹|inr)?\s*"
        r"(\d{1,5}(?:\.\d{1,2})?)",
    ]

    for i, item in enumerate(items):

        text = item["text"]

        for pattern in patterns:

            match = re.search(
                pattern,
                text,
                re.I,
            )

            if match:

                value = match.group(1)

                if len(
                    re.sub(
                        r"\D",
                        "",
                        value,
                    )
                ) <= 5:
                    return value

        if re.fullmatch(
            r"mrp",
            text,
            re.I,
        ):

            nearby = " ".join(
                x["text"]
                for x in items[
                    i:min(
                        i + 3,
                        len(items),
                    )
                ]
            )

            match = re.search(
                r"\bmrp\b\s*"
                r"(?:rs\.?|₹|inr)?\s*"
                r"(\d{1,5}(?:\.\d{1,2})?)",
                nearby,
                re.I,
            )

            if match:
                return match.group(1)

    return None


# ============================================================
# UNIT SALE PRICE
# ============================================================

def extract_unit_sale_price(records):

    items = _records_with_text(records)

    for i, item in enumerate(items):

        text = item["text"]

        if not re.search(
            r"unit\s+sale\s+price",
            text,
            re.I,
        ):
            continue

        match = re.search(
            r"unit\s+sale\s+price"
            r"\s*[:\-]?\s*"
            r"(?:rs\.?|₹|inr)?\s*"
            r"(\d{1,6}(?:\.\d{1,2})?)",
            text,
            re.I,
        )

        if match:
            return match.group(1)

        nearby = " ".join(
            x["text"]
            for x in items[
                i:min(
                    i + 3,
                    len(items),
                )
            ]
        )

        match = re.search(
            r"unit\s+sale\s+price"
            r"\s*[:\-]?\s*"
            r"(?:rs\.?|₹|inr)?\s*"
            r"(\d{1,6}(?:\.\d{1,2})?)",
            nearby,
            re.I,
        )

        if match:
            return match.group(1)

    return None


# ============================================================
# DATES
# ============================================================

DATE_PATTERN = (
    r"\b("
    r"\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}"
    r"|"
    r"\d{1,2}[\/\-][A-Za-z]{3,9}[\/\-]\d{2,4}"
    r"|"
    r"[A-Za-z]{3,9}\s+\d{4}"
    r"|"
    r"\d{1,2}\s+[A-Za-z]{3,9}\s+\d{2,4}"
    r")\b"
)


def _extract_date_near_label(
    items,
    label_pattern,
):

    for i, item in enumerate(items):

        text = item["text"]

        if not re.search(
            label_pattern,
            text,
            re.I,
        ):
            continue

        match = re.search(
            DATE_PATTERN,
            text,
            re.I,
        )

        if match:
            return match.group(1)

        nearby = " ".join(
            x["text"]
            for x in items[
                i:min(
                    i + 4,
                    len(items),
                )
            ]
        )

        match = re.search(
            DATE_PATTERN,
            nearby,
            re.I,
        )

        if match:
            return match.group(1)

    return None


def extract_manufacture_date(records):

    items = _records_with_text(records)

    return _extract_date_near_label(
        items,
        r"\b(mfd|manufactured|manufacture)\b",
    )


def extract_packing_date(records):

    items = _records_with_text(records)

    return _extract_date_near_label(
        items,
        r"\b(packed|packing|pkd)\b",
    )


def extract_best_before(records):

    items = _records_with_text(records)

    return _extract_date_near_label(
        items,
        r"best\s+before",
    )


def extract_use_by(records):

    items = _records_with_text(records)

    return _extract_date_near_label(
        items,
        r"use\s+by",
    )


# ============================================================
# CONSUMER CARE
# ============================================================

def extract_consumer_care(records):

    items = _records_with_text(records)

    texts = [
        item["text"]
        for item in items
    ]

    email_pattern = (
        r"\b[A-Z0-9._%+\-]+"
        r"@[A-Z0-9.\-]+\.[A-Z]{2,}\b"
    )

    # --------------------------------------------------------
    # Search around consumer-care/service text
    # --------------------------------------------------------

    for i, text in enumerate(texts):

        if not _matches_any(
            text,
            CONTACT_PATTERNS,
        ):
            continue

        nearby = " ".join(
            texts[
                max(0, i - 1):
                min(
                    len(texts),
                    i + 5,
                )
            ]
        )

        phone = _find_toll_free_phone(
            nearby
        )

        email = re.search(
            email_pattern,
            nearby,
            re.I,
        )

        result = []

        if phone:
            result.append(
                "Phone: " + phone
            )

        if email:
            result.append(
                "Email: "
                + email.group(0)
            )

        if result:
            return "; ".join(result)

    # --------------------------------------------------------
    # Explicit CALL US / EMAIL US
    # --------------------------------------------------------

    full_text = " ".join(texts)

    if re.search(
        r"(call\s+us|email\s+us)",
        full_text,
        re.I,
    ):

        phone = _find_toll_free_phone(
            full_text
        )

        email = re.search(
            email_pattern,
            full_text,
            re.I,
        )

        result = []

        if phone:
            result.append(
                "Phone: " + phone
            )

        if email:
            result.append(
                "Email: "
                + email.group(0)
            )

        if result:
            return "; ".join(result)

    # --------------------------------------------------------
    # Toll-free fallback
    # --------------------------------------------------------

    phone = _find_toll_free_phone(
        full_text
    )

    if phone:
        return "Phone: " + phone

    # --------------------------------------------------------
    # Email fallback
    # --------------------------------------------------------

    email = re.search(
        email_pattern,
        full_text,
        re.I,
    )

    if email:
        return (
            "Email: "
            + email.group(0)
        )

    return None


# ============================================================
# PACKAGE TYPE
# ============================================================

def extract_package_type(records):

    full = _full_text(records).lower()

    if re.search(
        r"\b(pouch|sachet|packet)\b",
        full,
    ):
        return "pouch"

    if re.search(
        r"\b(bottle|jar|container)\b",
        full,
    ):
        return "container"

    if re.search(
        r"\b(box|carton)\b",
        full,
    ):
        return "box"

    if re.search(
        r"\b(can|tin)\b",
        full,
    ):
        return "can"

    return "unknown"


# ============================================================
# MAIN EXTRACTION
# ============================================================

def extract_fields(records):

    manufacturer = extract_manufacturer(
        records
    )

    manufacturing_address = (
        extract_manufacturing_address(
            records
        )
    )

    packer = extract_packer(
        records
    )

    packer_address = (
        extract_packer_address(
            records
        )
    )

    importer = extract_importer(
        records
    )

    importer_address = (
        extract_importer_address(
            records
        )
    )

    is_imported = extract_is_imported(
        records
    )

    country = extract_country_of_origin(
        records
    )

    commodity = extract_commodity_name(
        records
    )

    net_quantity, unit = extract_net_quantity(
        records
    )

    mrp = extract_mrp(
        records
    )

    unit_sale_price = (
        extract_unit_sale_price(
            records
        )
    )

    manufacture_date = (
        extract_manufacture_date(
            records
        )
    )

    packing_date = (
        extract_packing_date(
            records
        )
    )

    best_before = extract_best_before(
        records
    )

    use_by = extract_use_by(
        records
    )

    consumer_care = extract_consumer_care(
        records
    )

    package_type = extract_package_type(
        records
    )

    return {
        "commodity_name": commodity,

        "manufacturer": manufacturer,

        "manufacturing_address":
            manufacturing_address,

        "packer": packer,

        "packer_address":
            packer_address,

        "importer": importer,

        "importer_address":
            importer_address,

        "is_imported": is_imported,

        "country_of_origin":
            country,

        "net_quantity":
            net_quantity,

        "unit":
            unit,

        "mrp":
            mrp,

        "manufacture_date":
            manufacture_date,

        "packing_date":
            packing_date,

        "best_before":
            best_before,

        "use_by":
            use_by,

        "consumer_care":
            consumer_care,

        "unit_sale_price":
            unit_sale_price,

        "package_type":
            package_type,
    }


# ============================================================
# PIPELINE INTERFACE
# ============================================================

def extract_product_record(
    records,
    declaration_data=None,
):
    """
    Interface required by pipeline.py.
    """

    product = extract_fields(
        records
    )

    if isinstance(
        declaration_data,
        dict,
    ):

        field_mapping = {
            "net_quantity":
                "net_quantity",

            "unit":
                "unit",

            "mrp":
                "mrp",

            "manufacture_date":
                "manufacture_date",

            "packing_date":
                "packing_date",

            "best_before":
                "best_before",

            "use_by":
                "use_by",

            "consumer_care":
                "consumer_care",

            "unit_sale_price":
                "unit_sale_price",
        }

        for (
            source_field,
            product_field
        ) in field_mapping.items():

            value = declaration_data.get(
                source_field
            )

            if value is None:
                continue

            if product.get(
                product_field
            ) is None:

                product[
                    product_field
                ] = value

    return product


# ============================================================
# COMPATIBILITY WRAPPERS
# ============================================================

def extract_product_fields(records):
    return extract_fields(
        records
    )


def extract_declarations(records):

    fields = extract_fields(
        records
    )

    return {
        "net_quantity":
            fields["net_quantity"],

        "unit":
            fields["unit"],

        "mrp":
            fields["mrp"],

        "manufacture_date":
            fields["manufacture_date"],

        "packing_date":
            fields["packing_date"],

        "best_before":
            fields["best_before"],

        "use_by":
            fields["use_by"],

        "consumer_care":
            fields["consumer_care"],

        "unit_sale_price":
            fields["unit_sale_price"],
    }