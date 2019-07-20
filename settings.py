# 数据库配置
from pymongo import MongoClient
MGDB = MongoClient(host='127.0.0.1',port=27017)['AIToy']



# 音乐资源目录配置
MUSIC_PATH = 'source/儿歌大全/music'
COVER_PATH = 'source/儿歌大全/cover'


#二维码个数
QR_NUM=10
#二维码生成API(联动接口)
QR_URL='http://qr.topscan.com/api.php?text='

# 响应数据格式配置
RESPONSE = {
    'CODE': 0,
    'MSG': '',
    'DATA': {}
}
