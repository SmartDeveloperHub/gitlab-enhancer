"""
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=#
  This file is part of the Smart Developer Hub Project:
    http://www.smartdeveloperhub.org
  Center for Open Middleware
        http://www.centeropenmiddleware.com/
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=#
  Copyright (C) 2015 Center for Open Middleware.
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=#
  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at
            http://www.apache.org/licenses/LICENSE-2.0
  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=#
"""

from flask import request, make_response, Flask
from flask_negotiate import produces
import glmodule
import datetime
import json

__author__ = 'Alejandro F. Carrera'


app = Flask(__name__)

# Enhancer Settings
app.config.from_pyfile('settings.py')

# GitLab Specific Enhancer
enhancer = glmodule.GlEnhancer(app.config)

# GitLab API Mapping


# /api
# Get gitlab
@app.route('/api', methods=['GET'])
@produces('application/json')
def api():
    return make_response(json.dumps(enhancer.api_ping()))


# /api/projects
# Get gitlab projects
@app.route('/api/projects', methods=['GET'])
@produces('application/json')
def api_projects():
    return make_response(json.dumps(enhancer.api_projects()))


# /api/projects/:pid
# Get specific gitlab project
@app.route('/api/projects/<int:pid>', methods=['GET'])
@produces('application/json')
def api_project(pid):
    return make_response(json.dumps(enhancer.api_project(pid)))


# /api/projects/:pid/owner
# Get owner about specific gitlab project
@app.route('/api/projects/<int:pid>/owner', methods=['GET'])
@produces('application/json')
def api_project_owner(pid):
    return make_response(json.dumps(enhancer.api_project_owner(pid)))


# /api/projects/:pid/milestones
# Get milestone about specific gitlab project
@app.route('/api/projects/<int:pid>/milestones', methods=['GET'])
@produces('application/json')
def api_project_milestones(pid):
    return make_response(json.dumps(enhancer.api_project_milestones(pid)))


# /api/projects/:pid/milestones/:mid
# Get specific milestone about specific gitlab project
@app.route('/api/projects/<int:pid>/milestones/<int:mid>', methods=['GET'])
@produces('application/json')
def api_project_milestone(pid, mid):
    return make_response(json.dumps(enhancer.api_project_milestone(pid, mid)))


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
    return make_response(json.dumps(enhancer.api_project_branches(pid, default)))


# /api/projects/:pid/branches/:bid
# Get specific branch about specific gitlab project
@app.route('/api/projects/<int:pid>/branches/<string:bid>', methods=['GET'])
@produces('application/json')
def api_project_branch(pid, bid):
    return make_response(json.dumps(enhancer.api_project_branch(pid, bid)))


# /api/projects/:pid/branches/:bid/contributors[?long:start_time][?long:end_time]
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
            enhancer.api_project_branch_contributors(pid, bid, t_window)
        )
    )


# /api/projects/:pid/branches/:bid/commits[?int:uid][?long:start_time][?long:end_time]
# # uid = user identifier
# # start_time = time (start) filter
# # end_time = time (end) filter
# Get commits of specific branch about specific gitlab project
# It is possible filter by user with gitlab uid
# It is possible filter by range (time)
@app.route('/api/projects/<int:pid>/branches/<string:bid>/commits', methods=['GET'])
@produces('application/json')
def api_project_branch_commits(pid, bid):
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
            enhancer.api_project_branch_commits(pid, bid, user, t_window)
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
            enhancer.api_project_commits(pid, user, t_window)
        )
    )


# /api/projects/:pid/commits/:cid
# Get specific commit about specific gitlab project
@app.route('/api/projects/<int:pid>/commits/<string:cid>', methods=['GET'])
@produces('application/json')
def api_project_commit(pid, cid):
    return make_response(json.dumps(enhancer.api_project_commit(pid, cid)))


# /api/projects/:pid/merge_requests[?string:state]
# # state = [opened, closed, merged]
# Get merge requests about specific gitlab project
# It is possible filter by state
@app.route('/api/projects/<int:pid>/merge_requests', methods=['GET'])
@produces('application/json')
def api_project_requests(pid):
    mrstate = request.args.get('state', 'all')
    if mrstate is not 'all':
        if mrstate is not 'opened' and mrstate is not 'closed' and mrstate is not 'merged':
            return make_response("400: state parameter is not a valid state (opened|closed|merged|all)", 400)
    return make_response(json.dumps(enhancer.api_project_requests(pid, mrstate)))


# /api/projects/:pid/merge_requests/:mrid
# Get specific merge request about specific gitlab project
@app.route('/api/projects/<int:pid>/merge_requests/<int:mrid>', methods=['GET'])
@produces('application/json')
def api_project_request(pid, mrid):
    return make_response(json.dumps(enhancer.api_project_request(pid, mrid)))


# /api/projects/:pid/merge_requests/:mrid/changes
# Get changes of specific merge request about specific gitlab project
@app.route('/api/projects/<int:pid>/merge_requests/<int:mrid>/changes', methods=['GET'])
@produces('application/json')
def api_project_request_changes(pid, mrid):
    return make_response(json.dumps(enhancer.api_project_request_changes(pid, mrid)))


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
            enhancer.api_project_contributors(pid, t_window)
        )
    )


# /api/users
# Get gitlab users
@app.route('/api/users', methods=['GET'])
@produces('application/json')
def api_users():
    return make_response(json.dumps(enhancer.api_users()))

# /api/users/:uid
# Get specific gitlab user
@app.route('/api/users/<int:uid>', methods=['GET'])
@produces('application/json')
def api_user(uid):
    return make_response(json.dumps(enhancer.api_user(uid)))


# /api/users/:uid/projects[?string:relation]
# # relation = [contributor only in default branch, owner]
# # start_time = time (start) filter
# # end_time = time (end) filter
# Get projects about specific gitlab user
# It is possible filter by relation between user and project
@app.route('/api/users/<int:uid>/projects', methods=['GET'])
@produces('application/json')
def api_user_projects(uid):
    t_window = check_time_window(request.args)
    if t_window['st_time'] == 'Error' or t_window['en_time'] == 'Error':
        return make_response("400: start_time or end_time is bad format", 400)
    relation = request.args.get('relation', 'contributor')
    if relation != 'contributor' and relation != 'owner':
        return make_response("400: relation parameter is not a valid relation (contributor|owner)", 400)
    return make_response(json.dumps(enhancer.api_user_projects(uid, relation, t_window)))


# /api/groups
# Get gitlab groups
@app.route('/api/groups', methods=['GET'])
@produces('application/json')
def api_groups():
    return make_response(json.dumps(enhancer.api_groups()))


# /api/groups/:gid
# Get specific gitlab groups
@app.route('/api/groups/<int:gid>', methods=['GET'])
@produces('application/json')
def api_group(gid):
    return make_response(json.dumps(enhancer.api_group(gid)))


# /api/groups/:gid/projects[?string:relation]
# # start_time = time (start) filter
# # end_time = time (end) filter
# # relation = [contributor only in default branch, owner]
# Get projects about specific gitlab group
# It is possible filter by relation between user and project
@app.route('/api/groups/<int:gid>/projects', methods=['GET'])
@produces('application/json')
def api_group_projects(gid):
    t_window = check_time_window(request.args)
    if t_window['st_time'] == 'Error' or t_window['en_time'] == 'Error':
        return make_response("400: start_time or end_time is bad format", 400)
    relation = request.args.get('relation', 'contributor')
    if relation != 'contributor' and relation != 'owner':
        return make_response("400: relation parameter is not a valid relation (contributor|owner)", 400)
    return make_response(json.dumps(enhancer.api_group_projects(gid, relation, t_window)))


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
