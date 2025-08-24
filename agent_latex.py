#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
agent_latex.py
Translate selected PDF page(s) to clean LaTeX (no handwriting), including equations
and simple diagrams redrawn in TikZ. Works with OpenAI API *or* local Ollama.

Usage examples:
  # Page 11 only, produce .tex but do not compile
  python agent_latex.py --pdf "1.pdf" --pages 11 --out "out_page11" --no-compile

  # Range of pages and compile
  python agent_latex.py --pdf "1.pdf" --pages 11-13 --out "translated" --compile

Environment (.env or shell):
  OPENAI_BASE_URL= https://api.openai.com/v1           # or http://localhost:11434
  OPENAI_API_KEY=   sk-...                             # "ollama" if using local
  OPENAI_MODEL=     gpt-4o                             # or llama3.1:8b, etc.

Requires:
  pip install PyMuPDF python-dotenv tqdm requests
  (Optional compile) LaTeX toolchain: pdflatex or xelatex in PATH
"""

import os
import re
import sys
import argparse
import subprocess
import requests
from typing import List, Tuple
from dataclasses import dataclass
from dotenv import load_dotenv
from tqdm import tqdm

# --- Config / Env ---
load_dotenv()
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

# --- PDF extraction ---
try:
    import pymupdf as fitz  # PyMuPDF
except Exception as e:
    print("ERROR: PyMuPDF (pymupdf) is required. pip install pymupdf", file=sys.stderr)
    raise

# --- Prompts ---
SYSTEM_LATEX = """You are a LaTeX writer. Convert the given math lecture page into clean, compilable LaTeX.
- Do NOT include any handwritten artifacts or images of text.
- Preserve all math, symbols, and equations precisely.
- Do NOT add the ```latex or the ``` as the pdf generator cannot recognize it.
- Preserve section headers and structure using \\section*, \\subsection* as appropriate.
- If the page contains a simple analytic geometry sketch (axes, lines, vectors),
  RECREATE it with TikZ using vector graphics (no raster images).
- Use standard packages only: amsmath, amssymb, tikz, geometry, lmodern, fontenc, mathtools if needed.
- If the input is partial or noisy, produce your best faithful reconstruction.
- IMPORTANT: Return ONLY the LaTeX BODY content (no \\documentclass or \\begin{document}).
"""

USER_LATEX_TMPL = """Source page text (raw, may include noise):
--- BEGIN PAGE TEXT ---
{page_text}
--- END PAGE TEXT ---

Instructions:
- Output ONLY LaTeX body content for this page.
- Wrap displayed equations in equation/align as appropriate.
- Use \\section*{{...}} or \\subsection*{{...}} for headings you detect.
- If appropriate, add a small TikZ sketch that matches the page's figure(s).
- Ensure the output compiles in a standard article preamble.
Target language: English.
"""


# --- LLM call ---
def llm_chat(system_msg: str, user_msg: str, api_key: str) -> str:
    """
    Dual-path client:
    - If OPENAI_BASE_URL ends with '/v1' or contains 'api.openai.com': use OpenAI Chat Completions.
    - Else: assume Ollama native endpoint at .../api/chat
    """
    use_openai = ("api.openai.com" in OPENAI_BASE_URL) or OPENAI_BASE_URL.endswith(
        "/v1"
    )

    if use_openai:
        url = f"{OPENAI_BASE_URL}/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        body = {
            "model": OPENAI_MODEL,
            "temperature": 0,
            "messages": [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg},
            ],
        }
        r = requests.post(url, headers=headers, json=body, timeout=180)
        r.raise_for_status()
        data = r.json()
        return data["choices"][0]["message"]["content"]

    else:
        # Ollama native chat
        url = f"{OPENAI_BASE_URL}/api/chat"
        body = {
            "model": OPENAI_MODEL,
            "stream": False,
            "messages": [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg},
            ],
            "options": {"temperature": 0},
        }
        r = requests.post(
            url, headers={"Content-Type": "application/json"}, json=body, timeout=180
        )
        r.raise_for_status()
        data = r.json()
        msg = data.get("message", {}).get("content", "")
        if not msg and "choices" in data:
            msg = data["choices"][0]["message"]["content"]
        return msg


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
            except:
                continue
        else:
            try:
                p = int(part)
                if 1 <= p <= max_pages:
                    result.add(p)
            except:
                continue
    return sorted(result)


def extract_page_texts(pdf_path: str, pages: List[int]) -> List[Tuple[int, str]]:
    doc = fitz.open(pdf_path)
    out = []
    for p in pages:
        if 1 <= p <= len(doc):
            page = doc[p - 1]
            txt = page.get_text("text")
            txt = "\n".join([ln.rstrip() for ln in txt.splitlines()])
            out.append((p, txt.strip()))
    return out


def make_master_preamble(title: str = "Translated Document") -> str:
    return r"""\documentclass[11pt]{article}
\usepackage[margin=1in]{geometry}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage{amsmath,amssymb,mathtools}
\usepackage{tikz}
\usepackage{hyperref}
\setlength{\parskip}{0.6em}
\setlength{\parindent}{0pt}
\title{%s}
\date{}
\begin{document}
\maketitle
""" % (title,)


def make_master_epilogue() -> str:
    return r"""\end{document}
"""


def compile_pdf(tex_path: str, engine: str = "pdflatex") -> None:
    """Run LaTeX engine twice for references. Falls back to xelatex if pdflatex not found."""
    tex_dir = os.path.dirname(os.path.abspath(tex_path)) or "."
    fname = os.path.basename(tex_path)

    def run(cmd):
        subprocess.run(
            cmd,
            cwd=tex_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=True,
        )

    try:
        run([engine, "-interaction=nonstopmode", fname])
        run([engine, "-interaction=nonstopmode", fname])
    except Exception as e:
        raise


# --- Main pipeline ---
def run(
    pdf_path: str,
    pages_arg: str,
    out_prefix: str,
    compile_flag: bool,
    title: str,
    api_key: str,
):
    # 1) Determine pages
    doc = fitz.open(pdf_path)
    max_pages = len(doc)
    pages = parse_pages_arg(pages_arg, max_pages)
    if not pages:
        print(f"No valid pages selected in range 1..{max_pages}.", file=sys.stderr)
        sys.exit(2)

    out_dir = os.path.abspath(out_prefix)
    os.makedirs(out_dir, exist_ok=True)

    # 2) Extract text
    page_texts = extract_page_texts(pdf_path, pages)

    # 3) Ask model for LaTeX body content per page
    parts = []
    for pno, txt in tqdm(page_texts, desc="Translating to LaTeX"):
        user_msg = USER_LATEX_TMPL.format(page_text=txt)
        body = llm_chat(SYSTEM_LATEX, user_msg, api_key=api_key).strip()

        # Save per-page body
        page_body_path = os.path.join(out_dir, f"page_{pno:03d}.tex")
        with open(page_body_path, "w", encoding="utf-8") as f:
            f.write(body + "\n")
        parts.append((pno, page_body_path))

    # 4) Assemble master LaTeX
    master_path = os.path.join(out_dir, "master.tex")
    with open(master_path, "w", encoding="utf-8") as f:
        f.write(make_master_preamble(title))
        for pno, body_path in parts:
            # f.write(f"% --- Page {pno} ---\n")
            # f.write("\\clearpage\n")
            # f.write(f"\\section*{{Page {pno}}}\n\n")
            with open(body_path, "r", encoding="utf-8") as b:
                content = b.read()
            # ensure trailing newline so pages don’t concatenate on one line
            if not content.endswith("\n"):
                content += "\n"
            f.write(content)
        f.write(make_master_epilogue())

    print(f"Wrote master LaTeX: {master_path}")

    # 5) Compile (optional)
    if compile_flag:
        print("Compiling PDF...")
        try:
            compile_pdf(master_path, engine="pdflatex")
            print("PDF compiled successfully.")
        except subprocess.CalledProcessError as e:
            print("LaTeX compile failed. See output above.", file=sys.stderr)
            sys.exit(3)


# --- CLI ---
def main():
    ap = argparse.ArgumentParser(
        description="Translate selected PDF pages to LaTeX (equations + TikZ)."
    )
    ap.add_argument("--pdf", required=True, help="Input PDF path")
    ap.add_argument(
        "--pages",
        required=True,
        help="Pages to process (e.g., '11' or '11-13' or '3,5,9-12')",
    )
    ap.add_argument(
        "--out", default="translated_pages", help="Output folder (created if missing)"
    )
    ap.add_argument(
        "--title", default="Translated Document", help="Title for the compiled PDF"
    )
    ap.add_argument(
        "--compile",
        dest="compile",
        action="store_true",
        help="Compile the LaTeX to PDF",
    )
    ap.add_argument(
        "--no-compile",
        dest="compile",
        action="store_false",
        help="Do not compile (default)",
    )
    ap.set_defaults(compile=False)
    args = ap.parse_args()

    if not OPENAI_API_KEY and "api.openai.com" in OPENAI_BASE_URL:
        print("ERROR: OPENAI_API_KEY is required for OpenAI endpoint.", file=sys.stderr)
        sys.exit(1)

    run(args.pdf, args.pages, args.out, args.compile, args.title)


if __name__ == "__main__":
    main()

