import os
import requests
import json

text_url = "https://60s.viki.moe/60s?e=text"

text_response = requests.get(text_url)
content = text_response.text
QYWX_KEY = get_environ("webhook")
webhook = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=" + QYWX_KEY
headers = {"Content-Type": "text/plain"}
data = {
    "msgtype": "text",
    "text": {
        "content": content
    }

}

if QYWX_KEY != "":
    r = requests.post(url=webhook, headers=headers, json=data).json()
    if r["errmsg"] == "ok":
        print("企业微信机器人推送成功")
    else:
        print("企业微信机器人推送失败")
    print()
else:
    print()
