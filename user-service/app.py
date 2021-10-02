import os
from datetime import datetime, timezone
from flask import Flask, request, jsonify as jsonify_old
from json import load
from requests import post


LOGGING_URL = os.getenv('LOGGING_URL')
USERS_FILE = 'data/users.json'


app = Flask(__name__)


class User:
    def __init__(self, dictionary):
        self.id = dictionary['id']
        self.name = dictionary['name']

    def serialize(self):
        return self.__dict__

    def __str__(self):
        return "{} ({})".format(self.name, self.id)


@app.route('/users')
def get_users():
    users = read_users()
    response = jsonify(users)
    send_log(request.path, 200, ', '.join([str(user) for user in users]))
    return response


@app.route('/user/<user_id>')
def get_user(user_id):
    users = read_users()
    matching_users = [user for user in users if str(user.id) == user_id]

    if len(matching_users) == 0:
        error_message = "User id={} Not found".format(user_id)
        send_log(request.path, 404, error_message)
        return error_message, 404

    elif len(matching_users) > 1:
        error_message = "Internal error, {} users found with id={}".format(len(matching_users), user_id)
        send_log(request.path, 500, error_message)
        return error_message, 500
    else:
        user = matching_users[0]
        send_log(request.path, 200, str(user))
        return jsonify(user)


@app.route('/favicon.ico')
def get_favicon():
    return "I'm a teapot", 418


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    error_message = 'Bad request, no API available on {}'.format(request.path)
    send_log(request.path, 400, error_message)
    return error_message, 400


def send_log(path, code, data=None):
    if LOGGING_URL:
        timestamp = datetime.now(tz=timezone.utc).isoformat(timespec='milliseconds')
        post(LOGGING_URL, json={
            'timestamp': timestamp,
            'request_path': path,
            'status_code': code,
            'additional_info': data})


def read_users():
    file = open(USERS_FILE)
    users = load(file)
    file.close()
    return [User(user) for user in users]


def jsonify(data):
    if isinstance(data, list):
        return jsonify_old([item.serialize() for item in data])
    elif isinstance(data, User):
        return jsonify_old(data.serialize())
    elif isinstance(data, dict):
        return jsonify_old(data)
    else:
        return data

