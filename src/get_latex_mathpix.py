
import requests

pdf_id = "2025_09_22_b446bbc1b7e26a258007g"
headers = {
  "app_id": "uciresearch_19be13_3e936c",
  "app_key": "6fded6433c2b3cd7f73b01a268527b96400da1559d1dac76201c3ce348d7dffd"
}

# get docx response
url = "https://api.mathpix.com/v3/pdf/" + pdf_id + ".docx"
response = requests.get(url, headers=headers)
with open(pdf_id + ".docx", "wb") as f:
    f.write(response.content)

# get LaTeX zip file
url = "https://api.mathpix.com/v3/pdf/" + pdf_id + ".tex"
response = requests.get(url, headers=headers)
with open(pdf_id + ".tex.zip", "wb") as f:
    f.write(response.content)


