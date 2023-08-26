import requests
import bs4
import os
QYWX_KEY =  os.environ['webhook']
# 自定义一个请求函数，参数是网址\请求头\请求参数，没有参数就空着，请求成功后返回页面的新闻列表
def catchnewslist(newsurl, headers, params):
    urllist = []
    titlelist = []
    resultlist = []
    response = requests.get(newsurl, headers=headers)
    if response.status_code == 200:
        print("请求成功！")
        response.encoding = 'utf-8'
        content = bs4.BeautifulSoup(response.text, 'html.parser')
        elements = content.select("body ol a")               # 这一句就是提取请求到的页面内容中要提取的新闻，根据不同的页面结构进行修改
        for i in range(8):                                 # 把取到的新闻列表数据存到一个python列表中，方便后面使用
            urllist.append(elements[i].get('href'))
            titlelist.append(elements[i].string)
        resultlist = [[a, b] for a, b in zip(urllist, titlelist)]   # 把标题和地址组合成一个嵌套列表，并返回
    else:
        print(response.status_code)
        print("请求失败！")
    return resultlist

# 定义一个向企业微个webhook地址post数据的函数，参数为地址和数据，这里post的是md5格式的字符串
def postmsg(url, post_data):
    post_data = '{"msgtype":"markdown","markdown":{"content":"%s"}}' % post_data
    # print(post_data)

    if url == '':
        print('url is blank')
    else:
        r = requests.post(url, data=post_data.encode())
        rstr = r.json()
        if r.status_code == 200 and 'error' not in rstr:
            result = 'success!'
            return result
        else:
            return 'Error'

# 主函数
if __name__ == '__main__':
    newsurl = "http://rss.io.dc-wind.eu.org"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0"}
    # params = {"datatype":"jsonp", "page":"1", "callback":"flightHandler"}  参数视需求添加
    newslist = catchnewslist(newsurl, headers, '')
    print(newslist)
    # 把请求回来的数据，按照要post到接口的md的格式再处理一下
    newslistdata = u"### 最新新闻： \n"
    for i in newslist:
        # print("[%s](%s)" % (i[1], i[0]))
        newslistdata = newslistdata + "%s [%s](%s)" % (newslist.index(i) + 1, i[1], i[0]) + "\n"
    print(newslistdata)
    url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=" + QYWX_KEY  # 要post的群机器人的webhook地址
    # post_data = '[这是一个链接](http://work.weixin.qq.com/api/doc)' # 带链接的md字符串格式
    result = postmsg(url, newslistdata)  # 调用post，向webhook发送数据
    print(result)
