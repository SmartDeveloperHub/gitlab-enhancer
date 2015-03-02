
__author__ = 'Alejandro F. Carrera'

from flask import request, make_response, Flask
from flask_negotiate import consumes
from gitlab import system

app = Flask(__name__)
app.config.from_pyfile('settings.py')

@app.route('/system', methods=['POST'])
@consumes('application/json')
def hook_system():
    if app.config['DEBUGGER']:
        print('System event: %s' % request.data)
    system.hook_system(request.json)
    resp = make_response('', 204)
    return resp

@app.route('/hook', methods=['POST'])
@consumes('application/json')
def hook_specific():
    if app.config['DEBUGGER']:
        print('Hook event: %s' % request.data)
    # system.hook_specific(request.json)
    resp = make_response('', 204)
    return resp

if __name__ == '__main__':
    app.run(host='0.0.0.0')