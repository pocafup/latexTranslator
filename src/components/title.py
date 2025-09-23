import streamlit as st
def make_title():
    st.set_page_config(
        page_title="PDF → LaTeX Translator", page_icon="📄", layout="centered"
    )

    st.title("📄 PDF → LaTeX Translator")

    st.caption(
        "Upload a PDF, set your model credentials (OpenAI or Mathpix), choose pages, "
        "and generate a clean LaTeX document and a compiled PDF document" 
        "⚠️ API keys are used for this session only and are not stored."
    )
