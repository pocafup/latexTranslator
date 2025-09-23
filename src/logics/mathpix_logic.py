import requests
import json
import time
from api.mathpix import mathpix,mathpix_writeback,mathpix_isprocessing
def mathpix_logic(app_id:str, app_key:str, pdf_path:str, out_dir:str):
    try:
        r = mathpix(app_id=app_id,app_key=app_key,pdf_path=pdf_path)    
        pdf_id = r.json()["pdf_id"]
        while(mathpix_isprocessing(pdf_id=pdf_id,app_id=app_id,app_key=app_key)):
            time.sleep(1)
            
        mathpix_writeback(pdf_id=pdf_id,app_id=app_id,app_key=app_key,out_dir=out_dir)
    except Exception as e:
        raise Exception("Mathpix writeback failed. Error: ",e)
   

