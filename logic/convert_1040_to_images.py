from pdf2image import convert_from_path
from pathlib import Path

def convert_1040_to_images(pdf_path: str, output_dir: str = "logic/templates") -> None:
    """
    Converts the official 1040 IRS PDF into PNG images (1 per page).
    These images will be used as background templates for ReportLab overlays.
    """
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    print(f"📄 Converting: {pdf_path}")
    pages = convert_from_path(pdf_path, dpi=300)

    for i, page in enumerate(pages, start=1):
        out_file = out_path / f"f1040_page{i}.png"
        page.save(out_file, "PNG")
        print(f"✅ Saved {out_file}")

    print("🎉 Conversion complete! You can now use these images in your ReportLab generator.")
    

if __name__ == "__main__":
    convert_1040_to_images("logic/templates/f1040.pdf")
