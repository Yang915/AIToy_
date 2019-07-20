from flask import Flask
from serv_api.content import bp_content
from serv_api.user import bp_user

app = Flask(__name__)
app.debug = True

app.register_blueprint(bp_content)
app.register_blueprint(bp_user)

if __name__ == '__main__':
    app.run('0.0.0.0', 9527)
