from fpdf import FPDF
from pathlib import Path

def save_resume_pdf(text, filename):
    pdf = FPDF()
    pdf.set_auto_page_break(True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=11)

    for line in text.split("\n"):
        pdf.multi_cell(0, 6, line)

    output_dir = Path(__file__).resolve().parents[2] / "data" / "generated_resumes"
    output_dir.mkdir(parents=True, exist_ok=True)

    path = output_dir / f"{filename}.pdf"
    pdf.output(str(path))

    return str(path)
