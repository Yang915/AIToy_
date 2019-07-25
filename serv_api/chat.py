import os
import time
from uuid import uuid4

from bson import ObjectId
from flask import Blueprint, request, jsonify

from baiduAI import tts
from chat_count import get_redis
from settings import RESPONSE, MGDB, CHAT_PATH

bp_chat = Blueprint("bp_chat", __name__)


# App获取历史消息
@bp_chat.route("/chat_list", methods=["post"])
def chat_list():
    data = request.form.to_dict()
    print(data)
    # {'chat_id': '5d3569e0b3023de977701c1d', 'from_user': '5d3569e0b3023de977701c1c','to_user': '5d3568cb479e8a5ac7a43e11'}

    window_chat = MGDB.Chats.find_one({"_id": ObjectId(data.get("chat_id"))})

    chat_list = window_chat.get("chat_list")
    chats = []
    for chat in chat_list:
        chat.pop("to_user")
        chats.append(chat)

    RESPONSE['CODE'] = 0
    RESPONSE['MSG'] = "查询聊天记录"
    RESPONSE['DATA'] = chats

    get_redis(data.get("to_user"),data.get("from_user"))

    return jsonify(RESPONSE)


# Toy接收未读消息:
@bp_chat.route("/recv_msg", methods=["post"])
def recv_msg():
    data = request.form.to_dict()
    # ImmutableMultiDict([('from_user', '5d36e5852a3b1c2b3f9e7882'), ('to_user', '5d36e5ae2a3b1c2b3f9e7884')])
    from_user = data.get("from_user")
    to_user = data.get("to_user")


    count = get_redis(to_user, from_user)

    # 语音合成提示信息
    to_toy_info = MGDB.Toys.find_one({"_id": ObjectId(to_user)})
    to_toy_friends = to_toy_info.get("friend_list")
    for friend in to_toy_friends:
        if friend.get("friend_id") == from_user:
            text = f"以下播放来自{friend.get('friend_remark')}的{count}条语音消息!" if count else f"当前没有收到来自{friend.get('friend_remark')}的任何语音消息!"
            # if count:
            #     text = f"以下播放来自{friend.get('friend_remark')}的{count}条语音消息!"
            # else:
            #     text=f"当前没有收到来自{friend.get('friend_remark')}的任何语音消息!"
            break
    ring_name = f"cout_{uuid4()}.wav"
    ring_path = os.path.join(CHAT_PATH, ring_name)
    tts(text, ring_path)
    ring_chat={
        "from_user": from_user,
        "chat": ring_name,
        "create_time": time.time()
    }
    chat_list = MGDB.Chats.find_one({"user_list": {"$all": [from_user, to_user]}}).get("chat_list")[-count:]#type:list
    chat_list.reverse()
    chat_list.append(ring_chat)


    return jsonify(chat_list)


