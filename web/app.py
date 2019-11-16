"""Phuey Web App

"""
from datetime import datetime
import os
import signal
import subprocess
import sys


from flask import Flask, redirect
from flask import jsonify
from flask import request
from flask import render_template
from flask_redis import FlaskRedis

PHUEY_CLI_APPLICATION = '/usr/local/bin/phuey'

app = Flask(__name__)
app.config['REDIS_URL'] = "redis://:@192.168.50.10:6379/0"

redis_client = FlaskRedis(app)


@app.route('/')
def index():
    data = {}
    data['status'] = _get_status()
    return render_template('index.html', **data)

@app.route('/settings')
def settings_form():
    data = {}
    data['global_brightness'] = _get_json_redis('phuey_global_brightness')
    if not data['global_brightness']:
        data['global_brightness'] = 254
    return render_template('settings_form.html', **data)

@app.route('/settings-save', methods=['GET', 'POST'])
def settings_save():
    if 'global-brightness' in request.form:
        redis_client.set('phuey_global_brightness', request.form['global-brightness'])
        print('Saving Key: %s Value:%s' % ('phuey_global_brightness', request.form['global-brightness']))

    return redirect('/')


@app.route('/animation-list')
def animations():
    data = {}
    return render_template('animations.html', **data)


@app.route('/animation-configure/<animation>')
def animation_configure(animation):
    data = {
        'name': animation
    }
    return render_template('animation_configure.html', **data)

@app.route('/animation-configure-save', methods=['GET', 'POST'])
def animation_configure_save():
    animation_name = request.form['animate-name']
    animation_name = animation_name.replace('-', '_')
    key_prefix = 'phuey_animation_%s' % animation_name
    if 'animate-delay' in request.form:
        redis_key = '%s_delay' % key_prefix
        redis_client.set(redis_key, request.form['animate-delay'])
        print('Saving Key: %s Value:%s' % (redis_key, request.form['animate-delay']))

    return redirect('/')


@app.route('/api/animate/<animation>', methods=['GET', 'POST'])
def api_animate(animation):
    """
    Runs a selected animation indefinitely.

    """
    data = {}
    data['animation'] = animation
    if not _validate_animation(animation):
        data['error'] = 'Could not validate animation: %s' % animation
        data['status'] = 'failed'
        return jsonify(data)

    if _get_json_redis('phuey_status') == 'running':
        print('Found running process, attempting to kill.')
        kill_data = kill_animation()
        data.update(kill_data)

    options = _format_options(request.args)
    data['status'] = 'success'
    data = run_animation(animation, options)
    return jsonify(data)


@app.route('/api/stop', methods=['GET', 'POST'])
def api_stop():
    """
    Stops the current running animation.

    """
    data = {}
    data['animation'] = 'vapor'
    kill_data = kill_animation()
    data.update(kill_data)
    return jsonify(data)


@app.route('/api/status', methods=['GET', 'POST'])
def api_status():
    """
    Gets the current status of Phuey, including status, current animation, start time and more.

    """
    data = _get_status()
    return jsonify(data)


def run_animation(animation, options=[]):
    """
    Verifies and runs an animation, setting the appropriate keys in redis.

    """
    options.append('--no-restore')
    # options.append('--delay=.2')
    start_cmd = [PHUEY_CLI_APPLICATION, animation] + options
    print('Running: %s' % start_cmd)
    process = subprocess.Popen(start_cmd)
    data = {
        'status': 'running',
        'animation': animation,
        'start': str(datetime.now()),
        'pid': process.pid,
        'command': start_cmd,
        'options': options,
    }
    data = _get_decoded_dict(data)
    redis_client.set('phuey_status', data['status'])
    redis_client.set('phuey_animation', data['animation'])
    redis_client.set('phuey_start', data['start'])
    redis_client.set('phuey_pid', data['pid'])
    redis_client.set('phuey_options', ' '.join(data['options']))

    return data


def kill_animation() -> dict:
    """
    Kills an animation based on the pid found in redis key phuey_pid

    """
    data = {}    
    current_proc = _get_json_redis('phuey_pid')
    if not current_proc:
        data['error'] = "Couldn't find a process to stop"
        data['status'] = "failed"
        return data

    current_proc = int(current_proc)
    data['pid'] = current_proc
    print('Killing proc %s' % current_proc)
    redis_client.set('phuey_status', 'stopped')
    try:
        os.kill(current_proc, signal.SIGTERM)
    except ProcessLookupError:
        data['error'] = "Couldn't find process ID: %s" % data['pid']
        data['status'] = "failed"
        data['killed_notes'] = "Couldn't find process ID: %s" % data['pid']
        redis_client.delete('phuey_pid')
        return data

    data['killed_notes'] = 'Successfully killed running proc %s' % current_proc
    data['status'] = "success"
    redis_client.set('phuey_animation', 'None')
    redis_client.delete('phuey_options')
    redis_client.delete('phuey_pid')

    return data


def _validate_animation(animation: str) -> bool:
    """
    Validates that the requested animation is a known, registered Phuey animation.

    """
    if animation in ['vapor', 'cycle-color', 'marquee']:
        return True
    return False


def _get_json_redis(key: str) -> str:
    """
    Gets a JSONable string from redis.

    """
    value = redis_client.get(key)
    if not value:
        return None
    return value.decode('ascii')


def _get_decoded_dict(the_dict: dict) -> dict:
    """
    This method might be over kill, but redis appears to be sending back non ASCII data, so this
    method prunes all possible non usable data, to something that's usable.
    @note: This should be revisited!

    """
    new_dict = {}
    for key, value in the_dict.items():
        try:
            new_dict[key] = value.decode('ascii')
        except AttributeError:
            new_dict[key] = value

    return new_dict


def _format_options(raw_options) -> list:
    if not raw_options:
        return []

    options = []
    if 'delay' in raw_options:
        options.append('--delay=%s' % raw_options['delay'])
    if 'verbose' in raw_options:
        options.append('-v')
    if 'no-restore' in raw_options:
        options.append('--no-restore')

    return options

def _get_status() -> dict:
    data = {
        'status': _get_json_redis('phuey_status'),
        'animation': _get_json_redis('phuey_animation')
    }
    if data['status'] == 'running':
        data['start'] = _get_json_redis('phuey_start')
        data['pid'] = _get_json_redis('phuey_pid')
        data['options'] = _get_json_redis('phuey_options')
    return data

if __name__ == '__main__':
    port = 5000
    if len(sys.argv) > 1:
        port = sys.argv[1]
    app.run(host="0.0.0.0", port=port)

# End File: phuey/web/app.py
