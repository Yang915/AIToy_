import os
import time
import hashlib
import requests
from uuid import uuid4
from settings import MGDB

#二维码目录
QR_PATH='qr' if os.path.exists('qr') else os.makedirs('qr')
#二维码个数
QR_NUM=10
#二维码生成API(联动接口)
QR_URL='http://qr.topscan.com/api.php?text='


qr_list = []

for i in range(QR_NUM):
    str = f'{uuid4()}{time.time()}{uuid4()}'
    random_string = hashlib.md5(str.encode('utf-8')).hexdigest()

    res = requests.get(QR_URL + random_string)

    qr_path = os.path.join(QR_PATH, random_string + '.jpg')
    with open(qr_path, 'wb') as f:
        f.write(res.content)
    qr_list.append({"device_key": random_string})

MGDB['Devices'].insert_many(qr_list)
