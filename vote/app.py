import json
import os
import random
import socket

from flask import Flask, g, make_response, render_template, request

from redis import Redis

option_a = os.getenv('OPTION_A', "Trump")
option_b = os.getenv('OPTION_B', "Orangutan")
hostname = socket.gethostname()

app = Flask(__name__)

def get_redis():
    redis_host = os.environ.get("REDIS_HOST", None)
    redis_password = os.environ.get("REDIS_PASSWORD", None)
    
    if not hasattr(g, 'redis'):
        g.redis = Redis(host=redis_host,password=redis_password,socket_timeout=5)
    return g.redis

@app.route("/", methods=['POST','GET'])
def hello():
    voter_id = request.cookies.get('voter_id')
    if not voter_id:
        voter_id = hex(random.getrandbits(64))[2:-1]

    vote = None

    if request.method == 'POST':
        redis = get_redis()
        vote = request.form['vote']
        data = json.dumps({'voter_id': voter_id, 'vote': vote})
        redis.rpush('votes', data)

    resp = make_response(render_template(
        'index.html',
        option_a=option_a,
        option_b=option_b,
        hostname=hostname,
        vote=vote,
    ))
    resp.set_cookie('voter_id', voter_id)
    return resp


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True, threaded=True)
