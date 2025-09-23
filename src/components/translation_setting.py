import streamlit as st
def translation_setting():
    with st.expander("PDF & Translation Settings", expanded=True):
        uploaded = st.file_uploader("Upload PDF", type=["pdf"])
        pages = st.text_input("Pages (e.g., 1,3,5-9, or 1-999 for all)", value="1-999")
    return {
        "uploaded": locals().get("uploaded"),
        "pages":pages,
    }


