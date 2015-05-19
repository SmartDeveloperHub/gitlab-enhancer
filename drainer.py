__author__ = 'alejandrofcarrera'

from flask import request, make_response, Flask
from flask_negotiate import consumes, produces
import glmodule
import datetime
import json

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

# /api/projects
# Get gitlab projects
@app.route('/api/projects', methods=['GET'])
@produces('application/json')
def api_projects():
    return make_response(json.dumps(drainer.api_projects()))

# /api/projects/:pid
# Get specific gitlab project
@app.route('/api/projects/<int:pid>', methods=['GET'])
@produces('application/json')
def api_project(pid):
    return make_response(json.dumps(drainer.api_project(pid)))

# /api/projects/:pid/owner
# Get owner about specific gitlab project
@app.route('/api/projects/<int:pid>/owner', methods=['GET'])
@produces('application/json')
def api_project_owner(pid):
    return make_response(json.dumps(drainer.api_project_owner(pid)))

# /api/projects/:pid/milestones
# Get milestone about specific gitlab project
# @app.route('/api/projects/<int:pid>/milestones', methods=['GET'])
# @produces('application/json')
# def api_project_milestones(pid):
# return make_response(json.dumps(drainer.api_project_milestones(pid)))

# /api/projects/:pid/milestones/:mid
# Get specific milestone about specific gitlab project
# @app.route('/api/projects/<int:pid>/milestones/<int:mid>', methods=['GET'])
# @produces('application/json')
# def api_project_milestone(pid, mid):
#     return make_response(json.dumps(drainer.api_project_milestone(pid, mid)))

# /api/projects/:pid/branches[?bool:default]
# # default = [true|false] for get default branch only
# Get branches about specific gitlab project
# It is possible only get the default branch
@app.route('/api/projects/<int:pid>/branches', methods=['GET'])
@produces('application/json')
def api_project_branches(pid):
    default = request.args.get('default', 'false')
    if default != 'false' and default != 'true':
        return make_response("400: default parameter must be true or false", 400)
    return make_response(json.dumps(drainer.api_project_branches(pid, default)))

# /api/projects/:pid/branches/:bid
# Get specific branch about specific gitlab project
@app.route('/api/projects/<int:pid>/branches/<string:bid>', methods=['GET'])
@produces('application/json')
def api_project_branch(pid, bid):
    return make_response(json.dumps(drainer.api_project_branch(pid, bid)))

# /api/projects/:pid/branches/:bid[?long:start_time][?long:end_time]
# # start_time = time (start) filter
# # end_time = time (end) filter
# Get contributors of specific branch about specific gitlab project
# It is possible filter by range (time)
@app.route('/api/projects/<int:pid>/branches/<string:bid>/contributors', methods=['GET'])
@produces('application/json')
def api_project_branch_contributors(pid, bid):
    t_window = check_time_window(request.args)
    if t_window['st_time'] == 'Error' or t_window['en_time'] == 'Error':
        return make_response("400: start_time or end_time is bad format", 400)
    return make_response(
        json.dumps(
            drainer.api_project_branch_contributors(pid, bid, t_window)
        )
    )

# /api/projects/:pid/branches/:bid/commits[?int:offset][?int:uid][?long:start_time][?long:end_time]
# # offset = start from number of commits
# # uid = user identifier
# # start_time = time (start) filter
# # end_time = time (end) filter
# Get commits of specific branch about specific gitlab project
# It is possible filter by user with gitlab uid
# It is possible filter by range (time)
@app.route('/api/projects/<int:pid>/branches/<string:bid>/commits', methods=['GET'])
@produces('application/json')
def api_project_branch_commits(pid, bid):
    offset = request.args.get('offset', None)
    if offset is not None:
        try:
            offset = int(offset)
        except ValueError:
            return make_response("400: offset parameter is not an integer", 400)
    user = request.args.get('uid', None)
    if user is not None:
        try:
            user = int(user)
        except ValueError:
            return make_response("400: uid parameter is not an integer (user identifier)", 400)
    t_window = check_time_window(request.args)
    if t_window['st_time'] == 'Error' or t_window['en_time'] == 'Error':
        return make_response("400: start_time or end_time is bad format", 400)
    return make_response(
        json.dumps(
            drainer.api_project_branch_commits(pid, bid, user, offset, t_window)
        )
    )

# /api/projects/:pid/commits[?int:uid][?long:start_time][?long:end_time]
# # uid = user identifier
# # start_time = time (start) filter
# # end_time = time (end) filter
# Get commits about specific gitlab project
# It is possible filter by user with gitlab uid
# It is possible filter by range (time)
@app.route('/api/projects/<int:pid>/commits', methods=['GET'])
@produces('application/json')
def api_project_commits(pid):
    offset = request.args.get('offset', None)
    if offset is not None:
        try:
            offset = int(offset)
        except ValueError:
            return make_response("400: offset parameter is not an integer", 400)
    user = request.args.get('uid', None)
    if user is not None:
        try:
            user = int(user)
        except ValueError:
            return make_response("400: uid parameter is not an integer (user identifier)", 400)
    t_window = check_time_window(request.args)
    if t_window['st_time'] == 'Error' or t_window['en_time'] == 'Error':
        return make_response("400: start_time or end_time is bad format", 400)
    return make_response(
        json.dumps(
            drainer.api_project_commits(pid, user, offset, t_window)
        )
    )

# /api/projects/:pid/commits/:cid
# Get specific commit about specific gitlab project
@app.route('/api/projects/<int:pid>/commits/<string:cid>', methods=['GET'])
@produces('application/json')
def api_project_commit(pid, cid):
    return make_response(json.dumps(drainer.api_project_commit(pid, cid)))

# /api/projects/:pid/commits/:cid/diff
# Get differences of specific commit about specific gitlab project
@app.route('/api/projects/<int:pid>/commits/<string:cid>/diff', methods=['GET'])
@produces('application/json')
def api_project_commit_diff(pid, cid):
    return make_response(json.dumps(drainer.api_project_commit_diff(pid, cid)))

# /api/projects/:pid/merge_requests[?string:state]
# # state = [opened, closed, merged]
# Get merge requests about specific gitlab project
# It is possible filter by state
# @app.route('/api/projects/<int:pid>/merge_requests', methods=['GET'])
# @produces('application/json')
# def api_project_requests(pid):
#     mrstate = request.args.get('state', 'all')
#     if mrstate is not 'all':
#         if mrstate is not 'opened' and mrstate is not 'closed' and mrstate is not 'merged':
#             return make_response("400: state parameter is not a valid state (opened|closed|merged|all)", 400)
#     return make_response(json.dumps(drainer.api_project_requests(pid, mrstate)))

# /api/projects/:pid/merge_requests/:mrid
# Get specific merge request about specific gitlab project
# @app.route('/api/projects/<int:pid>/merge_requests/<int:mrid>', methods=['GET'])
# @produces('application/json')
# def api_project_request(pid, mrid):
#     return make_response(json.dumps(drainer.api_project_request(pid, mrid)))

# /api/projects/:pid/merge_requests/:mrid/changes
# Get changes of specific merge request about specific gitlab project
# @app.route('/api/projects/<int:pid>/merge_requests/<int:mrid>/changes', methods=['GET'])
# @produces('application/json')
# def api_project_request_changes(pid, mrid):
#     return make_response(json.dumps(drainer.api_project_request_changes(pid, mrid)))

# /api/projects/:pid/file_tree[?string:view][?string:path][?string:branch]
# # view = [simple, full]
# # path = optional path
# # branch = optional branch
# Get file tree about specific gitlab project
# It is possible only get a simple or full representation
# It is possible start from a specific path
# It is possible filter by branch or get default branch
@app.route('/api/projects/<int:pid>/file_tree', methods=['GET'])
@produces('application/json')
def api_project_file_tree(pid):
    view = request.args.get('view', 'full')
    if view != 'full':
        if view != 'full' and view != 'simple':
            return make_response("400: view parameter is not a valid view (full|simple)", 400)
    path = request.args.get('path', None)
    branch = request.args.get('branch', None)
    return make_response(json.dumps(drainer.api_project_file_tree(pid, view, branch, path)))

# /api/projects/:pid/contributors
# # start_time = time (start) filter
# # end_time = time (end) filter
# Get contributors about specific gitlab project
# It is possible filter by range (time)
@app.route('/api/projects/<int:pid>/contributors', methods=['GET'])
@produces('application/json')
def api_project_contributors(pid):
    t_window = check_time_window(request.args)
    if t_window['st_time'] == 'Error' or t_window['en_time'] == 'Error':
        return make_response("400: start_time or end_time is bad format", 400)
    return make_response(
        json.dumps(
            drainer.api_project_contributors(pid, t_window)
        )
    )

# /api/users[?int:offset]
# # offset = start from number of users
# Get gitlab users
@app.route('/api/users', methods=['GET'])
@produces('application/json')
def api_users():
    offset = request.args.get('offset', None)
    if offset is not None:
        try:
            offset = int(offset)
        except ValueError:
            return make_response("400: offset parameter is not an integer", 400)
    return make_response(json.dumps(drainer.api_users(offset)))

# /api/users/:uid
# Get specific gitlab user
@app.route('/api/users/<int:uid>', methods=['GET'])
@produces('application/json')
def api_user(uid):
    return make_response(json.dumps(drainer.api_user(uid)))

# /api/users/:uid/projects[?string:relation]
# # relation = [contributor only in default branch, owner]
# Get projects about specific gitlab user
# It is possible filter by relation between user and project
@app.route('/api/users/<int:uid>/projects', methods=['GET'])
@produces('application/json')
def api_user_projects(uid):
    relation = request.args.get('relation', 'contributor')
    if relation != 'contributor' and relation != 'owner':
        return make_response("400: relation parameter is not a valid relation (contributor|owner)", 400)
    return make_response(json.dumps(drainer.api_user_projects(uid, relation)))

# /api/groups
# Get gitlab groups
@app.route('/api/groups', methods=['GET'])
@produces('application/json')
def api_groups():
    return make_response(json.dumps(drainer.api_groups()))

# /api/groups/:gid
# Get specific gitlab groups
@app.route('/api/groups/<int:gid>', methods=['GET'])
@produces('application/json')
def api_group(gid):
    return make_response(json.dumps(drainer.api_group(gid)))

# /api/groups/:gid/projects[?string:relation]
# # relation = [contributor only in default branch, owner]
# Get projects about specific gitlab group
# It is possible filter by relation between user and project
@app.route('/api/groups/<int:gid>/projects', methods=['GET'])
@produces('application/json')
def api_group_projects(gid):
    relation = request.args.get('relation', 'contributor')
    if relation != 'contributor' and relation != 'owner':
        return make_response("400: relation parameter is not a valid relation (contributor|owner)", 400)
    return make_response(json.dumps(drainer.api_group_projects(gid, relation)))


# Functions to help another functions


def check_time_window(args):
    start_time = args.get('start_time', None)
    if start_time is not None:
        try:
            start_time = long(start_time)
        except ValueError:
            start_time = 'Error'
    end_time = args.get('end_time', None)
    if end_time is not None:
        try:
            end_time = long(end_time)
        except ValueError:
            end_time = 'Error'
    if end_time is None:
        end_time = long(datetime.datetime.now().strftime("%s")) * 1000
    if start_time is None:
        start_time = long(0)
    if start_time > end_time:
        start_time = 'Error'
        end_time = 'Error'
    return {
        'st_time': start_time,
        'en_time': end_time
    }


# Main

if __name__ == '__main__':
    if drainer.redis is None:
        print " * [REDIS] Redis is not available at http://%s:%d" % (
            app.config.get('REDIS_IP', '127.0.0.1'),
            app.config.get('REDIS_PORT', 6379)
        )
    else:
        print " * [REDIS] Status: online"
    if drainer.git is None:
        print " * [SCM] Gitlab is not available at %s://%s:%d" % (
            app.config.get('GITLAB_PROT', 'http'),
            app.config.get('GITLAB_IP', '127.0.0.1'),
            app.config.get('GITLAB_PORT', 8080)
        )
    else:
        print " * [SCM] Status: online"
    if drainer.git is not None or (drainer.redis is not None and drainer.redis_status is True):
        app.run(app.config.get('DRAINER_LISTEN_IP', '0.0.0.0'), app.config.get('DRAINER_PORT', 5000))
    else:
        print " * Drainer finished"