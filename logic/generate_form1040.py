# logic/generate_form1040.py
import io
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfReader, PdfWriter

# --------------------------------------------------------------------
# Locate your static IRS Form 1040 template
# --------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(BASE_DIR, "templates", "f1040.pdf")

if not os.path.exists(TEMPLATE_PATH):
    raise FileNotFoundError(f"⚠️ Missing IRS 1040 template at: {TEMPLATE_PATH}")

# --------------------------------------------------------------------
# Approximate coordinate map (tuned for 2024 IRS layout)
# You can adjust any x,y pair to nudge the text on-page.
# --------------------------------------------------------------------
COORDS = {
    # Header
    "taxpayer_name": (95, 710),
    "taxpayer_ssn": (445, 710),
    "address_line": (95, 695),

    # Filing-status checkmarks
    "filing_status_single": (95, 652),
    "filing_status_married_joint": (160, 652),
    "filing_status_married_sep": (250, 652),
    "filing_status_head": (340, 652),

    # Income lines (Page 1)
    "line1a_wages": (520, 520),
    "line2b_taxable_interest": (520, 505),
    "line8_other_income": (520, 395),
    "line9_total_income": (520, 380),
    "line11_AGI": (520, 350),

    # Deductions / Tax
    "line12_standard_or_itemized": (520, 335),
    "line15_taxable_income": (520, 305),
    "line16_tax": (520, 285),

    # Payments / Refund
    "line25a_withheld_w2": (520, 255),
    "line25d_total_payments": (520, 225),
    "line34_refund": (520, 170),
    "line37_amount_owed": (520, 135),

    # Signature line
    "signature_line": (90, 70),
}

# --------------------------------------------------------------------
# Main PDF generator
# --------------------------------------------------------------------
def generate_form_1040(calc_data: dict, filing_status: str, taxpayer_name: str, ssn=None, address=None) -> bytes:
    """
    Draws the filled 1040 onto the static PDF using ReportLab overlay.
    Returns bytes for download or saving.
    """

    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    can.setFont("Helvetica", 10)

    # Header info
    if taxpayer_name:
        can.drawString(*COORDS["taxpayer_name"], taxpayer_name)
    if ssn:
        can.drawString(*COORDS["taxpayer_ssn"], ssn)
    if address:
        can.drawString(*COORDS["address_line"], address)

    # Filing-status checkmark
    filing_mark = {
        "single": COORDS["filing_status_single"],
        "married_filing_jointly": COORDS["filing_status_married_joint"],
        "married_filing_separately": COORDS["filing_status_married_sep"],
        "head_of_household": COORDS["filing_status_head"],
    }
    if filing_status in filing_mark:
        x, y = filing_mark[filing_status]
        can.setFont("Helvetica-Bold", 14)
        can.drawString(x, y, "✔")
        can.setFont("Helvetica", 10)

    # Numeric lines
    def draw_amount(key, value):
        if key in COORDS and value not in (None, "", "missing"):
            can.drawRightString(COORDS[key][0], COORDS[key][1], f"{float(value):,.2f}")

    draw_amount("line1a_wages", calc_data.get("wages") or calc_data.get("line1a_wages"))
    draw_amount("line2b_taxable_interest", calc_data.get("interest") or calc_data.get("line2b_taxable_interest"))
    draw_amount("line8_other_income", calc_data.get("nec") or calc_data.get("line8_other_income"))
    draw_amount("line11_AGI", calc_data.get("agi"))
    draw_amount("line12_standard_or_itemized", calc_data.get("standard_deduction"))
    draw_amount("line15_taxable_income", calc_data.get("taxable_income"))
    draw_amount("line16_tax", calc_data.get("estimated_tax"))
    draw_amount("line25a_withheld_w2", calc_data.get("withholding"))
    draw_amount("line25d_total_payments", calc_data.get("withholding"))
    draw_amount("line34_refund", calc_data.get("refund"))
    draw_amount("line37_amount_owed", calc_data.get("balance_due"))

    # Signature line
    can.drawString(*COORDS["signature_line"], "Taxpayer Signature: ____________________________   Date: __________")

    can.save()

    # Merge overlay onto template
    packet.seek(0)
    overlay_pdf = PdfReader(packet)
    template_pdf = PdfReader(open(TEMPLATE_PATH, "rb"))
    output = PdfWriter()

    base_page = template_pdf.pages[0]
    base_page.merge_page(overlay_pdf.pages[0])
    output.add_page(base_page)

    # add remaining pages unchanged
    for i in range(1, len(template_pdf.pages)):
        output.add_page(template_pdf.pages[i])

    out_bytes = io.BytesIO()
    output.write(out_bytes)
    out_bytes.seek(0)
    return out_bytes.getvalue()
