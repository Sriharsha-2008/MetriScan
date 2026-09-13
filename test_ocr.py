"""Standalone SIH26034 OCR + compliance + PDF report runner.

Usage:
    python test_ocr.py "C:\path\to\product.jpg"

The terminal only shows progress. The detailed result is saved as a PDF
under reports/<image>_compliance_report.pdf.
"""

import json
import sys
from pathlib import Path

from ocr_engine import run_ocr
from declaration_ocr import extract_validated_declarations
from field_extractor import extract_product_record
from compliance_engine import evaluate_compliance
from report_generator import generate_compliance_report


def main():
    if len(sys.argv) != 2:
        print("Usage: python test_ocr.py <image_path>")
        print(r'Example: python test_ocr.py "C:\path\to\product.jpg"')
        sys.exit(1)

    image_path = Path(sys.argv[1])

    if not image_path.exists():
        print(f"ERROR: Image not found: {image_path}")
        sys.exit(1)

    print("=" * 70)
    print("MATRIScan - OCR + COMPLIANCE + PDF REPORT")
    print("=" * 70)
    print(f"Image: {image_path}")
    print()

    # 1. OCR
    print("[1/4] Running OCR...")
    try:
        records = run_ocr(str(image_path))
    except Exception as exc:
        print(f"ERROR: OCR failed: {exc}")
        sys.exit(1)

    print(f"      OCR records: {len(records)}")

    # 2. Declaration extraction
    print("[2/4] Extracting declarations...")
    try:
        declarations = extract_validated_declarations(records)
    except Exception as exc:
        print(f"ERROR: Declaration extraction failed: {exc}")
        sys.exit(1)

    print(f"      Declarations detected: {len(declarations)}")

    # 3. Product + actual compliance engine
    print("[3/4] Running compliance rules...")
    try:
        product = extract_product_record(
            records,
            declaration_data=declarations
        )
        compliance = evaluate_compliance(
            product=product,
            declarations=declarations,
            ocr_records=records,
        )
    except Exception as exc:
        print(f"ERROR: Compliance evaluation failed: {exc}")
        sys.exit(1)

    # Preserve the JSON output as before, but now include compliance.
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / f"{image_path.stem}_ocr_result.json"

    result = {
        "image": str(image_path),
        "ocr_record_count": len(records),
        "ocr_records": records,
        "declarations": declarations,
        "product": product,
        "compliance": compliance,
    }

    with output_file.open("w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False, default=str)

    # 4. PDF
    print("[4/4] Generating PDF report...")
    try:
        report_file = generate_compliance_report(
            image_path=image_path,
            product=product,
            declarations=declarations,
            compliance=compliance,
            ocr_records=records,
            output_path=Path("reports") /
                        f"{image_path.stem}_compliance_report.pdf",
        )
    except Exception as exc:
        print(f"ERROR: PDF generation failed: {exc}")
        sys.exit(1)

    print()
    print("=" * 70)
    print("DONE")
    print(f"PDF REPORT: {report_file}")
    print(f"JSON DATA : {output_file}")
    print(f"OVERALL   : {compliance.get('overall_status')}")
    print("=" * 70)


if __name__ == "__main__":
    main()
