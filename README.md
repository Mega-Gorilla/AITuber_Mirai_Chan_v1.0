# AITuber MIRAI Chan 1.0
<div align="center">

![Alt text](https://github.com/Mega-Gorilla/AI_Tuber_Mirai_old/blob/main/image/mirai_image1.png?raw=true)

</div>
AITuber みらいちゃん( https://www.youtube.com/live/ho7qBvd-SF4?si=3NkqxXElxrf1UrSg ) のソースコードです。<br>
みらいちゃんは、GPT4 x GPT3.5 x Azure Speech x OBS Plugin x VoiceVox x VTube Studioで動作しており、リンク配信のような応答、アニメーション、声質の変更をすることが出来ます。
<br><br>
<注意:このレポジトリは今後更新される予定はありません。issuesは公開されていますが、今後メンテナンスされる予定はありません。このレポジトリは、旧みらいちゃんの墓標として公開されています。>
<BR><BR>

# 利用規約 Terms of Use
本コードは「Apache License 2.0」に準拠していますが、以下の点を追記します。
- 本コードを元に、ソフトウェアおよび配信をする場合、概要欄、説明欄等に「AITuber みらい Beta」を用いてることを示してください。
- 商用利用可能ですが、法人様、企業様での商用利用は「kotatsugiken@gmail.com」にご一報ください。
- 過激な暴力的な表現を含むコンテンツ、情報商材への使用および掲載、宗教的なコンテンツ、その他、社会通念に反するコンテンツに対する使用は固く禁じます。

This code is compliant with the "Apache License 2.0", but the following points should be added.
- If you distribute software based on this code, please indicate that you are using "AITuber Mirai Beta" in the summary, description, etc.
- Commercial use is allowed, but please inform "kotatsugiken@gmail.com" for commercial use by corporations and companies.
- Use of the content for any content that contains extreme violent expressions, use or publication in information products, religious content, or any other content that is contrary to socially accepted norms is strictly prohibited.

# Installation

## Python install
```
git clone https://github.com/Mega-Gorilla/AI_Tuber_Mirai_old.git
cd AITuber_Mirai_Chan_v1.0
pip install -r requirements.txt
```

## Setting Environment Variables
In the Windows Environment Variables editor, add the following environment variables to the User Environment Variables section. After inputting a custom key for each, reboot the system. (For information on how to obtain each key, refer to the respective service pages.)
- AZURE_API_KEY
- OPENAI_API_KEY
- DEEPL_KEY

Azure Speech to Text → https://azure.microsoft.com/en-us/services/cognitive-services/speech-to-text/
<BR>OpenAI → https://openai.com/
<BR>DeepL → https://www.deepl.com/

## OBS Setup

### OBS Settings
1. Launch OBS.
1. From the "Tools" menu, select "WebSocket Server Settings."
1. Check the box for "Enable WebSocket Server."
1. Under Server Settings, input a custom port number in the "Server Port" field (e.g., 4455).
1. Check the box for "Enable Authentication."
1. Set server password.
1. Open main.py and replace "OBS_key = "R59emfpeavscjYy7" with your configured password.

### OBS Subtitles Setting

Add two "Text" sources to the OBS source (the source name can be arbitrary). Name them "subs" and "subs1" respectively. You can enter any text you like into the "text" sources.

## VoiceVox Setup
1. Download and install VOICEVOX from https://voicevox.hiroshiba.jp/.
1. Launch VICEVOX.

##  VB-AUDIO Installation
VB-AUDIO is used to make the AITUBER's lips move. This is achieved by playing audio data through a virtual microphone.

To install VB-AUDIO, visit the URL below.
VB-AUDIO ( https://vb-audio.com/Cable/ )

## VTS (VTube Studio) Setup
<div align="center">
<img src="https://github.com/Mega-Gorilla/AI_Tuber_Mirai_old/blob/main/image/VTS_API_setting.png?raw=true" width="500"><BR>
</div><BR>

1. Install VTS (https://store.steampowered.com/app/1325860/VTube_Studio/)
1. Launch VTS
1. Double-click on the VTS screen, then click the gear icon and check the box for "StartAPI"
1. In "Lip Sync Settings," check the box for "Use Microphone." and "Preview microphone"
1. Under "Select Microphone," choose "VB-Audio."
1. Upon first execution, the following screen will appear in VTS. Press "Allow" to add the Token.

### [If the message "VTS Tokenが正しくありません。再認証する場合は、Setting.txtのTokenの値を消去してください。" appears]
> Open Module/VtuberStudio_plugin and set it to:  
> 
> `token:`  
>
> Save it in this state.

## Launch
Run the following code to launch AITuber. 

Upon first execution, a screen will appear in VTS; please grant permission.
<div align="center">
<img src="https://github.com/Mega-Gorilla/AI_Tuber_Mirai_old/blob/main/image/VTS_token.png?raw=true" width="500"><BR>
</div><BR>
Congratulations! Mirai is now near you!<BR><BR>

After speaking into the microphone, press the spacebar and "Mirai-chan" will start talking.
