# ui.py — Streamlit front-end for agent_latex.py
import os
import io
import time
import tempfile
import pathlib
import traceback
import streamlit as st
import zipfile
from stqdm import stqdm

# Import the pipeline function from your agent
# (assumes agent_latex.py is in the same directory)
from agent_latex import run as agent_run
from status import add_listener,clear_listeners


st.set_page_config(
    page_title="PDF → LaTeX Translator", page_icon="📄", layout="centered"
)

st.title("📄 PDF → LaTeX (with TikZ) Translator")

st.caption(
    "Upload a PDF, set your model credentials (OpenAI or local Ollama), choose pages, "
    "and generate a clean LaTeX document (and optionally compile to PDF). "
    "⚠️ API keys are used for this session only and are not stored."
)

with st.expander("Engine & Model Settings", expanded=True):
    engine_choice = st.radio(
        "Model backend",
        ["OpenAI (cloud)", "Mathpix (cloud)", "Custom"],
        index=0,
        help="OpenAI: api.openai.com; Mathpix: api.mathpix.com; Custom: your own gateway.",
    )
    colA, colB = st.columns(2)
    
    urlMap = {"OpenAI (cloud)": "https://api.openai.com/v1", "Mathpix (cloud)": "https://api.mathpix.com/v3", "Custom": "Enter Your LLM Domain"}
    modelMap = {"OpenAI (cloud)": "gpt-4o", "Mathpix (cloud)": "", "Custom": ""}
    apikeyMap = {"OpenAI (cloud)": "sk-...", "Mathpix (cloud)": "ollama", "Custom": None}
    with colA:
        base_url = st.text_input("Base URL", value=urlMap[engine_choice])
        if (engine_choice == "OpenAI (cloud)"):
            models = ["gpt-4o","gpt-5","gpt-4.1"]
            model = st.selectbox("Model",models)
        elif (engine_choice == "Mathpix (cloud)"):
            app_id = st.text_input("App_id")
        else:
            model = st.text_input("Model", value=modelMap[engine_choice], disabled=True)

    with colB:
        title = st.text_input("Document Title", value="Translated Document")
        api_key = st.text_input("API Key", type="password", placeholder=apikeyMap[engine_choice])

with st.expander("Customization Settings", expanded = True):
    user_prompt = st.text_input("Project Prompt",placeholder='e.g. generate the pdf with green text color') 
    math_equation = st.checkbox("Contains Math Equations",value = True)
    language_translation = st.checkbox("Translate To Another Langauge",value=False)
    language_selected = ""
    if (language_translation):
        languages = ["English","Chinese","Spanish","Japanese","Korean","Other"]
        language_selected = st.selectbox("Language To Translate",languages)
    user_input = [user_prompt,math_equation,language_selected ]

    content_page = st.checkbox("Generate Table of Content",value=False)

with st.expander("PDF & Translation Settings", expanded=True):
    uploaded = st.file_uploader("Upload PDF", type=["pdf"])
    pages = st.text_input("Pages (e.g., 1,3,5-9, or 1-999 for all)", value="1-999")
    out_dir_name = st.text_input("Output folder name", value="translated_output")
    compile_flag = st.checkbox("Compile to PDF", value=True)

run_btn = st.button(
    "Generate", type="primary", use_container_width=True, disabled=(uploaded is None)
)


def set_env_temporarily(vars_dict):
    """Context manager to set env vars for the duration of a block."""

    class _Ctx:
        def __enter__(self_nonlocal):
            self_nonlocal.old = {}
            for k, v in vars_dict.items():
                self_nonlocal.old[k] = os.environ.get(k)
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v

        def __exit__(self_nonlocal, exc_type, exc, tb):
            for k, oldv in self_nonlocal.old.items():
                if oldv is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = oldv

    return _Ctx()

if __name__ == "__main__":

    if run_btn:
        st_bar = stqdm(total=100,desc="Operation in progress", bar_format="{l_bar}{bar} | {percentage:3.0f}% • {elapsed} < {remaining}")
        clear_listeners()
        def update_status_value(value):
            st_bar.update(value)
            if (st_bar.n == 100):
                st_bar.set_description("Operation success")
        add_listener(update_status_value)
        if uploaded is None:
            st.error("Please upload a PDF first.")
            st.stop()

        if (engine_choice == "OpenAI (cloud)") and not api_key:
            st.error("Please provide an OpenAI API key.")
            st.stop()

        os.system('rm -rf ./translated_output')

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                tmpdir_path = pathlib.Path(tmpdir)
                # Save uploaded PDF to a temp file
                pdf_path = tmpdir_path / uploaded.name
                with open(pdf_path, "wb") as f:
                    f.write(uploaded.read())

                # Prepare output directory under the current working dir
                out_dir = pathlib.Path(out_dir_name).absolute()
                out_dir.mkdir(parents=True, exist_ok=True)

                # Set environment for the agent during this run
                env_vars = {
                    "OPENAI_BASE_URL": base_url.strip(),
                    "OPENAI_API_KEY": api_key.strip() or "",
                    "OPENAI_MODEL": model.strip(),
                }

                # Generate Payload
                payload = {
                    "engine_choice": engine_choice, 
                    "pdf_path": str(pdf_path),
                    "app_id": locals().get("app_id"),
                    "base_url": base_url,
                    "pages_arg": pages,
                    "out_prefix": str(out_dir),
                    "compile_flag": compile_flag,
                    "title": title,
                    "api_key": api_key.strip(),
                    "user_input": user_input,
                    "content_page": content_page,
                    "model": locals().get("model"),
                }
                with set_env_temporarily(env_vars):
                    with st.status(
                        "Processing… This can take a while for large PDFs.", state="running"
                    ) as status:
                        st.write(f"**Model:** `{model}`  •  **Base URL:** `{base_url}`")
                        st.write(f"**Output folder:** `{out_dir}`")
                        st.write(
                            f"**Pages:** `{pages}`  •  **Compile:** ``{compile_flag}``"
                        )

                       # Call the agent pipeline
                        start = time.time()
                        agent_run(payload)

                        elapsed = time.time() - start

                        status.update(label="Done!", state="complete")
                        st.success(f"Completed in {elapsed:.1f}s")

                # Offer downloads if present
                master_tex = out_dir / "master.tex"
                master_pdf = out_dir / "master.pdf"
                master_zip = out_dir / "master.zip"
                page_files = sorted(out_dir.glob("page_*.tex"))

                with zipfile.ZipFile(master_zip, 'w', zipfile.ZIP_DEFLATED, False) as zipf: 
                    if master_tex.exists():
                        zipf.write(master_tex,arcname=master_tex.name)
                    if compile_flag and master_pdf.exists():
                        zipf.write(master_pdf,arcname=master_pdf.name)
                    if page_files:
                        for p in page_files:
                            zipf.write(p,arcname=p.name)

                with open(master_zip, "rb") as file:
                    st.download_button(
                        "Download master.zip",
                        data=file,
                        file_name="master.zip",
                        mime="application/zip"
                    )
                if master_tex.exists():
                    st.subheader("Downloads")
                    st.download_button(
                        "Download master.tex",
                        data=master_tex.read_bytes(),
                        file_name="master.tex",
                        mime="text/x-tex",
                    )
                else:
                    st.warning("master.tex not found (unexpected).")

                if compile_flag and master_pdf.exists():
                    st.download_button(
                        "Download master.pdf",
                        data=master_pdf.read_bytes(),
                        file_name="master.pdf",
                        mime="application/pdf",
                    )
                elif compile_flag:
                    st.warning(
                        "Compilation was requested, but master.pdf was not produced. Check LaTeX installation (MiKTeX/TeX Live)."
                    )

        except Exception as e:
            st.error("An error occurred.")
            st.exception(e)
            st.text(traceback.format_exc())


