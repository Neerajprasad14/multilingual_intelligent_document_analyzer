import hashlib
import re
from pathlib import Path
from pypdf import PdfReader
from docx import Document


def extract_text(file_path: str) -> str:
    path = Path(file_path)
    ext = path.suffix.lower()

    if ext == ".pdf":
        reader = PdfReader(str(path))
        pages = []
        for i, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            pages.append(f"\n[Page {i}]\n{text}")
        return "\n".join(pages)

    if ext == ".docx":
        doc = Document(str(path))
        return "\n".join(p.text for p in doc.paragraphs)

    if ext == ".txt":
        return path.read_text(encoding="utf-8", errors="ignore")

    raise ValueError("Unsupported file type. Use PDF, DOCX or TXT.")


def clean_text(text: str) -> str:
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def chunk_text(text: str, chunk_size: int = 900, overlap: int = 150):
    words = text.split()
    chunks = []

    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    start = 0
    chunk_id = 0

    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end]).strip()

        if chunk:
            chunks.append({
                "id": chunk_id,
                "text": chunk,
                "start_word": start,
                "end_word": end
            })

        chunk_id += 1
        if end == len(words):
            break
        start = end - overlap

    return chunks


def process_document(file_path: str, chunk_size=900, overlap=150):
    text = clean_text(extract_text(file_path))
    if not text:
        raise ValueError("No readable text was found in the document.")

    chunks = chunk_text(text, chunk_size, overlap)

    raw_id = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]

    for c in chunks:
        c["doc_id"] = raw_id
        c["source"] = Path(file_path).name

    return raw_id, chunks
