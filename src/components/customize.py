import streamlit as st
def customize(engine_choice:str) -> dict:
    if (engine_choice!="Mathpix (cloud)"):
        with st.expander("Customization Settings", expanded = True): 
            user_prompt = st.text_input("Project Prompt",placeholder='e.g. generate the pdf with green text color') 
            language_translation = st.checkbox("Translate To Another Langauge",value=False)
            if (language_translation):
                languages = ["English","Chinese","Spanish","Japanese","Korean","Other"]
                language_selected = st.selectbox("Language To Translate",languages)
            content_page = st.checkbox("Generate Table of Content",value=False)
    return {
        "user_prompt":locals().get("user_prompt"),
        "language_selected": locals().get("language_selected") or "",
        "content_page":locals().get("content_page"),
    }


