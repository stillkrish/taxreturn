# logic/field_map_1040_2024.py

FORM_1040_FIELD_MAP = {
    # ─── Taxpayer info ──────────────────────────────────────────────
    "taxpayer_name":  "f1_01[0]",   # Name and address line
    "taxpayer_ssn":   "f1_02[0]",   # SSN box (top right)
    "address":        "f1_03[0]",   # Street, city, state ZIP

    # ─── Income section (Lines 1–9) ─────────────────────────────────
    "wages":          "f1_08[0]",   # Line 1 – Wages, salaries, tips
    "interest":       "f1_09[0]",   # Line 2b – Taxable interest
    # 1099-NEC / other income usually flows to line 8; for demo use:
    "nec":            "f1_16[0]",   # treat as “Other income”
    "agi":            "f1_11[0]",   # Line 11 – Adjusted gross income

    # ─── Deductions & taxable income ────────────────────────────────
    "standard_deduction": "f1_14[0]",   # Line 14 – Standard deduction
    "taxable_income":     "f1_15[0]",   # Line 15 – Taxable income

    # ─── Tax, payments, refund ──────────────────────────────────────
    "estimated_tax":  "f1_16[0]",   # Line 16 – Tax
    "withholding":    "f1_25[0]",   # Line 25 – Federal income tax withheld
    "refund":         "f1_34[0]",   # Line 34 – Refund
    "balance_due":    "f1_37[0]",   # Line 37 – Amount you owe

    # ─── Optional lines if you wish to expand later ─────────────────
    # "child_tax_credit": "f1_19[0]",
    # "total_tax": "f1_24[0]",
}
