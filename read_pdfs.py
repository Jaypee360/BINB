import PyPDF2
import os

pdf_files = [
    "Final Exam - SW Project W26 (1).pdf",
    "BINB_ProjectProposal.pdf",
    "3 Agile Process W26.pdf",
    "4 Requirements Engg W26.pdf",
    "5 System Model W26.pdf",
    "6 Architectural Design W26.pdf"
]

for pdf in pdf_files:
    if os.path.exists(pdf):
        print(f"Reading {pdf}...")
        try:
            with open(pdf, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            out_file = pdf.replace(".pdf", ".txt")
            with open(out_file, "w", encoding="utf-8") as out:
                out.write(text)
            print(f"Saved to {out_file}")
        except Exception as e:
            print(f"Error reading {pdf}: {e}")
    else:
        print(f"{pdf} not found.")
