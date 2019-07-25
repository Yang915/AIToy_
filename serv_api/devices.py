import os

from bson import ObjectId
from flask import Blueprint, request, jsonify, send_file

from settings import MGDB, RESPONSE

bp_devices = Blueprint('bp_devices', __name__)


# App扫描二维码验证接口
@bp_devices.route('/scan_qr', methods=['POST'])
def scan_qr():
    qr_dict = request.form.to_dict()
    print(qr_dict)
    if qr_dict:
        res_Devices = MGDB.Devices.find_one(qr_dict)
        res_Toys = MGDB.Toys.find_one(qr_dict)

        if not res_Devices:
            RESPONSE['CODE'] = 3
            RESPONSE['MSG'] = "无效二维码！！！"
        elif not res_Toys:
            RESPONSE['CODE'] = 0
            RESPONSE['MSG'] = "二维码扫描成功"
            RESPONSE['DATA'] = qr_dict
        else:
            toy_id = str(res_Toys.get('_id'))
            res_Users = MGDB['Users'].find_one({'bind_toys': toy_id})
            if res_Users:
                RESPONSE['CODE'] = 2
                RESPONSE['MSG'] = "设备已经进行绑定！"

                RESPONSE['DATA'] = {
                    'toy_id': str(res_Toys.get('_id')),
                }

    else:
        RESPONSE['CODE'] = 1
        RESPONSE['MSG'] = "请扫描玩具二维码"

    return jsonify(RESPONSE)


# App绑定设备接口
@bp_devices.route('/bind_toy', methods=['POST'])
def bind_toy():
    res_chat = MGDB.Chats.insert_one({
        "user_list": [],
        "chat_list": []
    })

    chat_id = str(res_chat.inserted_id)

    toy_dict = request.form.to_dict()
    # print(toy_dict)
    # {'toy_name': '娃哈哈', 'baby_name': '0', 'remark': '123', 'device_key': '0f83854da59d42d2f0a9e1e5223f0c65', 'user_id': '5d328bc0472a3a09ec32ec58'}
    user_id = ObjectId(toy_dict.get('user_id'))
    user_info = MGDB.Users.find_one({'_id': user_id})
    # 创建toy
    toy_info = {
        "toy_name": toy_dict.get("toy_name"),
        "baby_name": toy_dict.get("baby_name"),
        "device_key": toy_dict.get("device_key"),
        "avatar": "toy.jpg",
        "bind_user": toy_dict.get("user_id"),
        "friend_list": []
    }
    toy_friend = {
        "friend_id": toy_dict.get('user_id'),  # 好友id
        "friend_nick": user_info.get("nickname"),  # 好友的昵称
        "friend_remark": user_info.get("username"),  # 好友备注
        "friend_avatar": user_info.get("avatar"),  # 好友头像
        "friend_chat": chat_id,  # 私聊窗口ID 聊天数据表对应值
        "friend_type": "app",  # 好友类型
    }
    toy_info.get("friend_list").append(toy_friend)
    res_toy = MGDB['Toys'].insert_one(toy_info)  # 返回的是一个InsertedId,可以直接拿到_id
    toy_id = str(res_toy.inserted_id)
    print('---------------------',toy_id, toy_dict.get('user_id'))

    MGDB.Chats.update({"_id":ObjectId(chat_id)},{"$set":{"user_list": [toy_id,toy_dict.get('user_id')]}})

    # 更新user当前的bind_toys和friend_list
    user_friend = {
        "friend_id": toy_id,  # 好友id
        "friend_nick": toy_dict.get("baby_name"),  # 好友的昵称
        "friend_remark": toy_dict.get("toy_name"),  # 好友备注
        "friend_avatar": "toy.jpg",  # 好友头像
        "friend_chat": chat_id,  # 私聊窗口ID 聊天数据表对应值
        "friend_type": "toy",  # 好友类型
    }

    MGDB['Users'].update_one({'_id': user_id}, {'$push': {'bind_toys': toy_id, "friend_list": user_friend}})

    RESPONSE['CODE'] = 0
    RESPONSE['MSG'] = "绑定完成"
    RESPONSE['DATA'] = {}
    return jsonify(RESPONSE)


# App获取绑定Toy信息接口
@bp_devices.route('/toy_list', methods=['POST'])
def toy_list():
    user_id = request.form.get('_id')
    bind_toys = list(MGDB.Toys.find({"bind_user": user_id}))
    for toy in bind_toys:
        toy["_id"] = str(toy.get("_id"))
    RESPONSE['MSG'] = "获取Toy列表"
    RESPONSE['DATA'] = bind_toys
    return jsonify(RESPONSE)


# 设备启动登录接口 (硬件接口)
@bp_devices.route('/open_toy', methods=['POST'])
def open_toy():#考虑IO操作，注意查表顺序
    device_key = request.form.to_dict()
    res_Toys = MGDB.Toys.find_one(device_key)
    if res_Toys:
        res_data = {
            "code": 0,
            "music": "Success.mp3",
            "toy_id": str(res_Toys.get("_id")),
            "name": res_Toys.get("toy_name")
        }
    else:
        res_Device = MGDB.Devices.find_one(device_key)
        if res_Device:
            res_data = {"code": 2, "music": "Nolic.mp3"}
        else:
            res_data = {"code": 1, "music": "Nobind.mp3"}

    return jsonify(res_data)

#开机提示音：直接在app的路由进行接收返回
# @bp_devices.route('/getMusic/<music>')
# def get_music(music):
#     music_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'rings', music)
#     print(music_path)
#     return send_file(music_path)
