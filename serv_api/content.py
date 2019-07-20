import os

from flask import Blueprint, request, jsonify, send_file

from settings import MGDB,MUSIC_PATH,COVER_PATH

bp_content = Blueprint('bp_content', __name__)

#获取资源内容
@bp_content.route('/content_list', methods=['POST'])
def content_list():
    source_data = MGDB['Content'].find({})
    data_list = list(source_data)
    for index,data in enumerate(data_list):
        data_list[index]['_id']=str(data.get('_id'))
    return jsonify(data_list)


#获取图片资源
@bp_content.route('/get_cover/<covername>',methods=['GET'])
def get_cover(covername):
    cover_path=os.path.join(COVER_PATH,covername)
    return send_file(cover_path)

#获取音乐资源
@bp_content.route('/get_music/<musicname>',methods=['GET'])
def get_music(musicname):
    music_path=os.path.join(MUSIC_PATH,musicname)
    return send_file(music_path)