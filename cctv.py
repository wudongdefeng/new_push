import re,os 

import requests 

from lxml import etree 
from os import environ
import time 

import yagmail 

  

  

  

# 设置请求头 

headers = { 

    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4651.0 Safari/537.36', 

} 

# 获取日期 

timeStruct = time.localtime() 

strTime = time.strftime("%Y%m%d", timeStruct) 

str_time = int(strTime)-1    #  如果是上午8点以后推送的，括号外的“-1”要删除 

  

# 获取新闻 

def hq_news(): 

  

    news = [] 

    url = f'https://tv.cctv.com/lm/xwlb/day/{str_time}.shtml' 

    response = requests.get(url, headers=headers) 

    response.encoding = 'RGB' 

    resp = response.text 

    etr = etree.HTML(resp) 

    titles = etr.xpath("//div[@class='title']/text()") 

    hrefs = etr.xpath("//li/a/@href") 

    for title, href in zip(titles, hrefs): 

        news_response = requests.get(href, headers=headers) 

        news_response.encoding = 'RGB' 

        news_resp = news_response.text 

        news_gz = '.*(<div class="cnt_bd"><!--repaste.body.begin-->.*?</div>).*' 

        news_zw = re.findall(news_gz, news_resp) 

        news_th = news_zw[0] 

        news.append(f"<font color='#000079'><b>{title}</b></font>\n{news_th}视频地址：{href}\n\n\n") 

    return news 

  

# 邮箱推送 

def main(event, context): 

    username = 'xxxxxxxx@163.com' 

    password = 'xxxxxxxx' 

    yag = yagmail.SMTP(user=username, password=password, host='smtp.163.com', port=465) 

    content = hq_news() 

    yag.send(to=['xxxxxxxx@qq.com'], subject=f'{str_time}新闻联播推送', contents=content) 

    return '邮件发送成功' 
def weixin_push(content):
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
    #设定天气预报城市与查询时间
    city_code =os.environ['city_code'] #先在weather.com.cn上查询城市天气，网址结尾的数字替换即可
    cookie =os.environ['cookie'] #在查询天气的时候，按F12，在控制台复制对应的cookie并填入
    info_time = datetime.now()
    timestamps = round(datetime.timestamp(info_time)*1000)
    #设定企业微信推送参数
    wxid =os.environ['wxid']
    wxsecret =os.environ['wxsecret']
    # 设定新闻时间（当天）与类型
    #财经：finance_0_suda 社会：news_society_suda 国内：news_china_suda 国际：news_world_suda
    #科技：tech_news_suda 军事：news_mil_suda 娱乐：ent_suda 体育：sports_suda 总排行：www_www_all_suda_suda
    news_type = 'news_china_suda'
    news_time = datetime.strftime(info_time,"%Y%m%d") 
    weixin_push(message_content(city_code,timestamps,info_time,get_news(news_type,news_time),get_sentence()))
