import os

from bson import ObjectId
from flask import Blueprint, request, jsonify, send_file

from settings import MGDB, MUSIC_PATH, COVER_PATH, RESPONSE, QR_PATH, CHAT_PATH

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
    print(cover_path)
    return send_file(cover_path)


# 获取音乐资源
@bp_content.route('/get_music/<musicname>', methods=['GET'])
def get_music(musicname):
    music_path = os.path.join(MUSIC_PATH, musicname)
    return send_file(music_path)

# 获取二维码图片资源
@bp_content.route('/get_qr/<device>', methods=['GET'])
def get_qr(device):
    qr_path = os.path.join(QR_PATH, device)
    return send_file(qr_path)

# 获取语音消息资源
@bp_content.route("/get_chat/<chatname>", methods=['GET'])
def get_chat(chatname):
    chatfile=os.path.join(CHAT_PATH,chatname)
    return send_file(chatfile)




