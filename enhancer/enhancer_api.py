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
from datetime import datetime

import logging
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

            # r = requests.get('%s/api/repositories' % self.git_url,
            #                   headers=request.headers)
            # return make_response(r.text, r.status_code, r.headers.items())
            return make_response(json.dumps(enhancer.get_projects()))
            # return redirect('%s/api/repositories' % self.git_url, code=307)

        # Get specific gitlab project
        @self.app.route('/api/projects/<int:pid>/', methods=['GET'])
        @produces('application/json')
        def api_project(pid):

            return make_response(json.dumps(
                enhancer.get_project(pid)
            ))

        # Get owner about specific gitlab project
        @self.app.route('/api/projects/<int:pid>/owner/', methods=['GET'])
        @produces('application/json')
        def api_project_owner(pid):

            return make_response(json.dumps(
                enhancer.get_project_owner(pid)
            ))

        # Get milestone about specific gitlab project
        @self.app.route('/api/projects/<int:pid>/milestones/', methods=['GET'])
        @produces('application/json')
        def api_project_milestones(pid):

            return make_response(json.dumps(
                enhancer.get_project_milestones(pid)
            ))

        # Get specific milestone about specific gitlab project
        @self.app.route('/api/projects/<int:pid>/milestones/<int:mid>/',
                        methods=['GET'])
        @produces('application/json')
        def api_project_milestone(pid, mid):

            return make_response(json.dumps(
                enhancer.get_project_milestone(pid, mid)
            ))

        # # default = [true|false] for get default branch only
        # Get branches about specific gitlab project
        # It is possible only get the default branch
        @self.app.route('/api/projects/<int:pid>/branches/', methods=['GET'])
        @produces('application/json')
        def api_project_branches(pid):

            default = request.args.get('default', 'false')
            if default != 'false' and default != 'true':
                return make_response("400: default parameter must be true or "
                                     "false", 400)
            return make_response(json.dumps(
                enhancer.get_project_branches(pid, default)
            ))

        # Get specific branch about specific gitlab project
        @self.app.route('/api/projects/<int:pid>/branches/<string:bid>/',
                        methods=['GET'])
        @produces('application/json')
        def api_project_branch(pid, bid):

            return make_response(json.dumps(
                enhancer.get_project_branch(pid, bid)
            ))

        # Get contributors of specific branch about specific gitlab project
        @self.app.route('/api/projects/<int:pid>/branches/<string:bid>/'
                        'contributors/', methods=['GET'])
        @produces('application/json')
        def api_project_branch_contributors(pid, bid):

            return make_response(json.dumps(
                enhancer.get_project_branch_contributors(pid, bid)
            ))

        # Query Params:
        # # uid = user identifier
        # # start_time = time (start) filter
        # # end_time = time (end) filter
        # Get commits of specific branch about specific gitlab project
        # It is possible filter by user with gitlab uid
        # It is possible filter by range (time)
        @self.app.route('/api/projects/<int:pid>/branches/<string:bid>/'
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

            return make_response(json.dumps(
                enhancer.get_project_branch_commits(pid, bid, user,
                                                         t_window)
            ))

        # Query Params:
        # # uid = user identifier
        # # start_time = time (start) filter
        # # end_time = time (end) filter
        # Get commits about specific gitlab project
        # It is possible filter by user with gitlab uid
        # It is possible filter by range (time)
        @self.app.route('/api/projects/<int:pid>/commits/', methods=['GET'])
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

            return make_response(json.dumps(
                enhancer.get_project_commits(pid, user, t_window)
            ))

        # Get specific commit about specific gitlab project
        @self.app.route('/api/projects/<int:pid>/commits/<string:cid>/',
                        methods=['GET'])
        @produces('application/json')
        def api_project_commit(pid, cid):

            return make_response(json.dumps(
                enhancer.get_project_commit(pid, cid)
            ))

        # Query Params:
        # # state = [opened, closed, merged]
        # Get merge requests about specific gitlab project
        # It is possible filter by state
        @self.app.route('/api/projects/<int:pid>/merge_requests/',
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

            return make_response(json.dumps(
                enhancer.get_project_requests(pid, mrstate)
            ))

        # Get specific merge request about specific gitlab project
        @self.app.route('/api/projects/<int:pid>/merge_requests/<int:mrid>/',
                        methods=['GET'])
        @produces('application/json')
        def api_project_request(pid, mrid):

            return make_response(json.dumps(
                enhancer.get_project_request(pid, mrid)
            ))

        # Get changes of specific merge request about specific gitlab project
        @self.app.route('/api/projects/<int:pid>/merge_requests/<int:mrid>/'
                        'changes/', methods=['GET'])
        @produces('application/json')
        def api_project_request_changes(pid, mrid):

            return make_response(json.dumps(
                enhancer.get_project_request_changes(pid, mrid)
            ))

        # Get contributors about specific gitlab project
        @self.app.route('/api/projects/<int:pid>/contributors/', methods=['GET'])
        @produces('application/json')
        def api_project_contributors(pid):

            return make_response(json.dumps(
                enhancer.get_project_contributors(pid)
            ))

        # Get gitlab users
        @self.app.route('/api/users/', methods=['GET'])
        @produces('application/json')
        def api_users():

            return make_response(json.dumps(
                enhancer.get_users()
            ))

        # Get specific gitlab user
        @self.app.route('/api/users/<string:uid>/', methods=['GET'])
        @produces('application/json')
        def api_user(uid):

            return make_response(json.dumps(
                enhancer.get_user(uid)
            ))

        # Query Params:
        # # relation = [contributor only in default branch, owner]
        # Get projects about specific gitlab user
        # It is possible filter by relation between user and project
        @self.app.route('/api/users/<string:uid>/projects/', methods=['GET'])
        @produces('application/json')
        def api_user_projects(uid):

            relation = request.args.get('relation', 'contributor')
            if relation != 'contributor' and relation != 'owner':
                return make_response("400: relation parameter is not a valid"
                                     "relation (contributor|owner)", 400)
            return make_response(json.dumps(
                enhancer.get_user_projects(uid, relation)
            ))

        # Get Gitlab groups
        @self.app.route('/api/groups/', methods=['GET'])
        @produces('application/json')
        def api_groups():

            return make_response(json.dumps(
                enhancer.get_groups()
            ))

        # Get specific gitlab groups
        @self.app.route('/api/groups/<int:gid>/', methods=['GET'])
        @produces('application/json')
        def api_group(gid):

            return make_response(json.dumps(
                enhancer.get_group(gid)
            ))

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

            return make_response(json.dumps(
                enhancer.get_group_projects(gid, relation)
            ))

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
