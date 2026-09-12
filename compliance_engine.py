# compliance_engine.py

import re

from compliance_rules import COMPLIANCE_RULES


# =========================================================
# BASIC HELPERS
# =========================================================

def get_extracted_declaration(declarations, key):
    """
    Find a declaration using its logical key.

    Supports:
        {"MRP": {...}}

    and:
        [{"field": "MRP", ...}]
    """

    if not declarations:
        return None

    if isinstance(declarations, dict):

        value = declarations.get(key)

        if value is not None:
            return value

        aliases = {
            "MFD & USE BY": [
                "MFD_USE_BY",
                "MFD_USE_BY_DATE",
            ],
            "NET QTY": [
                "NET_QUANTITY",
                "NET_QTY",
            ],
            "UNIT SALE PRICE": [
                "UNIT_SALE_PRICE",
            ],
            "MRP": [
                "MRP",
            ],
        }

        for alias in aliases.get(key, []):
            if alias in declarations:
                return declarations[alias]

    elif isinstance(declarations, list):

        for item in declarations:

            if not isinstance(item, dict):
                continue

            field = str(
                item.get("field", "")
            ).strip().upper()

            label = str(
                item.get("label", "")
            ).strip().upper()

            if (
                field == key.upper()
                or label == key.upper()
            ):
                return item

    return None


def get_ocr_text(ocr_records):
    """
    Convert OCR records into one searchable string.
    """

    if not ocr_records:
        return ""

    texts = []

    for record in ocr_records:

        if isinstance(record, dict):
            text = record.get("text", "")
        else:
            text = str(record)

        if text:
            texts.append(str(text))

    return " ".join(texts)


def has_text_marker(text, markers):
    """
    Check whether any marker exists in OCR text.
    """

    if not text:
        return False

    text_upper = text.upper()

    for marker in markers:

        if marker.upper() in text_upper:
            return True

    return False


# =========================================================
# QUANTITY VALIDATION
# =========================================================

VALID_UNITS = {
    "mg",
    "g",
    "kg",
    "ml",
    "l",
    "litre",
    "liter",
    "litres",
    "liters",
}


def normalize_unit(unit):
    """
    Normalize common unit variations.
    """

    if not unit:
        return None

    unit = str(unit).strip().lower()

    aliases = {
        "gm": "g",
        "gram": "g",
        "grams": "g",

        "kgs": "kg",
        "kilogram": "kg",
        "kilograms": "kg",

        "milligram": "mg",
        "milligrams": "mg",

        "millilitre": "ml",
        "millilitres": "ml",
        "milliliter": "ml",
        "milliliters": "ml",
    }

    return aliases.get(unit, unit)


def quantity_has_valid_unit(value):
    """
    Check whether a quantity contains a recognizable unit.
    """

    if not value:
        return False

    value = str(value)

    pattern = (
        r"\b\d+(?:\.\d+)?\s*"
        r"(mg|g|kg|ml|l|litre|liter|litres|liters)\b"
    )

    return (
        re.search(
            pattern,
            value,
            re.IGNORECASE,
        )
        is not None
    )


def parse_quantity(value):
    """
    Extract numeric quantity and unit.
    """

    if not value:
        return None, None

    match = re.search(
        r"\b(\d+(?:\.\d+)?)\s*"
        r"(mg|g|kg|ml|l|litre|liter|litres|liters)\b",
        str(value),
        re.IGNORECASE,
    )

    if not match:
        return None, None

    quantity = float(match.group(1))

    unit = normalize_unit(
        match.group(2)
    )

    return quantity, unit


# =========================================================
# PACKAGE APPLICABILITY
# =========================================================

def is_imported_product(product, ocr_text):
    """
    Determine whether the package appears to be imported.

    Conservative approach:
    classify as imported only when there is explicit
    importer/origin evidence.
    """

    importer = product.get("importer")

    if importer:
        return True

    markers = [
        "IMPORTED BY",
        "IMPORTER",
        "COUNTRY OF ORIGIN",
        "MADE IN",
        "PRODUCT OF",
    ]

    return has_text_marker(
        ocr_text,
        markers,
    )


def is_multi_piece_package(product, ocr_text):

    markers = [
        "PIECES",
        "PCS",
        "COUNT",
        "NO. OF PIECES",
        "NUMBER OF PIECES",
    ]

    package_type = str(
        product.get(
            "package_type",
            "",
        )
    ).lower()

    return (
        "multi" in package_type
        or has_text_marker(
            ocr_text,
            markers,
        )
    )


def is_group_combination_package(product, ocr_text):

    markers = [
        "COMBO",
        "COMBINATION",
        "ASSORTED",
        "SET OF",
        "PACK OF",
    ]

    package_type = str(
        product.get(
            "package_type",
            "",
        )
    ).lower()

    return (
        "group" in package_type
        or "combination" in package_type
        or has_text_marker(
            ocr_text,
            markers,
        )
    )


# =========================================================
# APPLICABILITY
# =========================================================

def determine_applicability(
    rule,
    product,
    declarations,
    ocr_text,
):

    applicability = rule.get(
        "applicability"
    )

    if applicability == "imported_product":

        return is_imported_product(
            product,
            ocr_text,
        )

    if applicability == "commodity_specific":

        # Commodity-specific applicability cannot always
        # be determined automatically from OCR.
        return True

    if applicability == "where_character_size_requirement_applies":

        return True

    if applicability == "required_declaration_present":

        return True

    if applicability == "quantity_declared":

        return True

    if applicability == "retail_package":

        return True

    return True


# =========================================================
# RESULT HELPER
# =========================================================

def make_result(
    rule,
    status,
    reason,
    evidence=None,
):
    """
    Create a consistent rule result.

    This is important for both:
    - PDF generation
    - frontend/backend integration
    """

    return {
        "rule_id": rule.get("id"),
        "requirement": rule.get(
            "description",
            "",
        ),
        "status": status,
        "legal_reference": rule.get(
            "legal_reference",
            "",
        ),
        "reason": reason,
        "evidence": evidence or {},
    }


# =========================================================
# RULE EVALUATION
# =========================================================

def evaluate_rule(
    rule,
    product,
    declarations,
    ocr_records=None,
    visual=None,
):

    field = rule["field"]

    ocr_text = get_ocr_text(
        ocr_records
    )

    applicable = determine_applicability(
        rule,
        product,
        declarations,
        ocr_text,
    )

    # -----------------------------------------------------
    # NOT APPLICABLE
    # -----------------------------------------------------

    if not applicable:

        return make_result(
            rule,
            "NOT_APPLICABLE",
            "This rule is not applicable to the detected package.",
        )

    # =====================================================
    # LM001
    # MANUFACTURER / PACKER / IMPORTER
    # =====================================================

    if field == "manufacturer_packer_importer":

        manufacturer = product.get(
            "manufacturer"
        )

        packer = product.get(
            "packer"
        )

        importer = product.get(
            "importer"
        )

        if (
            manufacturer
            or packer
            or importer
        ):

            return make_result(
                rule,
                "PASS",
                "Manufacturer, packer or importer information was detected.",
                {
                    "manufacturer": manufacturer,
                    "packer": packer,
                    "importer": importer,
                },
            )

        return make_result(
            rule,
            "NON_COMPLIANT",
            "Manufacturer, packer or importer information was not detected.",
        )

    # =====================================================
    # LM002
    # COMMON / GENERIC NAME
    # =====================================================

    if field == "common_generic_name":

        value = product.get(
            "commodity_name"
        )

        if value:

            return make_result(
                rule,
                "PASS",
                "Common or generic commodity name was detected.",
                {
                    "value": value,
                },
            )

        return make_result(
            rule,
            "NON_COMPLIANT",
            "Common or generic commodity name was not detected.",
        )

    # =====================================================
    # LM003
    # COUNTRY OF ORIGIN
    # =====================================================

    if field == "country_of_origin":

        value = product.get(
            "country_of_origin"
        )

        if value:

            return make_result(
                rule,
                "PASS",
                "Country of origin was detected.",
                {
                    "value": value,
                },
            )

        return make_result(
            rule,
            "MANUAL_REVIEW",
            "Imported-package applicability was detected, but country of origin could not be reliably extracted.",
        )

    # =====================================================
    # LM004
    # NET QUANTITY
    # =====================================================

    if field == "net_quantity":

        declaration = get_extracted_declaration(
            declarations,
            "NET QTY",
        )

        value = None

        if isinstance(
            declaration,
            dict,
        ):

            value = declaration.get(
                "value"
            )

        if (
            value
            and quantity_has_valid_unit(
                value
            )
        ):

            return make_result(
                rule,
                "PASS",
                "Net quantity with a recognizable unit was detected.",
                {
                    "value": value,
                },
            )

        if declaration:

            return make_result(
                rule,
                "MANUAL_REVIEW",
                "Net quantity declaration was detected, but the quantity value could not be reliably validated.",
                declaration,
            )

        return make_result(
            rule,
            "MANUAL_REVIEW",
            "Net quantity could not be reliably detected from the available OCR evidence.",
        )

    # =====================================================
    # LM005
    # UNIT OF MEASUREMENT
    # =====================================================

    if field == "unit_of_measurement":

        declaration = get_extracted_declaration(
            declarations,
            "NET QTY",
        )

        value = None

        if isinstance(
            declaration,
            dict,
        ):

            value = declaration.get(
                "value"
            )

        if (
            value
            and quantity_has_valid_unit(
                value
            )
        ):

            return make_result(
                rule,
                "PASS",
                "Declared quantity uses a recognized unit of measurement.",
                {
                    "value": value,
                },
            )

        return make_result(
            rule,
            "MANUAL_REVIEW",
            "A quantity declaration was not sufficiently reliable for automatic unit validation.",
            {
                "value": value,
            },
        )

    # =====================================================
    # LM006
    # MANUFACTURE / PACKING / IMPORT DATE
    # =====================================================

    if field == "manufacture_pack_import_date":

        declaration = get_extracted_declaration(
            declarations,
            "MFD & USE BY",
        )

        value = None

        if isinstance(
            declaration,
            dict,
        ):

            value = declaration.get(
                "value"
            )

        if value:

            return make_result(
                rule,
                "PASS",
                "A manufacture, packing or related date declaration was detected.",
                declaration,
            )

        if declaration:

            return make_result(
                rule,
                "MANUAL_REVIEW",
                "Date declaration label was detected but its value could not be reliably extracted.",
                declaration,
            )

        return make_result(
            rule,
            "MANUAL_REVIEW",
            "Manufacture, packing or import date could not be reliably detected from the available OCR evidence.",
        )

    # =====================================================
    # LM007
    # BEST BEFORE / USE BY
    # =====================================================

    if field == "best_before_use_by":

        declaration = get_extracted_declaration(
            declarations,
            "MFD & USE BY",
        )

        value = None

        if isinstance(
            declaration,
            dict,
        ):

            value = declaration.get(
                "value"
            )

        if value:

            return make_result(
                rule,
                "PASS",
                "Best-before/use-by information was detected.",
                declaration,
            )

        return make_result(
            rule,
            "MANUAL_REVIEW",
            "Best-before/use-by applicability is commodity-specific and the value could not be reliably validated.",
            declaration or {},
        )

    # =====================================================
    # LM008
    # MRP
    # =====================================================

    if field == "mrp":

        declaration = get_extracted_declaration(
            declarations,
            "MRP",
        )

        value = None

        if isinstance(
            declaration,
            dict,
        ):

            value = declaration.get(
                "value"
            )

        if value:

            return make_result(
                rule,
                "PASS",
                "MRP declaration was detected.",
                declaration,
            )

        if declaration:

            return make_result(
                rule,
                "MANUAL_REVIEW",
                "MRP label was detected but a reliable price value was not extracted.",
                declaration,
            )

        return make_result(
            rule,
            "MANUAL_REVIEW",
            "MRP could not be reliably detected from the available OCR evidence.",
        )

    # =====================================================
    # LM009
    # CONSUMER CARE
    # =====================================================

    if field == "consumer_care":

        value = product.get(
            "consumer_care"
        )

        if value:

            return make_result(
                rule,
                "PASS",
                "Consumer complaint/contact information was detected.",
                {
                    "value": value,
                },
            )

        return make_result(
            rule,
            "MANUAL_REVIEW",
            "Consumer complaint/contact information could not be reliably detected from the available OCR evidence.",
        )

    # =====================================================
    # LM010
    # PRINCIPAL DISPLAY PANEL
    # =====================================================

    if field == "principal_display_panel":

        return make_result(
            rule,
            "MANUAL_REVIEW",
            "Principal display panel placement requires visual inspection of the package.",
        )

    # =====================================================
    # LM011
    # LEGIBILITY
    # =====================================================

    if field == "legibility":

        return make_result(
            rule,
            "MANUAL_REVIEW",
            "Legibility requires visual inspection of the package image.",
        )

    # =====================================================
    # LM012
    # PROMINENCE
    # =====================================================

    if field == "prominence":

        return make_result(
            rule,
            "MANUAL_REVIEW",
            "Prominence of declarations requires visual inspection.",
        )

    # =====================================================
    # LM013
    # CHARACTER SIZE
    # =====================================================

    if field == "character_size":

        return make_result(
            rule,
            "MANUAL_REVIEW",
            "Character/numeral size requires calibrated visual measurement.",
        )

    # =====================================================
    # LM014
    # DECLARATION VISIBILITY
    # =====================================================

    if field == "declaration_visibility":

        return make_result(
            rule,
            "MANUAL_REVIEW",
            "Declaration visibility and obstruction require visual inspection.",
        )

    # =====================================================
    # LM015
    # MISLEADING / DECEPTIVE DECLARATION
    # =====================================================

    if field == "misleading_declaration":

        return make_result(
            rule,
            "MANUAL_REVIEW",
            "Determining whether a package or declaration is misleading requires semantic and visual review.",
        )

    # =====================================================
    # FALLBACK
    # =====================================================

    return make_result(
        rule,
        "MANUAL_REVIEW",
        "Rule is not configured for automatic evaluation.",
    )


# =========================================================
# MAIN COMPLIANCE EVALUATION
# =========================================================

def evaluate_compliance(
    product,
    declarations,
    ocr_records=None,
    visual=None,
):

    results = []

    for rule in COMPLIANCE_RULES:

        result = evaluate_rule(
            rule=rule,
            product=product,
            declarations=declarations,
            ocr_records=ocr_records,
            visual=visual,
        )

        # -------------------------------------------------
        # Ensure every result contains the frontend/report
        # fields even if a rule implementation changes later.
        # -------------------------------------------------

        result["rule_id"] = rule.get(
            "id",
            result.get("rule_id"),
        )

        result["requirement"] = rule.get(
            "description",
            result.get("requirement", ""),
        )

        result["legal_reference"] = rule.get(
            "legal_reference",
            result.get("legal_reference", ""),
        )

        results.append(result)

    # =====================================================
    # COUNT STATUSES
    # =====================================================

    counts = {
        "PASS": 0,
        "NON_COMPLIANT": 0,
        "MANUAL_REVIEW": 0,
        "NOT_APPLICABLE": 0,
    }

    for result in results:

        status = result.get(
            "status"
        )

        if status in counts:
            counts[status] += 1

    # =====================================================
    # OVERALL STATUS
    # =====================================================

    if counts["NON_COMPLIANT"] > 0:

        overall_status = "NON_COMPLIANT"

    elif counts["MANUAL_REVIEW"] > 0:

        overall_status = "MANUAL_REVIEW"

    else:

        overall_status = "PASS"

    # =====================================================
    # FINAL OUTPUT CONTRACT
    # =====================================================

    return {
        "overall_status": overall_status,
        "results": results,
        "counts": counts,
        "package_type": product.get(
            "package_type",
            "unknown",
        ),
    }