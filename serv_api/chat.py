from bson import ObjectId
from flask import Blueprint, request, jsonify

from settings import RESPONSE, MGDB

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

    return jsonify(RESPONSE)


# Toy接收未读消息:
@bp_chat.route("/recv_msg", methods=["post"])
def recv_msg():
    data = request.form.to_dict()
    # ImmutableMultiDict([('from_user', '5d36e5852a3b1c2b3f9e7882'), ('to_user', '5d36e5ae2a3b1c2b3f9e7884')])
    from_user = data.get("from_user")
    to_user = data.get("from_user")
    chat_list=MGDB.Chats.find_one({"user_list":{"$all":[from_user,to_user]}}).get("chat_list")


    return jsonify(chat_list)

