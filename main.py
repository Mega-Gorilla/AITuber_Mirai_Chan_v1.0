import os
import sys
import multiprocessing
import azure.cognitiveservices.speech as speechsdk
import ctypes
import time
import openai
import json
import re
import VtubeStudio_API
import websockets
import asyncio
import pyaudio
import platform
from pprint import pprint
from Module.OBS_plugin_5 import obs_socket
from Module.print_color import print_color
from Module.voicevox import text_to_wave
from pynput import keyboard
from Module.deepl_translator import translate_client
from Module.vtubeStudio_GPT_motion import VtubeStudio_GPTmotion_Stream,VtubeStudio_emotion
from Module.voicevox_GPT import VoiceVoxGPT_AutoPich,Create_AutoPich_Preset
 
# 初期設定
speech_key = os.getenv("AZURE_API_KEY")
openai.api_key = os.getenv("OPENAI_API_KEY")
speech_region = "japaneast"
obs= obs_socket()
scene_name = "auto"
 
# Process1 / 音声認識を行う関数
def recognize_speech(speech_key, speech_region, SubList, stop_event):
    try:
        speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region, speech_recognition_language='ja-JP')
        audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    except Exception as e:
        print_color(f"エラーが発生しました: {e}")

    print_color("音声認識を開始しました。","green")

    def on_recognized(args):
        recognized_text = args.result.text
        print_color(f"{recognized_text}","blue")
        if recognized_text != "": 
            #print_color(f"{recognized_text}","blue")
            SubList['userSub']+=recognized_text
            obs.text_change(sceneName=scene_name,inputName="subs1",inputSettings={"text":recognized_text},overlay=False,subDisplayAnchor='top',subDisplayOffset=36,fontsize=48,bk_color=8721863,bk_opacity=60)

            DeepL_time = time.time() 
            en_user=translate_client(recognized_text,'EN','JA').replace('\n', '')
            transrate_time = time.time()-DeepL_time
            if transrate_time < 2:
                time.sleep(2-transrate_time)
            else:
                print_color(f'\n<注意>翻訳時間が長い可能性があります。\nDeepLTranslate Time:{time.time()-DeepL_time}sec\n{en_user}',"yellow")
            
            obs.text_change(sceneName=scene_name,inputName="subs1",inputSettings={"text":en_user},overlay=False,subDisplayAnchor='top',subDisplayOffset=36,fontsize=48,bk_color=8721863,bk_opacity=60)
    def on_canceled(args):
        if args.reason == speechsdk.CancellationReason.Error:
            print_color(f"音声認識エラーが発生しました: {args.error_details}")

    try:
        speech_recognizer.recognized.connect(on_recognized)
        speech_recognizer.canceled.connect(on_canceled)  # エラーハンドリングを追加
        speech_recognizer.start_continuous_recognition()
    except Exception as e:
        print(f"エラーが発生しました: {e}")
    # stop_eventがセットされるまで音声認識を続ける
    stop_event.wait()
    speech_recognizer.stop_continuous_recognition()

# Process2 / GPTに問い合わせを行うプロセス
def gpt_process(SubList,gpt_result_list,openai_key,key_flag,end_flag,MemoryList):
    Talk_Data_str=""
    with end_flag.get_lock():
        loop_flag = end_flag.value
    
    while not loop_flag:
        read_flag = False
        with key_flag.get_lock():
            if key_flag.value:
                read_flag = True
                key_flag.value = False
        if read_flag:
            #読み上げフラグが立っている
            if not SubList['userSub']=="":
                Talk_Data_str = SubList['userSub']
                OpenAI_Stream(openai_key,Talk_Data_str,gpt_result_list,MemoryList)
                Talk_Data_str=""
                SubList['userSub'] = ""
        
        #終了する必要があるか判別
        with end_flag.get_lock():
            loop_flag = end_flag.value
        time.sleep(0.1)

#Process2関連 / OpenAI問い合わせ
def OpenAI_Stream(key,talk_str,gpt_result_list,MemoryList,max_retries = 3):
    openai.api_key = key
     
    #メモリ容量
    #1メモリ=１応答,メモリー量は、応答時間およびToken Maxを考慮すること
    memory_capacity = 4
    memory_capacity = memory_capacity *2
    
    process_time=time.time()
    ###Promptの読み込み###
    prompts={}
    current_key=""
    
    ##システムプロンプトの取得
    #txtファイルよりプロンプトの取得
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),"prompt.txt")
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file: 
            if line.strip().endswith("::"):
                current_key = line.strip()[:-2]
                current_key = current_key.strip() #空欄の消去
                prompts[current_key] = ""
            else:
                if line != '' or line != '\n':
                    prompts[current_key] += line.strip() + "\n"
    #システムプロンプトの追加
    ChatGPT_Prompt=[{"role": "system", "content": prompts.get("system")}]
    #メモリープロンプトの処理
    if len(MemoryList)!=0:
        #メモリ容量を超えたデータは破棄する。
        while len(MemoryList) > memory_capacity:
            MemoryList.pop(0) #切り取り
        ChatGPT_Prompt+=list(MemoryList) #メモリデータプロンプトの追加
        print("メモリ内容:",list(MemoryList))
    
    #取得した会話内容をユーザープロンプトとして追加
    ChatGPT_Prompt.append({"role": "user", "content": talk_str})
    
    #メモリーにユーザー読み上げデータの追加
    MemoryList.append({"role": "user", "content": talk_str})
    
    #print_color("#####プロンプト#####","yellow")  
    #for prompt in ChatGPT_Prompt:
    #    print_color(f"[{{'content': '{prompt['content']}'}}]","yellow")
    
    ###OpenAI Stream 実行###
    process_time=time.time()
    for i in range(max_retries):
        try:
            for chunk in openai.ChatCompletion.create(
                model="gpt-4", 
                messages=ChatGPT_Prompt,
                stream=True,
            ): 
                content = chunk["choices"][0].get("delta", {}).get("content")
                if content is not None:
                    print_color(f"{content}",'green',True)
                    gpt_result_list.put(content)
            # 成功したらループを抜ける
            break

        except openai.error.RateLimitError:
            # エラーメッセージを表示
            print_color(f"モデルが他のリクエストで過負荷となっています。")
            # エラーが持続する場合はOpenAIのヘルプセンターに連絡を促すメッセージを表示
            print_color(f"エラーが持続する場合は、help.openai.com に連絡してください。")
            # リトライの間隔を設定（ここでは例として1秒）
            time.sleep(1)
        except Exception as e:
            # その他のエラーを表示
            print_color(f"OpenAI問い合わせ中に、予期せぬエラーが発生しました：{e}")
            break
    print_color(f" / GPT4問い合わせ時間: {(time.time()-process_time):.1f}sec","yellow")
    #メモリーをテキストに記録
    with open('memory.txt', 'w',encoding='utf-8') as f:
        for item in MemoryList:
            f.write(json.dumps(item, ensure_ascii=False))
            f.write('\n')

#Process3 / GPTの出力を監視し、読み上げ文章があるときは加工して読み上げと表情変更の関数を作成する。
def convert_mirai_subGPT(gpt_result_list,VoiceVox_text_list,end_flag,MemoryList,shared_emotion_value,SubList,speakflag): 
    punctuation_marks = ("。", "？", "！",'!','?','"',')')
    VoiceVoxText=""
    emotion=""
    memoryText=""
    obs_mirai_sub = ""
    Mode_is = 0
    Readonly_mode=0
    VoiceVoxMode=1
    emotionMode=2
    
    with end_flag.get_lock():
        loop_flag = end_flag.value
     
    while not loop_flag:
        while not gpt_result_list.empty():
            #読み上げ文章がある
            TempText=gpt_result_list.get() #GPT出力テキストの取得
            memoryText+=TempText #一時メモリにテキストを追加

            #GPT出力終了記号検知
            if "}" in TempText:

                #メモリへGPT出力内容を追加
                MemoryList.append({"role": "assistant", "content": memoryText})
                print_color(f"メモリー追加:{memoryText}","green")
                memoryText = ""

                #英語字幕の表示
                DeepL_time=time.time()
                EN_sub = translate_client(obs_mirai_sub,'EN','JA').replace('\n', '')
                transrate_time = time.time()-DeepL_time
                if transrate_time < 2:
                    time.sleep(2-transrate_time)
                else:
                    print_color(f'\n<注意>翻訳時間が長い可能性があります。\nDeepLTranslate Time:{time.time()-DeepL_time}sec\n{EN_sub}',"yellow")
                obs.text_change(sceneName=scene_name,inputName="subs",inputSettings={"text":EN_sub},overlay=False,subDisplayAnchor='bottom',subDisplayOffset=36,fontsize=48,bk_color=14772545,bk_opacity=60)
                obs_mirai_sub = ""

                Mode_is =Readonly_mode
                continue
            #特殊記号の時は無視 
            elif any(mark in TempText for mark in ("{",":",'"',"->","assistant")):
                continue
            #contentの場合は、VoiceVox音声読み上げモード
            elif TempText == "content":
                Mode_is = VoiceVoxMode

                # 表情データの送信 (プロンプトにて、emotionとcontentの順番が変わった場合変更必要)
                shared_emotion_value["emotion"] = emotion
                emotion = ""
                continue
            #emotionの場合は、VtubeStudio表情変更モード
            elif TempText == "emotion":
                Mode_is = emotionMode
                continue
            
            if Mode_is == VoiceVoxMode:
                #ViceVox 声質の受信
                speakflag.wait()
                #VoiceVox Mode
                VoiceVoxText+=TempText
                obs_mirai_sub+=TempText
                
                #punctuation_marksを参照し、対象の記号が含まれる場合、VoiceVoxによる読み上げを行う
                #print(VoiceVoxText)
                if any(mark in VoiceVoxText for mark in punctuation_marks):
                    VoiceVox_text_list.put(VoiceVoxText) #VoiceVoxで読み上げるテキストをリストに追加
                    #OBS字幕の表示
                    SubList['miraiSub']=obs_mirai_sub
                    obs.text_change(sceneName=scene_name,inputName="subs",inputSettings={"text":obs_mirai_sub},overlay=False,subDisplayAnchor='bottom',subDisplayOffset=36,fontsize=48,bk_color=14772545,bk_opacity=60)
                    VoiceVoxText=""
            elif Mode_is == emotionMode:
                #emotion mode
                emotion+=TempText
            elif Mode_is == Readonly_mode:
                continue
            
        #終了する必要があるか判別
        with end_flag.get_lock():
            loop_flag = end_flag.value
        time.sleep(0.1)

#Process4 VoiceVox読み上げプロセス
def VoiceVoxPlayVoice(VoiceVox_text_list,end_flag,charactor_preset):
    with end_flag.get_lock():
        loop_flag = end_flag.value
    stream = audio_stream_start()
    while not loop_flag:
        while not VoiceVox_text_list.empty():
            #音声読み上げの実施
            Speech_text=VoiceVox_text_list.get()
            wavedata=text_to_wave(Speech_text,preset_id=0,speaker=charactor_preset["style_id"])
            stream.write(wavedata)
            time.sleep(0.01)
        #終了する必要があるか判別
        with end_flag.get_lock(): 
            loop_flag = end_flag.value
        time.sleep(0.1)
    audio_stream_stop(stream)

#Process4
def audio_stream_start():
    p = pyaudio.PyAudio()

    # VB-CABLEのインデックスを見つける
    current_os = platform.system()
    mic_name =""
    vb_cable_index = -1
    if current_os == "Windows":
        mic_name = "CABLE Input"
    else:
        mic_name = "VB"

    for i in range(p.get_device_count()):
        dev_info = p.get_device_info_by_index(i)
        #print(dev_info['name'])
        if mic_name in dev_info["name"]:
            vb_cable_index = dev_info["index"]
            #print(f'再生デバイス名: {dev_info["name"]}')
            break

    if vb_cable_index == -1:
        print("VB-Audio Virtualが見つかりませんでした。インストール済みかどうか確認してください。")
        return
    
    # ストリームを開く
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=24000,
                    output=True,
                    output_device_index=vb_cable_index)
    #プツ音防止の為、待機
    time.sleep(0.4)
    return stream
#Process4
def audio_stream_stop(stream):
    p = pyaudio.PyAudio()
    stream.stop_stream()
    stream.close()

    p.terminate()

#Process5
def background_GPT(OpenAI_key,shared_emotion_value,end_flag,speak_flag,charactor_preset):
    openai.api_key=OpenAI_key
    current_emotion=""

    with end_flag.get_lock():
        loop_flag = end_flag.value
    
    while not loop_flag:
        emotion = shared_emotion_value['emotion']

        #VTS表情+声ピッチに関する問い合わせ実施
        if current_emotion != emotion:
            asyncio.run(async_func(openai_key,emotion,speak_flag,charactor_preset))
            current_emotion = emotion
        
        #終了する必要があるか判別
        with end_flag.get_lock():
            loop_flag = end_flag.value
        time.sleep(0.1)

async def async_func(openai_key,emotion,speak_flag,charactor_preset):
    print_color(f'Emotion:{emotion}','yellow')

    result1 = VoiceVoxGPT_AutoPich(openai_key,emotion)
    if result1 != True:
        Create_AutoPich_Preset(charactor_preset,result1)
    print_color(f'VoiceControl:{result1}','yellow')
    speak_flag.set()

    result2 = VtubeStudio_GPTmotion_Stream(openai_key,emotion)
    print_color(f'VTSControl:{result2}','yellow')
    if result2 != True:
        await VtubeStudio_emotion(result2,200)

#Process6 関連
def on_press(key, key_flag):
    try:
        if key == keyboard.Key.space:
            with key_flag.get_lock():
                key_flag.value = True
                print_color("space","green")
    except AttributeError:
        pass
    time.sleep(0.1)

#Process6 関連
def on_release(key, key_flag,end_flag):
    if key == keyboard.Key.esc:
        with end_flag.get_lock():
            end_flag.value = True
    time.sleep(0.1)

#Process6 / キーボード入力を監視 
def monitor_key(key_flag,end_flag):
    with keyboard.Listener(on_press=lambda key: on_press(key, key_flag), on_release=lambda key: on_release(key, key_flag,end_flag)) as listener:
        listener.join()

# multiprocessingで音声認識を実行する
if __name__ == "__main__":
    #キャラクタ設定
    charactor_preset={
        'CharacterName': 'みらい',
        'speaker_uuid': '882a636f-3bac-431a-966d-c5e6bba9f949',
        'style_id':48,
        'speakingSpeed':{'min':0.9,'default':1.0,'max':1.1},
        'pitch':{'min':-0.12,'default':-0.04,'max':0.01},
        'intonation':{'min':0.8,'default':1.3,'max':1.4}
        }
    #ネットワーク接続の確認
    response = os.system("ping -n 1 google.com > nul 2>&1") # Windowsの場合
    if response == 0:
        print_color("Internet Connection is Available",'green')
    else:
        print_color("Internet Connection is Not Available")
        sys.exit(1)
    
    #VTS認証確認
    asyncio.get_event_loop().run_until_complete(VtubeStudio_API.VTS_main().Authentication_Check())

    #共有配列の作成(出し入れあり)
    GPT_reslut_list = multiprocessing.Queue()
    VoiceVox_text_list = multiprocessing.Queue()

    #共有配列を作成
    MemoryList = multiprocessing.Manager().list()

    SubList = multiprocessing.Manager().dict()
    SubList["miraiSub"]=''
    SubList['userSub']=''

    shared_emotion_value = multiprocessing.Manager().dict()
    shared_emotion_value["emotion"] = ""

    #音声認識を止めるためのフラグ
    Speak_Flag = multiprocessing.Event()
    stop_event = multiprocessing.Event()
    
    #共有boolの作成
    key_flag = multiprocessing.Value(ctypes.c_bool, False)
    end_flag = multiprocessing.Value(ctypes.c_bool, False)
    
    #プロセスの作成 
    process1 = multiprocessing.Process(target=recognize_speech, args=(speech_key, speech_region, SubList, stop_event,))
    process2 = multiprocessing.Process(target=gpt_process, args=(SubList, GPT_reslut_list, openai_key, key_flag, end_flag,MemoryList,))
    process3 = multiprocessing.Process(target=convert_mirai_subGPT, args=(GPT_reslut_list,VoiceVox_text_list,end_flag,MemoryList,shared_emotion_value,SubList,Speak_Flag,))
    process4 = multiprocessing.Process(target=VoiceVoxPlayVoice, args=(VoiceVox_text_list,end_flag,charactor_preset,))
    process5 = multiprocessing.Process(target=background_GPT, args=(openai_key,shared_emotion_value,end_flag,Speak_Flag,charactor_preset,))
    process6 = multiprocessing.Process(target=monitor_key, args=(key_flag,end_flag))
    process1.start()
    process2.start()
    process3.start()
    process4.start()
    process5.start()
    process6.start()
    
    while end_flag.value == False:
        time.sleep(0.5)
    
    stop_event.set()
    print("終了")

    process1.join()
    process2.join()
    process3.join()
    process4.join()
    process5.join()
    process6.join()