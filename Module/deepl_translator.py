import requests
import os

DEEPL_KEY = os.getenv("DEEPL_KEY")

color_dic = {"black":"\033[30m", "red":"\033[31m", "green":"\033[32m", "yellow":"\033[33m", "blue":"\033[34m", "end":"\033[0m"}
def print_color(text, color="red"):
    print(color_dic[color] + text + color_dic["end"])

def translate_client(text,target_language='JA' ,source_language='EN',API_KEY=DEEPL_KEY):
    params = {
            'auth_key' : API_KEY,
            'text' : text,
            'source_lang' : source_language, # 翻訳対象の言語
            "target_lang": target_language  # 翻訳後の言語
    }
    request = requests.post("https://api-free.deepl.com/v2/translate", data=params) 
    result = request.json()["translations"][0]["text"]
    #print_color(f"{source_language}:{text}\n{target_language}:{result}","blue")
    return result

if __name__ == "__main__": 
    print(translate_client("趣味は何ですか？","EN","JA"))