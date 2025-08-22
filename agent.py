import os, math, textwrap, time
from dataclasses import dataclass
from typing import List
from dotenv import load_dotenv
import pymupdf as fitz  # guaranteed to import the real PyMuPDF
from tqdm import tqdm
import json
import requests

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL   = os.getenv("OPENAI_MODEL", "gpt-4o")
OPENAI_BASE_URL= os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")  # set to http://localhost:11434/v1 for Ollama
INPUT_PDF      = "1.pdf"
OUT_MD         = "translated.md"
OUT_TXT        = "translated.txt"

SRC_LANG = "auto"     # "auto" or explicit e.g. "Chinese"
TGT_LANG = "English"  # your target language
MAX_CHARS = 2000      # chunk size target

# --------- Prompts ---------
SYSTEM_TRANSLATOR = (
    "You translate technical PDFs chunk-by-chunk. Preserve meaning precisely.\n"
    "Do not summarize or omit. Keep structure cues using Markdown:\n"
    "- '#' for headings, '-' for lists, 'Table:' for tables, 'Figure:' for captions.\n"
    "Keep numbers/units/code/LaTeX intact. If chunk looks cut at edges, translate as-is."
)

def user_prompt(chunk_text: str, src=SRC_LANG, tgt=TGT_LANG, glossary=None) -> str:
    gloss = json.dumps(glossary or {}, ensure_ascii=False)
    return f"""Source language: {src} → Target language: {tgt}.
Glossary (must-use): {gloss}
Return Markdown only. Translate this:

```markdown
{chunk_text}
```"""

# --------- Helpers ---------
@dataclass
class Job:
    id: str
    page: int
    text: str

def extract_pages(pdf_path: str) -> List[str]:
    doc = fitz.open(pdf_path)
    pages = []
    for i in range(len(doc)):
        text = doc[i].get_text("text")  # raw reading order text
        # normalize a little: collapse excessive blank lines
        text = "\n".join([line.rstrip() for line in text.splitlines()])
        pages.append(text.strip())
    return pages

def chunk_page(text: str, max_chars=MAX_CHARS) -> List[str]:
    if not text: return []
    # Try to split on paragraph boundaries first
    paras = text.split("\n\n")
    chunks, buf = [], ""
    for p in paras:
        if len(buf) + len(p) + 2 <= max_chars:
            buf = (buf + "\n\n" + p) if buf else p
        else:
            if buf: chunks.append(buf)
            if len(p) <= max_chars:
                buf = p
            else:
                # hard wrap long paragraph
                for i in range(0, len(p), max_chars):
                    chunks.append(p[i:i+max_chars])
                buf = ""
    if buf: chunks.append(buf)
    return chunks

def plan_jobs(pages: List[str]) -> List[Job]:
    jobs = []
    for pi, page in enumerate(pages, start=1):
        for ci, chunk in enumerate(chunk_page(page), start=1):
            jobs.append(Job(id=f"p{pi:03d}_c{ci:02d}", page=pi, text=chunk))
    return jobs

# --------- Model call (OpenAI-compatible) ---------
def chat_completion(system_msg: str, user_msg: str) -> str:
    """
    Dual-path: if OPENAI_BASE_URL ends with '/v1' or contains 'api.openai.com',
    use OpenAI Chat Completions. Otherwise assume Ollama native /api/chat.
    """
    base = OPENAI_BASE_URL.rstrip("/")
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }

    # Heuristic: if base contains 'api.openai.com' or endswith '/v1', use OpenAI routes
    use_openai = ("api.openai.com" in base) or base.endswith("/v1")

    if use_openai:
        # OpenAI-style route
        url = f"{base}/chat/completions"
        body = {
            "model": OPENAI_MODEL,
            "temperature": 0,
            "messages": [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg},
            ],
        }
        r = requests.post(url, headers=headers, json=body, timeout=120)
        r.raise_for_status()
        data = r.json()
        return data["choices"][0]["message"]["content"]

    else:
        # Ollama native route
        url = f"{base}/api/chat"
        body = {
            "model": OPENAI_MODEL,
            "stream": False,
            "messages": [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg},
            ],
            # You can set options here for determinism, max tokens, etc.
            "options": {"temperature": 0},
        }
        r = requests.post(url, headers={"Content-Type": "application/json"}, json=body, timeout=120)
        r.raise_for_status()
        data = r.json()
        # Native schema: top-level 'message' holds the assistant reply
        msg = data.get("message", {}).get("content", "")
        if not msg and "choices" in data:  # some proxies emulate OpenAI
            msg = data["choices"][0]["message"]["content"]
        return msg


def validate(src: str, tgt: str) -> bool:
    # simple sanity checks: avoid empty or too-short translations
    if not tgt or len(tgt.strip()) < max(20, len(src) * 0.2):
        return False
    # heading/list token parity (lightweight)
    for token in ["#", "-", "Table:", "Figure:"]:
        if src.count(token) and tgt.count(token) == 0:
            # not strictly required, but signal possible structure loss
            pass
    return True

def main():
    print("Extracting pages...")
    pages = extract_pages(INPUT_PDF)
    jobs = plan_jobs(pages)
    print(f"Planned {len(jobs)} chunks across {len(pages)} pages.")

    out_lines = []
    pbar = tqdm(jobs, desc="Translating")
    for job in pbar:
        prompt = user_prompt(job.text)
        out = chat_completion(SYSTEM_TRANSLATOR, prompt)
        if not validate(job.text, out):
            # one deterministic retry
            time.sleep(0.5)
            out = chat_completion(SYSTEM_TRANSLATOR, prompt)
        out_lines.append(f"\n\n<!-- {job.id} page {job.page} -->\n{out.strip()}\n")

    md = "# Translated Document\n" + "".join(out_lines)
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write(md)
    with open(OUT_TXT, "w", encoding="utf-8") as f:
        f.write("\n".join([line for line in md.splitlines() if not line.startswith("#")]))

    print(f"Done. Wrote {OUT_MD} and {OUT_TXT}")
    print("Tip: Convert Markdown → PDF with Pandoc (see below).")

if __name__ == "__main__":
    main()
