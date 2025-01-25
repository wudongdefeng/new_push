import feedparser
import requests
import os

# List of RSS feed URLs
rss_urls = [
    "https://fuliba2025.net/feed",
    "https://www.yddx.net/feed",
    "https://hao.su/feed",
    "https://rsshub.app/zhihuzhuanlan/c_1085975047386050560",
    "https://rsshub.app/zaker/source/660",
    "https://rsshub.app/zhihu/daily",
    "https://www.zhihu.com/rss",
    "https://rsshub.app/netease/news/special/1",
    "https://rsshub.app/banyuetan/jicengzhili",
    "https://rsshub.app/zaobao/realtime/china"
]

# Fetch and format RSS feed updates
def fetch_rss_updates():
    updates = []
    for url in rss_urls:
        feed = feedparser.parse(url)
        for entry in feed.entries[:5]:  # Limit to the first 5 entries per feed
            updates.append(f"Title: {entry.title}\nLink: {entry.link}\n")
        except Exception as e:
            print(f"Error fetching updates from {url}: {e}")
    return updates

# Send updates to WeCom
def send_to_wecom(updates):
    corp_id = os.getenv("WECOM_CORP_ID")
    agent_id = os.getenv("WECOM_AGENT_ID")
    agent_secret = os.getenv("WECOM_AGENT_SECRET")

    # Get WeCom access token
    token_url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={corp_id}&corpsecret={agent_secret}"
    token_res = requests.get(token_url).json()
    access_token = token_res['access_token']

    # Prepare message
    message = {
        "touser": "PanDeng",
        "msgtype": "text",
        "agentid": agent_id,
        "text": {
            "content": "\n\n".join(updates)
        },
        "safe": 0
    }

    # Send message to WeCom
    send_url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}"
    send_res = requests.post(send_url, json=message)
    return send_res.json()
if __name__ == "__main__":
    updates = fetch_rss_updates()
    if updates:
        response = send_to_wecom(updates)
        print(response)
    else:
        print("No updates found.")  
