import requests
import json

url = "https://datasets-server.huggingface.co/first-rows?dataset=lmsys%2Fchatbot_arena_conversations&config=default&split=train"
resp = requests.get(url).json()

if "rows" in resp and len(resp["rows"]) > 0:
    row = resp["rows"][0]["row"]
    print("Keys in Chatbot Arena dataset:", row.keys())
    print("Example row:", json.dumps(row, indent=2))
else:
    print("Error:", resp)
