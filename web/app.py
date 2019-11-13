"""Phuey Web App

"""
from datetime import datetime
import os
import signal
import subprocess

from flask import Flask
from flask import jsonify
from flask import request
from flask_redis import FlaskRedis

PHUEY_CLI_APPLICATION = '/usr/local/bin/phuey'

app = Flask(__name__)
app.config['REDIS_URL'] = "redis://:@192.168.50.10:6379/0"

redis_client = FlaskRedis(app)


@app.route('/')
def hello():
    return "Hello World!"


@app.route('/api/animate/<animation>', methods=['GET', 'POST'])
def api_animate(animation):
    """
    """
    print('\n\nREQUEST')
    print(request.data)
    print(request.get_json())
    print('\n\n')
    data = {}
    data['animation'] = animation
    if not _validate_animation(animation):
        data['error'] = 'Could not validate animation: %s' % animation
        return jsonify(data)

    data = run_animation(animation)
    print(data)
    return jsonify(data)


@app.route('/api/stop', methods=['GET', 'POST'])
def api_stop():
    """
    """
    data = {}
    data['animation'] = 'vapor'
    data = kill_animation()
    return jsonify(data)


@app.route('/api/status', methods=['GET', 'POST'])
def api_status():
    """
    """
    data = {
        'status': _get_json_redis('phuey_status'),
        'animation': _get_json_redis('phuey_animation')
    }
    if data['status'] == 'running':
        data['start'] = _get_json_redis('phuey_start')
        data['pid'] = _get_json_redis('phuey_current_proc')
    print(data)

    return jsonify(data)


def run_animation(animation, options=[]):
    """
    Verifies and runs an animation, setting the appropriate keys in Redis
    """
    start_cmd = [PHUEY_CLI_APPLICATION, animation] + options
    process = subprocess.Popen(start_cmd)
    data = {
        'status': 'running',
        'animation': animation,
        'start': str(datetime.now()),
        'pid': process.pid
    }
    data = _get_decoded_dict(data)
    redis_client.set('phuey_status', data['status'])
    redis_client.set('phuey_animation', data['animation'])
    redis_client.set('phuey_start', data['start'])
    redis_client.set('phuey_pid', data['pid'])
    return data


def kill_animation():
    """
    Kills an animation based on the pid found in redis
    @todo: Fix error returns

    """
    current_proc = int(_get_json_redis('phuey_current_proc'))
    data = {}
    # data['pid'] = str(current_proc)
    print('Killing proc %s' % current_proc)
    try:
        os.kill(current_proc, signal.SIGTERM)
    except ProcessLookupError:
        # data['error'] = "Couldn't find process ID: %s" % data['pid']
        print(data)

        return "Error"
    redis_client.set('phuey_status', 'stopped')
    return data


def _validate_animation(animation):
    """
    """
    if animation in ['vapor']:
        return True
    return False


def _get_json_redis(key):
    """
    Gets a JSONable string from redis.

    """
    value = redis_client.get(key)
    if not value:
        return None
    return value.decode('ascii')


def _get_decoded_dict(the_dict):
    new_dict = {}
    for key, value in the_dict.items():
        try:
            new_dict[key] = value.decode('ascii')
        except AttributeError:
            new_dict[key] = value

    return new_dict


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)

# End File: phuey/web/app.py
