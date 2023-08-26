# 默认百度，可在第8行修改其他源：1.Baidu 2.DouYin 3.SoGou 4.So 5.WeiBo 6.ZhiHu 7.TouTiao 8.KuaiShou 9.BiliBli 10.BaiduTieBa
import requests
import json
import notify
orig = 'TouTiao' #如需改成抖音就填DouYin，以此类推
url = f'https://api.gumengya.com/Api/{orig}Hot?format=json'
resp = requests.get(url)
data = json.loads(resp.text)
news = ""
for i in range(8):
    item = data['data'][i]
    news += item['title'] + ' ' + item['url'] + "\n" + "\n"
notify.send("今日热搜", news)
