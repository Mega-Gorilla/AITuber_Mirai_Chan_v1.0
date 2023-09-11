import asyncio
import websockets
import json
from PIL import Image
import base64
import io
import os
from pprint import pprint
import time
import csv

class VTS_main:
    def __init__(self):
        self.uri = "ws://localhost:8001"
        self.current_directory = os.path.dirname(os.path.abspath(__file__))
        self.pluginName="AITuber_API"
        self.pluginDeveloper="Gorilla"
        self.api_ver="1.0" #配布されているAPIのバージョン。基本変更禁止
        self.api_name="VTubeStudioPublicAPI" #同上
        self.key_check=False

        #設定ファイルの読み込み
        data = {}
        current_key = ""
        self.setting_file_path= os.path.join(self.current_directory,"VtuberStudio_plugin","setting.txt")
        with open(self.setting_file_path, 'r', encoding='utf-8') as file:
            for line in file:
                if line.strip().endswith(":"):
                    current_key = line.strip()[:-1]
                    data[current_key] = ""
                else:
                    data[current_key] += line.strip() + "\n"
        for key in data.keys():
            data[key] = data[key].strip()
        if data['token'] =="":
            self.VTS_token= None
        else:
            self.VTS_token = data['token']

    #アニメーション用 easeBothイメージング関数
    def easeInOutCubic(self,a, b, c, d):
        a /= d / 2
        if a < 1:
            result = c / 2 * a * a * a + b
        else:
            a -= 2
            result = c / 2 * (a * a * a + 2) + b
        return round(result, 1)

    def encode_image(self,file_path, target_size=(128, 128)):
        #アイコン用の画像ファイルを開き変換して返す。
        try:
            # 画像を開く
            image = Image.open(file_path)

            # 画像の形式を確認 (PNG または JPEG)
            if image.format not in ['PNG', 'JPEG']:
                raise ValueError("画像形式がPNGまたはJPGではありません。")

            # 画像をリサイズ
            resized_image = image.resize(target_size)

            # 画像をバイナリ形式で読み込む
            buffered = io.BytesIO()
            resized_image.save(buffered, format="PNG")
            buffered.seek(0)

            # 画像をBase64エンコード
            img_base64 = base64.b64encode(buffered.read()).decode("utf-8")

            return img_base64
        except Exception as e:
            print("アイコン取得エラー:", e)
            return None

    async def send_request(websocket, request):
        #websocketの送受信用
        try:
            await websocket.send(json.dumps(request))
            response_str = await websocket.recv()
            response = json.loads(response_str)
            formatted_response = json.dumps(response, indent=2)
            print(f"受信データ ({request['messageType']}):\n{formatted_response}")
        except Exception as e:
            print(f"リクエスト ({request['messageType']}) でエラーが発生しました: {e}")
        return response

    async def API_Server_Discovery(self,websocket,requestID="MyIDWithLessThan64Characters1"):
        #VTSのバージョン確認
        request = {
                "apiName": "VTubeStudioPublicAPI",
                "apiVersion": "1.0",
                "requestID": requestID,
                "messageType": "APIStateRequest"
            }
        
        await websocket.send(json.dumps(request))
        response = await websocket.recv()
        json_response = json.loads(response)
        
        if json_response["requestID"] == requestID:
            self.api_ver = json_response["apiVersion"]
            self.api_name = json_response["apiName"]
            return {"timestamp":json_response["timestamp"],
                    "messageType":json_response["messageType"],
                    "active":json_response["data"]["active"],
                    "vTubeStudioVersion":json_response["data"]["vTubeStudioVersion"],
                    "currentSessionAuthenticated":json_response["data"]["currentSessionAuthenticated"]}
        """
        Response Example:
        {
        "apiName": "VTubeStudioPublicAPI",
        "apiVersion": "1.0",
        "timestamp": 1625405710728,
        "messageType": "APIStateResponse",
        "requestID": "MyIDWithLessThan64Characters",
        "data": {
            "active": true,
            "vTubeStudioVersion": "1.9.0",
            "currentSessionAuthenticated": false
        }
        }
        """

    async def Requesting_list_of_hotkeys(self,websocket,requestID="MyIDWithLessThan64Characters1"):
        #13:現行モデルまたは他のVTSモデルで使用可能なホットキーのリストを要求する
        #本コードは複数モデル非対応
        request = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": self.api_ver,
            "requestID": requestID,
            "messageType": "HotkeysInCurrentModelRequest"
            }
        
        await websocket.send(json.dumps(request))
        response = await websocket.recv()
        json_response = json.loads(response) 
        available_hotkeys = json_response['data']['availableHotkeys']
        return available_hotkeys
        keys = {}

        for hotkey in available_hotkeys:
            name = hotkey['name']
            hotkey_id = hotkey['hotkeyID']
            keys[name] = hotkey_id

        print("現行モデルまたは他のVTSモデルで使用可能なホットキーのリスト/\nname : hotkeyID")
        pprint(keys)
        return keys

        """ Examples:
        "availableHotkeys": [
            {
                "name": "My Animation 1",
                "type": "TriggerAnimation",
                "description": "Triggers an animation",
                "file": "hiyori_m01.motion3.json",
                "hotkeyID": "14d17d37e79b4ed0a3c640acba1b95db",
                "keyCombination": [],
                "onScreenButtonID": 1
            },
            {
                "name": "My Animation 2",
                "type": "TriggerAnimation",
                "description": "Triggers an animation",
                "file": "hiyori_m02.motion3.json",
                "hotkeyID": "533fd7c12f934eaba6c5094427590efd",
                "keyCombination": [],
                "onScreenButtonID": 2
            },
            {
                "name": "My Animation 3",
                "type": "TriggerAnimation",
                "description": "Triggers an animation",
                "file": "hiyori_m03.motion3.json",
                "hotkeyID": "2729934fd6cd46af899281ae3e57092c",
                "keyCombination": [],
                "onScreenButtonID": 3
            },
            {
                "name": "My Animation 4",
                "type": "TriggerAnimation",
                "description": "Triggers an animation",
                "file": "hiyori_m04.motion3.json",
                "hotkeyID": "362ccfbb9139465fbf1fa1173563a3e6",
                "keyCombination": [],
                "onScreenButtonID": 4
            }
        """
    
    async def Requesting_execution_of_hotkeys(self,websocket,hotkeyID,itemInstanceID="",requestID="MyIDWithLessThan64Characters1"):
        #12:ホットキーの実行を要求する
        #本コードは複数モデル非対応
        request = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": self.api_ver,
            "requestID": requestID,
            "messageType": "HotkeyTriggerRequest",
            "data": {
                "hotkeyID": hotkeyID,
                "itemInstanceID": itemInstanceID
                }
            }
        
        await websocket.send(json.dumps(request))
        response = await websocket.recv()
        json_response = json.loads(response) 
        print(f"ホットキー{hotkeyID}の実行を要求")
        #print(json.dumps(json_response,indent=4))

        """ Examples:
        """

    async def Requesting_activation_or_deactivation_of_expressions(self,websocket,expressionFile,active=True,requestID="MyIDWithLessThan64Characters1"):
        #14:表情の活性化・非活性化の要求
        #本コードは複数モデル非対応 非推奨コード
        request = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": self.api_ver,
            "requestID": requestID,
            "messageType": "ExpressionActivationRequest",
            "data": {
                "expressionFile": expressionFile,
                "active": active
            }
            }
        
        await websocket.send(json.dumps(request))
        response = await websocket.recv()
        json_response = json.loads(response)
        if active: 
            print(f"表情 {expressionFile}を活性化")
        else:
            print(f"表情 {expressionFile}を非活性化")
        #print(json.dumps(json_response,indent=4))

        """ Examples:
        """

    async def Requesting_current_expression_state_list(self,websocket,expressionFile="",requestID="MyIDWithLessThan64Characters1"):
        #13:現在の表現状態を要求する
        request = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": self.api_ver,
            "requestID": requestID,
            "messageType": "ExpressionStateRequest",
            "data": {
                "details": False,
                "expressionFile": expressionFile
                }
            }
        
        await websocket.send(json.dumps(request))
        response = await websocket.recv()
        json_response = json.loads(response)
        expression_result = json_response['data']['expressions']
        #print("現在の表現状態/") 
        result = []
        for dictionary in expression_result:
            add_data = {}
            for name, value in dictionary.items():
                if name == "name" or name== "file" or name== "active":
                    add_data[name]=value
            result.append(add_data)
        #pprint(result)
        return expression_result
        print(json.dumps(json_response,indent=4))

        """Example:
        "expressions": [
            {
                "name": "EyesCry",
                "file": "EyesCry.exp3.json",
                "active": false,
                "deactivateWhenKeyIsLetGo": false,
                "autoDeactivateAfterSeconds": false,
                "secondsRemaining": 0.0,
                "secondsSinceLastActive": 0.0,
                "usedInHotkeys": [],
                "parameters": []
            },
            {
                "name": "EyesLove",
                "file": "EyesLove.exp3.json",
                "active": true,
                "deactivateWhenKeyIsLetGo": false,
                "autoDeactivateAfterSeconds": false,
                "secondsRemaining": 0.0,
                "secondsSinceLastActive": 0.0,
                "usedInHotkeys": [],
                "parameters": []
            },
            {
                "name": "SignAngry",
                "file": "SignAngry.exp3.json",
                "active": true,
                "deactivateWhenKeyIsLetGo": false,
                "autoDeactivateAfterSeconds": false,
                "secondsRemaining": 0.0,
                "secondsSinceLastActive": 0.0,
                "usedInHotkeys": [],
                "parameters": []
            },
            {
                "name": "SignShock",
                "file": "SignShock.exp3.json",
                "active": false,
                "deactivateWhenKeyIsLetGo": false,
                "autoDeactivateAfterSeconds": false,
                "secondsRemaining": 0.0,
                "secondsSinceLastActive": 0.0,
                "usedInHotkeys": [],
                "parameters": []
            }
        ]
        """
    async def Requesting_list_of_available_tracking_parameters(self,websocket,requestID="MyIDWithLessThan64Characters1"):
        #19:使用可能なトラッキングパラメーターのリストを要求する
        """返答例：
        [{'defaultValue': 0.0,
        'max': 1.0,
        'min': 0.0,
        'name': 'HandRightFinger_4_Ring',
        'value': 0.0},
        {'defaultValue': 0.0,
        'max': 1.0,
        'min': 0.0,
        'name': 'HandRightFinger_5_Pinky',
        'value': 0.0}]"""

        request = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": self.api_ver,
            "requestID": requestID,
            "messageType": "InputParameterListRequest"
            }
        
        await websocket.send(json.dumps(request))
        response = await websocket.recv()
        json_response = json.loads(response)
        expression_result = json_response['data']['defaultParameters']
        result = []
        for dictionary in expression_result:
            add_data = {}
            for name, value in dictionary.items():
                if name == "name" or name== "value" or name== "min" or name== "max" or name=="defaultValue":
                    add_data[name]=value
            result.append(add_data)
        return result
        pprint(result)
        print(json.dumps(json_response,indent=4))
    
    async def Get_the_value_for_one_specific_parameter_default_or_custom(self,websocket,ParamName,requestID="MyIDWithLessThan64Characters1"):
        #20:特定の1つのパラメータ（デフォルトまたはカスタム）の値を取得します。
        #配列にて、値を返す
        request = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": self.api_ver,
            "requestID": requestID,
            "messageType": "ParameterValueRequest",
            "data": {
                "name":ParamName
                }
        }
        await websocket.send(json.dumps(request))
        response = await websocket.recv()
        json_response = json.loads(response)
        result = json_response['data']
        return result
        pprint(result)
        print(json.dumps(json_response,indent=4))
    
    async def Get_the_value_for_all_Live2D_parameters_in_the_current_model(self,websocket,requestID="MyIDWithLessThan64Characters1"):
        #21:現在のモデルにおけるすべてのLive2Dパラメータの値を取得する
        #配列にて、値を返す
        """return Example
        [
            {'defaultValue': 0.0,
                 'max': 30.0,
                 'min': -30.0,
                 'name': 'ParamAngleX',
                 'value': -1.5333151817321777},
                {'defaultValue': 0.0,
                'max': 30.0,
                'min': -30.0,
                'name': 'ParamAngleY',
                'value': 19.998842239379883}
                ]"""
        #Live2D keyをVTSAPI関数に置き換える辞書関数{Live2Dkey:VTSkey}
        mapping = {'ParamAngleX':'FaceAngleX','ParamAngleY':'FaceAngleY','ParamAngleZ':'FaceAngleZ','ParamEyeBallX':'EyeLeftX','ParamEyeBallY':'EyeLeftY','ParamMouthForm':'MouthSmile','ParamMouthOpenY':'MouthOpen','ParamBrowLY':'BrowLeftY','ParamBrowRY':'BrowRightY','ParamEyeLOpen':'EyeOpenLeft','ParamEyeROpen':'EyeOpenRight'}
        eyeR_mapping={'EyeLeftX':'EyeRightX','EyeLeftY':'EyeRightY'}
        request = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": self.api_ver,
            "requestID": requestID,
            "messageType": "Live2DParameterListRequest"
        }

        await websocket.send(json.dumps(request))
        response = await websocket.recv()
        json_response = json.loads(response)
        result = json_response['data']['parameters']

        #VTS API向けに関数名を変換
        result_VTS=[]
        for item in result:
            new_item = item.copy()
            new_item['value'] = round(item['value'],1)

            if new_item['name'] in mapping:
                new_item['name']=mapping[new_item['name']]
            
            result_VTS.append(new_item)
            #右目関数はないので、左目データをコピーする。
            if new_item['name'] in eyeR_mapping:
                eye_R=new_item.copy()
                eye_R['name']=eyeR_mapping[new_item['name']]
                result_VTS.append(eye_R)
        
        return result_VTS
        pprint(result)
        print(json.dumps(json_response,indent=4))
    
    async def Feeding_in_data_for_default_or_custom_parameters(self,websocket,Parameters):
        #24:デフォルトまたはカスタムパラメーターのデータを投入する
        # ParameterValues Example
        """
        {
            "id": "FaceAngleX",
            "value": 12.31
        },
        {
            "id": "MyNewParamName",
            "weight": 0.8,
            "value": 0.7
        }
        """
        request = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": "SomeID",
            "messageType": "InjectParameterDataRequest",
            "data": {
                "faceFound": False,
                "mode": "set",
                "parameterValues": Parameters
            }
        }
        #print(json.dumps(request,indent=4))
        await websocket.send(json.dumps(request))
        response = await websocket.recv()
        json_response = json.loads(response)
        return json_response
        print(json.dumps(json_response,indent=4))

    async def Reset_all_expressions(self,websocket):
        #すべてのexpressionsをリセット
        expressions_list=await self.Requesting_current_expression_state_list(websocket=websocket,requestID="Reset_all_expressions")
        for dictionary in expressions_list:
            json_name = ""
            expression_reset =False
            for name, value in dictionary.items():
                if name == "active" and value == True:
                    expression_reset = True
                elif name == "file":
                    json_name = value
            #表情のリセット実行
            if expression_reset:
                await self.Requesting_activation_or_deactivation_of_expressions(websocket,json_name,active=False,requestID="Reset_expression")

    async def request_token(self,websocket,pluginName,pluginDeveloper,api_ver,request_ID="SomeID"):
        #１回のみ必要な認証処理 返り値は、tokenデータ
        #pngファイル読み込み
        file_path = os.path.join(self.current_directory,"VtuberStudio_plugin","icon.png")
        icon=self.encode_image(file_path)
        request = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": api_ver,
            "requestID": request_ID,
            "messageType": "AuthenticationTokenRequest",
            "data": {
                "pluginName": pluginName,
                "pluginDeveloper": pluginDeveloper,
                "pluginIcon": icon
                }
            }
        print(json.dumps(request))
        await websocket.send(json.dumps(request))
        response = await websocket.recv()
        json_response = json.loads(response)

        if json_response["messageType"] == "AuthenticationTokenResponse":
            return json_response["data"]["authenticationToken"]
        else:
            print(f"認証エラー: {json_response}")
            return None
    
    async def authenticate(self,websocket, plugin_name, plugin_developer, api_ver, authentication_token,request_ID="SomeID"):
        #トークン認証確認
        request = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": api_ver,
            "requestID": request_ID,
            "messageType": "AuthenticationRequest",
            "data": {
                "pluginName": plugin_name,
                "pluginDeveloper": plugin_developer,
                "authenticationToken": authentication_token
            }
        }

        await websocket.send(json.dumps(request))
        response = await websocket.recv()
        json_response = json.loads(response)

        if json_response["messageType"] == "AuthenticationResponse":
            return json_response["data"]["authenticated"]
        else:
            print(f"認証エラー: {json_response}")
            return None
    
    async def Authentication_Check(self):
        #認証処理
        if self.VTS_token == None:
            #初回認証の実施
            key = None
            async with websockets.connect(self.uri) as websocket:
                key = await self.request_token(websocket=websocket,pluginName=self.pluginName,pluginDeveloper=self.pluginDeveloper,api_ver=self.api_ver)
                if key:
                    #キーの保存
                    with open(self.setting_file_path,"r", encoding='utf-8')as file:
                        lines = file.readlines()
                    updated_lines = []
                    for line in lines:
                        if "token:" in line:
                            updated_lines.append(line + "\n" + key)
                            #updated_lines.append(key)
                        else:
                            updated_lines.append(line)
                    with open(self.setting_file_path,"w", encoding='utf-8')as file:
                        file.writelines(updated_lines)
                    self.VTS_token=key
                    self.key_check = True
                    print("AI_Tuber_APIの認証成功")
                else:
                    raise UserWarning("VTS認証が完了できませんでした。")
        elif self.key_check != True:
            #すでにkeyを取得している+初回の場合　キー有効確認
            async with websockets.connect(self.uri) as websocket:
                result = await self.authenticate(websocket=websocket,plugin_name=self.pluginName,plugin_developer=self.pluginDeveloper,api_ver=self.api_ver,authentication_token=self.VTS_token)
                if result:
                    print("VTSの認証が完了しました。")
                    self.key_check = True
                elif result == False:
                    raise UserWarning("VTS Tokenが正しくありません。再認証する場合は、Setting.txtのTokenの値を消去してください。")
                else:
                    raise UserWarning(f"VTS認証が完了できませんでした。/n{result}")

    async def hotkey_demo(self):
        hotkey_list={}
        try:
            async with websockets.connect(self.uri) as websocket:
                #認証確認
                await self.authenticate(websocket=websocket,plugin_name=self.pluginName,plugin_developer=self.pluginDeveloper,api_ver=self.api_ver,authentication_token=self.VTS_token)
                
                hotkey_list = await self.Requesting_list_of_hotkeys(websocket)
                #pprint(hotkey_list)
                for dictionary in hotkey_list:
                    for name, value in dictionary.items():
                        if name == "name":
                            print(f"{value}を実行/")
                        elif name == "file":
                            expressionFile = value
                            print(expressionFile)
                        elif name == "hotkeyID":
                            if "exp3" in expressionFile:
                                #表情の時、
                                await self.Reset_all_expressions(websocket)#表情のリセット
                                await self.Requesting_execution_of_hotkeys(websocket,hotkeyID=value)
                                await self.Requesting_current_expression_state_list(websocket=websocket) #表情状態の取得
                                time.sleep(3)
                            elif "motion3" in expressionFile:
                                await self.Requesting_execution_of_hotkeys(websocket,hotkeyID=value)
                                time.sleep(3)
        except Exception as e:
            print(f"WebSocket接続時にエラーが発生しました: {e}")
    
    async def get_value_demo(self):
        try:
            async with websockets.connect(self.uri) as websocket:
                #認証確認
                await self.authenticate(websocket=websocket,plugin_name=self.pluginName,plugin_developer=self.pluginDeveloper,api_ver=self.api_ver,authentication_token=self.VTS_token)
                result=await self.Get_the_value_for_all_Live2D_parameters_in_the_current_model(websocket)
                pprint(result)
                print("""
                
                """)
                all_params = await self.Requesting_list_of_available_tracking_parameters(websocket)
                pprint(all_params)
                    
        except Exception as e:
            print(f"WebSocket接続時にエラーが発生しました: {e}")
    
    async def simple_motion_demo(self):
        try:
            async with websockets.connect(self.uri) as websocket:
                #認証確認
                await self.authenticate(websocket=websocket,plugin_name=self.pluginName,plugin_developer=self.pluginDeveloper,api_ver=self.api_ver,authentication_token=self.VTS_token)
                await self.Feeding_in_data_for_default_or_custom_parameters(websocket,[{"id":'FaceAngleZ',"value":30.0}])
                    
        except Exception as e:
            print(f"WebSocket接続時にエラーが発生しました: {e}")
    
    async def emotion_demo(self):
        try:
            async with websockets.connect(self.uri) as websocket:
                #認証確認
                await self.authenticate(websocket=websocket,plugin_name=self.pluginName,plugin_developer=self.pluginDeveloper,api_ver=self.api_ver,authentication_token=self.VTS_token)
                #すべてのパラメータの取得
                all_params = await self.Requesting_list_of_available_tracking_parameters(websocket)
                print(all_params)
                duration = 1000 #アニメーション時間(ms)
                """
                for t in range(0, duration + 1,10):#10msごとに更新
                    min=int(all_params[5]['min'])
                    space=int(all_params[5]['max'])-int(all_params[5]['min'])
                    value = self.easeInOutCubic(t,min,space,duration)
                    print(value)
                    await self.Feeding_in_data_for_default_or_custom_parameters(websocket,[{"id":all_params[5]['name'],"value":str(value)}])
                    time.sleep(0.01)
                """
                    
                for item in all_params:
                    print(f"Name:{item['name']} //",end="")
                    print(f"Value:[{item['min']}/",end="")
                    await self.Feeding_in_data_for_default_or_custom_parameters(websocket,[{"id":item['name'],"value":item['max']}])
                    time.sleep(2)
                    print(f"{item['max']}/",end="")
                    await self.Feeding_in_data_for_default_or_custom_parameters(websocket,[{"id":item['name'],"value":item['min']}])
                    time.sleep(2)
                    print(f"{(item['max']-item['min'])/2}/",end="")
                    await self.Feeding_in_data_for_default_or_custom_parameters(websocket,[{"id":item['name'],"value":(item['max']-item['min'])/2}])
                    time.sleep(2)
                    print(f"{item['defaultValue']}]")
                    await self.Feeding_in_data_for_default_or_custom_parameters(websocket,[{"id":item['name'],"value":item['defaultValue']}])
                    input("Press Enter")
                #track_params = await self.Get_the_value_for_one_specific_parameter_default_or_custom(websocket,"FacePositionX")
                
        except Exception as e:
            print(f"WebSocket接続時にエラーが発生しました: {e}")

if __name__ == "__main__":         
    #認証確認
    asyncio.get_event_loop().run_until_complete(VTS_main().Authentication_Check())
    asyncio.run(VTS_main().get_value_demo())
    #asyncio.run(VTS_main().simple_motion_demo())