import pymupdf as fitz 
import argparse,base64
from typing import List, Tuple
# --- Utilities ---
def parse_pages_arg(pages_arg: str, max_pages: int) -> List[int]:
    """
    Parse CLI --pages like "11", "11-14", "3,5,9-12". Pages are 1-based.
    Clamp to [1, max_pages].
    """
    result = set()
    for part in pages_arg.split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-", 1)
            try:
                a = int(a)
                b = int(b)
                if a > b:
                    a, b = b, a
                for p in range(a, b + 1):
                    if 1 <= p <= max_pages:
                        result.add(p)
            except Exception as e:
                raise ValueError(f"Invalid page range. Error: {e}")
        else:
            try:
                p = int(part)
                if 1 <= p <= max_pages:
                    result.add(p)
            except Exception as e:
                raise ValueError(f"Invalid page number. Error: {e}")
    return sorted(result)

def extract_page(doc: fitz.Document, pages: List[int], max_width: int = 1600, jpg_quality: int = 80):
    out = []
    for i in pages:
        p = doc[i-1]
        rect = p.rect
        scale = min(max_width / float(rect.width or max_width), 4.0)
        mat = fitz.Matrix(scale, scale)
        pix = p.get_pixmap(matrix=mat, alpha=False)
        jpg = pix.tobytes("jpg", jpg_quality=jpg_quality)
        data_url = "data:image/jpeg;base64," + base64.b64encode(jpg).decode("ascii")
        out.append((i, {"type": "image_url", "image_url": {"url": data_url}}))
    return out

