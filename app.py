import json
import streamlit as st

from logic.parse_documents import parse_documents
from logic.tax_2024 import compute_tax_summary
# ✅ make sure this import name matches your actual file:
from logic.generate_form1040 import generate_form_1040

# ------------------------------------------------------------
# Streamlit Configuration
# ------------------------------------------------------------
st.set_page_config(page_title="AI Tax Return Agent (Demo)", layout="wide")

st.title("AI Tax Return Agent — Prototype")
st.caption(
    "Upload W-2 / 1099-INT / 1099-NEC PDFs. "
    "The app extracts income, calculates 2024 federal tax using the standard deduction, "
    "and generates a filled Form 1040 for review."
)

# ------------------------------------------------------------
# Sidebar: Filing Status & Taxpayer Info
# ------------------------------------------------------------
with st.sidebar:
    st.header("Filing Information")
    filing_status = st.selectbox(
        "Filing Status",
        ["single", "married_filing_jointly", "married_filing_separately", "head_of_household"],
        index=0,
    )

    # ✅ add the missing identity fields so they appear on the PDF
    taxpayer_name = st.text_input("Taxpayer Name", placeholder="John A. Doe")
    ssn = st.text_input("SSN", placeholder="123-45-6789")
    address = st.text_input("Address", placeholder="123 Main St, Irvine CA 92617")

# ------------------------------------------------------------
# File Upload
# ------------------------------------------------------------
uploaded = st.file_uploader(
    "Upload one or more tax PDFs", type=["pdf"], accept_multiple_files=True
)

# ------------------------------------------------------------
# Processing Logic
# ------------------------------------------------------------
if uploaded:
    # Step 1 – Parse documents
    parsed = parse_documents(uploaded)
    st.subheader("Parsed Documents")
    st.json(parsed["documents"], expanded=False)

    # Step 2 – Compute totals
    s = parsed["summary"]
    income_components = {
        "w2_wages": float(s["income"].get("w2_wages", 0.0)),
        "interest": float(s["income"].get("int_interest", 0.0)),
        "nec": float(s["income"].get("nec_nonemployee_comp", 0.0)),
    }
    total_withholding = float(s["withholding"].get("federal", 0.0))

    # Step 3 – Compute Tax Summary
    calc = compute_tax_summary(
        income_components=income_components,
        total_withholding=total_withholding,
        filing_status=filing_status,
    )

    # Step 4 – Show summary metrics
    st.subheader("Tax Summary (2024)")
    col1, col2, col3 = st.columns(3)
    col1.metric("AGI", f"${calc['agi']:.2f}")
    col2.metric("Taxable Income", f"${calc['taxable_income']:.2f}")
    col3.metric("Estimated Tax", f"${calc['estimated_tax']:.2f}")
    col1.metric("Withholding", f"${calc['withholding']:.2f}")
    col2.metric("Refund", f"${calc['refund']:.2f}")
    col3.metric("Balance Due", f"${calc['balance_due']:.2f}")

    # JSON details
    st.code(json.dumps(calc, indent=2), language="json")

    # ------------------------------------------------------------
    # Step 5 – Generate & Download 1040 PDF
    # ------------------------------------------------------------
    try:
        pdf_bytes = generate_form_1040(
            calc_data=calc,
            filing_status=filing_status,
            taxpayer_name=taxpayer_name,
            ssn=ssn,
            address=address,
        )

        st.success("✅ Form 1040 generated successfully!")

        # ✅ download button
        st.download_button(
            "📄 Download Filled Form 1040 (PDF)",
            data=pdf_bytes,
            file_name="Form1040_Filled.pdf",
            mime="application/pdf",
        )

        # ✅ optional inline preview inside the app
        import base64
        pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")
        st.markdown(
            f'<iframe src="data:application/pdf;base64,{pdf_base64}" '
            'width="700" height="950" type="application/pdf"></iframe>',
            unsafe_allow_html=True,
        )

    except FileNotFoundError as e:
        st.error(str(e))
    except Exception as e:
        st.error(f"❌ Error generating Form 1040: {e}")

else:
    st.info("📤 Upload at least one PDF to begin.")
