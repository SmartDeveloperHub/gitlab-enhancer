"""
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=#
  This file is part of the Smart Developer Hub Project:
    http://www.smartdeveloperhub.org
  Center for Open Middleware
        http://www.centeropenmiddleware.com/
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=#
  Copyright (C) 2016 Center for Open Middleware.
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
import json
import logging
from datetime import datetime

import validators
from flask import Flask, jsonify, request, make_response
from flask_negotiate import produces, consumes

__author__ = 'Ignacio Molina Cuquerella'


class EnhancerService:

    def __init__(self, config, enhancer):

        self.app = Flask(__name__)
        self.ip = config.GE_LISTEN_IP
        self.port = config.GE_LISTEN_PORT
        self.enhancer = enhancer

        @self.app.route('/api/collectors/', methods=['GET'])
        @produces('application/json')
        def get_collectors():

            return json_response(enhancer.git_collectors.get_collectors())

        @self.app.route('/api/collectors/<string:coll_id>/', methods=['GET'])
        @produces('application/json')
        def get_collector(coll_id):

            collector = enhancer.git_collectors.get_collector(coll_id)

            if collector:
                return json_response(collector)

            return make_response('', 404)

        @self.app.route('/api/collectors/', methods=['POST'])
        @consumes('application/json')
        @produces('application/json')
        def add_collector():

            coll_id = enhancer.git_collectors.add_collector(request.json)

            if coll_id:
                return json_response(coll_id)

            return make_response('', 400)

        @self.app.route('/api/collectors/<string:coll_id>/', methods=['DELETE'])
        def remove_collector(coll_id):

            enhancer.git_collectors.remove_collector(coll_id)

            return make_response('', 200)

        # Get information about Git Enhancer
        @self.app.route('/api/', methods=['GET'])
        @produces('application/json')
        def api():
            return jsonify(Name=config.GE_LONGNAME,
                           Version=config.GE_VERSION,
                           Status='OK')

        # Get Git projects
        @self.app.route('/api/projects/', methods=['GET'])
        @produces('application/json')
        def api_get_projects():

            return json_response(enhancer.get_projects())

        # Get specific gitlab project
        @self.app.route('/api/projects/<string:rid>/', methods=['GET'])
        @produces('application/json')
        def api_project(rid):

            project = enhancer.get_project(rid)
            if project:
                return json_response(project)
            return make_response('', 404)

        # Get owner about specific gitlab project
        @self.app.route('/api/projects/<string:rid>/owner/', methods=['GET'])
        @produces('application/json')
        def api_project_owner(rid):

            owner = enhancer.get_project_owner(rid)
            if owner:
                return json_response(owner)
            return make_response('', 404)

        # Get milestone about specific gitlab project
        @self.app.route('/api/projects/<string:pid>/milestones/',
                        methods=['GET'])
        @produces('application/json')
        def api_project_milestones(pid):

            milestones = enhancer.get_project_milestones(pid)
            if milestones:
                return json_response(milestones)
            return make_response('', 404)

        # Get specific milestone about specific gitlab project
        @self.app.route('/api/projects/<string:pid>/milestones/<int:mid>/',
                        methods=['GET'])
        @produces('application/json')
        def api_project_milestone(pid, mid):

            milestone = enhancer.get_project_milestone(pid, mid)
            if milestone:
                return json_response(milestone)
            return make_response('', 404)

        # # default = [true|false] for get default branch only
        # Get branches about specific gitlab project
        # It is possible only get the default branch
        @self.app.route('/api/projects/<string:pid>/branches/', methods=['GET'])
        @produces('application/json')
        def api_project_branches(pid):

            default = request.args.get('default', 'false')
            if default != 'false' and default != 'true':
                return make_response("400: default parameter must be true or "
                                     "false", 400)
            default = json.loads(default)

            return json_response(enhancer.get_project_branches(pid, default))

        # Get specific branch about specific gitlab project
        @self.app.route('/api/projects/<string:pid>/branches/<string:bid>/',
                        methods=['GET'])
        @produces('application/json')
        def api_project_branch(pid, bid):

            branch = enhancer.get_project_branch(pid, bid)
            if branch:
                return json_response(branch)
            return make_response('', 404)

        # Get contributors of specific branch about specific gitlab project
        @self.app.route('/api/projects/<string:pid>/branches/<string:bid>/'
                        'contributors/', methods=['GET'])
        @produces('application/json')
        def api_project_branch_contributors(pid, bid):

            users_id = enhancer.get_project_branch_contributors(pid, bid)

            if users_id:

                contributors = list()
                for user_id in users_id:
                    contributors.append(enhancer.get_user(user_id))
                return json_response(contributors)

            return make_response()

        # Query Params:
        # # uid = user identifier
        # # start_time = time (start) filter
        # # end_time = time (end) filter
        # Get commits of specific branch about specific gitlab project
        # It is possible filter by user with gitlab uid
        # It is possible filter by range (time)
        @self.app.route('/api/projects/<string:pid>/branches/<string:bid>/'
                        'commits/', methods=['GET'])
        @produces('application/json')
        def api_project_branch_commits(pid, bid):

            user = request.args.get('uid', None)

            if user is not None:
                try:
                    user = int(user)
                except ValueError:
                    return make_response("400: uid parameter is not an integer "
                                         "(user identifier)", 400)

            t_window = check_time_window(request.args)

            if t_window['st_time'] == 'Error' or t_window['en_time'] == 'Error':
                return make_response("400: start_time or end_time is bad "
                                     "format", 400)

            commits = enhancer.get_project_branch_commits(pid, bid, user,
                                                          t_window)

            if commits:
                return json_response(commits)
            return make_response('', 404)

        # Query Params:
        # # uid = user identifier
        # # start_time = time (start) filter
        # # end_time = time (end) filter
        # Get commits about specific gitlab project
        # It is possible filter by user with gitlab uid
        # It is possible filter by range (time)
        @self.app.route('/api/projects/<string:pid>/commits/', methods=['GET'])
        @produces('application/json')
        def api_project_commits(pid):

            user = request.args.get('uid', None)

            if user is not None:
                try:
                    user = int(user)
                except ValueError:
                    return make_response("400: uid parameter is not an integer "
                                         "(user identifier)", 400)

            t_window = check_time_window(request.args)

            if t_window['st_time'] == 'Error' or t_window['en_time'] == 'Error':
                return make_response("400: start_time or end_time is bad "
                                     "format", 400)

            commits = enhancer.get_project_commits(pid, user, t_window)
            if commits:
                return json_response(commits)
            return make_response('', 404)

        # Get specific commit about specific gitlab project
        @self.app.route('/api/projects/<string:pid>/commits/<string:cid>/',
                        methods=['GET'])
        @produces('application/json')
        def api_project_commit(pid, cid):

            commit = enhancer.get_project_commit(pid, cid)

            if commit:
                return json_response(commit)

            return make_response('', 404)

        # Query Params:
        # # state = [opened, closed, merged]
        # Get merge requests about specific gitlab project
        # It is possible filter by state
        @self.app.route('/api/projects/<string:pid>/merge_requests/',
                        methods=['GET'])
        @produces('application/json')
        def api_project_requests(pid):

            mrstate = request.args.get('state', 'all')

            if mrstate is not 'all':
                if mrstate is not 'opened' and \
                                mrstate is not 'closed' and \
                                mrstate is not 'merged':

                    return make_response("400: state parameter is not a valid "
                                         "state (opened|closed|merged|all)",
                                         400)

            return json_response(enhancer.get_project_requests(pid, mrstate))

        # Get specific merge request about specific gitlab project
        @self.app.route('/api/projects/<string:pid>/merge_requests/<int:mrid>/',
                        methods=['GET'])
        @produces('application/json')
        def api_project_request(pid, mrid):

            return json_response(enhancer.get_project_request(pid, mrid))

        # Get changes of specific merge request about specific gitlab project
        @self.app.route('/api/projects/<string:pid>/merge_requests/<int:mrid>/'
                        'changes/', methods=['GET'])
        @produces('application/json')
        def api_project_request_changes(pid, mrid):

            return json_response(enhancer.get_project_request_changes(pid,
                                                                      mrid))

        # Get contributors about specific gitlab project
        @self.app.route('/api/projects/<string:pid>/contributors/',
                        methods=['GET'])
        @produces('application/json')
        def api_project_contributors(pid):

            return json_response(enhancer.get_project_contributors(pid))

        # Get gitlab users
        @self.app.route('/api/users/', methods=['GET'])
        @produces('application/json')
        def api_users():

            return json_response(enhancer.get_users())

        # Get specific gitlab user
        @self.app.route('/api/users/<string:uid>/', methods=['GET'])
        @produces('application/json')
        def api_user(uid):

            user = enhancer.get_user(uid)
            if user:
                return json_response(user)
            return make_response('', 404)

        # Query Params:
        # # relation = [contributor only in default branch, owner]
        # Get projects about specific gitlab user
        # It is possible filter by relation between user and project
        @self.app.route('/api/users/<int:uid>/projects/', methods=['GET'])
        @produces('application/json')
        def api_user_projects(uid):

            relation = request.args.get('relation', 'contributor')
            if relation != 'contributor' and relation != 'owner':
                return make_response("400: relation parameter is not a valid"
                                     "relation (contributor|owner)", 400)

            return json_response(enhancer.get_user_projects(uid, relation))

        # Get Gitlab groups
        @self.app.route('/api/groups/', methods=['GET'])
        @produces('application/json')
        def api_groups():

            return json_response(enhancer.get_groups())

        # Get specific gitlab groups
        @self.app.route('/api/groups/<int:gid>/', methods=['GET'])
        @produces('application/json')
        def api_group(gid):

            return json_response(enhancer.get_group(gid))

        # Query Params:
        # # relation = [contributor only in default branch, owner]
        # Get projects about specific gitlab group
        # It is possible filter by relation between user and project
        @self.app.route('/api/groups/<int:gid>/projects/', methods=['GET'])
        @produces('application/json')
        def api_group_projects(gid):

            relation = request.args.get('relation', 'contributor')

            if relation != 'contributor' and relation != 'owner':
                return make_response("400: relation parameter is not a valid "
                                     "relation (contributor|owner)", 400)

            return json_response(enhancer.get_group_projects(gid, relation))

    def start(self):

        logging.info('Starting Enhancer.')
        self.enhancer.start()
        logging.info('Deploying API.')
        self.app.run(self.ip, self.port)


#######################################
# Functions to help another functions #
#######################################

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
        end_time = long(datetime.now().strftime("%s")) * 1000
    if start_time is None:
        start_time = long(0)
    if start_time > end_time:
        start_time = 'Error'
        end_time = 'Error'
    return {
        'st_time': start_time,
        'en_time': end_time
    }


###########################
# Util functions for http #
###########################

def check_url(url):
    try:
        return validators.url(url)
    except validators.ValidationFailure:
        return False


def json_response(json_object, state=200):
    obj = json_object
    if isinstance(obj, set):
        obj = list(obj)
    r = make_response(json.dumps(obj), state)
    r.headers['Content-Type'] = 'application/json'
    return r


def generate_json_error():
    return json_response({
        "Error": "JSON at request body is bad format."
    }, 422)
