import requests
import json

options = {
    "conversion_formats": {"docx": True, "tex.zip": True},
    "math_inline_delimiters": ["$", "$"],
    "rm_spaces": True
}
r = requests.post("https://api.mathpix.com/v3/pdf",
    headers={
        "app_id": "uciresearch_19be13_3e936c",
        "app_key": "6fded6433c2b3cd7f73b01a268527b96400da1559d1dac76201c3ce348d7dffd"
    },
    data={
        "options_json": json.dumps(options)
    },
    files={
        "file": open("week2.pdf","rb")
    }
)
print(r.text.encode("utf8"))

