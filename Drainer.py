
__author__ = 'alejandrofcarrera'

from flask import request, make_response, Flask
from flask_negotiate import consumes, produces
import glmodule
import json

app = Flask(__name__)
app.config.from_pyfile('settings.py')

drainer = glmodule.GlDrainer(app.config)

@app.route('/system', methods=['POST'])
@consumes('application/json')
def hook_system():
    if app.config.get('DEBUGGER', True):
        print('System event: %s' % request.data)
    drainer.hook_system(request.json)
    resp = make_response('', 204)
    return resp

@app.route('/hook', methods=['POST'])
@consumes('application/json')
def hook_specific():
    if app.config.get('DEBUGGER', True):
        print('Hook event: %s' % request.data)
    drainer.hook_specific(request.json)
    resp = make_response('', 204)
    return resp

@app.route('/api/<name>', methods=['GET'])
@produces('application/json')
def api_gitlab(name):
    resp = make_response(json.dumps(drainer.api_gitlab(name)), 200)
    return resp

if __name__ == '__main__':
    app.run(app.config.get('DRAINER_LISTEN_IP', '0.0.0.0'), app.config.get('DRAINER_PORT', 5000))