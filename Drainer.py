
__author__ = 'alejandrofcarrera'

from flask import request, make_response, Flask
from flask_negotiate import consumes, produces
import glmodule

app = Flask(__name__)

# Drainer Settings
app.config.from_pyfile('settings.py')

# GitLab Specific Drainer
drainer = glmodule.GlDrainer(app.config)

# GitLab Hook Mapping

@app.route('/system', methods=['POST'])
@consumes('application/json')
def hook_system():
    if app.config.get('DEBUGGER', True):
        print('System event: %s' % request.data)
    drainer.hook_system(request.json)
    resp = make_response('', 200)
    return resp

@app.route('/hook', methods=['POST'])
@consumes('application/json')
def hook_specific():
    if app.config.get('DEBUGGER', True):
        print('Hook event: %s' % request.data)
    drainer.hook_specific(request.json)
    resp = make_response('', 200)
    return resp

# GitLab API Mapping

@app.route('/api/projects', methods=['GET'])
@produces('application/json')
def api_projects():
    return drainer.api_projects()

@app.route('/api/projects/<int:id>', methods=['GET'])
@produces('application/json')
def api_project(id):
    return drainer.api_project(id)

@app.route('/api/projects/<int:id>/owner', methods=['GET'])
@produces('application/json')
def api_project_owner(id):
    return drainer.api_project_owner(id)

# Main

if __name__ == '__main__':
    if drainer.git is None:
        print "[WARN] Gitlab is not available at %s://%s:%d" % (
            app.config.get('GITLAB_PROT', 'http'),
            app.config.get('GITLAB_IP', '127.0.0.1'),
            app.config.get('GITLAB_PORT', 8080)
        )
    app.run(app.config.get('DRAINER_LISTEN_IP', '0.0.0.0'), app.config.get('DRAINER_PORT', 5000))
