# logic/map_w2_to_1040.py
def map_w2_to_1040(w2_fields: dict) -> dict:
    """
    Convert a single W-2's parsed_fields into 1040 line contributions.
    Expects W-2 keys like:
      "1_wages_tips_other_comp", "2_federal_income_tax_withheld", ...
    Returns a dict with keys that match form1040_model.
    """
    out = {}

    # Line 1a – wages
    try:
        out["line1a_wages"] = float(w2_fields.get("1_wages_tips_other_comp", 0) or 0)
    except Exception:
        out["line1a_wages"] = 0.0

    # Line 25a – federal withholding from W-2
    try:
        out["line25a_withheld_w2"] = float(w2_fields.get("2_federal_income_tax_withheld", 0) or 0)
    except Exception:
        out["line25a_withheld_w2"] = 0.0

    # Optional: state withholding (not directly on 1040 Pg1)
    # out["state_income_tax_withheld"] = float(w2_fields.get("17_state_income_tax", 0) or 0)

    return out
