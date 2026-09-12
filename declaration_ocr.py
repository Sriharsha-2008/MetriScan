import re
from typing import Iterable

from config import DECLARATION_ALIASES, DATE_PATTERNS, MRP_PATTERN, QUANTITY_PATTERN
from io_utils import normalize_space


def normalize_label(text: str) -> str:
    text = normalize_space(text).upper()
    text = text.replace("—", "-").replace("–", "-")
    text = re.sub(r"[^A-Z0-9₹./& -]", " ", text)
    return normalize_space(text)


def label_matches(text: str, aliases: Iterable[str]) -> bool:
    text = normalize_label(text)

    for alias in aliases:
        alias = normalize_label(alias)

        if not alias:
            continue

        # Avoid overly broad aliases such as "PER", "MFG", etc.
        if len(alias) < 4:
            continue

        if alias in text:
            return True

    return False


def find_declaration_labels(records):
    found = []

    for index, record in enumerate(records):
        text = str(record.get("text", ""))

        for label, aliases in DECLARATION_ALIASES.items():
            if label_matches(text, aliases):
                found.append({
                    "label": label,
                    "matched_label": label,
                    "ocr_text": text,
                    "ocr_index": index,
                    "confidence": record.get("confidence"),
                    "box": record.get("box"),
                })
                break

    return found


def _box_to_rect(box):
    if not box:
        return None

    try:
        if len(box) == 4:
            return (
                float(box[0]),
                float(box[1]),
                float(box[2]),
                float(box[3]),
            )

        # Polygon format
        xs = [float(p[0]) for p in box]
        ys = [float(p[1]) for p in box]

        return (
            min(xs),
            min(ys),
            max(xs),
            max(ys),
        )

    except Exception:
        return None


def _center(box):
    rect = _box_to_rect(box)

    if rect is None:
        return None

    x1, y1, x2, y2 = rect

    return (
        (x1 + x2) / 2,
        (y1 + y2) / 2,
    )


def _height(box):
    rect = _box_to_rect(box)

    if rect is None:
        return 0

    return max(0, rect[3] - rect[1])


def _horizontal_distance(box1, box2):
    c1 = _center(box1)
    c2 = _center(box2)

    if not c1 or not c2:
        return 999999

    return abs(c1[0] - c2[0])


def _vertical_distance(box1, box2):
    c1 = _center(box1)
    c2 = _center(box2)

    if not c1 or not c2:
        return 999999

    return abs(c1[1] - c2[1])


def _same_line(box1, box2):
    r1 = _box_to_rect(box1)
    r2 = _box_to_rect(box2)

    if not r1 or not r2:
        return False

    h = max(_height(box1), _height(box2), 1)

    return abs(
        ((r1[1] + r1[3]) / 2)
        -
        ((r2[1] + r2[3]) / 2)
    ) <= h * 1.5


def _record_text(record):
    return normalize_space(str(record.get("text", "")))


def _extract_quantity(text: str):
    match = re.search(
        QUANTITY_PATTERN,
        text,
        re.IGNORECASE
    )

    if not match:
        return None

    value = normalize_space(match.group(0))

    # Reject suspiciously long numeric strings.
    digits = re.sub(r"\D", "", value)

    if len(digits) > 6:
        return None

    return value


def _extract_mrp(text: str):
    """
    Extract an actual MRP value.

    Important:
    FSSAI licence numbers and other long numeric identifiers
    must never be interpreted as MRP.
    """

    # First look for explicit MRP + price on the same text.
    patterns = [
        r"\bMRP\b\s*[:\-]?\s*(?:₹|RS\.?|INR)?\s*(\d{1,5}(?:[.,]\d{1,2})?)",
        r"MRP\s*(?:₹|RS\.?|INR)?\s*(\d{1,5}(?:[.,]\d{1,2})?)",
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:
            value = normalize_space(match.group(1))

            digits = re.sub(r"\D", "", value)

            if 1 <= len(digits) <= 5:
                return value

    # Do NOT search arbitrary nearby numbers for MRP.
    # This prevents FSSAI licence numbers from becoming MRP.
    return None


def _extract_date(text: str):
    for pattern in DATE_PATTERNS:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:
            return normalize_space(match.group(0))

    return None


def _extract_unit_sale_price(text: str):
    """
    Unit sale price must contain an actual price/value.

    Things such as:
        Per 100 g
        Per 100 g 553 kcal
        Nutrients
    are NOT unit-sale-price values.
    """

    patterns = [
        r"(?:UNIT\s+SALE\s+PRICE)\s*[:\-]?\s*(?:₹|RS\.?|INR)?\s*(\d{1,5}(?:[.,]\d{1,2})?)"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:
            return normalize_space(match.group(1))

    return None


def _spatial_candidates(records, label_index, max_vertical=120):
    label_record = records[label_index]

    label_box = label_record.get("box")

    if not label_box:
        return []

    candidates = []

    label_center = _center(label_box)

    if not label_center:
        return []

    lx, ly = label_center

    for index, record in enumerate(records):

        if index == label_index:
            continue

        text = _record_text(record)

        if not text:
            continue

        box = record.get("box")

        if not box:
            continue

        center = _center(box)

        if not center:
            continue

        x, y = center

        dx = abs(x - lx)
        dy = abs(y - ly)

        if dy > max_vertical:
            continue

        # Ignore extremely distant records.
        distance = dx + dy

        candidates.append({
            "index": index,
            "text": text,
            "box": box,
            "dx": dx,
            "dy": dy,
            "distance": distance,
        })

    candidates.sort(
        key=lambda item: item["distance"]
    )

    return candidates


def _extract_spatial(records, index, field):

    label_record = records[index]

    candidates = _spatial_candidates(
        records,
        index,
        max_vertical=100
    )

    for candidate in candidates:

        text = candidate["text"]

        # Never use FSSAI licence numbers.
        if re.search(
            r"\b(?:LIC|LICENCE|LICENSE)\b",
            text,
            re.IGNORECASE
        ):
            continue

        if field == "MRP":

            value = _extract_mrp(text)

            if value:
                return value

        elif field == "NET_QTY":

            value = _extract_quantity(text)

            if value:
                return value

        elif field == "MFD_USE_BY":

            value = _extract_date(text)

            if value:
                return value

        elif field == "UNIT_SALE_PRICE":

            value = _extract_unit_sale_price(text)

            if value:
                return value

    return None


def _nearby_text(records, index: int, radius: int = 2) -> str:

    start = max(0, index - radius)
    end = min(len(records), index + radius + 1)

    return " ".join(
        _record_text(r)
        for r in records[start:end]
    )


def _extract_after_label(records, index, field):

    # 1. Prefer spatial extraction.
    value = _extract_spatial(
        records,
        index,
        field
    )

    if value:
        return value

    # 2. Very small OCR-order fallback.
    context = _nearby_text(
        records,
        index,
        radius=1
    )

    if field == "NET_QTY":
        return _extract_quantity(context)

    if field == "MRP":
        return _extract_mrp(context)

    if field == "MFD_USE_BY":
        return _extract_date(context)

    if field == "UNIT_SALE_PRICE":
        return _extract_unit_sale_price(context)

    return None


def extract_validated_declarations(records):

    labels = find_declaration_labels(records)

    by_label = {}

    for item in labels:
        by_label.setdefault(
            item["label"],
            []
        ).append(item)

    output = []

    field_map = {
        "MRP": "MRP",
        "NET QTY": "NET_QTY",
        "MFD & USE BY": "MFD_USE_BY",
        "UNIT SALE PRICE": "UNIT_SALE_PRICE",
    }

    for label, field in field_map.items():

        candidates = by_label.get(
            label,
            []
        )

        best = None

        for candidate in candidates:

            value = _extract_after_label(
                records,
                candidate["ocr_index"],
                field
            )

            candidate_result = {
                "field": field,
                "label": label,
                "status": (
                    "EXTRACTED"
                    if value
                    else "MANUAL_REVIEW"
                ),
                "value": value,
                "confidence": candidate.get(
                    "confidence"
                ),
                "source_text": candidate.get(
                    "ocr_text"
                ),
                "box": candidate.get(
                    "box"
                ),
                "ocr_index": candidate.get(
                    "ocr_index"
                ),
            }

            if value:
                best = candidate_result
                break

            if best is None:
                best = candidate_result

        if best is None:

            best = {
                "field": field,
                "label": label,
                "status": "NOT_DETECTED",
                "value": None,
                "confidence": None,
                "source_text": None,
                "box": None,
                "ocr_index": None,
            }

        output.append(best)

    return output