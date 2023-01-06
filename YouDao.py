import requests
import json


class YouDao:

    def __init__(self):
        # 有道词典 api
        self.url = 'http://fanyi.youdao.com/translate?smartresult=dict&smartresult=rule&smartresult=ugc&sessionFrom=null'

    def translate(self, word):
        # 传输的参数，其中 i 为需要翻译的内容
        key = {
            'type': "AUTO",
            'i': word,
            "doctype": "json",
            "version": "2.1",
            "keyfrom": "fanyi.web",
            "ue": "UTF-8",
            "action": "FY_BY_CLICKBUTTON",
            "typoResult": "true"
        }
        # key 这个字典为发送给有道词典服务器的内容
        response = requests.post(self.url, data=key)
        # 判断服务器是否相应成功
        if response.status_code == 200:
            # 然后相应的结果
            result = json.loads(response.text)
            result = result['translateResult'][0][0]['tgt']
        else:
            result = "有道词典调用失败"

        return result


if __name__ == '__main__':
    # 调用
    print(YouDao().translate('The 21st century'))
