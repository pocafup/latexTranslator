import os,re,sys
from dataclasses import dataclass
from logics.openai_logic import openai_logic
from logics.mathpix_logic import mathpix_logic
import pymupdf as fitz 

# --- Main pipeline ---
def run(
    payload: dict()
):
    globals().update(payload)
    try:
        match engine_choice:
            case "OpenAI (cloud)":
                openai_logic(
                    pdf_path=pdf_path,
                    pages_arg=pages_arg,
                    out_dir=out_dir,
                    language_selected=language_selected,
                    user_prompt=user_prompt, 
                    api_key=api_key,
                    model=model,
                    title=title,
                    content_page=content_page,
                )
            case "Mathpix (cloud)":
                mathpix_logic(
                    pdf_path=pdf_path,
                    out_dir=out_dir,
                    app_key=api_key,
                    pages_arg=pages_arg,
                    app_id=app_id,
                )
                
            case "Custom":
                raise Exception("Custom Model is not available yet")
    except Exception as e:
        raise e

