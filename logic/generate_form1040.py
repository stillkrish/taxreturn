import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def generate_form_1040(calc_data, filing_status, taxpayer_name, ssn, address):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    # --- PAGE 1 ---
    c.drawImage("logic/templates/f1040_page1.png", 0, 0, width=612, height=792)
    c.setFont("Helvetica", 10)
    c.drawString(100, 720, taxpayer_name)
    c.drawString(400, 720, ssn)
    c.drawString(100, 700, address)

    # Income fields
    c.drawRightString(510, 490, f"{calc_data['agi']:.2f}")
    c.drawRightString(510, 460, f"{calc_data['taxable_income']:.2f}")
    c.drawRightString(510, 430, f"{calc_data['estimated_tax']:.2f}")
    c.drawRightString(510, 390, f"{calc_data['withholding']:.2f}")
    c.drawRightString(510, 360, f"{calc_data['refund']:.2f}")
    c.drawRightString(510, 330, f"{calc_data['balance_due']:.2f}")

    c.showPage()
    c.drawImage("logic/templates/f1040_page2.png", 0, 0, width=612, height=792)
    c.save()

    buffer.seek(0)
    return buffer.getvalue()
