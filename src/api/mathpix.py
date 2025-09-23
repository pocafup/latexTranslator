import json,requests

def mathpix(pdf_path:str,app_id:str,app_key:str) -> requests.Response:
    options = {
        "conversion_formats": {"docx": True, "tex.zip": True},
        "math_inline_delimiters": ["$", "$"],
        "rm_spaces": True
    }
    return requests.post("https://api.mathpix.com/v3/pdf",
        headers={
            "app_id": app_id, 
            "app_key": app_key, 
        },
        data={
            "options_json": json.dumps(options)
        },
        files={
            "file": open(pdf_path,"rb")
        }
    )

def mathpix_writeback(pdf_id:str, app_id:str,app_key:str,out_dir:str): 
    headers = {
        "app_id": app_id,
        "app_key": app_key 
    }
    # get docx response
    url = "https://api.mathpix.com/v3/pdf/" + pdf_id + ".docx"
    response = requests.get(url, headers=headers)
    with open(out_dir + "/master.docx", "wb") as f:
        f.write(response.content)
    # get LaTeX zip file
    url = "https://api.mathpix.com/v3/pdf/" + pdf_id + ".tex"
    response = requests.get(url, headers=headers)
    with open(out_dir + "/master.tex.zip", "wb") as f:
        f.write(response.content)


def mathpix_isprocessing(pdf_id:str,app_id:str,app_key:str) -> bool:
    headers = {
        "app_id": app_id,
        "app_key": app_key 
    }
    url = "https://api.mathpix.com/v3/pdf/" + pdf_id
    r = requests.get(url, headers=headers)
    if (r.json()["status"]!="completed"):
        return True 
    url = "https://api.mathpix.com/v3/converter/" + pdf_id
    r = requests.get(url,headers=headers)
    if (r.json()["status"]!="completed" 
            or r.json()["conversion_status"]["docx"]["status"]=="processing" 
            or r.json()["conversion_status"]["tex.zip"]["status"]=="processing"):
        return True 
    return False 



