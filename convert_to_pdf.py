#!/usr/bin/env python3
"""
Convert application text files to PDF
Usage: python3 convert_to_pdf.py <job_id>
"""

import sys
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

def convert_application_to_pdf(job_id):
    """Convert resume and cover letter to PDF"""

    # Find application folder
    app_folders = list(Path("applications").glob(f"*_{job_id}*")) + list(Path("applications").glob(f"*AI*"))

    # Find most recent folder for this job
    matching_folders = [f for f in Path("applications").iterdir() if f.is_dir() and (str(job_id) in f.name or "AI" in f.name)]

    if not matching_folders:
        print(f"No application folder found for job #{job_id}")
        return False

    # Use most recent
    app_folder = sorted(matching_folders, key=lambda x: x.stat().st_mtime, reverse=True)[0]
    print(f"Processing: {app_folder}")

    # Find text files
    resume_txt = app_folder / "Matthew_Scott_Resume_AI_Transition.txt"
    cover_txt = app_folder / "Matthew_Scott_Cover_Letter.txt"

    if not resume_txt.exists():
        resume_txt = list(app_folder.glob("*Resume*.txt"))[0] if list(app_folder.glob("*Resume*.txt")) else None
    if not cover_txt.exists():
        cover_txt = list(app_folder.glob("*Cover*.txt"))[0] if list(app_folder.glob("*Cover*.txt")) else None

    if not resume_txt or not cover_txt:
        print(f"Text files not found in {app_folder}")
        return False

    # Convert resume
    resume_pdf = app_folder / "Matthew_Scott_Resume.pdf"
    create_simple_pdf(resume_txt, resume_pdf)
    print(f"Created: {resume_pdf}")

    # Convert cover letter
    cover_pdf = app_folder / "Matthew_Scott_Cover_Letter.pdf"
    create_simple_pdf(cover_txt, cover_pdf)
    print(f"Created: {cover_pdf}")

    print(f"\nPDFs ready for submission in: {app_folder}")
    return True

def create_simple_pdf(text_file, pdf_file):
    """Create PDF from text file"""
    with open(text_file, 'r') as f:
        content = f.read()

    c = canvas.Canvas(str(pdf_file), pagesize=letter)
    width, height = letter

    # Set up text object
    text_obj = c.beginText(0.75 * inch, height - 0.75 * inch)
    text_obj.setFont("Helvetica", 10)

    # Add text line by line
    for line in content.split('\n'):
        if len(line) > 90:
            # Wrap long lines
            words = line.split()
            current_line = ""
            for word in words:
                if len(current_line + word) < 90:
                    current_line += word + " "
                else:
                    text_obj.textLine(current_line)
                    current_line = word + " "
            if current_line:
                text_obj.textLine(current_line)
        else:
            text_obj.textLine(line)

        # Check if we need a new page
        if text_obj.getY() < inch:
            c.drawText(text_obj)
            c.showPage()
            text_obj = c.beginText(0.75 * inch, height - 0.75 * inch)
            text_obj.setFont("Helvetica", 10)

    c.drawText(text_obj)
    c.save()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 convert_to_pdf.py <job_id>")
        print("\nExample: python3 convert_to_pdf.py 74")
        sys.exit(1)

    convert_application_to_pdf(int(sys.argv[1]))
