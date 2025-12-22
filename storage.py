from docx import Document
from datetime import datetime
from config import OUTPUT_FILE

def save_doc(records):
    document = Document()
    document.add_heading("Digital Health News Summary", level=1)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    
    file_name = OUTPUT_FILE.replace(".docx", f"_{timestamp}.docx")

    for i, record in enumerate(records, 1):
        document.add_heading(f"Article {i}", level=2)
        for key, value in record.items():
            p = document.add_paragraph()
            p.add_run(f"{key}: ").bold = True
            p.add_run(str(value))
        document.add_paragraph()  # blank line

    document.save(file_name)
    print(f"✅ Saved {len(records)} articles to {file_name}")