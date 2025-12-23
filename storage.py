from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from datetime import datetime
from config import OUTPUT_FILE
import re

def save_doc(records):
    """
    Save articles to a properly formatted Word document.
    Uses Q&A format with top 5 questions extracted from article analysis.
    """
    document = Document()
    
    # Add title
    title = document.add_heading("Digital Health News Summary - Australia", level=1)
    title.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    
    # Add metadata
    meta = document.add_paragraph()
    meta.add_run(f"Generated: {datetime.now().strftime('%d %B %Y at %I:%M %p')}").italic = True
    meta.add_run(f"\nTotal Articles: {len(records)}").italic = True
    meta.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    
    document.add_paragraph()  # Spacing
    document.add_paragraph("_" * 80)  # Separator line
    document.add_paragraph()
    
    # Add each article
    for i, record in enumerate(records, 1):
        # Article header
        heading = document.add_heading(f"Article {i}: {record.get('Title', 'Untitled')}", level=2)
        
        # Extract Q&A pairs from summary
        summary = record.get('Summary', '')
        qa_pairs = extract_qa_pairs(summary)
        
        if qa_pairs:
            # Add each Q&A pair
            for q_num, (question, answer) in enumerate(qa_pairs, 1):
                # Question
                q_para = document.add_paragraph()
                q_para.add_run(f"Question {q_num}: {question}").bold = True
                
                # Answer
                a_para = document.add_paragraph()
                a_para.add_run(f"Answer: {answer}")
                
                # Add spacing between Q&A pairs
                if q_num < len(qa_pairs):
                    document.add_paragraph()
        else:
            # Fallback if parsing fails
            document.add_paragraph(summary)
        
        # Add metadata
        document.add_paragraph()
        document.add_paragraph("─" * 60)
        
        source_para = document.add_paragraph()
        source_para.add_run("Source: ").bold = True
        source_para.add_run(record.get('Link', 'N/A'))
        
        date_para = document.add_paragraph()
        date_para.add_run("Published: ").bold = True
        date_para.add_run(record.get('Date', 'N/A'))
        
        # Add separator between articles
        document.add_paragraph()
        document.add_paragraph("═" * 80)
        document.add_paragraph()
    
    # Save with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = OUTPUT_FILE.replace(".docx", f"_{timestamp}.docx")
    
    document.save(file_name)
    print(f"\n✅ Saved {len(records)} articles to {file_name}")
    print(f"📄 Format: Top 5 Questions & Answers (3-4 sentences each)")

def extract_qa_pairs(text: str) -> list:
    """
    Extract question and answer pairs from the structured summary text.
    Returns list of (question, answer) tuples.
    """
    if not text:
        return []
    
    qa_pairs = []
    
    # Pattern to match "Question X: ... Answer: ..."
    # This handles multi-line answers
    pattern = r'Question \d+:\s*(.+?)\s*Answer:\s*(.+?)(?=Question \d+:|$)'
    
    matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
    
    for question, answer in matches:
        # Clean up the text
        question = ' '.join(question.split()).strip()
        answer = ' '.join(answer.split()).strip()
        
        # Remove any trailing newlines or extra whitespace
        question = question.rstrip('?') + '?'  # Ensure question ends with ?
        
        if question and answer and len(answer) > 20:  # Ensure substantial content
            qa_pairs.append((question, answer))
    
    return qa_pairs