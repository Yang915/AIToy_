import json
import time
from bson import ObjectId
from geventwebsocket.handler import WebSocketHandler
from geventwebsocket.server import WSGIServer
from geventwebsocket.websocket import WebSocket
from flask import Flask, request, render_template



ws_app = Flask(__name__)
ws_app.debug=True

client_dict = {}

#App通讯
@ws_app.route('/app/<user_id>')
def app(user_id):
    app_socket = request.environ.get("wsgi.websocket")  # type:WebSocket
    if app_socket:
        client_dict[user_id] = app_socket
    while True:
        print('ap:',app_socket)
        app_data = app_socket.receive()
        app_data_dict=json.loads(app_data)
        to_user=app_data_dict.get("to_user")
        to_client=client_dict.get(to_user)
        try:
            to_client.send(app_data)
        except:
            pass




@ws_app.route('/toy/<toy_id>')
def toy(toy_id):
    toy_socket = request.environ.get("wsgi.websocket")  # type:WebSocket
    if toy_socket:
        client_dict[toy_id] = toy_socket
    while True:
        print('toy:',toy_socket)
        print(toy_id)
        toy_data = toy_socket.receive()
        toy_data_dict = json.loads(toy_data)
        to_user = toy_data_dict.get("to_user")
        to_client = client_dict.get(to_user)
        try:
            to_client.send(toy_data)
        except:
            pass


#玩具toy
@ws_app.route('/WebToy')
def index():
    return render_template('WebToy.html')

if __name__ == '__main__':
    http_server = WSGIServer(('0.0.0.0', 9528), application=ws_app, handler_class=WebSocketHandler)
    http_server.serve_forever()
