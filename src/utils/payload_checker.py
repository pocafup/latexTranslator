def payload_checker(payload:dict):
    globals().update(payload) 

    # Errors precheck
    if uploaded is None:
        raise Exception("please upload a PDF First")

    if base_url is None or base_url=="":
        raise Exception("base_url cannot be empty")

    if (engine_choice == "OpenAI (cloud)") and not api_key:
        raise Exception("Please provide an OpenAI API key")

    if (engine_choice == "Mathpix (cloud)" and (not api_key or not app_id)):
        raise Exception("Please provide Mathpix API key and APP id")

    if (pages_arg == ""):
        raise Exception("Please enter a page number")


