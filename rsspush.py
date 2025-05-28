import feedparser
import requests
import os
import re
from urllib.parse import urljoin
from datetime import datetime

# 配置RSS源列表（可按需增减）
rss_urls = [
    "https://news.un.org/feed/subscribe/zh/news/all/rss.xml",
    "https://news.un.org/feed/subscribe/zh/audio-product/all/audio-rss.xml",
    "https://plink.anyfeeder.com/infzm/news",
    "https://sputniknews.cn/export/rss2/archive/index.xml"
]

DEFAULT_IMAGE = "https://r.yna.co.kr/global/home/v01/img/yonhapnews_logo_600x600_ck01.jpg"

def fetch_rss_updates():
    """获取RSS更新（2025年改进版：增强图片识别）"""
    updates = []
    for url in rss_urls:
        try:
            feed = feedparser.parse(url)
            feed_base = feed.get('href', url)  # 获取基准URL
            
            for entry in feed.entries[:5]:  # 每个源取最新5条
                entry_data = {
                    "title": entry.get('title', '无标题'),
                    "description": _parse_description(entry),
                    "url": entry.get('link', url),
                    "picurl": _find_image_url(entry, feed_base)
                }
                updates.append(entry_data)
                
        except Exception as e:
            print(f"[{datetime.now().isoformat()}] RSS解析错误: {url}")
            print(f"错误详情: {str(e)}")
            continue
            
    return updates

def _find_image_url(entry, base_url):
    """四级图片识别策略（2025年最新参数修复版）"""
    # 修正版安全访问函数（接收4参数）
    def safe_get(entry_dict, field_name, index=0, default=None):
        """安全获取嵌套字段值"""
        field_data = entry_dict.get(field_name, [{}])
        if isinstance(field_data, list) and len(field_data) > index:
            return field_data[index].get('url', default)
        return default

    # 第一级：显式媒体声明（参数顺序修正）
    media_sources = [
        lambda: safe_get(entry, 'media_content', 0, None),
        lambda: safe_get(entry, 'media_thumbnail', 0, None),
        lambda: safe_get(entry, 'enclosures', 0, None)
    ]

    # 第二级：元数据声明
    meta_source = lambda: _extract_meta_image(entry, base_url)
    
    # 第三级：内容首图
    content_source = lambda: _extract_first_image(entry, base_url)
    
    # 第四级：默认图片
    for source in [*media_sources, meta_source, content_source]:
        if (img_url := source()) and img_url.strip():
            return _normalize_url(img_url, base_url)
    
    return DEFAULT_IMAGE
    
def _parse_description(entry):
    """解析内容描述（修复空content列表问题）"""
    content_fields = ['summary', 'content', 'description']
    for field in content_fields:
        if (content := entry.get(field)) and isinstance(content, list) and len(content) > 0:
            return _clean_html(content[0].get('value', ''))
        elif content:
            return _clean_html(content)
    return ""

def _extract_meta_image(entry, base_url):
    """提取<meta>声明图片"""
    content = _parse_description(entry)
    match = re.search(
        r'<meta\s+name=["\']image["\']\s+content=["\']([^"\']+)["\']',
        content, 
        re.IGNORECASE
    )
    return urljoin(base_url, _unescape(match.group(1))) if match else None

def _extract_first_image(entry, base_url):
    """提取内容首图"""
    content = _parse_description(entry)
    match = re.search(
        r'<img[^>]+src=["\']([^"\']+)["\']',
        content,
        re.IGNORECASE
    )
    return urljoin(base_url, _unescape(match.group(1))) if match else None

def _clean_html(text):
    """基础HTML清理"""
    return re.sub(r'<[^>]+>', '', text).replace('&nbsp;', ' ')

def _normalize_url(url, base):
    """URL标准化处理"""
    url = _unescape(url)
    if url.startswith('//'):
        return f'https:{url}'
    return urljoin(base, url)

def _unescape(html):
    """处理HTML实体"""
    return html.replace('&amp;', '&').replace('&quot;', '"')

# 以下为数据存储和通知功能（保持原逻辑）----------------------------------------------------------------

def save_updates_to_file(updates, file_path):
    """保存更新到HTML文件"""
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('<html><body>\n')
        for update in updates:
            f.write(f"<h2>Title: {update['title']}</h2>\n")
            f.write(f"<p>Link: <a href='{update['url']}'>{update['url']}</a></p>\n")
        f.write('\n</body></html>')

def load_updates_from_file(file_path):
    """从文件加载历史记录"""
    if not os.path.exists(file_path):
        return []
    
    updates = []
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        items = content.split('<h2>Title: ')[1:]  # 跳过首空元素
        for item in items:
            title = item.split('</h2>')[0]
            url = item.split("href='")[1].split("'")[0]
            updates.append({"title": title, "url": url})
    return updates

def check_for_updates(new_updates, saved_updates):
    """检测新更新"""
    saved_titles = {u["title"] for u in saved_updates}
    return [u for u in new_updates if u["title"] not in saved_titles]

def send_to_wecom(updates):
    """推送消息到企业微信"""
    corp_id = os.getenv("WECOM_CORP_ID")
    agent_id = os.getenv("WECOM_AGENT_ID")
    agent_secret = os.getenv("WECOM_AGENT_SECRET")
    
    # 获取访问令牌
    token_url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={corp_id}&corpsecret={agent_secret}"
    token_res = requests.get(token_url).json()
    
    if 'access_token' not in token_res:
        print("获取Token失败:", token_res)
        return
    
    access_token = token_res['access_token']
    
    # 分批发送（每次8条）
    batch_size = 8
    for i in range(0, len(updates), batch_size):
        batch = updates[i:i+batch_size]
        articles = [{
            "title": u["title"],
            "description": u["description"][:100] + "...",  # 摘要截断
            "url": u["url"],
            "picurl": u["picurl"]
        } for u in batch]
        
        message = {
            "touser": "@all",
            "msgtype": "news",
            "agentid": agent_id,
            "news": {"articles": articles},
            "safe": 0
        }
        
        send_url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}"
        requests.post(send_url, json=message)

# 主执行流程 ----------------------------------------------------------------------------------------
if __name__ == "__main__":
    # 获取并处理更新
    latest_updates = fetch_rss_updates()
    
    if not latest_updates:
        print("未获取到任何更新")
        exit()
        
    # 检测新内容
    file_path = 'docs/index.html'
    saved = load_updates_from_file(file_path)
    new_items = check_for_updates(latest_updates, saved)
    
    if new_items:
        save_updates_to_file(latest_updates, file_path)
        send_to_wecom(new_items)
        print(f"成功推送 {len(new_items)} 条新内容")
    else:
        print("未发现新更新")
