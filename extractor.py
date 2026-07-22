"""
extractor.py
------------
Reads PDF / DOCX / TXT lecture files and returns:
  - Full text content (str)
  - Filtered list of meaningful page images (list[dict])

Image filtering uses pixel variance and unique-color count to
skip blank pages, cover pages, and title slides.
"""

import os
from PIL import Image
import numpy as np


def is_informative_image(pil_img: Image.Image) -> bool:
    """
    Returns True only if the image contains actual visual content.

    Rejects:
      - Near-uniform images (std < 20) — blank / solid-colour pages
      - Images with very few unique colours (<50) — simple title slides
    """
    arr = np.array(pil_img)
    if arr.std() < 20:
        return False
    unique_colors = len(np.unique(arr.reshape(-1, arr.shape[-1]), axis=0))
    return unique_colors >= 50


def extract_text_and_images(filepath: str) -> tuple[str, list[dict]]:
    """
    Parameters
    ----------
    filepath : str
        Path to a .pdf, .docx, .txt, or .md file.

    Returns
    -------
    text : str
        Full extracted text content.
    images : list[dict]
        Each dict has keys: 'page' (int), 'pil' (PIL.Image), 'page_text' (str).
        Only meaningful pages are included.
    """
    ext = os.path.splitext(filepath)[1].lower()

    if ext == ".pdf":
        return _extract_pdf(filepath)
    elif ext == ".docx":
        return _extract_docx(filepath)
    elif ext in (".txt", ".md"):
        return _extract_text(filepath)
    else:
        raise ValueError(f"Unsupported file format: {ext}. Use PDF, DOCX, TXT, or MD.")


# ── Private helpers ────────────────────────────────────────────────────────────

def _extract_pdf(filepath: str) -> tuple[str, list[dict]]:
    try:
        import fitz  # PyMuPDF
    except ImportError:
        raise ImportError("PyMuPDF is required for PDF support. Run: pip install PyMuPDF")

    doc = fitz.open(filepath)
    full_text = ""
    images = []

    for page_num, page in enumerate(doc):
        page_text = page.get_text()
        full_text += page_text

        # Skip cover page
        if page_num == 0:
            continue

        # Skip pages with no embedded images
        if not page.get_images(full=True):
            continue

        # Skip title-only pages (very little text)
        if len(page_text.split()) < 10:
            continue

        # Render page as high-res screenshot (2× scale)
        mat = fitz.Matrix(2, 2)
        pix = page.get_pixmap(matrix=mat)
        pil_img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        if not is_informative_image(pil_img):
            continue

        images.append({
            "page":      page_num + 1,
            "pil":       pil_img,
            "page_text": page_text.strip(),
        })

    return full_text.strip(), images


def _extract_docx(filepath: str) -> tuple[str, list[dict]]:
    try:
        import docx
    except ImportError:
        raise ImportError("python-docx is required. Run: pip install python-docx")

    doc = docx.Document(filepath)
    text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    return text.strip(), []


def _extract_text(filepath: str) -> tuple[str, list[dict]]:
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        return f.read().strip(), []
