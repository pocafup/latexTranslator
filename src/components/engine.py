import streamlit as st
def engine() -> dict:
    with st.expander("Engine & Model Settings", expanded=True):
        engine_choice = st.radio(
            "Model backend",
            ["OpenAI (cloud)", "Mathpix (cloud)", "Custom"],
            index=0,
            help="OpenAI: api.openai.com; Mathpix: api.mathpix.com; Custom: your own gateway.",
        )
        colA, colB = st.columns(2)
        
        urlMap = {"OpenAI (cloud)": "https://api.openai.com/v1", "Mathpix (cloud)": "https://api.mathpix.com/v3", "Custom": "Enter Your LLM Domain"}
        modelMap = {"OpenAI (cloud)": "gpt-4o", "Mathpix (cloud)": "Your app_id goes here", "Custom": ""}
        apikeyMap = {"OpenAI (cloud)": "sk-...", "Mathpix (cloud)": "Your api_key goes here", "Custom": None}
        with colA:
            base_url = st.text_input("Base URL", value=urlMap[engine_choice])
            if (engine_choice == "OpenAI (cloud)"):
                models = ["gpt-4o","gpt-5","gpt-4.1"]
                model = st.selectbox("Model",models)
            elif (engine_choice == "Mathpix (cloud)"):
                app_id = st.text_input("App_id",placeholder="Your app_id goes here")
            else:
                model = st.text_input("Model", value=modelMap[engine_choice], disabled=True)

        with colB:
            title = st.text_input("Document Title", value="Translated Document")
            api_key = st.text_input("API Key", type="password", placeholder=apikeyMap[engine_choice])
        return {
            "engine_choice":engine_choice,
            "base_url":base_url, 
            "model":locals().get("model") or "",
            "app_id":locals().get("app_id"),
            "title":title,
            "api_key":api_key,
        }


