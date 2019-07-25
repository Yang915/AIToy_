import hashlib
import os
import time
from uuid import uuid4

from bson import ObjectId
from flask import Blueprint, request, jsonify

from TuringRobotAPI import turingRobotAnswer
from baiduAI import tts, asr, nlp
from chat_count import set_redis
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
    #amr语音格式转换mp3
    filename = filename + ".mp3"
    os.system(f"ffmpeg -i {file_path} {os.path.join(CHAT_PATH,filename)}")
    os.remove(file_path)

    # 语音合成提示信息
    to_toy_info = MGDB.Toys.find_one({"_id": ObjectId(to_user)})
    to_toy_friends = to_toy_info.get("friend_list")
    for friend in to_toy_friends:
        if friend.get("friend_id") == from_user:
            text = f"收到一条来自{friend.get('friend_remark')}的语音消息！"
            break
    ring_name = filename.rsplit(".")[0] + ".wav"
    ring_path = os.path.join(CHAT_PATH, ring_name)
    tts(text, ring_path)

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
    set_redis(to_user,from_user)

    return jsonify(RESPONSE)


# Toy录制语音上传接口
@bp_uploader.route("/toy_uploader", methods=["POST"])
def toy_uploader():
    data = request.form.to_dict()
    print(data)
    # {'user_id': '5d36e5ae2a3b1c2b3f9e7884', 'friend_type': 'undefined', 'to_user': '5d36e5852a3b1c2b3f9e7882'}
    file = request.files.get("reco")
    filename = f"{uuid4()}.wav"
    print("--------", filename)
    file_path = os.path.join(CHAT_PATH, filename)


    from_user = data.get("user_id")
    to_user = data.get("to_user")
    type = data.get("friend_type")
    if to_user:
        file.save(file_path)
        chat = {
            "from_user": from_user,  # 信息发送方ID
            "to_user": to_user,  # 信息接收方ID
            "chat": filename,  # 语音消息文件名
            "createTime": time.time()   # 聊天创建时间
        }
        MGDB.Chats.update_one({"user_list": {"$all": [from_user, to_user]}}, {"$push": {"chat_list": chat}})

        set_redis(to_user,from_user)
        #通过to_user获取到发送目标的type
        friend_list=MGDB.Toys.find_one({"_id":ObjectId(from_user)}).get("friend_list")
        for friend in friend_list:
            if friend.get("friend_id")==to_user:
                type=friend.get("friend_type")
                break
         #如果是发给toy的得先发送一条语音提示
        if type=='toy':
            # 语音合成提示信息
            to_toy_info = MGDB.Toys.find_one({"_id": ObjectId(to_user)})
            to_toy_friends = to_toy_info.get("friend_list")
            for friend in to_toy_friends:
                if friend.get("friend_id") == from_user:
                    text = f"收到一条来自{friend.get('friend_remark')}的语音消息！"
                    break
            ring_name ="toy2toy"+filename.rsplit(".")[0] + ".wav"
            ring_path = os.path.join(CHAT_PATH, ring_name)
            tts(text, ring_path)
            filename=ring_name



        RESPONSE['CODE'] = 0
        RESPONSE['MSG'] = "上传成功"
        RESPONSE['DATA'] = {
            "code":0,
            "filename": filename,
            "friend_type": "toy"
        }
    # else:
    #     RESPONSE['CODE']=1
    #     RESPONSE['MSG']="请先告诉我你想和谁聊天！"
    #     RESPONSE['DATA']={
    #         "code": 1,
    #         "filename": filename,
    #         "friend_type": "toy"
    #     }
    return jsonify(RESPONSE)


# Toy录制语音上传AI接口
@bp_uploader.route("/ai_uploader", methods=["POST"])
def ai_uploader():
    data = request.form.to_dict()
    file = request.files.get("reco")

    # print(data)
    # print(file)
    """
    {'toy_id': '5d3569e0b3023de977701c1c'}
    <FileStorage: 'blob' ('audio_pcm/wav')>
    """

    filename = f"{uuid4()}.wav"
    file_path = os.path.join(CHAT_PATH, filename)
    file.save(file_path)
    question_text = asr(file_path)
    print(question_text)
    if "播放" in question_text or "音乐" in question_text or "想听" in question_text or "放一首" in question_text:
        for song in MGDB.Content.find():
            text = song.get('title')
            print("---------------",song.get('title'))
            if nlp(question_text, text):
                response_data = {
                    "from_user": "ai",
                    "music": song.get("music")
                }
                return jsonify(response_data)

    if "聊天" in question_text or "发消息" in question_text or "说话" in question_text:
        toy_friend_list = MGDB.Toys.find_one({"_id": ObjectId(data.get('toy_id'))}).get("friend_list")
        for friend in toy_friend_list:
            if friend.get("friend_nick") in question_text or friend.get("friend_remark") in question_text:
                answer_name = f"answer_{filename}"
                answer_path = os.path.join(CHAT_PATH, answer_name)
                text_answer=f"现在可以开始和{friend.get('friend_remark')}聊天了！"
                tts(text_answer, answer_path)
                response_data = {
                    "from_user": friend.get("friend_id"),
                    "chat": answer_name,
                    "friend_type":friend.get("friend_type")
                }
                return jsonify(response_data)
    #最后匹配不到交给图灵机器人
    text_answer = turingRobotAnswer(question_text)
    answer_name = f"answer_{filename}"
    answer_path = os.path.join(CHAT_PATH, answer_name)
    tts(text_answer, answer_path)
    response_data = {
        "from_user": "ai",
        "chat": answer_name
    }
    return jsonify(response_data)



