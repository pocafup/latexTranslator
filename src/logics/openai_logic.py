import pymupdf as fitz
import os,sys,subprocess,argparse
from utils.page_parser import parse_pages_arg,extract_page
from utils.compile_pdf import compile_pdf
from sanitization.sanitize_llm import sanitize_for_xelatex
from utils.latex_formatter import make_master_preamble, make_master_epilogue
from api.openai import openai_api
from constants.constants import SYSTEM_LATEX,SYSTEM_TOC,USER_MSG,CONTENT_PAGE,cor,HEADING_PATTERNS
from status import set_total_page,update_status
from utils.misc import printf
from typing import List, Tuple

def openai_logic(pdf_path:str, pages_arg:str, out_dir:str, language_selected:str, user_prompt:str ,api_key:str, model:str, title:str, content_page: bool):
    try:
        doc = fitz.open(pdf_path)
        max_pages = len(doc)
        pages = parse_pages_arg(pages_arg, max_pages)
        if not pages:
            printf(f"No valid pages selected in range 1..{max_pages}.", file=sys.stderr)
            raise RuntimeError(f"No valid pages selected in range 1..{max_pages}.", file=sys.stderr)

        # Page extraction logic:
        page_extracted = extract_page(doc, pages)
        set_total_page(len(page_extracted))

        out_dir = os.path.abspath(out_dir)
        os.makedirs(out_dir, exist_ok=True)
        parts_written = []

        cor_prompts = f"\nUser input contains math formula. Translate those into latex.\n \
                        IMPORTANT: Translate all the text into {language_selected} BEFORE GENERATING TEXT \n \
                        - Make sure the generated text is compatible with {cor[language_selected]}\n"
        

        if language_selected:
            user_prompt += cor_prompts

        if content_page:
            user_prompt += CONTENT_PAGE

        # Send each page separately
        for pno, img_part in page_extracted:
            # Build content parts for this single page
            page_parts = [
                {"type": "text", "text": USER_MSG},  # your fixed user message
                img_part,                            # the page image
            ]
            body = sanitize_for_xelatex(openai_api(
                api_key=api_key,
                model=model,
                system_msg= SYSTEM_LATEX + user_prompt,
                page = page_parts,
            ).strip())
            # Save per-page body
            page_body_path = os.path.join(out_dir, f"page_{pno:03d}.tex")
            with open(page_body_path, "w", encoding="utf-8") as f:
                f.write(body + "\n")
            parts_written.append((pno, page_body_path))
            update_status()

        # Assemble master.tex (unchanged)
        master_path = os.path.join(out_dir, "master.tex")
        with open(master_path, "w", encoding="utf-8") as f:
            f.write(make_master_preamble(title, language_selected, content_page))

            for pno, body_path in parts_written:
                with open(body_path, "r", encoding="utf-8") as b:
                    content = b.read()
                if not content.endswith("\n"):
                    content += "\n"
                f.write(content)
            f.write(make_master_epilogue())
        
        printf(f"Wrote master LaTeX: {master_path}")
        printf("Compiling PDF...")
        try:
            compile_pdf(master_path, engine="xelatex",passes=5)
            printf("PDF compiled successfully.")
        except subprocess.CalledProcessError:
            print("LaTeX compile failed.\n--- xelatex output ---\n")
    except Exception as e:
        raise e
    finally:
        doc.close()


