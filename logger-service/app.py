from flask import Flask, request, send_file

app = Flask(__name__)


LOG_FILE = 'data/log.txt'


@app.get('/logs')
def get_logs():
    return send_file(LOG_FILE, mimetype='text/plain')


@app.post('/log')
def post_log():
    timestamp = request.json['timestamp']
    url = request.json['request_path']
    code = request.json['status_code']
    data = request.json['additional_info']

    log_line = \
        '{}  {:10}  ->  {}:  {}'.format(timestamp, url, code, data) if data is not None else \
        '{}  {}  ->  {}'.format(timestamp, url, code)

    with open(LOG_FILE, 'a') as log_file:
        log_file.write(log_line + '\n')

    return '', 201

