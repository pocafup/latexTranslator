import os,re,sys,argparse,base64,subprocess,requests,pymupdf,tempfile
from openai import OpenAI
from typing import List, Tuple
from dataclasses import dataclass
from dotenv import load_dotenv
from tqdm import tqdm
from constants import SYSTEM_LATEX,SYSTEM_TOC,USER_MSG,CONTENT_PAGE,cor,HEADING_PATTERNS

# --- Config / Env ---
load_dotenv()
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

__DEBUG__ = True

# --- PDF extraction ---
try:
    import pymupdf as fitz  # PyMuPDF
except Exception as e:
    print("ERROR: PyMuPDF (pymupdf) is required. pip install pymupdf", file=sys.stderr)
    raise


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

def content_page_generation(master_tex: str, api_key: str):
    with open(master_tex, 'r', encoding='utf-8') as f:
        doc_src = f.read()

    # Feed the FULL document as the user content
    parts = [{"type": "text", "text": doc_src}]
    edited = sanitize_for_xelatex(llm_chat(
        system_msg=CONTENT_PAGE,
        user_msg="Insert the contents page per rules.",
        page=parts,
        api_key=api_key,
    ).strip())
    print("Edited: ", edited)

    # Basic sanity checks so we don't clobber a good file with junk
    must_have = ["\\documentclass", "\\begin{document}", "\\end{document}", "\\tableofcontents"]
    if not all(token in edited for token in must_have):
        raise RuntimeError("LLM did not return a valid LaTeX file with a table of contents.")

    if "% === TOC_ANCHOR_AFTER_MAKETITLE ===" not in doc_src:
        # In case someone uses an older preamble without the anchor
        raise RuntimeError("TOC anchor not found in master.tex preamble; update make_master_preamble().")

    return edited

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

def _sanitize_toc_title(s: str) -> str:
    # remove inline math variants
    s = re.sub(r'\\\((.*?)\\\)', r'\1', s)   # \( ... \) -> ...
    s = re.sub(r'\\\[(.*?)\\\]', r'\1', s)   # \[ ... \] -> ...
    s = re.sub(r'\$(.*?)\$', r'\1', s)       # $ ... $   -> ...
    # strip other fragile bits you don’t want in ToC text
    s = re.sub(r'\\textbf\{([^}]*)\}', r'\1', s)
    s = re.sub(r'\\emph\{([^}]*)\}', r'\1', s)
    s = re.sub(r'\\[a-zA-Z]+\*?(?:\[[^\]]*\])?(?:\{[^}]*\})?', '', s)  # drop stray macros
    # escape specials
    s = s.replace('%', r'\%').replace('#', r'\#').replace('&', r'\&')
    s = s.replace('{', r'\{').replace('}', r'\}')
    return s.strip()

def inject_toc_entries(tex: str) -> str:
    def _inject(tex, pat, level):
        out, i = [], 0
        for m in re.finditer(pat, tex):
            start, end = m.span()
            raw_title = m.group(1).strip()
            toc_title = _sanitize_toc_title(raw_title)

            out.append(tex[i:start])
            out.append(m.group(0))

            window = tex[end:end+200]
            already = re.search(
                r'\\addcontentsline\{toc\}\{' + re.escape(level) + r'\}\{', window
            )
            if not already:
                out.append(f'\n\\addcontentsline{{toc}}{{{level}}}{{{toc_title}}}')
            i = end
        out.append(tex[i:])
        return ''.join(out)

    for pat, level in HEADING_PATTERNS:
        tex = _inject(tex, pat, level)
    return tex


def ensure_phantomsection(tex: str) -> str:
    """
    Insert \\phantomsection immediately before each \\addcontentsline{toc}{...}{...}
    so hyperref has a proper anchor and doesn't drop the entry.
    """
    return re.sub(
        r'(?<!\\phantomsection)\s*(\n\\addcontentsline\{toc\}\{(?:section|subsection|subsubsection)\}\{)',
        r'\n\\phantomsection\1',
        tex
    )

def sanitize_for_xelatex(tex: str) -> str:
    # Remove any CJK environments (if the model ignores instructions)
    tex = re.sub(r'\\begin\{CJK\}.*?\\end\{CJK\}', '', tex, flags=re.S|re.I)
    tex = re.sub(r'\\begin\{CJK\*?\}.*?\\end\{CJK\*?\}', '', tex, flags=re.S|re.I)
    tex = re.sub(r'\\end\{CJK\*?\}', '', tex, flags=re.I)
    tex = re.sub(r'\\begin\{CJK\*?\}(?:\[[^\]]*\])?(?:\{[^}]*\}){0,3}', '', tex, flags=re.I)
    # Remove package lines if they slip in
    tex = re.sub(r'\\usepackage(?:\[[^\]]*\])?\{CJK\*?u?t?f?8?\}', '', tex, flags=re.I)
    return tex

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
\usepackage[hidelinks]{hyperref} % for clickable ToC links
""" + f"\\setCJKmainfont{{{cor[language]}}}\n" + r"""\defaultfontfeatures{Ligatures=TeX}
\setmainfont{Liberation Serif}
\setsansfont{Liberation Sans}
\setmonofont{Liberation Mono}
\setlength{\parskip}{0.6em}
\setlength{\parindent}{0pt}

\title{""" + t + r"""}
\date{}
\begin{document}
\maketitle
\setcounter{tocdepth}{2}
% === TOC_ANCHOR_AFTER_MAKETITLE ===
"""

def make_master_epilogue() -> str:
    return r"""\end{document}
"""


def compile_pdf(tex_path: str, engine: str = "xelatex", passes: int = 2) -> None:
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
    for i in range(passes): 
        run_once()
# --- Main pipeline ---
def run(
    pdf_path: str,
    pages_arg: str,
    out_prefix: str,
    compile_flag: bool,
    title: str,
    api_key: str,
    user_input: list[str],
    content_page: bool,
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

            body = sanitize_for_xelatex(llm_chat(
                SYSTEM_LATEX + user_prompt,  # system content
                USER_MSG,                    # (kept for signature; actual text is in page_parts[0])
                page_parts,                  # <-- list of parts, not raw bytes/dict
                api_key=api_key,
            ).strip())

            # Save per-page body
            page_body_path = os.path.join(out_dir, f"page_{pno:03d}.tex")
            with open(page_body_path, "w", encoding="utf-8") as f:
                f.write(body + "\n")
            parts_written.append((pno, page_body_path))

        # Assemble master.tex (unchanged)
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

        # NEW: retrofit \addcontentsline for starred headings BEFORE LLM edit
        with open(master_path, "r", encoding="utf-8") as f:
            src = f.read()

        fixed = ensure_phantomsection(inject_toc_entries(src))
        if fixed != src:
            with open(master_path, "w", encoding="utf-8") as f:
                f.write(fixed)

        # Now let the LLM insert the ToC based on the actual master.tex
        if content_page:
            edited = content_page_generation(master_path, api_key)
            edited = sanitize_for_xelatex(edited)  # keep this if you already have it
            with open(master_path, "w", encoding="utf-8") as f:
                f.write(edited) 
        
        print(f"Wrote master LaTeX: {master_path}")

        if compile_flag:
            print("Compiling PDF...")
            try:
                compile_pdf(master_path, engine="xelatex",passes=2)
                print("PDF compiled successfully.")
            except subprocess.CalledProcessError:
                print("LaTeX compile failed.\n--- xelatex output ---\n")
    except Exception as e:
        raise e
    finally:
        doc.close()