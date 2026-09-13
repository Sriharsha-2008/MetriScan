import re
from typing import Iterable
from config import DECLARATION_ALIASES, DATE_PATTERNS, MRP_PATTERN, QUANTITY_PATTERN
from io_utils import normalize_space


def normalize_label(text: str) -> str:
    text = normalize_space(text).upper()
    text = text.replace("—", "-").replace("–", "-")
    text = re.sub(r"[^A-Z0-9₹./&:%()\- ]", " ", text)
    return normalize_space(text)


def label_matches(text: str, aliases: Iterable[str]) -> bool:
    text = normalize_label(text)
    for alias in aliases:
        alias = normalize_label(alias)
        if len(alias) < 3:
            continue
        # Exact/word-aware matching avoids labels being swallowed by unrelated text.
        if text == alias or re.search(rf"(?<![A-Z0-9]){re.escape(alias)}(?![A-Z0-9])", text):
            return True
    return False


def find_declaration_labels(records):
    found = []
    for index, record in enumerate(records or []):
        text = str(record.get("text", ""))
        for label, aliases in DECLARATION_ALIASES.items():
            if label_matches(text, aliases):
                found.append({
                    "label": label, "matched_label": label, "ocr_text": text,
                    "ocr_index": index, "confidence": record.get("confidence"),
                    "box": record.get("box"),
                })
                break
    return found


def _box_to_rect(box):
    if not box:
        return None
    try:
        if len(box) == 4:
            return tuple(float(v) for v in box)
        xs = [float(p[0]) for p in box]; ys = [float(p[1]) for p in box]
        return min(xs), min(ys), max(xs), max(ys)
    except Exception:
        return None


def _center(box):
    r = _box_to_rect(box)
    return None if not r else ((r[0]+r[2])/2, (r[1]+r[3])/2)


def _height(box):
    r = _box_to_rect(box)
    return max(1.0, r[3]-r[1]) if r else 1.0


def _width(box):
    r = _box_to_rect(box)
    return max(1.0, r[2]-r[0]) if r else 1.0


def _same_line(a, b):
    ra, rb = _box_to_rect(a), _box_to_rect(b)
    if not ra or not rb:
        return False
    h = max(1.0, min(_height(a), _height(b)))
    return abs((ra[1]+ra[3])/2 - (rb[1]+rb[3])/2) <= h * 0.8


def _horizontal_overlap(a, b):
    ra, rb = _box_to_rect(a), _box_to_rect(b)
    if not ra or not rb:
        return 0.0
    overlap = max(0.0, min(ra[2],rb[2])-max(ra[0],rb[0]))
    return overlap / max(1.0, min(ra[2]-ra[0], rb[2]-rb[0]))


def _value_text(record):
    return normalize_space(str(record.get("text", "")))


def _extract_quantity(text):
    match = re.search(QUANTITY_PATTERN, text, re.I)
    return normalize_space(match.group(0)) if match else None


def _extract_mrp(text):
    """Extract MRP only when the text itself is an MRP declaration/value.

    Never interpret arbitrary alphanumeric codes such as ``BS0424`` as MRP.
    Plain numeric values are allowed because they are only passed here after
    the value box has already been associated with an MRP label.
    """
    text = normalize_space(text)

    match = re.search(MRP_PATTERN, text, re.I)
    if match:
        value = normalize_space(match.group(1))
        digits = re.sub(r"\D", "", value)
        return value if 1 <= len(digits) <= 5 else None

    # Currency-marked standalone value: ``₹ 36.00`` / ``Rs 36``.
    match = re.fullmatch(
        r"(?:₹|RS\.?|INR)\s*(\d{1,5}(?:[.,]\d{1,2})?)",
        text,
        re.I,
    )
    if match:
        return match.group(1).replace(",", ".")

    # A value box immediately associated with an MRP label may contain only
    # the number, e.g. ``36.00``.  Do not accept alphanumeric batch codes.
    match = re.fullmatch(
        r"\d{1,5}(?:[.,]\d{1,2})?",
        text,
    )
    if match:
        return match.group(0).replace(",", ".")

    return None


def _extract_price(text, allow_plain=False):
    # Price parser used only after a price label, so plain numbers are safe here.
    text = text.replace(",", ".")
    m = re.search(r"(?:₹|RS\.?|INR)?\s*(\d{1,5}(?:\.\d{1,2})?)\b", text, re.I)
    if not m:
        return None
    value = m.group(1)
    if not allow_plain and not re.search(r"(?:₹|RS\.?|INR)", text, re.I):
        # In a value box directly next to a price label, plain numeric values are valid.
        pass
    return value


def _extract_date(text, duration=False):
    patterns = DATE_PATTERNS + (
        [r"\b\d{1,2}\s*(?:MONTHS?|DAYS?|YEARS?)\b"] if duration else []
    )
    for pattern in patterns:
        m = re.search(pattern, text, re.I)
        if m:
            return normalize_space(m.group(0))
    return None


def _field_parser(field, text):
    if field == "MRP":
        return _extract_mrp(text)
    if field == "NET_QTY":
        return _extract_quantity(text)
    if field in {"MFD_USE_BY", "MANUFACTURE_DATE", "PACKING_DATE"}:
        return _extract_date(text)
    if field in {"BEST_BEFORE", "USE_BY"}:
        return _extract_date(text, duration=True)
    if field == "UNIT_SALE_PRICE":
        return _extract_price(text)
    return None


def _label_tokens(field):
    return {
        "MRP": ["MRP", "MAXIMUM RETAIL PRICE", "MAX RETAIL PRICE"],
        "NET_QTY": ["NET QTY", "NET QUANTITY", "NET WT", "NET WEIGHT", "NET VOL", "NET VOLUME"],
        "MANUFACTURE_DATE": ["MFD", "MANUFACTURED ON", "DATE OF MANUFACTURE", "MANUFACTURE"],
        "PACKING_DATE": ["PACKED ON", "PACKING DATE", "PKD"],
        "BEST_BEFORE": ["BEST BEFORE", "BEST BEFORE DATE"],
        "USE_BY": ["USE BY", "USE BY DATE", "EXPIRY"],
        "UNIT_SALE_PRICE": ["UNIT SALE PRICE", "UNIT PRICE", "PRICE PER UNIT", "SALE PRICE PER"],
    }.get(field, [])


def _is_label_for_field(text, field):
    return label_matches(text, _label_tokens(field))


def _candidate_score(label_box, value_box, value_text, field, label_index, all_labels, confidence):
    lr, vr = _box_to_rect(label_box), _box_to_rect(value_box)
    if not lr or not vr:
        return -999.0
    lx, ly = _center(label_box); vx, vy = _center(value_box)
    lh = _height(label_box)

    score = 0.0
    # Direction: values normally appear to the right, otherwise below.
    right = vr[0] >= lr[2] - lh * 0.5
    below = vr[1] >= lr[3] - lh * 0.5
    same = _same_line(label_box, value_box)

    if same and right:
        score += 7.0
    elif below and _horizontal_overlap(label_box, value_box) > 0.15:
        score += 5.5
    elif right:
        score += 3.0
    elif below:
        score += 2.0
    else:
        score -= 4.0

    # Penalize a candidate that is visually much closer to another declaration label.
    nearest_other = 10**9
    for li in all_labels:
        if li["ocr_index"] == label_index:
            continue
        c = _center(li.get("box"))
        if c:
            nearest_other = min(nearest_other, abs(vx-c[0]) + abs(vy-c[1]))
    own_dist = abs(vx-lx) + abs(vy-ly)
    if nearest_other < own_dist * 0.85:
        score -= 7.0

    # Distance normalization.
    score += max(0.0, 3.0 - own_dist / max(1.0, lh * 8.0))
    score += min(1.5, float(confidence or 0.0) * 1.5)

    # Field semantics are the strongest protection against wrong assignment.
    value = _field_parser(field, value_text)
    if value:
        score += 8.0
    else:
        score -= 8.0
    return score


def _joined_candidates(records, label_index, field, all_labels):
    """Return geometrically plausible single boxes and pairs, not OCR-list-order windows."""
    label_box = records[label_index].get("box")
    if not label_box:
        return []
    lr = _box_to_rect(label_box)
    lh = _height(label_box)
    pool = []
    for i, r in enumerate(records):
        if i == label_index or not r.get("box"):
            continue
        text = _value_text(r)
        if not text:
            continue
        rr = _box_to_rect(r["box"])
        if not rr:
            continue
        c = _center(r["box"])
        if not c:
            continue
        # Search a bounded area around label.
        if abs(c[1]-_center(label_box)[1]) > max(120.0, lh*5.5):
            continue
        if abs(c[0]-_center(label_box)[0]) > max(500.0, lh*14):
            continue
        if any(li["ocr_index"] == i for li in all_labels):
            continue
        val = _field_parser(field, text)
        if val:
            score = _candidate_score(label_box, r["box"], text, field, label_index, all_labels, r.get("confidence"))
            pool.append((score, val, text, i, r["box"], r.get("confidence")))
    # Handle split OCR: e.g. "MRP" + "₹" + "20", or "NET QTY" + "100" + "g".
    for i, a in enumerate(records):
        if i == label_index or not a.get("box"): continue
        if any(li["ocr_index"] == i for li in all_labels): continue
        for j, b in enumerate(records):
            if j <= i or j == label_index or not b.get("box"): continue
            if any(li["ocr_index"] == j for li in all_labels): continue
            if not (_same_line(a["box"], b["box"]) or _horizontal_overlap(a["box"], b["box"]) > 0.2):
                continue
            ar, br = _box_to_rect(a["box"]), _box_to_rect(b["box"])
            if ar[2] > br[0] + max(_height(a["box"]), _height(b["box"]))*1.5:
                continue
            combined = normalize_space(f"{_value_text(a)} {_value_text(b)}")
            val = _field_parser(field, combined)
            if val:
                box = [min(ar[0],br[0]), min(ar[1],br[1]), max(ar[2],br[2]), max(ar[3],br[3])]
                score = _candidate_score(label_box, box, combined, field, label_index, all_labels, max(a.get("confidence") or 0,b.get("confidence") or 0)) + 0.5
                pool.append((score, val, combined, (i,j), box, max(a.get("confidence") or 0,b.get("confidence") or 0)))
    pool.sort(key=lambda x: x[0], reverse=True)
    return pool


def _extract_spatial(records, index, field):
    labels = find_declaration_labels(records)
    return _best_for_label(records, index, field, labels)


def _best_for_label(records, index, field, labels=None):
    labels = labels or find_declaration_labels(records)
    candidates = _joined_candidates(records, index, field, labels)
    if candidates:
        return candidates[0][1]
    return None


def extract_field_value(records, field):
    """Robust layout-aware extraction for one logical field."""
    records = records or []
    labels = find_declaration_labels(records)

    # Specific labels for dates are handled independently.
    target_indices = [x["ocr_index"] for x in labels if _is_label_for_field(x["ocr_text"], field)]
    if not target_indices:
        # Combined MFD & USE BY declaration can still support legacy callers.
        if field == "MFD_USE_BY":
            target_indices = [x["ocr_index"] for x in labels if x["label"] == "MFD & USE BY"]
    best = None
    for idx in target_indices:
        for c in _joined_candidates(records, idx, field, labels):
            if best is None or c[0] > best[0]:
                best = c
    return best[1] if best else None


def _extract_after_label(records, index, field):
    return _best_for_label(records, index, field)


def extract_validated_declarations(records):
    labels = find_declaration_labels(records)
    field_map = {
        "MRP": "MRP",
        "NET QTY": "NET_QTY",
        "MFD & USE BY": "MFD_USE_BY",
        "UNIT SALE PRICE": "UNIT_SALE_PRICE",
    }
    output = []
    for label, field in field_map.items():
        candidates = [x for x in labels if x["label"] == label]
        best = None
        for lab in candidates:
            for c in _joined_candidates(records, lab["ocr_index"], field, labels):
                result = {
                    "field": field, "label": label,
                    "status": "EXTRACTED" if c[1] else "MANUAL_REVIEW",
                    "value": c[1], "confidence": c[5],
                    "source_text": c[2], "box": c[4],
                    "ocr_index": lab["ocr_index"],
                    "association_score": round(c[0], 3),
                }
                if best is None or c[0] > best[0]:
                    best = (c[0], result)
        if best:
            output.append(best[1])
        else:
            output.append({
                "field": field, "label": label, "status": "NOT_DETECTED",
                "value": None, "confidence": None, "source_text": None,
                "box": None, "ocr_index": None, "association_score": 0,
            })
    return output
