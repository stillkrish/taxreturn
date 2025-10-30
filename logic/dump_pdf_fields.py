# logic/dump_pdf_fields.py
from pypdf import PdfReader

def dump_fields(pdf_path="logic/templates/f1040.pdf", out_path="fields_1040.txt"):
    reader = PdfReader(pdf_path)
    fields = reader.get_form_text_fields()  # includes most AcroForm fields
    # Write a stable list for human mapping
    with open(out_path, "w", encoding="utf-8") as f:
        for k in sorted(fields.keys()):
            v = fields[k]
            f.write(f"{k} = {v}\n")
    print(f"Wrote {len(fields)} fields to {out_path}")

if __name__ == "__main__":
    dump_fields()
