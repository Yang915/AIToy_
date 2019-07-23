from flask import Flask
from flask_cors import CORS#pip install Flask-CORS#跨域请求模块
from serv_api.content import bp_content
from serv_api.user import bp_user
from serv_api.devices import  bp_devices
from serv_api.friend import bp_friend
from serv_api.uploader import bp_uploader
from serv_api.chat import bp_chat


app = Flask(__name__)
app.debug = True

app.register_blueprint(bp_content)
app.register_blueprint(bp_user)
app.register_blueprint(bp_devices)
app.register_blueprint(bp_friend)
app.register_blueprint(bp_uploader)
app.register_blueprint(bp_chat)


CORS(app)#跨域请求

if __name__ == '__main__':
    app.run('0.0.0.0', 9527)
