# ui.py — Streamlit front-end for agent_latex.py
import os
import io
import time
import tempfile
import pathlib
import traceback
import streamlit as st
import zipfile
from datetime import datetime
from stqdm import stqdm
from components.engine import engine
from components.title import make_title
from components.customize import customize
from components.translation_setting import translation_setting
from components.downloads import downloads
# Import the pipeline function from your agent
# (assumes agent_latex.py is in the same directory)
from agent import run as agent_run
from status import add_listener,clear_listeners
from utils.payload_checker import payload_checker



if __name__ == "__main__":

    make_title()
    globals().update(engine())
    globals().update(customize(engine_choice))
    globals().update(translation_setting())
    run_btn = st.button(
        "Generate", type="primary", use_container_width=True, disabled=(uploaded is None)
    )

    if run_btn:

        st_bar = stqdm(total=100,desc="Operation in progress", bar_format="{l_bar}{bar} | {percentage:3.0f}% • {elapsed} < {remaining}")
        clear_listeners()
        def update_status_value(value):
            st_bar.update(value)
            if (st_bar.n == 100):
                st_bar.set_description("Operation success")
        add_listener(update_status_value)
        os.system('rm -rf ./translated_output')

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                tmpdir_path = pathlib.Path(tmpdir)
                # Save uploaded PDF to a temp file
                pdf_path = tmpdir_path / uploaded.name
                with open(pdf_path, "wb") as f:
                    f.write(uploaded.read())
                translation_time = datetime.now() 
                # Prepare output directory under the current working dir
                out_dir = pathlib.Path(f"translated_output/{translation_time}").absolute()
                out_dir.mkdir(parents=True, exist_ok=True)

               # Generate Payload
                payload = {
                    "engine_choice": engine_choice, 
                    "pdf_path": str(pdf_path),
                    "app_id": locals().get("app_id"),
                    "base_url": base_url,
                    "pages_arg": pages,
                    "out_dir": str(out_dir),
                    "title": title,
                    "api_key": api_key.strip(),
                    "user_prompt":user_prompt,
                    "language_selected": locals().get("language_selected") or "",
                    "content_page":content_page,
                    "model": locals().get("model"),
                    "uploaded":locals().get("uploaded"),
                }
                payload_checker(payload)

                with st.status(
                    "Processing… This can take a while for large PDFs.", state="running"
                ) as status:
                    st.write(
                        f"**Engine:** `{engine_choice}` "
                    )
                    # Call the agent pipeline
                    start = time.time()
                    try:
                        agent_run(payload)
                        elapsed = time.time() - start
                        status.update(label="Done!", state="complete")
                        st.success(f"Completed in {elapsed:.1f}s")
                    except Exception as e:
                        st.error("Translation Failed. Error: ",e)

            downloads(out_dir)                

        except Exception as e:
            st.error("An error occurred.")
            st.exception(e)
            st.text(traceback.format_exc())


