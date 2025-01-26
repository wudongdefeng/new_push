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
                updates.append({
                    "title": entry.title,
                    "description": entry.summary if 'summary' in entry else "",
                    "url": entry.link,
                    "picurl": entry.media_content[0]['url'] if 'media_content' in entry else ""
                })
        except Exception as e:
            print(f"Error fetching updates from {url}: {e}")
    return updates

def save_updates_to_file(updates, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write('<html><body>\n')
        for update in updates:
            file.write(f"<h2>Title: {update['title']}</h2>\n")
            file.write(f"<p>Link: <a href='{update['url']}'>{update['url']}</a></p>\n")
        file.write('\n</body></html>')

def load_updates_from_file(file_path):
    if not os.path.exists(file_path):
        return []
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read().split('\n')

def check_for_updates(new_updates, saved_updates):
    return new_updates != saved_updates

def send_to_wecom(updates):
    corp_id = os.getenv("WECOM_CORP_ID")
    agent_id = os.getenv("WECOM_AGENT_ID")
    agent_secret = os.getenv("WECOM_AGENT_SECRET")

    # Get WeCom access token
    token_url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={corp_id}&corpsecret={agent_secret}"
    token_res = requests.get(token_url).json()
    access_token = token_res['access_token']

    # Prepare message
    articles = [{
        "title": update["title"],
        "description": update["description"],
        "url": update["url"],
        "picurl": update["picurl"]
    } for update in updates]

    message = {
        "touser": "PanDeng",
        "msgtype": "news",
        "agentid": agent_id,
        "news": {
            "articles": articles
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
        file_path = 'docs/index.html'
        saved_updates = load_updates_from_file(file_path)
        if check_for_updates(updates, saved_updates):
            save_updates_to_file(updates, file_path)
            response = send_to_wecom(updates)
            print(response)
        else:
            print("No new updates found.")
    else:
        print("No updates found.")
