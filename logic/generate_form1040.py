import io
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfReader, PdfWriter

# --------------------------------------------------
# Locate the 1040 template
# --------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(BASE_DIR, "templates", "f1040.pdf")

# fallback absolute path if not found
if not os.path.exists(TEMPLATE_PATH):
    TEMPLATE_PATH = "/Users/stillkrish/Documents/taxreturn/logic/templates/f1040.pdf"

if not os.path.exists(TEMPLATE_PATH):
    raise FileNotFoundError(f"⚠️ Missing IRS 1040 template file at: {TEMPLATE_PATH}")

# --------------------------------------------------
# Main PDF generator
# --------------------------------------------------
def generate_form_1040(
    calc_data: dict,
    filing_status: str,
    taxpayer_name: str,
    ssn: str = "",
    address: str = "",
) -> bytes:
    """
    Generate an IRS Form 1040 (2024 layout) by overlaying calculated values
    onto the official PDF template using ReportLab + PyPDF2.
    """

    # --- Create a transparent overlay ---
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    can.setFont("Helvetica", 10)

    # --------------------------------------------------
    # Header / taxpayer info
    # --------------------------------------------------
    can.drawString(95, 708, taxpayer_name)         # name
    can.drawString(455, 708, ssn)                  # SSN
    can.drawString(95, 690, address)               # address line

    # Filing status checkmarks (approx positions)
    filing_positions = {
        "single": (90, 644),
        "married_filing_jointly": (90, 634),
        "married_filing_separately": (90, 624),
        "head_of_household": (90, 614),
        "qualifying_widow": (90, 604),
    }
    if filing_status in filing_positions:
        x, y = filing_positions[filing_status]
        can.setFont("Helvetica-Bold", 14)
        can.drawString(x, y, "✔")
        can.setFont("Helvetica", 10)

    # --------------------------------------------------
    # Income & Tax Section (line coordinates)
    # --------------------------------------------------
    can.setFont("Helvetica", 11)

    # Line 1 – Wages, salaries, tips
    can.drawRightString(510, 565, f"{calc_data.get('wages', 0):,.2f}")

    # Line 2b – Taxable interest
    can.drawRightString(510, 545, f"{calc_data.get('interest', 0):,.2f}")

    # Line 8 – Other income (for 1099-NEC etc.)
    can.drawRightString(510, 465, f"{calc_data.get('nec', 0):,.2f}")

    # Line 11 – Adjusted gross income
    can.drawRightString(510, 425, f"{calc_data.get('agi', 0):,.2f}")

    # Line 15 – Taxable income
    can.drawRightString(510, 380, f"{calc_data.get('taxable_income', 0):,.2f}")

    # Line 16 – Tax
    can.drawRightString(510, 360, f"{calc_data.get('estimated_tax', 0):,.2f}")

    # Line 25d – Federal income tax withheld
    can.drawRightString(510, 255, f"{calc_data.get('withholding', 0):,.2f}")

    # Line 34 – Refund
    can.drawRightString(510, 175, f"{calc_data.get('refund', 0):,.2f}")

    # Line 37 – Amount you owe
    can.drawRightString(510, 130, f"{calc_data.get('balance_due', 0):,.2f}")

    # --------------------------------------------------
    # Signature
    # --------------------------------------------------
    can.setFont("Helvetica", 10)
    can.drawString(
        95,
        70,
        "Taxpayer Signature: ____________________________     Date: __________",
    )

    # Finalize overlay
    can.save()
    packet.seek(0)

    # --------------------------------------------------
    # Merge overlay with the official 1040 template
    # --------------------------------------------------
    overlay_pdf = PdfReader(packet)
    template_pdf = PdfReader(open(TEMPLATE_PATH, "rb"))
    output = PdfWriter()

    base_page = template_pdf.pages[0]
    base_page.merge_page(overlay_pdf.pages[0])
    output.add_page(base_page)

    # Preserve any additional pages
    if len(template_pdf.pages) > 1:
        for i in range(1, len(template_pdf.pages)):
            output.add_page(template_pdf.pages[i])

    # Output to memory
    output_bytes = io.BytesIO()
    output.write(output_bytes)
    output_bytes.seek(0)
    return output_bytes.getvalue()


# --------------------------------------------------
# Optional test run
# --------------------------------------------------
if __name__ == "__main__":
    sample_data = {
        "wages": 5015.97,
        "interest": 1200.00,
        "nec": 12345.00,
        "agi": 18560.97,
        "standard_deduction": 14600.00,
        "taxable_income": 3960.97,
        "estimated_tax": 396.10,
        "withholding": 1119.31,
        "balance_due": 0.00,
        "refund": 723.21,
    }
    pdf_bytes = generate_form_1040(
        calc_data=sample_data,
        filing_status="single",
        taxpayer_name="John Doe",
        ssn="123-45-6789",
        address="123 Main St, Irvine, CA 92617",
    )

    # Save preview to local file for manual check
    with open("Form1040_preview.pdf", "wb") as f:
        f.write(pdf_bytes)
    print("✅ Generated Form1040_preview.pdf")
