import pygtrans

from baidufanyi import BaiduFanyi

from DeepL import DeepL
from YouDao import YouDao


class Translate:

    def __init__(self, **args):
        super().__init__()
        self.args = args

    def translate(self, text, target='en', source='auto'):
        return text


class GoogleTranslate(Translate):
    def __init__(self, **args):
        super().__init__(**args)

    def translate(self, text, target='en', source='auto'):
        return pygtrans.Translate(**self.args).translate(text, target, source).translatedText


class DeepLTranslate(Translate):
    def __init__(self, **args):
        super().__init__(**args)

    def translate(self, text, target='en', source='auto'):
        return DeepL(source, target).translate(text)


class BaiduTranslate(Translate):
    def __init__(self, **args):
        super().__init__(**args)

    def translate(self, text, target='en', source='auto'):
        return BaiduFanyi(**self.args).translate(text, fromLang=source, toLang=target)


class YoudaoTranslate(Translate):
    def __init__(self, **args):
        super().__init__(**args)

    def translate(self, text, target='en', source='auto'):
        return YouDao().translate(text)


if __name__ == '__main__':
    # a = GoogleTranslate(**{'proxies': {'https': 'http://localhost:60801'}})
    # print(a.translate(**{'text': '你好', 'target': 'en'}))

    # a = DeepLTranslate(**{'provider': 'deepl'})
    # print(a.translate(**{'text': '你好', 'target': 'English', 'source': 'Chinese'}))

    a = BaiduTranslate()
    print(a.translate(**{'text': '你好', 'target': 'en', 'source': 'zh'}))
