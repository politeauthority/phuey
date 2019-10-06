"""Phuey Web App

"""
import signal
import subprocess
import os


from flask import Flask
from flask_redis import FlaskRedis

app = Flask(__name__)
app.config['REDIS_URL'] = "redis://:@192.168.50.10:6379/0"

redis_client = FlaskRedis(app)


@app.route('/')
def hello():
    return "Hello World!"


@app.route('/vapor/<enabled>', methods=['GET', 'POST'])
def api_vapor(enabled=None):

    if enabled == 'start':
        start_cmd = 'phuey vapor --no-restore'
        process = subprocess.Popen(
            [start_cmd],
            shell=True)
        redis_client.set('current_proc', process.pid)
        return str(process.pid)
    elif enabled == 'stop':
        current_proc = int(redis_client.get('current_proc'))
        # cmd = ['kill -SIGINT %s' % int(current_proc)]
        print('Killing proc %s' % current_proc)
        os.kill(current_proc, signal.SIGTERM)
        return 'Killing proc %s' % current_proc

    return '?'


@app.route('/test-redis')
def test_redis():
    return redis_client.get('key1')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)

# End File: phuey/web/app.py
