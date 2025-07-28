import re
from pathlib import Path
from typing import List
import fitz  # PyMuPDF
from loguru import logger

def _is_likely_heading(span, avg_font_size):
    text = span["text"].strip()
    size = span["size"]
    is_bold = span["bold"]

    if not text or len(text) > 120:
        return False
    if size >= avg_font_size + 1.0:
        return True
    if is_bold and size >= avg_font_size - 0.5:
        return True

    # Fallback pattern checks
    patterns = [
    r'^\d+\.\s+[A-Z][a-zA-Z\s]{2,}',      # "1. Coastal Adventures"
    r'^[A-Z][A-Z\s]{4,100}$',             # ALL CAPS HEADINGS like "GENERAL INFORMATION"
    r'^[A-Z][a-z]+(\s[A-Z][a-z]+){1,20}$', # "Title Case Headings" up to 10 words
    r'^[A-Z][A-Za-z\s]{2,100}$'           # Flexible fallback for normal headings
    ]

    for pattern in patterns:
        if re.match(pattern, text) and len(text.split()) <= 8:
            return True
    return False

def parse_document(pdf_path: Path) -> List[dict]:
    logger.info(f"📄 Parsing document: {pdf_path.name}")

    doc = fitz.open(pdf_path)
    all_spans = []

    for page_num, page in enumerate(doc, start=1):
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    text = span["text"].strip()
                    if text:
                        all_spans.append({
                            "text": text,
                            "size": span["size"],
                            "bold": bool(span["flags"] & 2),
                            "page": page_num
                        })

    if not all_spans:
        logger.warning(f"No text found in {pdf_path.name}")
        return []

    font_sizes = [span["size"] for span in all_spans]
    avg_font_size = sum(font_sizes) / len(font_sizes)

    sections = []
    current_text = ""
    current_heading = None
    current_page = 1

    for span in all_spans:
        if _is_likely_heading(span, avg_font_size):
            if current_text.strip() and current_heading:
                sections.append({
                    "title": current_heading,
                    "text": current_text.strip(),
                    "page": current_page
                })
            current_heading = span["text"].strip()
            current_text = ""
            current_page = span["page"]
        else:
            current_text += " " + span["text"]

    # Final section
    if current_text.strip() and current_heading:
        sections.append({
            "title": current_heading,
            "text": current_text.strip(),
            "page": current_page
        })

    logger.success(f"✅ Extracted {len(sections)} sections from {pdf_path.name}")
    return sections
