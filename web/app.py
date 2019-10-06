"""Phuey Web App

"""
from datetime import datetime
import subprocess

from flask import Flask
from flask_redis import FlaskRedis

app = Flask(__name__)
app.config['REDIS_URL'] = "redis://:password@192.168.50.10:6379/0"

redis_client = FlaskRedis(app)


@app.route('/')
def hello():
    return "Hello World!"


@app.route('/vapor/<enabled>', methods=['GET', 'POST'])
def api_vapor(enabled=None):

    if enabled == 'start':
        process = subprocess.Popen(
            ['phuey vapor --no-restore'],
            shell=True)
        return str(process.pid)

    return '?'


@app.route('/test-redis')
def test_redis():
    return redis_client.get('key1')


if __name__ == '__main__':
    app.run()

# End File: phuey/web/app.py
