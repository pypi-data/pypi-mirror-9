from flask import Flask, jsonify
from werkzeug.exceptions import default_exceptions
from werkzeug.exceptions import HTTPException
import os
import pylibmc


def make_json_error(ex):
    response = jsonify(message=str(ex))
    if isinstance(ex, HTTPException):
        response.status_code = ex.code
    else:
        response.status_code = 500
    return response

app = Flask(__name__)
app.config.update(
    MEMCACHED_HOST='127.0.0.1',
    URL_PARSE_TIMEOUT=86400,  # 1 day
)

if os.access(os.path.expanduser('~/.config/podhub/follower/config.py')):
    app.config.from_pyffile('~/.config/podhub/follower/config.py', silent=True)
elif os.access('/etc/podhub/follower/config.py'):
    app.config.from_pyffile('/etc/podhub/follower/config.py', silent=True)

mc = pylibmc.Client(app.config.get('MEMCACHED_HOST', '127.0.0.1'),
                    binary=True,
                    behaviors={'tcp_nodelay': True, 'ketama': True})

for code in default_exceptions.iterkeys():
    app.error_handler_spec[None][code] = make_json_error
