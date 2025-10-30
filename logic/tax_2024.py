# logic/tax_2024.py
from typing import Dict, Tuple

# 2024 STANDARD DEDUCTION (IRS)
STANDARD_DEDUCTION = {
    "single": 14600.0,
    "married_filing_jointly": 29200.0,
    "married_filing_separately": 14600.0,
    "head_of_household": 21900.0,
}

# 2024 ORDINARY INCOME BRACKETS (taxable income, not AGI)
# Each list is tuples of (top_of_bracket, marginal_rate)
# 'None' top means no upper cap for the last bracket.
BRACKETS_2024 = {
    "single": [
        (11600, 0.10),
        (47150, 0.12),
        (100525, 0.22),
        (191950, 0.24),
        (243725, 0.32),
        (609350, 0.35),
        (None, 0.37),
    ],
    "married_filing_jointly": [
        (23200, 0.10),
        (94300, 0.12),
        (201050, 0.22),
        (383900, 0.24),
        (487450, 0.32),
        (731200, 0.35),
        (None, 0.37),
    ],
    "married_filing_separately": [
        (11600, 0.10),
        (47150, 0.12),
        (100525, 0.22),
        (191950, 0.24),
        (243725, 0.32),
        (365600, 0.35),
        (None, 0.37),
    ],
    "head_of_household": [
        (16550, 0.10),
        (63100, 0.12),
        (100500, 0.22),
        (191950, 0.24),
        (243700, 0.32),
        (609350, 0.35),
        (None, 0.37),
    ],
}

def standard_deduction(filing_status: str) -> float:
    key = filing_status.strip().lower()
    return float(STANDARD_DEDUCTION.get(key, STANDARD_DEDUCTION["single"]))

def tax_from_brackets(taxable_income: float, filing_status: str) -> float:
    """
    Piecewise apply 2024 marginal rates to 'taxable_income'.
    """
    if taxable_income <= 0:
        return 0.0

    key = filing_status.strip().lower()
    brackets = BRACKETS_2024.get(key, BRACKETS_2024["single"])

    tax = 0.0
    prev_top = 0.0
    remaining = taxable_income

    for top, rate in brackets:
        if top is None:
            # last bracket
            span = max(0.0, remaining)
            tax += span * rate
            break
        span = min(remaining, top - prev_top)
        if span > 0:
            tax += span * rate
            remaining -= span
            prev_top = top
        if remaining <= 0:
            break

    return round(tax, 2)

def compute_tax_summary(
    income_components: Dict[str, float],
    total_withholding: float,
    filing_status: str
) -> Dict[str, float]:
    """
    income_components example:
      {
        "w2_wages": 5015.97,
        "interest": 1200.00,
        "nec": 12345.00
      }
    """
    wages = float(income_components.get("w2_wages", 0.0))
    interest = float(income_components.get("interest", 0.0))
    nec = float(income_components.get("nec", 0.0))

    agi = wages + interest + nec  # prototype: no adjustments
    std_ded = standard_deduction(filing_status)
    taxable_income = max(0.0, agi - std_ded)
    estimated_tax = tax_from_brackets(taxable_income, filing_status)
    withholding = float(total_withholding)

    balance_due = max(0.0, estimated_tax - withholding)
    refund = max(0.0, withholding - estimated_tax)

    return {
        "wages": round(wages, 2),
        "interest": round(interest, 2),
        "nec": round(nec, 2),
        "agi": round(agi, 2),
        "standard_deduction": round(std_ded, 2),
        "taxable_income": round(taxable_income, 2),
        "estimated_tax": round(estimated_tax, 2),
        "withholding": round(withholding, 2),
        "balance_due": round(balance_due, 2),
        "refund": round(refund, 2),
    }
