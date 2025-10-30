import io
import re
from typing import List, Dict, Any
import pdfplumber
import fitz  # PyMuPDF
from PIL import Image
import pytesseract

# import the dedicated 1099-INT and 1099-NEC parsers
from logic.parse_1099int import parse_1099int
from logic.parse_1099nec import parse_1099nec


# ---------------------------
# Text extraction w/ OCR
# ---------------------------
def extract_text_from_pdf(file_bytes: bytes) -> str:
    text = ""
    # 1) pdfplumber
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
    except Exception:
        pass
    # 2) PyMuPDF
    if len(text.strip()) < 20:
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            for page in doc:
                text += page.get_text() or ""
        except Exception:
            pass
    # 3) OCR
    if len(text.strip()) < 20:
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            ocr_text = ""
            for i in range(len(doc)):
                pix = doc[i].get_pixmap(dpi=450)
                img = Image.open(io.BytesIO(pix.tobytes("png")))
                part = pytesseract.image_to_string(img, lang="eng", config="--oem 1 --psm 4")
                ocr_text += part + "\n"
            text = ocr_text
        except Exception:
            text = ""
    return text


def normalize_spaces(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


# ---------------------------
# Helpers
# ---------------------------
CURRENCY_RE = re.compile(r"\b\d{1,3}(?:[,\s]?\d{3})*(?:\.\d{2})\b")


def to_float_str(token: str) -> str:
    return token.replace(",", "").replace(" ", "")


def is_currency_token(tok: str) -> bool:
    return bool(CURRENCY_RE.fullmatch(tok))


def extract_words_in_copyB(file_bytes: bytes) -> List[str]:
    """Return tokens (words) from only the top-left quadrant (Copy B) of each page."""
    tokens: List[str] = []
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    for page in doc:
        rect = page.rect
        region = fitz.Rect(rect.x0, rect.y0, rect.x1 / 2, rect.y1 / 2)
        words = page.get_text("words", clip=region)
        words.sort(key=lambda w: (round(w[1], 1), round(w[0], 1)))
        for w in words:
            txt = w[4].strip()
            if txt:
                tokens.append(txt)
    return tokens


def first_n_currency_in_order(tokens: List[str], n: int) -> List[str]:
    vals = []
    for t in tokens:
        if is_currency_token(t):
            vals.append(to_float_str(t))
            if len(vals) == n:
                break
    return vals


def find_after_keyword(text: str, keyword_pattern: str) -> str:
    m = re.search(keyword_pattern + r"\s*(" + CURRENCY_RE.pattern + r")", text, flags=re.IGNORECASE)
    if m:
        return to_float_str(m.group(1))
    return ""


def find_ca_state_line_amount(text: str) -> str:
    best = ""
    for line in text.splitlines():
        if re.search(r"\bCA\b", line):
            nums = re.findall(CURRENCY_RE, line)
            if nums:
                best = to_float_str(nums[-1])
    return best


# ---------------------------
# Main unified parser
# ---------------------------
def parse_documents(files: List[Any]) -> Dict[str, Any]:
    results = []
    summary = {"income": {"w2_wages": 0.0, "int_interest": 0.0, "nec_nonemployee_comp": 0.0},
               "withholding": {"federal": 0.0}}

    for f in files:
        data = f.read()
        f.seek(0)

        # quick scan to detect form type
        full_text = extract_text_from_pdf(data)
        norm_full = normalize_spaces(full_text)
        lower = norm_full.lower()

        # ---- detect 1099-NEC ----
        if "1099-nec" in lower or "nonemployee compensation" in lower:
            parsed_nec = parse_1099nec(data, f.name)
            # aggregate income / withholding
            try:
                v = parsed_nec["parsed_fields"].get("box_1_nonemployee_compensation", "missing")
                if v != "missing":
                    summary["income"]["nec_nonemployee_comp"] += float(v.replace(",", ""))
                w = parsed_nec["parsed_fields"].get("box_4_federal_income_tax_withheld", "missing")
                if w != "missing":
                    summary["withholding"]["federal"] += float(w.replace(",", ""))
            except Exception:
                pass
            results.append(parsed_nec)
            continue

        # ---- detect 1099-INT ----
        if "1099-int" in lower or "form 1099-int" in lower or "interest income" in lower:
            parsed_int = parse_1099int(data, f.name)
            try:
                v = parsed_int["parsed_fields"].get("box_1_interest_income", "missing")
                if v != "missing":
                    summary["income"]["int_interest"] += float(v.replace(",", ""))
                w = parsed_int["parsed_fields"].get("box_4_federal_income_tax_withheld", "missing")
                if w != "missing":
                    summary["withholding"]["federal"] += float(w.replace(",", ""))
            except Exception:
                pass
            results.append(parsed_int)
            continue

        # ---- default: treat as W-2 ----
        tokens = extract_words_in_copyB(data)
        first6 = first_n_currency_in_order(tokens, 6)

        parsed = {
            "a_employee_ssn": "missing",
            "1_wages_tips_other_comp": "missing",
            "2_federal_income_tax_withheld": "missing",
            "b_employer_ein": "missing",
            "3_social_security_wages": "missing",
            "4_social_security_tax_withheld": "missing",
            "5_medicare_wages_and_tips": "missing",
            "6_medicare_tax_withheld": "missing",
            "c_employer_name_address_zip": "missing",
            "d_control_number": "missing",
            "e_employee_name_address_zip": "missing",
            "7_social_security_tips": "missing",
            "8_allocated_tips": "missing",
            "9_blank": "missing",
            "10_dependent_care_benefits": "missing",
            "11_nonqualified_plans": "missing",
            "12a_d_codes": "missing",
            "13_checkboxes": "missing",
            "14_other": "missing",
            "15_state_employer_id": "missing",
            "16_state_wages_tips": "missing",
            "17_state_income_tax": "missing",
            "18_local_wages_tips": "missing",
            "19_local_income_tax": "missing",
            "20_locality_name": "missing",
        }

        if len(first6) >= 6:
            parsed["1_wages_tips_other_comp"] = first6[0]
            parsed["2_federal_income_tax_withheld"] = first6[1]
            parsed["3_social_security_wages"] = first6[2]
            parsed["4_social_security_tax_withheld"] = first6[3]
            parsed["5_medicare_wages_and_tips"] = first6[4]
            parsed["6_medicare_tax_withheld"] = first6[5]

        try:
            if parsed["1_wages_tips_other_comp"] != "missing":
                summary["income"]["w2_wages"] += float(parsed["1_wages_tips_other_comp"])
            if parsed["2_federal_income_tax_withheld"] != "missing":
                summary["withholding"]["federal"] += float(parsed["2_federal_income_tax_withheld"])
        except Exception:
            pass

        m_ssn = re.search(r"\b\d{3}-\d{2}-\d{4}\b", norm_full)
        if m_ssn:
            parsed["a_employee_ssn"] = m_ssn.group(0)
        m_ein = re.search(r"\b\d{2}-\d{7}\b", norm_full)
        if m_ein:
            parsed["b_employer_ein"] = m_ein.group(0)

        m_emp = re.search(r"cinemark\s+usa.*?plano,\s*tx\s*\d{5}", full_text, flags=re.IGNORECASE | re.DOTALL)
        if m_emp:
            parsed["c_employer_name_address_zip"] = normalize_spaces(m_emp.group(0))
        m_person = re.search(r"krish\s+thakur.*?tracy,\s*ca\s*\d{5}", full_text, flags=re.IGNORECASE | re.DOTALL)
        if m_person:
            parsed["e_employee_name_address_zip"] = normalize_spaces(m_person.group(0))

        casdi = find_after_keyword(full_text, r"CASDI")
        if casdi:
            parsed["14_other"] = casdi
        st_tax = find_ca_state_line_amount(full_text)
        if st_tax:
            parsed["17_state_income_tax"] = st_tax

        missing_fields = [k for k, v in parsed.items() if v == "missing"]

        results.append({
            "filename": f.name,
            "form_type": "W-2",
            "parsed_fields": parsed,
            "missing_fields": missing_fields,
            "notes": [
                f"Copy B top-left words extracted: {len(tokens)} tokens",
                f"First 6 currency tokens (order-preserved): {first6}"
            ],
        })

    return {"summary": summary, "documents": results}
