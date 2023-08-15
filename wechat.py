import requests

QYWX_KEY =  os.environ['webhook']
#传入文件
def post_file(id_url,wx_url,file):
    data = {'file': open(file,'rb')}
    # 请求id_url(将文件上传微信临时平台),返回media_id
    # id_url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/upload_media?key=xxx&type=file'
    response = requests.post(url=id_url, files=data)
    json_res = response.json()
    media_id = json_res['media_id']

    data = {"msgtype": "file",
             "file": {"media_id": media_id}
            }
    result = requests.post(url=wx_url,json=data)
    return(result)


file1 = './wechat.py'		#文件路径
id_url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/upload_media?key=' + QYWX_KEY + '&type=file'	#把机器人的key放入
wx_url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=' + QYWX_KEY	#把机器人的key放入
post_file(id_url, wx_url, file=file1)

print('发送完成')
