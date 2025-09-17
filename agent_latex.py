import os,re,sys,argparse,base64,subprocess,requests,pymupdf,tempfile
from openai import OpenAI
from typing import List, Tuple
from dataclasses import dataclass
from dotenv import load_dotenv
from tqdm import tqdm
from constants.constants import SYSTEM_LATEX,SYSTEM_TOC,USER_MSG,CONTENT_PAGE,cor,HEADING_PATTERNS
from sanitization.sanitize_llm import sanitize_for_xelatex
from functions.latex_formatter import make_master_preamble, make_master_epilogue
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
def llm_chat(system_msg: str, user_msg:str, page: List[dict], api_key: str, model: str = "gpt-4o") -> str:
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
            model=model,
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
            "model": model,
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
    model:str,
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

        if content_page:
            user_prompt += CONTENT_PAGE
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
                model=model,
            ).strip())

            # Save per-page body
            page_body_path = os.path.join(out_dir, f"page_{pno:03d}.tex")
            with open(page_body_path, "w", encoding="utf-8") as f:
                f.write(body + "\n")
            parts_written.append((pno, page_body_path))

        # Assemble master.tex (unchanged)
        master_path = os.path.join(out_dir, "master.tex")
        with open(master_path, "w", encoding="utf-8") as f:
            f.write(make_master_preamble(title, user_input[2], content_page))
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
                compile_pdf(master_path, engine="xelatex",passes=5)
                print("PDF compiled successfully.")
            except subprocess.CalledProcessError:
                print("LaTeX compile failed.\n--- xelatex output ---\n")
    except Exception as e:
        raise e
    finally:
        doc.close()