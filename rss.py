import feedparser
import traceback
import db
import os
import traceback

def get_news():
    result = []
    rss = 'https://news.ycombinator.com/rss'
    print(f"crawl==> {rss}")
    data = feedparser.parse(rss)
    for item in data['entries']:
        title = item['title']
        link = item['link']
        content = item['published']
        result.append({
            'title': title,
            'link': link,
            'content': f'{content}\nfrom rss news'
        })
    return content 
 def weixin_push(content):
    wx_push_token = requests.post(url='https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=%s&corpsecret=%s'%(wxid,wxsecret),data="").json()['access_token']
    wx_push_data = {
            "agentid":1000008,
            "msgtype":"text",
            "touser":"@all",
            "text":{
                    "content":content
            },
            "safe":0
        }
    requests.post('https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=%s'%wx_push_token,json=wx_push_data)
    
    if __name__ == '__main__':      
    wxid =os.environ['wxid']
    wxsecret =os.environ['wxsecret']    
    weixin_push(message_content(get_news()))
