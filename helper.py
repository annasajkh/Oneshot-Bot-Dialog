import requests
import json

def get_gpt():

    file = open("input.txt", "r")

    payload = { 
        "prompt": file.read().encode("utf-8").decode("utf-8", "ignore"), 
        "temperature": 1,
        "top_k": 40, 
        "top_p": 0.9, 
        "seed": 0
    }

    file.close()

    url = "https://bellard.org/textsynth/api/v1/engines/gptj_6B/completions"


    r = requests.post(url, data=json.dumps(payload, ensure_ascii=False))

    while True:
        try:
            text = filter(lambda x: x != "", [chunk for chunk in r.text.split("\n")])
            text = "".join([json.loads(chunk)["text"] for chunk in text]).strip()
            break
        except:
            r = requests.post(url, data=json.dumps(payload, ensure_ascii=False))


    return text[:500]