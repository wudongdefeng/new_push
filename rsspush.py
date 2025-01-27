import feedparser
import requests
import os

# List of RSS feed URLs
rss_urls = [
    "https://cn.yna.co.kr/RSS/news.xml",
    "https://rsshub.app/zhihu/daily",
    "https://www.zhihu.com/rss",
    "https://news.un.org/feed/subscribe/zh/news/all/rss.xml",
    "https://sputniknews.cn/export/rss2/archive/index.xml",
    "https://plink.anyfeeder.com/zaobao/realtime/world"
]

# Fetch and format RSS feed updates
def fetch_rss_updates():
    updates = []
    for url in rss_urls:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:5]:  # Limit to the first 5 entries per feed
                pic_url = ""
                if 'media_content' in entry and len(entry.media_content) > 0:
                    pic_url = entry.media_content[0]['url']
                elif 'media_thumbnail' in entry and len(entry.media_thumbnail) > 0:
                    pic_url = entry.media_thumbnail[0]['url']
                elif 'links' in entry:
                    for link in entry.links:
                        if 'image' in link.type:
                            pic_url = link.href
                            break
                updates.append({
                    "title": entry.title,
                    "description": entry.summary if 'summary' in entry else "",
                    "url": entry.link,
                    "picurl": pic_url
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
    updates = []
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        items = content.split('<h2>Title: ')[1:]  # Split and skip the first empty element
        for item in items:
            title = item.split('</h2>')[0]
            url = item.split("href='")[1].split("'")[0]
            updates.append({"title": title, "url": url})
    return updates

def check_for_updates(new_updates, saved_updates):
    saved_titles = {update["title"] for update in saved_updates}
    new_unique_updates = [update for update in new_updates if update["title"] not in saved_titles]
    return new_unique_updates

def send_to_wecom(updates):
    corp_id = os.getenv("WECOM_CORP_ID")
    agent_id = os.getenv("WECOM_AGENT_ID")
    agent_secret = os.getenv("WECOM_AGENT_SECRET")

    # Get WeCom access token
    token_url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={corp_id}&corpsecret={agent_secret}"
    token_res = requests.get(token_url).json()
    access_token = token_res['access_token']

    # Determine the number of batches
    batch_size = 8
    total_batches = (len(updates) + batch_size - 1) // batch_size

    for batch_num in range(total_batches):
        start_index = batch_num * batch_size
        end_index = start_index + batch_size
        batch_updates = updates[start_index:end_index]

        # Prepare message
        articles = [{
            "title": update["title"],
            "description": update["description"],
            "url": update["url"],
            "picurl": update["picurl"]
        } for update in batch_updates]

        message = {
            "touser": "@all",
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
        print(send_res.json())

if __name__ == "__main__":
    updates = fetch_rss_updates()
    if updates:
        file_path = 'docs/index.html'
        saved_updates = load_updates_from_file(file_path)
        new_updates = check_for_updates(updates, saved_updates)
        if new_updates:
            save_updates_to_file(updates, file_path)
            send_to_wecom(new_updates)
        else:
            print("No new updates found.")
    else:
        print("No updates found.")
