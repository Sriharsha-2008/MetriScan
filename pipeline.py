from datetime import datetime, timezone
from pathlib import Path
import uuid

from config import OUTPUT_DIR
from io_utils import save_json
from ocr_engine import run_ocr
from declaration_ocr import extract_validated_declarations
from field_extractor import extract_product_record
from compliance_engine import evaluate_compliance
from report_generator import generate_pdf


def run_pipeline(image_path: str | Path):
    """
    Complete SIH26034 packaged-commodity compliance pipeline.

    Flow:
        Image
          ↓
        OCR
          ↓
        Declaration detection
          ↓
        Product-field extraction
          ↓
        Compliance evaluation
          ↓
        JSON report
          ↓
        PDF report
    """

    image_path = Path(image_path)

    # --------------------------------------------------------
    # Validate input
    # --------------------------------------------------------

    if not image_path.exists():
        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )

    if not image_path.is_file():
        raise ValueError(
            f"Input path is not a file: {image_path}"
        )

    report_id = (
        "RPT-"
        + uuid.uuid4().hex[:10].upper()
    )

    # ========================================================
    # 1. OCR
    # ========================================================

    print("[1/6] Running OCR...")

    ocr_records = run_ocr(image_path)

    if not isinstance(ocr_records, list):
        raise ValueError(
            "OCR engine returned an invalid result. "
            "Expected a list of OCR records."
        )

    save_json(
        OUTPUT_DIR / "ocr_result.json",
        ocr_records,
    )

    # ========================================================
    # 2. Declaration detection / extraction
    # ========================================================

    print("[2/6] Detecting declarations...")

    declarations = extract_validated_declarations(
        ocr_records
    )

    if not isinstance(declarations, list):
        raise ValueError(
            "Declaration extractor returned an invalid result."
        )

    save_json(
        OUTPUT_DIR / "declaration_ocr_result.json",
        declarations,
    )

    # --------------------------------------------------------
    # Declaration analysis
    # --------------------------------------------------------
    #
    # Keep both extraction status and OCR evidence.
    # This is useful for QA and the final report.
    #

    declaration_analysis = []

    for item in declarations:

        confidence = item.get(
            "confidence"
        )

        image_quality = "UNKNOWN"

        if confidence is not None:

            try:
                confidence_value = float(
                    confidence
                )

                if confidence_value >= 0.75:
                    image_quality = "GOOD"

                elif confidence_value >= 0.50:
                    image_quality = "FAIR"

                else:
                    image_quality = "POOR"

            except (
                TypeError,
                ValueError,
            ):
                image_quality = "UNKNOWN"

        declaration_analysis.append({

            "matched_label": item.get(
                "label"
            ),

            "field": item.get(
                "field"
            ),

            "status": item.get(
                "status"
            ),

            "value": item.get(
                "value"
            ),

            "source_text": item.get(
                "source_text"
            ),

            "image_quality": image_quality,

            "confidence": confidence,

            "box": item.get(
                "box"
            ),

            "ocr_index": item.get(
                "ocr_index"
            ),
        })

    save_json(
        OUTPUT_DIR / "declaration_analysis.json",
        declaration_analysis,
    )

    # ========================================================
    # 3. Product field extraction
    # ========================================================

    print("[3/6] Extracting product fields...")

    product = extract_product_record(
        ocr_records,
        declarations,
    )

    if not isinstance(product, dict):
        raise ValueError(
            "Product extractor returned an invalid result."
        )

    save_json(
        OUTPUT_DIR / "product_record.json",
        product,
    )

    # ========================================================
    # 4. Compliance evaluation
    # ========================================================

    print("[4/6] Evaluating compliance...")

    # Visual evidence can be added here later when calibrated
    # visual inspection is implemented.
    visual = []

    compliance = evaluate_compliance(
        product=product,
        declarations=declarations,
        visual=visual,
        ocr_records=ocr_records,
    )

    if not isinstance(compliance, dict):
        raise ValueError(
            "Compliance engine returned an invalid result."
        )

    if "overall_status" not in compliance:
        raise ValueError(
            "Compliance result does not contain overall_status."
        )

    if "results" not in compliance:
        raise ValueError(
            "Compliance result does not contain rule results."
        )

    save_json(
        OUTPUT_DIR / "compliance_result.json",
        compliance,
    )

    # ========================================================
    # 5. Final JSON report
    # ========================================================

    report = {
        "report_id": report_id,

        "generated_at": (
            datetime.now(
                timezone.utc
            ).isoformat()
        ),

        "overall_status": compliance[
            "overall_status"
        ],

        "counts": compliance[
            "counts"
        ],

        "package_type": compliance[
            "package_type"
        ],

        "product": product,

        "declarations": declarations,

        "declaration_analysis": (
            declaration_analysis
        ),

        "results": compliance[
            "results"
        ],

        "source_image": str(
            image_path
        ),
    }

    print("[5/6] Saving report JSON...")

    save_json(
        OUTPUT_DIR / "compliance_report.json",
        report,
    )

    # ========================================================
    # 6. PDF report
    # ========================================================

    print("[6/6] Generating PDF...")

    pdf_path = (
        OUTPUT_DIR
        / f"{report_id}.pdf"
    )

    generate_pdf(
        report,
        pdf_path,
        image_path=image_path,
    )

    # ========================================================
    # COMPLETE
    # ========================================================

    print()
    print("Completed.")
    print(
        f"Overall status : "
        f"{report['overall_status']}"
    )
    print(
        f"JSON report    : "
        f"{OUTPUT_DIR / 'compliance_report.json'}"
    )
    print(
        f"PDF report     : "
        f"{pdf_path}"
    )

    return report


# ============================================================
# COMMAND-LINE ENTRY POINT
# ============================================================

if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(
        description=(
            "SIH26034 packaged commodity "
            "compliance pipeline"
        )
    )

    parser.add_argument(
        "image",
        help=(
            "Path to the product/package image"
        ),
    )

    args = parser.parse_args()

    run_pipeline(
        args.image
    )