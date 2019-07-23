import uuid

from aip import AipSpeech

APP_ID = '16815394'
API_KEY = 'jM4b8GIG9gzrzySTRq3szK2E'
SECRET_KEY = 'iE626cEpjT1iAVwh24XV5h1QFuR8FPD2'

client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)

def tts(TEXT,ring_path):
    VOICE = {'vol': 5, 'spd': 4, 'pit': 5, 'per': 4}
    result  = client.synthesis(TEXT, 'zh', 1,VOICE )

    # 识别正确返回语音二进制 错误则返回dict 参照下面错误码
    if not isinstance(result, dict):
        with open(ring_path, 'wb') as f:
            f.write(result)

