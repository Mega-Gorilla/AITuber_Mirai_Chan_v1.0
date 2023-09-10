"""
このモジュールは、音声合成のVoiceVox APIと直接通信するためのPythonスクリプトです。
主な機能は、音声のプリセットを作成、更新、削除し、利用可能なスピーカーを取得、そしてテキストを音声に変換することです。さらに、合成された音声を再生するためのオーディオストリームを開始・停止する機能も提供します。

プリセットを新規作成し、音声データを作成、再生するサンプルコード:

Add_preset(id=0,name="ナースロボ-ノーマル",speaker_uuid="882a636f-3bac-431a-966d-c5e6bba9f949",style_id=47,speedScale=1.15,pitchScale=0.0,intonationScale=1.3,volumeScale=1.0,prePhonemeLength=0.0,postPhonemeLength=0.0)
stream = audio_stream_start()
data=text_to_wave('''みなさん、こんにちは！ みらいちゃんことみらいです！''',preset_id=0,speaker=47)
stream.write(data)
print(f"処理時間:{time.time()-processtime}")
audio_stream_stop(stream)
"""

# coding: utf-8
import requests
import json
import time
import pyaudio
import platform
from pprint import pprint

def audio_query(text, speaker, max_retry=3):
    """
    音声合成のための問い合わせを作成する関数。

    Args:
        text (str): 音声合成するテキスト。
        speaker (int): 使用するスピーカーのID。
        max_retry (int, optional): リトライの最大回数。デフォルトは3。

    Raises:
        ConnectionError: リトライ回数が上限に達した場合。

    Returns:
        dict: 問い合わせデータ。
    """
    query_payload = {"text": text, "speaker": speaker}
    for query_i in range(max_retry):
        r = requests.post("http://127.0.0.1:50021/audio_query", 
                        params=query_payload, timeout=(10.0, 300.0))
        if r.status_code == 200:
            query_data = r.json()
            break
        time.sleep(1)
    else:
        raise ConnectionError("リトライ回数が上限に到達しました。 audio_query : ", "/", text[:30], r.text)
    return query_data

def audio_query_from_preset(text, preset_id, max_retry=3):
    """
    プリセットを使用して音声合成のための問い合わせを作成する関数。

    Args:
        text (str): 音声合成するテキスト。
        preset_id (int): 使用するプリセットのID。
        max_retry (int, optional): リトライの最大回数。デフォルトは3。

    Raises:
        ConnectionError: リトライ回数が上限に達した場合。

    Returns:
        dict: 問い合わせデータ。
    """
    query_payload = {"text": text, "preset_id": preset_id}
    for query_i in range(max_retry):
        headers = {'accept': 'application/json'}
        r = requests.post("http://127.0.0.1:50021/audio_query_from_preset", 
                        params=query_payload,headers=headers,timeout=(10.0, 300.0))
        if r.status_code == 200:
            query_data = r.json()
            break
        time.sleep(1)
    else:
        raise ConnectionError("リトライ回数が上限に到達しました。 audio_query : ", "/", text[:30], r.text)
    return query_data

def synthesis(speaker, query_data,max_retry):
    """
    与えられた問い合わせデータを使用して音声合成を行う関数。

    Args:
        speaker (int): 使用するスピーカーのID。
        query_data (dict): 音声合成のための問い合わせデータ。
        max_retry (int): リトライの最大回数。

    Raises:
        ConnectionError: リトライ回数が上限に到達した場合。

    Returns:
        bytes: 音声ファイルのデータ。
    """
    synth_payload = {"speaker": speaker,"enable_interrogative_upspeak": "true"}
    headers = {"accept": "audio/wav", "Content-Type": "application/json"}
    for synth_i in range(max_retry):
        r = requests.post("http://127.0.0.1:50021/synthesis", params=synth_payload, 
                          data=json.dumps(query_data),headers=headers,timeout=(10.0, 300.0))
        if r.status_code == 200:
            #音声ファイルを返す
            return r.content
        time.sleep(1)
    else:
        raise ConnectionError("synthesis エラー：リトライ回数が上限に到達しました。 synthesis : ", r)

def Get_presets():
    """
    すべての作成されたプリセットを取得する関数。

    Returns:
        dict: プリセットのデータ。
    
    Return example:
    [{'id': 0,
  'intonationScale': 1.3,
  'name': 'ナースロボ-ノーマル',
  'pitchScale': 0.0,
  'postPhonemeLength': 0.0,
  'prePhonemeLength': 0.0,
  'speaker_uuid': '882a636f-3bac-431a-966d-c5e6bba9f949',
  'speedScale': 1.15,
  'style_id': 47,
  'volumeScale': 1.0}]
    """
    r = requests.get("http://127.0.0.1:50021/presets")
    if r.status_code == 200:
        query_data = r.json()
        return query_data
    else:
        print(f"Error: Received status code {r.status_code}")
        return None

def Add_preset(id: int,name: str,speaker_uuid: str,style_id=0,speedScale=1.0,pitchScale=0,intonationScale=1.0,volumeScale=1.00,prePhonemeLength=0,postPhonemeLength=0,max_retry=3):
    """
    新しいプリセットを追加する関数。
    Args:
        id (int): プリセットのID。任意番号でよい。このIDをプリセットを呼び出す際用いる。
        name (str): プリセットの名前。任意の名前で良い。
        speaker_uuid (str): 使用するスピーカーのUUID。
        style_id (int, optional): スタイルID。デフォルトは0。
        speedScale (float, optional): 速度のスケール。デフォルトは1.0。
        pitchScale (float, optional): ピッチのスケール。デフォルトは0。
        intonationScale (float, optional): 抑揚のスケール。デフォルトは1.0。
        volumeScale (float, optional): 音量のスケール。デフォルトは1.0。
        prePhonemeLength (float, optional): 開始無音の長さ。デフォルトは0。
        postPhonemeLength (float, optional): 終了無音の長さ。デフォルトは0。
        max_retry (int, optional): リトライの最大回数。デフォルトは3。

    Raises:
        ConnectionError: リトライ回数が上限に到達した場合。

    Returns:
        dict: 問い合わせデータ。
    
    Example:
        Add_preset(id=0,name="ナースロボ-ノーマル",speaker_uuid="882a636f-3bac-431a-966d-c5e6bba9f949",style_id=47,speedScale=1.15,pitchScale=0.0,intonationScale=1.3,volumeScale=1.0,prePhonemeLength=0.0,postPhonemeLength=0.0)
    """
    preset_payload = {
    "id": id,
    "name": name,
    "speaker_uuid": speaker_uuid,   #speakersより取得すること
    "style_id": style_id,           #speakersより取得すること
    "speedScale": speedScale,       #話速
    "pitchScale": pitchScale,       #音高
    "intonationScale": intonationScale, #抑揚
    "volumeScale": volumeScale,         #音量
    "prePhonemeLength": prePhonemeLength,   #開始無音
    "postPhonemeLength": postPhonemeLength  #終了無音
    }
    for query_i in range(max_retry):
        r = requests.post("http://127.0.0.1:50021/add_preset", 
                        json=preset_payload, timeout=(10.0, 300.0))
        if r.status_code == 200:
            query_data = r.json()
            break
        time.sleep(1)
        print("Add_preset 再問い合わせ")
    else:
        raise ConnectionError("Add_preset エラー：リトライ回数が上限に到達しました。 synthesis : ", r.json())

def update_preset(id: int,name: str,speaker_uuid: str,style_id=0,speedScale=1.0,pitchScale=0,intonationScale=1.0,volumeScale=1.00,prePhonemeLength=0,postPhonemeLength=0,max_retry=3):
    """
    既存のプリセットを更新する関数。

    Args:
        同上のAdd_preset関数参照。

    Raises:
        ConnectionError: リトライ回数が上限に到達した場合。

    Returns:
        dict: 問い合わせデータ。
    """

    preset_payload = {
    "id": id,
    "name": name,
    "speaker_uuid": speaker_uuid,   #speakersより取得すること
    "style_id": style_id,           #speakersより取得すること
    "speedScale": speedScale,       #話速
    "pitchScale": pitchScale,       #音高
    "intonationScale": intonationScale, #抑揚
    "volumeScale": volumeScale,         #音量
    "prePhonemeLength": prePhonemeLength,   #開始無音
    "postPhonemeLength": postPhonemeLength  #終了無音
    }
    for query_i in range(max_retry):
        r = requests.post("http://127.0.0.1:50021/update_preset", 
                        json=preset_payload, timeout=(10.0, 300.0))
        if r.status_code == 200:
            query_data = r.json()
            break
        time.sleep(1)
    else:
        raise ConnectionError("音声エラー：リトライ回数が上限に到達しました。 synthesis : ", r.json())

def delete_preset(id:int):
    """
    プリセットを削除する関数。

    Args:
        id (int): 削除するプリセットのID。

    Returns:
        bool: プリセットが正常に削除された場合はTrue、それ以外の場合はFalse。
    """
    payload = {'id': id}
    r = requests.post("http://127.0.0.1:50021/delete_preset", params=payload)
    if r.status_code == 204:
        print(f"Preset successfully deleted at ID{id}.")
        return True
    else:
        print(f"delete_preset Error: Received status code {r.status_code} at delete id {id}")
        return False

def remove_all_presets():
    presetlist=Get_presets()
    #delete all preset
    if presetlist != []:
        for item in presetlist:
            delete_preset(id=item['id'])

def speakers():
    """
    利用可能なすべてのspeakerを取得する関数。stylesやspeaker_uuidを取得する関数。

    Returns:
        dict: スピーカーのデータ、またはエラーが発生した場合はNone。

    Return Example:
    [{'name': '四国めたん',
  'speaker_uuid': '7ffcb7ce-00ec-4bdc-82cd-45a8889e43ff',
  'styles': [{'id': 2, 'name': 'ノーマル'},
             {'id': 0, 'name': 'あまあま'},
             {'id': 6, 'name': 'ツンツン'},
             {'id': 4, 'name': 'セクシー'},
             {'id': 36, 'name': 'ささやき'},
             {'id': 37, 'name': 'ヒソヒソ'}],
  'supported_features': {'permitted_synthesis_morphing': 'SELF_ONLY'},
  'version': '0.14.3'},
 {'name': 'ずんだもん',
  'speaker_uuid': '388f246b-8c41-4ac1-8e2d-5d79f3ff56d9',
  'styles': [{'id': 3, 'name': 'ノーマル'},
             {'id': 1, 'name': 'あまあま'},
             {'id': 7, 'name': 'ツンツン'},
             {'id': 5, 'name': 'セクシー'},
             {'id': 22, 'name': 'ささやき'},
             {'id': 38, 'name': 'ヒソヒソ'}],
  'supported_features': {'permitted_synthesis_morphing': 'SELF_ONLY'},
  'version': '0.14.3'}]
    """
    r = requests.get("http://127.0.0.1:50021/speakers")
    if r.status_code == 200:
        query_data = r.json()
        pprint(query_data)
        return query_data
    else:
        print(f"Error: Received status code {r.status_code}")
        return None
    
#Process4
def audio_stream_start():
    """
    オーディオストリームを開始する関数。

    Returns:
        object: 開始されたストリーム、またはVB-Audio Virtualが見つからない場合はNone。
    """

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
    """
    オーディオストリームを停止する関数。

    Args:
        stream (object): 停止するストリーム。
    """
    p = pyaudio.PyAudio()
    stream.stop_stream()
    stream.close()

    p.terminate()

def text_to_wave(texts, preset_id=None, speaker=8, max_retry=20):
    """
    テキストを音声に変換する関数。

    Args:
        texts (str): 音声に変換するテキスト。
        preset_id (int, optional): 使用するプリセットのID。
        speaker (int, optional): 使用するスピーカーのID。デフォルトは8。
        max_retry (int, optional): リトライの最大回数。デフォルトは20。

    Returns:
        bytes: 音声ファイルのデータ。
    """
    #http://localhost:50021/speakers
    if texts == "":
        return
    
    # audio_query
    if preset_id is not None:
        query_data = audio_query_from_preset(text=texts,preset_id=preset_id)
    else:
        query_data = audio_query(texts,speaker,max_retry)
    # synthesis
    voice_data=synthesis(speaker,query_data,max_retry)
    return voice_data

if __name__ == "__main__":
    #Add_preset(id=0,name="ナースロボ-ノーマル",speaker_uuid="882a636f-3bac-431a-966d-c5e6bba9f949",style_id=47,speedScale=1.37,pitchScale=0,intonationScale=1,volumeScale=1,prePhonemeLength=0,postPhonemeLength=0)
    presetlist=Get_presets()
    pprint(presetlist)
    #delete all preset
    '''
    if presetlist != []:
        for item in presetlist:
            delete_preset(id=item['id'])
            '''

    #プリセット追加
    Add_preset(id=1,name="ナースロボ-ノーマル",speaker_uuid="882a636f-3bac-431a-966d-c5e6bba9f949",style_id=47,speedScale=1.15,pitchScale=0.0,intonationScale=1.3,volumeScale=1.0,prePhonemeLength=0.0,postPhonemeLength=0.0)
    #Add_preset(id=1,name="ナースロボ-恐怖",speaker_uuid="882a636f-3bac-431a-966d-c5e6bba9f949",style_id=49,speedScale=1,pitchScale=0,intonationScale=1,volumeScale=1,prePhonemeLength=0,postPhonemeLength=0)

    processtime=time.time()
    stream = audio_stream_start()
    data=text_to_wave("""みなさん、こんにちは！ みらいちゃんことみらいです！""",preset_id=0,speaker=47)
    stream.write(data)
    data=text_to_wave("""みなさん、こんにちは！ みらいちゃんことみらいです！""",preset_id=1,speaker=47)
    stream.write(data)
    print(f"処理時間:{time.time()-processtime}")
    audio_stream_stop(stream)