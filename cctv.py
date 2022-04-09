import re
import os
import requests 
from lxml import etree 
from os import environ
import time 

import yagmail 

# 设置请求头 

headers = { 

"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4651.0 Safari/537.36",

} 

# 获取日期 

timeStruct = time.localtime() 
strTime = time.strftime("%Y%m%d", timeStruct) 
str_time = int(strTime)    #  如果是上午8点以后推送的，括号外的“-1”要删除 

  

# 获取新闻 

def hq_news(): 

  

    news = [] 

    url = f"https://tv.cctv.com/lm/xwlb/day/{str_time}.shtml" 

    response = requests.get(url, headers=headers) 

    response.encoding = "RGB" 

    resp = response.text 

    etr = etree.HTML(resp) 

    titles = etr.xpath("//div[@class='title']/text()") 

    hrefs = etr.xpath("//li/a/@href") 

    for title, href in zip(titles, hrefs): 

        news_response = requests.get(href, headers=headers) 

        news_response.encoding = 'RGB' 

        news_resp = news_response.text 

        news_gz = ".*(<div class="cnt_bd"><!--repaste.body.begin-->.*?</div>).*" 

        news_zw = re.findall(news_gz, news_resp) 

        news_th = news_zw[0] 

        news.append(f"<font color='#000079'><b>{title}</b></font>\n{news_th}视频地址：{href}\n\n\n") 

    return news 

  


def weixin_push(news):
    wx_push_token = requests.post(url='https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=%s&corpsecret=%s'%(wxid,wxsecret),data="").json()['access_token']
    wx_push_data = {
            "agentid":1000002,
            "msgtype":"text",
            "touser":"@all",
            "text":{
                    "content":news
            },
            "safe":0
        }
    requests.post('https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=%s'%wx_push_token,json=wx_push_data)

if __name__ == '__main__':
    #设定企业微信推送参数
    wxid =os.environ['wxid']
    wxsecret =os.environ['wxsecret']
    weixin_push(hq_news())
