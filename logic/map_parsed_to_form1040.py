# logic/map_parsed_to_form1040.py
def map_parsed_to_form1040(parsed_docs: dict) -> dict:
    """
    Map each parsed tax form's fields directly to the 1040 overlay keys.
    """

    f1040 = {}

    # ----------------- W-2 -----------------
    w2 = parsed_docs.get("w2", {}).get("parsed_fields", {})
    if w2:
        f1040["taxpayer_ssn"] = w2.get("a_employee_ssn")
        f1040["taxpayer_name"] = w2.get("e_employee_name_address_zip", "").split(" ")[0:2]
        f1040["address_line"] = w2.get("e_employee_name_address_zip")
        f1040["line1a_wages"] = w2.get("1_wages_tips_other_comp")
        f1040["line25a_withheld_w2"] = w2.get("2_federal_income_tax_withheld")

    # ----------------- 1099-INT -----------------
    i1099 = parsed_docs.get("1099-int", {}).get("parsed_fields", {})
    if i1099:
        f1040["line2b_taxable_interest"] = i1099.get("box_1_interest_income")
        f1040["line2a_tax_exempt_interest"] = i1099.get("box_8_tax_exempt_interest")
        # add its withholding if any
        if i1099.get("box_4_federal_income_tax_withheld") not in (None, "0.00", "missing"):
            f1040["line25a_withheld_w2"] = float(f1040.get("line25a_withheld_w2") or 0) + float(i1099["box_4_federal_income_tax_withheld"])

    # ----------------- 1099-NEC -----------------
    n1099 = parsed_docs.get("1099-nec", {}).get("parsed_fields", {})
    if n1099:
        f1040["line8_other_income"] = n1099.get("box_1_nonemployee_compensation")
        if n1099.get("box_4_federal_income_tax_withheld") not in (None, "0.00", "missing"):
            f1040["line25a_withheld_w2"] = float(f1040.get("line25a_withheld_w2") or 0) + float(n1099["box_4_federal_income_tax_withheld"])

    return f1040
