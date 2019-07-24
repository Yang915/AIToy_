'''
图灵机器人API V2.0接入文档：https://www.kancloud.cn/turing/www-tuling123-com/718227
'''
import json
import requests
def turingRobotAnswer(text_question):
    request_json={
        "perception": { #必须参数：输入信息（注意：输入参数必须包含inputText或inputImage或inputMedia）
            "inputText": {          #非必须参数：文本信息
                "text": text_question     #必须参数：1-128字符	，直接输入文本
            },
        },
        "userInfo": {   #必须参数：用户参数
            "apiKey": "11cb5ce350c54016974151892635388b",   #必须参数：32位，机器人标识
            "userId": "123"                                 #必须参数：长度小于等于32位，用户唯一标识
        }
    }
    result=requests.post('http://openapi.tuling123.com/openapi/api/v2',json=request_json)#POST请求，参数文档有说明
    # print(result)
    text_answer=json.loads(result.content).get('results')[0].get('values').get('text')
    return text_answer



