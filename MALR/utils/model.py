import openai
import requests
import json
    
def call_gpt(p,apikey,model_name):
    openai.api_base= "yourapibase"
    openai.api_key = apikey

    message = [
            {"role":"user",
             "content":p}]
    post_body = {"model": model_name,"messages": message,"temperature": 0,}
    r = requests.post(
           "yourapibase",
            headers={"Content-Type":"application/json", "Authorization": "Bearer "+openai.api_key}, 
            data=json.dumps(post_body))
    res = r.json()['data']['response']
    
    content = res['choices'][0]['message']['content']
    cb = res['usage']
    return content,cb
