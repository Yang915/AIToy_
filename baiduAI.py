import os

from aip import AipSpeech

from aip import AipNlp
from TuringRobotAPI import turingRobotAnswer

APP_ID = '16815394'
API_KEY = 'jM4b8GIG9gzrzySTRq3szK2E'
SECRET_KEY = 'iE626cEpjT1iAVwh24XV5h1QFuR8FPD2'

client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)
#file_
def tts(TEXT,file_path):
    VOICE = {'vol': 5, 'spd': 4, 'pit': 5, 'per': 4}
    result  = client.synthesis(TEXT, 'zh', 1,VOICE )

    # 识别正确返回语音二进制 错误则返回dict 参照下面错误码
    if not isinstance(result, dict):
        with open(file_path, 'wb') as f:
            f.write(result)


# tts('消息已发送成功！','rings\SendOK.mp3')


# 读取文件
def get_file_content(filepath):
    # 文件格式转换成pcm(前提是需要安装ffmpeg软件并配置环境变量)
    filename = os.path.basename(filepath)
    pcm_filename = filename.rsplit('.',1)[0] + '.pcm'
    pcm_filepath = os.path.join(os.path.dirname(filepath),pcm_filename)
    cmd_str = f'ffmpeg -y  -i {filepath}  -acodec pcm_s16le -f s16le -ac 1 -ar 16000 {pcm_filepath}'  # ffmpeg软件安装及环境变量配置
    os.system(cmd_str)  # 调用os.system()在CMD执行命令
    filepath = pcm_filepath

    with open(filepath, 'rb') as fp:
        return fp.read()


# 识别本地文件
def asr(filePath):
    pcm_file = get_file_content(filePath)
    result = client.asr(pcm_file, 'pcm', 16000, {
        'dev_pid': 1536,
    })
    try:
        text = result.get('result')[0]
    except:
        text = '!@#$%^&^%$#$%^&*'
    print("+++++++++++++++++++",filePath)
    os.remove(filePath.rsplit('.',1)[0]+".pcm")
    return text

NLP_client = AipNlp(APP_ID, API_KEY, SECRET_KEY)

def nlp(text_question,text):
    score = NLP_client.simnet(text_question, text).get('score')
    print(score)
    if score:
        res=score>0.60
    else:
        res=0
    return res

