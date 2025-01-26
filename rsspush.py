import feedparser
import requests
import os

# List of RSS feed URLs
rss_urls = [
    "https://feeds.bbci.co.uk/zhongwen/simp/rss.xml",
    "https://cn.nytimes.com/rss/world.xml",
    "https://cn.reuters.com/rssFeed/worldNews",
    "https://news.ifeng.com/rss/index.xml",
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
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:5]:  # Limit to the first 5 entries per feed
                updates.append(f"Title: {entry.title}\nLink: {entry.link}\n")
        except Exception as e:
            print(f"Error fetching updates from {url}: {e}")
    return updates

def send_to_feishu(updates):
    webhook_url = os.getenv("FSWEBHOOK")
    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        'msg_type': 'text',
        'content': {
            'text': f'\n\n'.join(updates)
        }
    }
    response = requests.post(webhook_url, json=data, headers=headers)
    if response.status_code == 200:
        print('消息发送成功')
    else:
        print('消息发送失败', response.text)

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

def save_updates_to_file(updates, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write('\n\n'.join(updates))

def load_updates_from_file(file_path):
    if not os.path.exists(file_path):
        return []
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read().split('\n\n')

def check_for_updates(new_updates, saved_updates):
    return new_updates != saved_updates

if __name__ == "__main__":
    updates = fetch_rss_updates()
    if updates:
        file_path = 'docs/index.html'
        saved_updates = load_updates_from_file(file_path)
        if check_for_updates(updates, saved_updates):
            save_updates_to_file(updates, file_path)
            response = send_to_wecom(updates)
            #response1 = send_to_feishu(updates)
            print(response)
            #print(response1)
        else:
            print("No new updates found.")
    else:
        print("No updates found.")
