# logic/form1040_model.py
from copy import deepcopy

FORM1040_TEMPLATE = {
    # Identification (shown on Page 1)
    "taxpayer_name": "",     # "First M Last" single string for overlay
    "taxpayer_ssn": "",
    "address_line": "",      # "123 Main St, City ST 99999"
    "filing_status": "single",  # single | married_filing_jointly | married_filing_separately | head_of_household | qualifying_widow

    # Income (Page 1, Lines 1–11)
    "line1a_wages": 0.0,
    "line2a_tax_exempt_interest": 0.0,
    "line2b_taxable_interest": 0.0,
    "line3a_qualified_dividends": 0.0,
    "line3b_ordinary_dividends": 0.0,
    "line4a_ira_distributions_total": 0.0,
    "line4b_ira_taxable": 0.0,
    "line5a_pensions_total": 0.0,
    "line5b_pensions_taxable": 0.0,
    "line6a_ss_benefits_total": 0.0,
    "line6b_ss_benefits_taxable": 0.0,
    "line7_capital_gain_or_loss": 0.0,
    "line8_other_income": 0.0,
    "line9_total_income": 0.0,
    "line10_adjustments": 0.0,
    "line11_AGI": 0.0,

    # Deductions & Tax (Page 1, Lines 12–18)
    "line12_standard_or_itemized": 0.0,  # std deduction for your prototype
    "line13_qbi_deduction": 0.0,
    "line15_taxable_income": 0.0,
    "line16_tax": 0.0,
    "line17_additional_taxes_sched2": 0.0,
    "line18_total_tax": 0.0,

    # Payments & Refund/Owe (Page 1, Lines 25–38)
    "line25a_withheld_w2": 0.0,
    "line25b_estimated": 0.0,
    "line25c_refundable_credits": 0.0,
    "line25d_total_payments": 0.0,
    "line33_total_payments": 0.0,
    "line34_refund": 0.0,
    "line37_amount_owed": 0.0,
    "line38_estimated_tax_penalty": 0.0,
}

def new_form1040():
    return deepcopy(FORM1040_TEMPLATE)
