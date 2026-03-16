import fitz  # PyMuPDF
import re
import os
from database import SessionLocal
from models import SourceDocument, ContentChunk

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract all text from a PDF file."""
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    doc.close()
    return full_text

def clean_text(text: str) -> str:
    """Remove extra whitespace and garbage characters."""
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = text.strip()
    return text

def chunk_text(text: str, chunk_size: int = 500) -> list:
    """Break text into chunks of roughly chunk_size characters."""
    # Split by newlines instead of periods
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    chunks = []
    current_chunk = ""

    for line in lines:
        if len(current_chunk) + len(line) < chunk_size:
            current_chunk += line + "\n"
        else:
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
            current_chunk = line + "\n"

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    # If we only got 1 chunk, split it in half
    if len(chunks) == 1 and len(chunks[0]) > 200:
        mid = len(chunks[0]) // 2
        chunks = [chunks[0][:mid], chunks[0][mid:]]

    return chunks

def detect_subject_grade(filename: str):
    """Detect subject and grade from filename."""
    filename = filename.lower()
    subject = "General"
    grade = 1

    if "english" in filename or "grammar" in filename:
        subject = "English"
    elif "science" in filename or "plants" in filename:
        subject = "Science"
    elif "math" in filename or "numbers" in filename:
        subject = "Math"

    for i in range(1, 13):
        if f"grade{i}" in filename or f"grade_{i}" in filename:
            grade = i
            break

    return subject, grade

def ingest_pdf(pdf_path: str, filename: str):
    """Full ingestion pipeline: extract → clean → chunk → store."""
    db = SessionLocal()
    try:
        raw_text = extract_text_from_pdf(pdf_path)
        clean = clean_text(raw_text)
        chunks = chunk_text(clean)
        subject, grade = detect_subject_grade(filename)

        source = SourceDocument(
            filename=filename,
            subject=subject,
            grade=grade
        )
        db.add(source)
        db.flush()

        for i, chunk_text_val in enumerate(chunks):
            chunk = ContentChunk(
                source_id=source.id,
                topic=f"{subject} - Part {i+1}",
                text=chunk_text_val
            )
            db.add(chunk)

        db.commit()
        return {
            "source_id": source.id,
            "chunks_created": len(chunks),
            "subject": subject,
            "grade": grade
        }

    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
