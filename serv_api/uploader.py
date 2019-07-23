import hashlib
import os
import time
from uuid import uuid4

from bson import ObjectId
from flask import Blueprint, request, jsonify

from TTS import tts
from settings import RESPONSE, MGDB, CHAT_PATH

bp_uploader = Blueprint("bp_uploader", __name__)

# App录制语音上传接口
@bp_uploader.route("/app_uploader", methods=["POST"])
def app_uploader():
    data = request.form.to_dict()
    file = request.files.get("reco_file")
    from_user = data.get("user_id")
    to_user = data.get("to_user")
    # filename=hashlib.md5(f"{uuid4()}{time.time()}{uuid4()}".encode('utf-8')).hexdigest()
    # cmd_str = f'ffmpeg -y  -i {filepath}  -acodec pcm_s16le -f s16le -ac 1 -ar 16000 {pcm_filepath}'  # ffmpeg软件安装及环境变量配置
    # os.system(cmd_str)  # 调用os.system()在CMD执行命令
    filename = file.filename
    file_path = os.path.join(CHAT_PATH, filename)
    file.save(file_path)
    # print(data)
    # print(file)
    # '''
    # {'user_id': '5d3568cb479e8a5ac7a43e11', 'to_user': '5d3569e0b3023de977701c1c'}
    # ImmutableMultiDict([('reco_file', <FileStorage: '1563854186214.amr' ('audio/amr')>)])
    # '''
    filename=filename+".mp3"
    os.system(f"ffmpeg -i {file_path} {os.path.join(CHAT_PATH,filename)}")
    os.remove(file_path)

    to_toy_info=MGDB.Toys.find_one({"_id":ObjectId(to_user)})
    to_toy_friends=to_toy_info.get("friend_list" )
    for friend in to_toy_friends:
        if friend.get("friend_id")==from_user:
            text = f"收到一条来自{friend.get('friend_remark')}的语音消息！"
            break
    ring_name =filename.rsplit(".")[0]+".wav"
    ring_path=os.path.join(CHAT_PATH,ring_name)
    tts(text,ring_path)


    chat = {
        "from_user": from_user,  # 信息发送方ID
        "to_user": to_user,  # 信息接收方ID
        "chat": filename,  # 语音消息文件名
        "createTime": time.time()  # 聊天创建时间
    }
    MGDB.Chats.update_one({"user_list": {"$all": [from_user, to_user]}}, {"$push": {"chat_list": chat}})



    RESPONSE['CODE'] = 0
    RESPONSE['MSG'] = "上传成功"
    RESPONSE['DATA'] = {
        "filename": ring_name,
        "friend_type": "app"
    }

    return jsonify(RESPONSE)

# Toy录制语音上传接口
@bp_uploader.route("/toy_uploader", methods=["POST"])
def toy_uploader():
    data = request.form.to_dict()
    # {'user_id': '5d36e5ae2a3b1c2b3f9e7884', 'friend_type': 'undefined', 'to_user': '5d36e5852a3b1c2b3f9e7882'}
    file = request.files.get("reco")
    filename=f"{uuid4()}.wav"
    print("--------",filename)
    file_path = os.path.join(CHAT_PATH, filename)
    file.save(file_path)

    from_user = data.get("user_id")
    to_user = data.get("to_user")
    type=data.get("friend_type")

    chat = {
        "from_user": from_user,  # 信息发送方ID
        "to_user": to_user,  # 信息接收方ID
        "chat": filename,  # 语音消息文件名
        "createTime": time.time()  # 聊天创建时间
    }
    MGDB.Chats.update_one({"user_list": {"$all": [from_user, to_user]}}, {"$push": {"chat_list": chat}})

    RESPONSE['CODE'] = 0
    RESPONSE['MSG'] = "上传成功"
    RESPONSE['DATA'] = {
        "filename": filename,
        "friend_type": "toy"
    }

    return jsonify(RESPONSE)

# Toy录制语音上传AI接口
@bp_uploader.route("/ai_uploader", methods=["POST"])
def ai_uploader():
    data = request.form.to_dict()
    file = request.files.get("blob")
    filename = f"{uuid4()}.wav"
    file_path = os.path.join(CHAT_PATH, filename)
    file.save(file_path)
    """
    通过ASR语音识别技术转换后才能文字，在进行NLP自然语言处理，获取反馈结果，通过TTS合成语音返回
    """
    # print(data)
    # print(file)
    # print(file.filename)
    """
    {'toy_id': '5d3569e0b3023de977701c1c'}
    <FileStorage: 'blob' ('audio_pcm/wav')>
    """
