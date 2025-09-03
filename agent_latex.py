#save: 

# # Latin
# brew install --cask font-noto-serif font-noto-sans font-noto-sans-mono

# # CJK (pick Serif or Sans; you can install both)
# brew install --cask font-noto-serif-cjk-sc font-noto-serif-cjk-jp font-noto-serif-cjk-kr
# brew install --cask font-noto-sans-cjk-sc   font-noto-sans-cjk-jp   font-noto-sans-cjk-kr

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
import base64
import subprocess
import requests
import pymupdf
import tempfile
from openai import OpenAI
from typing import List, Tuple
from dataclasses import dataclass
from dotenv import load_dotenv
from tqdm import tqdm

# --- Config / Env ---
load_dotenv()
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

__DEBUG__ = False

# --- PDF extraction ---
try:
    import pymupdf as fitz  # PyMuPDF
except Exception as e:
    print("ERROR: PyMuPDF (pymupdf) is required. pip install pymupdf", file=sys.stderr)
    raise

# --- Prompts ---
SYSTEM_LATEX = """You are a LaTeX writer. Convert the given math lecture page into clean, compilable LaTeX.
- Do NOT include any handwritten artifacts or images of text.
- Do NOT add the ```latex or the ``` as the pdf generator cannot recognize it.
- Have the footnote and a reference to it but do not use \cite
- Preserve section headers and structure using \\section*, \\subsection* as appropriate.
- If the page contains a simple analytic geometry sketch (axes, lines, vectors),
  RECREATE it with TikZ using vector graphics (no raster images).
- Use standard packages only: amsmath, amssymb, tikz, geometry, lmodern, fontenc, mathtools if needed.
- If the input is partial or noisy, produce your best faithful reconstruction.
- IMPORTANT: Return ONLY the LaTeX BODY content (no \\documentclass or \\begin{document}).
"""

USER_MSG = """Recognize and translate the pdf into a latex file
Instructions:
- Output ONLY LaTeX body content for this page.
- Wrap displayed equations in equation/align as appropriate.
- Use \\section*{{...}} or \\subsection*{{...}} for headings you detect.
- If appropriate, add a small TikZ sketch that matches the page's figure(s).
- Ensure the output compiles in a standard article preamble.
- Target language varies, English if not specified
"""
cor = { "Chinese" : "Noto Serif CJK SC",
        "Japanese": "Noto Serif CJK JP",
        "Korean"  : "Noto Serif CJK KR",
        "English" : "Arial",
        "Spanish" : "Arial",
        "": ""}

# --- LLM call ---
def llm_chat(system_msg: str, user_msg:str, page: List[dict], api_key: str) -> str:
    """
    Dual-path client:
    - If OPENAI_BASE_URL ends with '/v1' or contains 'api.openai.com': use OpenAI Chat Completions.
    - Else: assume Ollama native endpoint at .../api/chat
    """
    use_openai = ("api.openai.com" in OPENAI_BASE_URL) or OPENAI_BASE_URL.endswith(
        "/v1"
    )

    if use_openai:
        client = OpenAI(api_key=api_key)

        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user","content": page},
            ],
        )
        return completion.choices[0].message.content
        
        
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

def latex_escape(text: str) -> str:
    # Minimal escaping for common special chars in LaTeX titles
    repl = {
        "\\": r"\textbackslash{}", 
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    for k, v in repl.items():
        text = text.replace(k, v)
    return text

def make_master_preamble(title: str = "Translated Document", language: str = "English") -> str:
    t = latex_escape(title)
    return r"""\documentclass[11pt]{article}
\usepackage[margin=1in]{geometry}
\usepackage{fontspec}   
\usepackage{xeCJK}      
\usepackage[english,spanish,es-noshorthands]{babel}
\usepackage{newunicodechar}
\usepackage{amsmath,amssymb,mathtools}
\newunicodechar{−}{\ensuremath{-}}
\usepackage{tikz}
""" + f"\\setCJKmainfont{{{cor[language]}}}\n" + r"""\defaultfontfeatures{Ligatures=TeX}
\setmainfont{Times New Roman}
\setsansfont{Arial}
\usetikzlibrary{arrows.meta}
\setmonofont{Courier New}
\setlength{\parskip}{0.6em}
\setlength{\parindent}{0pt}

\title{""" + t + r"""}
\date{}
\begin{document}
\maketitle
"""

def make_master_epilogue() -> str:
    return r"""\end{document}
"""


def compile_pdf(tex_path: str, engine: str = "xelatex") -> None:
    tex_dir = os.path.dirname(os.path.abspath(tex_path)) or "."
    fname = os.path.basename(tex_path)
    def run_once():
        proc = subprocess.run(
            [engine, "-interaction=nonstopmode", fname],
            cwd=tex_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        if __DEBUG__:
            print(proc.stdout)
        if proc.returncode != 0:
            raise subprocess.CalledProcessError(proc.returncode, proc.args, output=proc.stdout)

    run_once()  # 1st pass
    run_once()  # 2nd pass

# --- Main pipeline ---
def run(
    pdf_path: str,
    pages_arg: str,
    out_prefix: str,
    compile_flag: bool,
    title: str,
    api_key: str,
    user_input: list[str],
):
    doc = fitz.open(pdf_path)
    try:
        max_pages = len(doc)
        pages = parse_pages_arg(pages_arg, max_pages)
        if not pages:
            print(f"No valid pages selected in range 1..{max_pages}.", file=sys.stderr)
            raise RuntimeError(f"No valid pages selected in range 1..{max_pages}.", file=sys.stderr)

        page_extracted = extract_page(doc, pages)

        out_dir = os.path.abspath(out_prefix)
        os.makedirs(out_dir, exist_ok=True)

        parts_written = []

        user_prompt = user_input[0]
        cor_prompts = [
            ". ",
            "User input contains math formula. Translate those into latex. ",
            f"IMPORTANT: Translate all the text into {user_input[2]} BEFORE GENERATING TEXT \n \
              - Make sure the generated text is compatible with {cor[user_input[2]]}",
        ]
        for i in range(len(user_input)):
            if user_input[i] != "":
                user_prompt += "- " + cor_prompts[i] + "\n"

        # Send each page separately
        for pno, img_part in page_extracted:
            # Build content parts for this single page
            page_parts = [
                {"type": "text", "text": USER_MSG},  # your fixed user message
                img_part,                            # the page image
            ]

            body = llm_chat(
                SYSTEM_LATEX + user_prompt,  # system content
                USER_MSG,                    # (kept for signature; actual text is in page_parts[0])
                page_parts,                  # <-- list of parts, not raw bytes/dict
                api_key=api_key,
            ).strip()

            # Save per-page body
            page_body_path = os.path.join(out_dir, f"page_{pno:03d}.tex")
            with open(page_body_path, "w", encoding="utf-8") as f:
                f.write(body + "\n")
            parts_written.append((pno, page_body_path))

        # Assemble master LaTeX
        master_path = os.path.join(out_dir, "master.tex")
        with open(master_path, "w", encoding="utf-8") as f:
            f.write(make_master_preamble(title, user_input[2]))
            for pno, body_path in parts_written:
                with open(body_path, "r", encoding="utf-8") as b:
                    content = b.read()
                if not content.endswith("\n"):
                    content += "\n"
                f.write(content)
            f.write(make_master_epilogue())

        print(f"Wrote master LaTeX: {master_path}")

        if compile_flag:
            print("Compiling PDF...")
            try:
                compile_pdf(master_path, engine="xelatex")
                print("PDF compiled successfully.")
            except subprocess.CalledProcessError:
                print("LaTeX compile failed.\n--- xelatex output ---\n")
    except Exception as e:
        raise e
    finally:
        doc.close()
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

