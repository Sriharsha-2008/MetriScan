# compliance_rules.py

COMPLIANCE_RULES = [

    {
        "id": "LM001",
        "field": "manufacturer_packer_importer",
        "description": "Manufacturer, packer or importer name and complete address",
        "legal_reference": "Rule 6(1)(a), Rule 10",
        "applicability": "retail_package",
        "automation": "ocr",
    },

    {
        "id": "LM002",
        "field": "common_generic_name",
        "description": "Common / generic product identification declaration",
        "legal_reference": "Rule 6(1)(b)",
        "applicability": "retail_package",
        "automation": "ocr",
    },

    {
        "id": "LM003",
        "field": "country_of_origin",
        "description": "Country of origin for applicable imported packages",
        "legal_reference": "Applicable imported-package requirements",
        "applicability": "imported_product",
        "automation": "ocr",
    },

    {
        "id": "LM004",
        "field": "net_quantity",
        "description": "Net quantity declaration",
        "legal_reference": "Rule 6(1)(c)",
        "applicability": "quantity_declared",
        "automation": "ocr",
    },

    {
        "id": "LM005",
        "field": "unit_of_measurement",
        "description": "Appropriate unit of measurement for the declared quantity",
        "legal_reference": "Rules 12–13",
        "applicability": "quantity_declared",
        "automation": "rule_based",
    },

    {
        "id": "LM006",
        "field": "manufacture_pack_import_date",
        "description": "Month and year of manufacture, pre-packing or import where applicable",
        "legal_reference": "Rule 6(1)(d)",
        "applicability": "retail_package",
        "automation": "ocr",
    },

    {
        "id": "LM007",
        "field": "best_before_use_by",
        "description": "Best-before or use-by information where applicable",
        "legal_reference": "Commodity-specific / applicable law",
        "applicability": "commodity_specific",
        "automation": "ocr",
    },

    {
        "id": "LM008",
        "field": "mrp",
        "description": "Maximum Retail Price (MRP) declaration",
        "legal_reference": "Rule 6(1)(e), Rule 2(m)",
        "applicability": "retail_package",
        "automation": "ocr",
    },

    {
        "id": "LM009",
        "field": "consumer_care",
        "description": "Consumer complaint / consumer-care contact information",
        "legal_reference": "Rule 6(2)",
        "applicability": "retail_package",
        "automation": "ocr",
    },

    {
        "id": "LM010",
        "field": "principal_display_panel",
        "description": "Required declarations are displayed on the principal display panel and in the required manner",
        "legal_reference": "Rule 8",
        "applicability": "retail_package",
        "automation": "manual_visual",
    },

    {
        "id": "LM011",
        "field": "legibility",
        "description": "Required declarations are legible",
        "legal_reference": "Rule 9(1)(a)",
        "applicability": "required_declaration_present",
        "automation": "manual_visual",
    },

    {
        "id": "LM012",
        "field": "prominence",
        "description": "Required declarations are prominent and properly displayed",
        "legal_reference": "Rules 8–9",
        "applicability": "required_declaration_present",
        "automation": "manual_visual",
    },

    {
        "id": "LM013",
        "field": "character_size",
        "description": "Required minimum character and numeral size is satisfied",
        "legal_reference": "Rule 7",
        "applicability": "where_character_size_requirement_applies",
        "automation": "manual_calibrated",
    },

    {
        "id": "LM014",
        "field": "declaration_visibility",
        "description": "Required declarations are visible and not obstructed",
        "legal_reference": "Rule 9",
        "applicability": "required_declaration_present",
        "automation": "manual_visual",
    },

    {
        "id": "LM015",
        "field": "misleading_declaration",
        "description": "Package or declaration does not appear misleading or deceptive",
        "legal_reference": "Rule 12(6), Rule 23",
        "applicability": "retail_package",
        "automation": "manual_semantic",
    },
]