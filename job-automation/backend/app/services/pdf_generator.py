from fpdf import FPDF
import os

def save_resume_pdf(text, filename):

    pdf = FPDF()
    pdf.set_auto_page_break(True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=11)

    for line in text.split("\n"):
        pdf.multi_cell(0, 6, line)

    os.makedirs("data/generated_resumes", exist_ok=True)

    path = f"data/generated_resumes/{filename}.pdf"
    pdf.output(path)

    return path