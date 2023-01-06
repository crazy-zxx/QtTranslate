import requests


class DeepL:
    def __init__(self, from_lang, to_lang):
        self.url = "https://hf.space/embed/mikeee/gradio-deepl/+/api/predict"
        self.from_lang = from_lang
        self.to_lang = to_lang

    def translate(self, text):
        data = [text, self.from_lang, self.to_lang]
        json_data = {"data": data}
        resp = requests.post(self.url, json=json_data)
        trans = resp.json()

        return trans['data'][0]


if __name__ == '__main__':
    print(DeepL("en", "zh").translate('My heart is slightly larger than the whole universe.'))
