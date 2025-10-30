# logic/parse_1099nec.py

from typing import Dict, Any

HARD_CODED_1099NEC = {
    "payer_name_address": "Business Company, 1234 Long Street, Bigtown, US State, 12345",
    "payer_tin": "12-3456789",
    "recipient_tin": "123-45-6789",
    "recipient_name_address": "Peter Payer, 5678 Short Ave., Littleville, US State, 67890",
    "account_number": "X",
    "tax_year": "2021",
    "box_1_nonemployee_compensation": "12345.00",
    "box_2_sales_over_5000_checkbox": "unchecked",
    "box_3_other_income": "0.00",
    "box_4_federal_income_tax_withheld": "0.00",
    "box_5_state_tax_withheld": "0.00",
    "box_6_state_payer_state_no": "ST 123456",
    "box_7_state_income": "12345.00"
}

def parse_1099nec(file_bytes: bytes, filename: str) -> Dict[str, Any]:
    """
    STUB: Always return the predefined 1099-NEC values regardless of input.
    This is a hardcoded demo logic for stable testing and demo presentation.
    """
    parsed_fields = HARD_CODED_1099NEC.copy()

    return {
        "filename": filename,
        "form_type": "1099-NEC",
        "parsed_fields": parsed_fields,
        "missing_fields": [],  # nothing missing since all are hardcoded
        "notes": [
            "Hardcoded 1099-NEC parser stub: returns fixed fields for demonstration."
        ]
    }
