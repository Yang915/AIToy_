from bson import ObjectId
from flask import Blueprint, request, jsonify

from settings import MGDB, RESPONSE

bp_user = Blueprint('bp_user', __name__)


# 用户注册
@bp_user.route('/reg', methods=['POST'])
def reg():
    reg_dict = request.form
    # print(reg_dict)
    res = MGDB['Users'].find_one({'username': reg_dict.get("username")})
    if res:
        RESPONSE['CODE'] = 1
        RESPONSE['MSG'] = '当前用户已存在！'
    else:
        user_info = {
            "username": reg_dict.get("username"),
            "password": reg_dict.get("password"),
            "nickname": reg_dict.get("nickname"),
            "gender": reg_dict.get("gender"),
            "avatar": "baba.jpg" if reg_dict.get("gender") == "2" else "mama.jpg",
            "bind_toys": [],
            "friend_list": []
        }
        try:
            MGDB['Users'].insert_one(user_info)
        except:
            RESPONSE['CODE'] = 1
            RESPONSE['MSG'] = '注册失败！'
        else:
            RESPONSE['MSG'] = '注册成功！'
    return jsonify(RESPONSE)


# 用户登录
@bp_user.route('/login', methods=['POST'])
def login():
    login_dict = request.form.to_dict()
    user_ = MGDB['Users'].find_one(login_dict)
    if user_:
        RESPONSE['MSG'] = '登录成功！'
        user_['_id'] = str(user_.get('_id'))
        user_.pop('password')
        RESPONSE['DATA'] = user_
    else:
        RESPONSE['CODE'] = 1
        RESPONSE['MSG'] = '账号或密码有误！'
    return jsonify(RESPONSE)


# 自动登录
@bp_user.route('/auto_login', methods=['POST'])
def auto_login():
    data_dict = request.form.to_dict()
    data_dict['_id'] = ObjectId(data_dict.get('_id'))
    user_ = MGDB['Users'].find_one(data_dict)
    if user_:
        RESPONSE['MSG'] = '自动登录成功！'
        user_['_id'] = str(user_.get('_id'))
        user_.pop('password')
        RESPONSE['DATA'] = user_
    return jsonify(RESPONSE)
