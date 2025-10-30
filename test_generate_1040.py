from logic.generate_form1040 import generate_form_1040

data = {
    "wages": 5015.97,
    "interest": 1200.00,
    "nec": 12345.00,
    "agi": 18560.97,
    "standard_deduction": 14600.00,
    "taxable_income": 3960.97,
    "estimated_tax": 396.10,
    "withholding": 1119.31,
    "refund": 723.21,
    "balance_due": 0.00,
}

pdf = generate_form_1040(
    calc_data=data,
    filing_status="single",
    taxpayer_name="Krish Thakur",
    ssn="616-41-6515",
    address="940 Cherry Blossom Ln, Tracy CA 95377",
)

with open("filled_1040_overlay.pdf", "wb") as f:
    f.write(pdf)

print("✅ Generated filled_1040_overlay.pdf — open to verify placement.")
