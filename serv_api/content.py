import os

from bson import ObjectId
from flask import Blueprint, request, jsonify, send_file

from settings import MGDB, MUSIC_PATH, COVER_PATH, RESPONSE

bp_content = Blueprint('bp_content', __name__)


# 获取资源内容
@bp_content.route('/content_list', methods=['POST'])
def content_list():
    source_data = MGDB['Content'].find({})
    data_list = list(source_data)
    for index, data in enumerate(data_list):
        data_list[index]['_id'] = str(data.get('_id'))
    return jsonify(data_list)


# 获取图片资源
@bp_content.route('/get_cover/<covername>', methods=['GET'])
def get_cover(covername):
    cover_path = os.path.join(COVER_PATH, covername)
    return send_file(cover_path)


# 获取音乐资源
@bp_content.route('/get_music/<musicname>', methods=['GET'])
def get_music(musicname):
    music_path = os.path.join(MUSIC_PATH, musicname)
    return send_file(music_path)


#App扫描二维码验证接口
@bp_content.route('/scan_qr', methods=['POST'])
def scan_qr():
    qr_dict = request.form.to_dict()
    print(qr_dict)
    if qr_dict:
        res_Devices = MGDB['Devices'].find_one(qr_dict)
        res_Users = MGDB['Users'].find_one(qr_dict)
        if not res_Devices:
            RESPONSE['CODE'] = 3
            RESPONSE['MSG'] = "无效二维码！！！"
        elif not res_Users:
            RESPONSE['CODE'] = 0
            RESPONSE['MSG'] = "二维码扫描成功"
            RESPONSE['DATA'] = qr_dict
        else:
            RESPONSE['CODE'] = 2
            RESPONSE['MSG'] = "设备已经进行绑定"
    else:
        RESPONSE['CODE'] = 1
        RESPONSE['MSG'] = "请扫描玩具二维码"
    return jsonify(RESPONSE)

#App绑定设备接口
@bp_content.route('/bind_toy', methods=['POST'])
def bind_toy():
    toy_dict = request.form.to_dict()
    # print(toy_dict)
    # {'toy_name': '娃哈哈', 'baby_name': '0', 'remark': '123', 'device_key': '0f83854da59d42d2f0a9e1e5223f0c65', 'user_id': '5d328bc0472a3a09ec32ec58'}

    toy_info = {
        "toy_name": toy_dict.get("toy_name"),
        "baby_name": toy_dict.get("baby_name"),
        "device_key": toy_dict.get("device_key"),
        "avatar": "toy.jpg",
        "bind_user": toy_dict.get("user_id"),
        "friend_list": []
    }

    try:
        MGDB['Toys'].insert_one(toy_info)
        toy_id = str(MGDB['Toys'].find_one(toy_info).get('_id'))
        user_id = ObjectId(toy_dict.get('user_id'))
        MGDB['Users'].update_one({'_id': user_id}, {'$push': {'bind_toys': toy_id}})
    except:
        pass
    else:
        RESPONSE['MSG'] = "绑定完成"
    return jsonify(RESPONSE)

#App获取绑定Toy信息接口
@bp_content.route('/toy_list', methods=['POST'])
def toy_list():
    user_id=ObjectId(request.form.get('_id'))
    bind_toys=MGDB['Users'].find_one({"_id":user_id}).get("bind_toys")
    # print(bind_toys)
    toy_id_list=[]
    for toy in bind_toys:
        toy_id_list.append(ObjectId(toy))
    _data=list(MGDB['Toys'].find({'_id':{'$in':toy_id_list}}))
    RESPONSE['MSG']="获取Toy列表"
    RESPONSE['DATA']=_data
    return jsonify(RESPONSE)

# #设备启动登录接口 (硬件接口)
# @bp_content.route('/open_toy',methods=['POST'])
# def open_toy():
#     device_key=request.form.get('device_key')
#     pass





