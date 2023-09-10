import time
import obsws_python as obs
import json
from pprint import pprint
from Module.print_color import print_color
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException

class obs_socket():
    def __init__(self):
        # OBSの接続設定
        self.host = "localhost"
        self.port = 4455
        self.password = "nDCgoGVKLiJBKKRr"
        self.request = obs.ReqClient(host=self.host, port=self.port, password=self.password)
        self.event = obs.EventClient(host=self.host, port=self.port, password=self.password)
        self.Display_size =[]

    def get_settings(self):
        #画面サイズの取得
        self.Display_size=[self.request.get_video_settings().base_width,self.request.get_video_settings().base_height]
        print(f"DisplaySize: {self.Display_size}")

    def GetSceneList(self):
        #Return Example
        #{'current_preview_scene_name': None, 'current_program_scene_name': 'scene1', 'scenes': [{'sceneIndex': 0, 'sceneName': 'scene2'}, {'sceneIndex': 1, 'sceneName': 'scene1'}]}
        mydirect=self.request.get_scene_list()
        results={}
        for item in mydirect.attrs():
            results[item] = getattr(mydirect,item)  # 各属性の値を辞書に保存します。
        return results

    def GetSceneItemList(self):
        mydirect=self.request.get_scene_item_list("scene1")
        print("GetSceneItemList:")
        for item in mydirect.attrs():
            print(f"{item}:")
            pprint(getattr(mydirect,item))
    
    def GetInputKindList(self,unversioned=True):
        mydirect=self.request.get_input_kind_list(unversioned)
        print("GetInputKindList:")
        for item in mydirect.attrs():
            print(f"{item}:")
            pprint(getattr(mydirect,item))
        return getattr(mydirect,item)
    
    def GetInputDefaultSettings(self,inputName):
        mydirect=self.request.get_input_default_settings(inputName)
        print("GetInputDefaultSettings:")
        for item in mydirect.attrs():
            print(f"{item}:")
            pprint(getattr(mydirect,item))
    
    def GetInputSettings(self,inputName):
        mydirect=self.request.get_input_settings(inputName)
        print("GetInputSettings:")
        for item in mydirect.attrs():
            print(f"{item}:")
            pprint(getattr(mydirect,item))
    
    def SetInputSettings(self,inputName,inputSettings,overlay=True):
        self.request.set_input_settings(name=inputName,settings=inputSettings,overlay=overlay)
    
    def GetSceneItemId(self,scene_name,source_name):
        mydirect=self.request.get_scene_item_id(scene_name=scene_name,source_name=source_name)
        for item in mydirect.attrs():
            print(f"{item}:")
            pprint(getattr(mydirect,item))
        return getattr(mydirect,item)
    
    def GetSceneItemTransform(self,scene_name,item_id):
        mydirect=self.request.get_scene_item_transform(scene_name=scene_name,item_id=item_id)
        print("GetSceneItemTransform:")
        for item in mydirect.attrs():
            print(f"{item}:")
            pprint(getattr(mydirect,item))
    
    def GetSceneItemIndex(self,scene_name,item_id):
        mydirect=self.request.get_scene_item_index(scene_name=scene_name,item_id=item_id)
        for item in mydirect.attrs():
            print(f"{item}:")
            pprint(getattr(mydirect,item))
    
    def GetSourceFilterList(self,source_name):
        mydirect=self.request.get_source_filter_list(source_name)
        for item in mydirect.attrs():
            print(f"{item}:")
            pprint(getattr(mydirect,item))
    
    def GetSourceFilterDefaultSettings(self,filterKind):
        mydirect=self.request.get_source_filter_default_settings(filterKind)
        for item in mydirect.attrs():
            print(f"{item}:")
            pprint(getattr(mydirect,item))
    
    #Record Request
    def StartRecord(self):
        self.request.start_record()
    
    def StopRecord(self):
        self.request.stop_record()
    
    def text_change(self,inputName,inputSettings,overlay,sceneName = 'auto',fontsize=48,bk_color=0,bk_opacity=0,subDisplayAnchor='bottom',subDisplayOffset = 0,lineBreakTextMax_jp=70,lineBreakTextMax_en=102):
        #フォント等設定 カラーはXlRgbColorで指定する。
        TextBoxSetting_JP={  'align': 'left',
                    'antialiasing': True,
                    'bk_color': bk_color,
                    'bk_opacity': bk_opacity,
                    'chatlog_lines': 6,
                    'color': 16777215,
                    'extents_cx': 100,
                    'extents_cy': 100,
                    'extents_wrap': True,
                    'font': {'face': 'コーポレート・ロゴ ver3 Medium', 'size': fontsize},
                    'gradient_color': 16777215,
                    'gradient_dir': 90.0,
                    'gradient_opacity': 100,
                    'opacity': 100,
                    'outline_color': 16777215,
                    'outline_opacity': 100,
                    'outline_size': 2,
                    'transform': 0,
                    'valign': 'top'}
        
        TextBoxSetting_EN={  'align': 'left',
                    'antialiasing': True,
                    'bk_color': bk_color,
                    'bk_opacity': bk_opacity,
                    'chatlog_lines': 6,
                    'color': 16777215,
                    'extents_cx': 100,
                    'extents_cy': 100,
                    'extents_wrap': True,
                    'font': {'face': 'Arial', 'size': fontsize},
                    'gradient_color': 16777215,
                    'gradient_dir': 90.0,
                    'gradient_opacity': 100,
                    'opacity': 100,
                    'outline_color': 16777215,
                    'outline_opacity': 100,
                    'outline_size': 2,
                    'transform': 0,
                    'valign': 'top'}
        
        #設定されたボックステキストが同一か確認
        if inputSettings == str(self.request.get_input_settings(inputName).input_settings):
            time.sleep(0.1)
            return
        #画面サイズを取得しているか確認
        if self.Display_size==[]:
            self.get_settings()
        
        #シーン名を取得
        if sceneName=='auto':
            scenelist=self.GetSceneList()
            sceneName=scenelist['current_program_scene_name']

        #テキストボックスのidを取得
        try:
            item_id=self.request.get_scene_item_id(scene_name=sceneName,source_name=inputName).scene_item_id
        except obs.error.OBSSDKError as e:
            print_color(f"OBSSDKError: {e}\n[字幕は更新されませんでした。]")
            return
        #print("Transform:")
        #print(self.request.get_scene_item_transform(scene_name=sceneName,item_id=item_id).scene_item_transform)

        
        #言語を判定し言語によりテキスト設定の変更
        try:
            if detect(inputSettings["text"]) == 'ja':
                lineBreakTextMax=lineBreakTextMax_jp
                TextBoxSetting = TextBoxSetting_JP
            else:
                lineBreakTextMax=lineBreakTextMax_en
                TextBoxSetting = TextBoxSetting_EN
        except LangDetectException as e:
            print_color(f"[OBS]Error detecting language: {e}\nInput Text:{inputSettings['text']}")
            # エラー発生時のデフォルト設定
            lineBreakTextMax=lineBreakTextMax_en
            TextBoxSetting = TextBoxSetting_EN\

        #文章長さを取得し長い場合改行する
        result = ""
        if len(inputSettings["text"])>= lineBreakTextMax:
            text = inputSettings["text"]
            for i in range(0, len(text), lineBreakTextMax):
                result += text[i:i+lineBreakTextMax]
                if i + lineBreakTextMax < len(text):
                    result += "\n"
            inputSettings["text"] = result
        
        inputSettings.update(TextBoxSetting)
        #print(f"Inputs:{inputSettings}")
        #テキストボックスを変更する
        self.request.set_input_settings(name=inputName,settings=inputSettings,overlay=overlay)
        BR_count = result.count('\n')+1
        positonY = 0
        #テキストボックス位置を変更
        if subDisplayAnchor == 'bottom':
            positonY = (self.Display_size[1] - (BR_count*fontsize) - subDisplayOffset).__round__(3)
        else:
            positonY = subDisplayOffset
        self.request.set_scene_item_transform(scene_name=sceneName,item_id=item_id,transform={'scaleX': 1,'scaleY': 1,'positionY':positonY})
        #print("after:")
        #pprint(self.request.get_scene_item_transform(scene_name=sceneName,item_id=item_id).scene_item_transform)

if __name__ == "__main__":
    obsclass=obs_socket()
    obsclass.get_settings()
    obsclass.GetSceneList()
    text_JP = """Aiユーチューバーって面白いよね。最近は技術が進化して、もう人間と見分けが付かないくらいリアルに動いたり喋ったりするよ！自分で画面の中で色々なことをして、みんなに笑いを提供できるなんてすごいことだよね。ありがと、博士！これからも面白い話題を提供できるように頑張るね！"""
    text_EN = '''Ai YouTubers are very interesting, aren't they? Technology has evolved so much recently that they can move and talk so realistically that you can hardly distinguish them from human beings! It's amazing how you can do things on screen and make people laugh. Thank you, Doctor! I will keep trying my best to provide interesting topics!'''
    obsclass.text_change(inputName="subs",inputSettings={"text":text_JP},overlay=False)
    time.sleep(3)
    obsclass.text_change(inputName="subs",inputSettings={"text":text_EN},overlay=False)
    
"""
    text=""
    for count in range(50):
        text+=str(count)
        obsclass.text_change(sceneName="scene1",inputName="sub_text",inputSettings={"text":text},overlay=False)
    for i in range(len(text), 0, -1):
        text = text[:i]
        obsclass.text_change(sceneName="scene1",inputName="sub_text",inputSettings={"text":text},overlay=False)
        """