from openai import OpenAI
from typing import List
def openai_api(api_key:str, model: str, system_msg:str, page:List[dict]):
    client = OpenAI(api_key=api_key)
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user","content": page},
        ],
    )
    return completion.choices[0].message.content

