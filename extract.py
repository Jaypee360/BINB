import pypdf
reader = pypdf.PdfReader('BINB_ProjectProposal.pdf')
for page in reader.pages:
    print(page.extract_text())
