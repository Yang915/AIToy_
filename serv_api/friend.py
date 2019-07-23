from bson import ObjectId
from flask import Blueprint, jsonify, request
from settings import RESPONSE, MGDB

bp_friend = Blueprint('bp_friend', __name__)


# App获取好友列表接口:
@bp_friend.route('/friend_list', methods=['POST'])
def friend_list():
    data = request.form.to_dict()
    data['_id'] = ObjectId(data.get('_id'))
    friend_list = MGDB.Users.find_one(data).get('friend_list')

    RESPONSE['CODE'] = 0
    RESPONSE['MSG'] = "好友查询"
    RESPONSE['DATA'] = friend_list
    return jsonify(RESPONSE)


# 添加好友请求接口:
@bp_friend.route('/add_req', methods=['POST'])
def add_req():
    data_dict = request.form.to_dict()
    # print(data_dict)
    # {'add_user': '5d36c3d32b626a3f371145ff', 'toy_id': '5d367a398848ad54039f0764', 'add_type': 'app', 'req_info': 'ABC', 'remark': 'YANG-球球'}

    type = data_dict.get("add_type")
    id = ObjectId(data_dict.get("add_user"))

    if type == 'app':
        req_info = MGDB.Users.find_one({"_id": id})
        nickname = req_info.get("nickname")
    elif type == 'toy':
        req_info = MGDB.Toys.find_one({"_id": id})
        nickname = req_info.get("toy_name")
    to_toy_info = MGDB.Toys.find_one({'_id': ObjectId(data_dict.get('toy_id'))})
    to_user_info = MGDB.Users.find_one({'_id': ObjectId(to_toy_info.get("bind_user"))})
    # print("-----------------",data_dict.get("toy_id"))
    request_info = {
        "add_user": data_dict.get("add_user"),  # 发起好友申请方
        "toy_id": data_dict.get("toy_id"),  # 收到好友申请方
        "add_type": type,  # 发起方的用户类型 app/toy
        "req_info": data_dict.get("req_info"),  # 请求信息
        "remark": data_dict.get("remark"),  # 发起方对接收方的好友备注
        "avatar": req_info.get("avatar"),  # 发起方的头像
        "nickname": nickname,  # 发起方的名称
        "status": 0,  # 请求状态 1同意 0未处理 2拒绝
        "toy_name": to_user_info.get("username")  # 接收方的名称
    }
    MGDB.Request.insert_one(request_info)

    RESPONSE['CODE'] = 0
    RESPONSE['MSG'] = "添加好友请求成功"
    RESPONSE['DATA'] = {}
    return jsonify(RESPONSE)







# 获取好友请求接口:
@bp_friend.route('/req_list', methods=['POST'])
def req_list():
    user_id = request.form.to_dict().get("user_id")
    toy_list = list(MGDB.Toys.find({"bind_user":user_id}))




    toy_id_list = [str(toy.get("_id")) for toy in toy_list]
    req_list = list(MGDB.Request.find({"toy_id": {"$in": toy_id_list}}))  # 无视状态全部查出返回

    for req in req_list:
        req['_id'] = str(req.get('_id'))

    print(req_list)

    RESPONSE['CODE'] = 0
    RESPONSE['MSG'] = "查询好友请求"
    RESPONSE['DATA'] = req_list
    return jsonify(RESPONSE)


# App拒绝好友请求接口
@bp_friend.route('/ref_req', methods=['POST'])
def ref_req():
    request_id = request.form.to_dict()
    req_info = MGDB.Request.update({'_id': ObjectId(request_id)}, {"status": 2})
    RESPONSE['CODE'] = 0
    RESPONSE['MSG'] = "拒绝添加好友"
    RESPONSE['DATA'] = {}
    return jsonify(RESPONSE)


# App同意好友请求接口
@bp_friend.route('/acc_req', methods=['POST'])
def acc_req():
    request_data = request.form.to_dict()
    print(request_data)
    '''
    {"req_id":req_id, //好友请求信息Id
    "remark":"friend_remark", //为请求方添加备注名称}
    '''
    remark = request_data.get("remark")
    # 获取请求方app信息
    request_id = request_data.get("req_id")
    req_info = MGDB.Request.find_one({'_id': ObjectId(request_id)})
    # 获取要添加的toy信息
    toy_id = req_info.get("toy_id")
    print(toy_id)
    toy_info = MGDB.Toys.find_one({"_id": ObjectId(toy_id)})
    # 获取接收请求的app信息
    res_id = toy_info.get("bind_user")
    res_info = MGDB.Users.find_one({"_id": ObjectId(res_id)})

    # 创建请求方app与接收方app之间的聊天记录
    chat_id_App2 = str(MGDB.Chats.insert_one({"user_list": [request_id, res_id], "chat_list": []}).inserted_id)
    # 创建请求方app与添加的toy之间的聊天记录
    chat_id_AppToy = str(MGDB.Chats.insert_one({"user_list": [request_id, toy_id], "chat_list": []}).inserted_id)


    req_friend1={
        "friend_id": res_id,
        "friend_nick": res_info.get("username"),
        "friend_remark": res_info.get("nickname"),
        "friend_avatar": res_info.get("avatar"),
        "friend_chat": chat_id_App2,
        "friend_type": "app"
    }
    req_friend2={
        "friend_id": toy_id,
        "friend_nick": toy_info.get("toy_name"),
        "friend_remark": res_info.get("baby_name"),
        "friend_avatar": res_info.get("avatar"),
        "friend_chat": chat_id_AppToy,
        "friend_type": "toy"
    }
    print("--------------",request_id)
    MGDB.Users.update_one({'_id': ObjectId(request_id)},{"$push":{"friend_list":req_friend1}})
    MGDB.Users.update_one({'_id': ObjectId(request_id)}, {"$push": {"friend_list": req_friend2}})



    res_friend={
        "friend_id": request_id,
        "friend_nick": req_info.get("username"),
        "friend_remark": req_info.get("nickname"),
        "friend_avatar": req_info.get("avatar"),
        "friend_chat": chat_id_App2,
        "friend_type": "app"
    }
    MGDB.Users.update({"_id":ObjectId(res_id)},{"$push":{"friend_list":res_friend}})


    res_friend["friend_chat"]=chat_id_AppToy
    toy_friend = res_friend
    MGDB.Toys.update({"_id": ObjectId(toy_id)},{"$push":{"friend_list":toy_friend}})



    req_info = MGDB.Request.update({'_id': ObjectId(request_id)}, {"status": 1})
    RESPONSE['CODE'] = 0
    RESPONSE['MSG'] = "同意添加好友"
    RESPONSE['DATA'] = {}
    return jsonify(RESPONSE)
