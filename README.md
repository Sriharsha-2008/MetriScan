# SIH26034 — Packaged Commodity Compliance Backend

This is a modular local pipeline for:

1. PaddleOCR OCR
2. Declaration-label detection
3. Declaration-focused value extraction
4. Structured product-field extraction
5. Compliance rule evaluation
6. JSON result generation
7. PDF compliance report generation

## Folder

Put these `.py` files in the same backend folder.

Create:

    images/
    output/

Put a package image in `images/`.

## Install

Create/activate your existing venv, then:

    pip install -r requirements.txt

If PaddleOCR/PaddleX is already installed and working in the team's current
environment, do NOT reinstall it unnecessarily.

## Run

    python run.py images\product1.jpg

Example on the SIH machine:

    python run.py "D:\SIH 26034\images\product1.jpg"

Outputs are written to:

    output/ocr_result.json
    output/declaration_analysis.json
    output/declaration_ocr_result.json
    output/product_record.json
    output/compliance_result.json
    output/compliance_report.json
    output/RPT-XXXXXXXXXX.pdf

## Important design decision

OCR failure or uncertain extraction is NOT automatically a violation.

The pipeline uses:

PASS
NON_COMPLIANT
MANUAL_REVIEW
NOT_APPLICABLE

A missing/uncertain OCR value normally becomes MANUAL_REVIEW because an OCR
system cannot prove that a declaration is legally absent merely because it
failed to read it.

## Integration with the existing SIH26034 project

The current team work already uses files such as:

    ocr_result.json
    product_record.json
    declaration_analysis.json
    declaration_ocr_result.json
    visual_compliance.json
    compliance_result.json

This version preserves those major data concepts while removing hard-coded
absolute paths such as `D:\SIH 26034\...`.

The rule catalogue is isolated in `compliance_rules.py`, so your team can
replace/update the rule metadata without changing OCR code.

## Legal scope

This is an engineering prototype, not a legal determination system.
Automated checks are conservative. Rules involving character size, prominence,
legibility, visibility, misleading claims, and other context-dependent
requirements intentionally return MANUAL_REVIEW unless sufficient evidence is
available.

Before the SIH final demo, the rule catalogue should be reviewed against the
specific current Legal Metrology requirements selected by the team.
