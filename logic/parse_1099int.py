# logic/parse_1099int.py
from typing import Dict, Any

HARD_CODED_1099INT = {
    # Identity / addresses
    "payer_name_address": "MICHAEL M JORDAN, STERLING HEIGHTS, LANSING MI 48310, 5172009968",
    "payer_tin": "10-9920202",
    "recipient_tin": "101-42-0204",
    "recipient_name_address": "WEST LIFE INSURANCE, 9 PRAIRIE COURT, BALTIMORE MD 20601",
    "account_number": "00202072",
    "payer_rtn": "5172009968",

    # Box values
    "box_1_interest_income": "1200.00",
    "box_2_early_withdrawal_penalty": "3000.00",
    "box_3_us_savings_bonds_interest": "6500.00",
    "box_4_federal_income_tax_withheld": "1000.00",
    "box_5_investment_expenses": "1780.00",
    "box_6_foreign_tax_paid": "1854.00",
    "box_7_foreign_country": "missing",
    "box_8_tax_exempt_interest": "3250.00",
    "box_9_specified_private_activity_bond_interest": "850.00",
    "box_10_market_discount": "1040.00",
    "box_11_bond_premium": "1800.00",
    "box_12_bond_premium_treasury": "4080.00",
    "box_13_bond_premium_tax_exempt": "1450.00",
    "box_14_tax_exempt_tax_credit_bond_no": "missing",
    "box_15_state": "MI",
    "box_16_state_identification_no": "missing",
    "box_17_state_tax_withheld": "missing",
}


def parse_1099int(file_bytes: bytes, filename: str) -> Dict[str, Any]:
    """
    Always return predefined 1099-INT field values for demonstration purposes.
    """
    parsed_fields = HARD_CODED_1099INT.copy()

    return {
        "filename": filename,
        "form_type": "1099-INT",
        "parsed_fields": parsed_fields,
        "missing_fields": [
            k for k, v in parsed_fields.items() if v == "missing"
        ],
        "notes": [
            "Hardcoded 1099-INT parser stub for demo prototype.",
            "All values are static placeholders to simulate a fully parsed form."
        ],
    }
