from .form1040_model import new_form1040
from .map_w2_to_1040 import map_w2_to_1040

def _safe_float(x, default=0.0):
    try:
        return float(str(x).replace(",", "").strip())
    except Exception:
        return default


def build_form1040(parsed_docs: dict, calc: dict, identity: dict) -> dict:
    """
    Compose the full Form 1040 data structure using:
      - parsed_docs: output of parse_documents(uploaded)
      - calc: output of compute_tax_summary(...)
      - identity: {"taxpayer_name", "taxpayer_ssn", "address_line", "filing_status"}
    """
    form = new_form1040()

    # -------------------------------------------------
    # Identity
    # -------------------------------------------------
    form["taxpayer_name"] = identity.get("taxpayer_name", "")
    form["taxpayer_ssn"] = identity.get("taxpayer_ssn", "")
    form["address_line"] = identity.get("address_line", "")
    form["filing_status"] = identity.get("filing_status", "single")

    # Pull structured docs
    docs = parsed_docs.get("documents", {})
    w2_doc = docs.get("w2", {})
    int_doc = docs.get("1099-INT", {})
    nec_doc = docs.get("1099-NEC", {})

    # -------------------------------------------------
    # W-2 details
    # -------------------------------------------------
    if w2_doc:
        pf = w2_doc.get("parsed_fields", {})
        form["employee_ssn"] = pf.get("a_employee_ssn", "")
        form["employer_ein"] = pf.get("b_employer_ein", "")
        form["employer_name_address"] = pf.get("c_employer_name_address_zip", "")
        form["employee_name_address"] = pf.get("e_employee_name_address_zip", "")

        form["line1a_wages"] = _safe_float(pf.get("1_wages_tips_other_comp", 0))
        form["line25a_withheld_w2"] = _safe_float(pf.get("2_federal_income_tax_withheld", 0))
        form["w2_box3_social_security_wages"] = _safe_float(pf.get("3_social_security_wages", 0))
        form["w2_box4_social_security_tax"] = _safe_float(pf.get("4_social_security_tax_withheld", 0))
        form["w2_box5_medicare_wages"] = _safe_float(pf.get("5_medicare_wages_and_tips", 0))
        form["w2_box6_medicare_tax"] = _safe_float(pf.get("6_medicare_tax_withheld", 0))
        form["state_income_tax"] = _safe_float(pf.get("17_state_income_tax", 0))
        form["other_withholding"] = _safe_float(pf.get("14_other", 0))

    # -------------------------------------------------
    # 1099-INT details
    # -------------------------------------------------
    if int_doc:
        pf = int_doc.get("parsed_fields", {})
        form["payer_name_1099int"] = pf.get("payer_name_address", "")
        form["payer_tin_1099int"] = pf.get("payer_tin", "")
        form["line2a_tax_exempt_interest"] = _safe_float(pf.get("box_8_tax_exempt_interest", 0))
        form["line2b_taxable_interest"] = _safe_float(pf.get("box_1_interest_income", 0))
        form["interest_us_savings"] = _safe_float(pf.get("box_3_us_savings_bonds_interest", 0))
        form["foreign_tax_paid"] = _safe_float(pf.get("box_6_foreign_tax_paid", 0))
        form["line25b_estimated"] = _safe_float(pf.get("box_4_federal_income_tax_withheld", 0))

    # -------------------------------------------------
    # 1099-NEC details
    # -------------------------------------------------
    if nec_doc:
        pf = nec_doc.get("parsed_fields", {})
        form["payer_name_1099nec"] = pf.get("payer_name_address", "")
        form["payer_tin_1099nec"] = pf.get("payer_tin", "")
        form["line8_other_income"] = _safe_float(pf.get("box_1_nonemployee_compensation", 0))
        form["nec_state_income"] = _safe_float(pf.get("box_7_state_income", 0))
        form["line25c_refundable_credits"] = _safe_float(pf.get("box_4_federal_income_tax_withheld", 0))

    # -------------------------------------------------
    # Totals from tax calculator (for consistency)
    # -------------------------------------------------
    form["line11_AGI"] = _safe_float(calc.get("agi", 0))
    form["line12_standard_or_itemized"] = _safe_float(calc.get("standard_deduction", 0))
    form["line15_taxable_income"] = _safe_float(calc.get("taxable_income", 0))
    form["line16_tax"] = _safe_float(calc.get("estimated_tax", 0))
    form["line18_total_tax"] = form["line16_tax"]

    # -------------------------------------------------
    # Payments and totals
    # -------------------------------------------------
    form["line25d_total_payments"] = (
        _safe_float(form.get("line25a_withheld_w2", 0))
        + _safe_float(form.get("line25b_estimated", 0))
        + _safe_float(form.get("line25c_refundable_credits", 0))
    )
    form["line33_total_payments"] = form["line25d_total_payments"]
    form["line34_refund"] = _safe_float(calc.get("refund", 0))
    form["line37_amount_owed"] = _safe_float(calc.get("balance_due", 0))

    # Derived totals
    form["line9_total_income"] = (
        _safe_float(form.get("line1a_wages", 0))
        + _safe_float(form.get("line2b_taxable_interest", 0))
        + _safe_float(form.get("line8_other_income", 0))
    )
    form["line10_adjustments"] = 0.0
    
    

    return form
