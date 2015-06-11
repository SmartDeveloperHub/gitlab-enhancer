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

__author__ = 'Alejandro F. Carrera'

from glmodule import glhook, glapi, glredis, glredispop
import gitlab
import redis
import time


class GlDrainer(object):
    def __init__(self, config):
        print " * Drainer Started"
        self.cfg = config
        self.git = None
        self.redis = None
        self.redis_status = False
        self.drainerHost = "%s://%s:%d/system" % (
            self.cfg.get('DRAINER_PROT', 'http'),
            self.cfg.get('DRAINER_IP', '127.0.0.1'),
            self.cfg.get('DRAINER_PORT', 8080)
        )
        self.hookHost = "%s://%s:%d/hook" % (
            self.cfg.get('DRAINER_PROT', 'http'),
            self.cfg.get('DRAINER_IP', '127.0.0.1'),
            self.cfg.get('DRAINER_PORT', 8080)
        )
        self.gitHost = "%s://%s:%d" % (
            self.cfg.get('GITLAB_PROT', 'http'),
            self.cfg.get('GITLAB_IP', '127.0.0.1'),
            self.cfg.get('GITLAB_PORT', 80)
        )
        self.connect_gitlab()
        self.connect_redis()

    @property
    def config(self):
        return self.cfg

# GITLAB HOOKS

    def hook_system(self, response_hook):
        glhook.hook_system(response_hook)

    def hook_specific(self, response_hook):
        glhook.hook_specific(response_hook)

# GITLAB CONNECTION

    def link_gitlab(self):
        self.git.addsystemhook(url=self.drainerHost)

    def link_repositories(self):

        # Get Git projects (visible to admin)
        __projects = self.git.getprojects()
        for e in __projects:

            # Check Hooks and Link with Git Projects
            __hooks = self.git.getprojecthooks(project_id=e['id'])
            __linked = False
            for j in __hooks:
                if j['url'] == self.hookHost:
                    __linked = True
            if not __linked:
                self.git.addprojecthook(project_id=e['id'], url=self.hookHost)

    def connect_gitlab(self):

        # Create git object and connect
        __linked = False
        __available = False
        __user = self.cfg.get('GITLAB_USER', 'user')
        __pwd = self.cfg.get('GITLAB_PASS', 'password')
        self.git = gitlab.Gitlab(host=self.gitHost)
        try:
            self.git.login(user=__user, password=__pwd)
            __available = True
        except Exception as e:
            self.git = None

        # Check Hooks and Link with Git Admin Area
        if __available:
            __hooks = self.git.getsystemhooks()
            for e in __hooks:
                if e['url'] == self.drainerHost:
                    __linked = True
            if not __linked:
                self.link_gitlab()

            # Check Projects instead of admin area
            self.link_repositories()

# REDIS CONNECTION

    def populate_redis(self):
        localtime = time.asctime(time.localtime(time.time()))
        print " * [REDIS] Start time :", localtime
        glredispop.populate_redis_users(self, self.redis)
        glredispop.populate_redis_groups(self, self.redis)
        glredispop.populate_redis_projects(self, self.redis)
        glredispop.populate_redis_branches(self, self.redis)
        glredispop.populate_redis_commits(self, self.redis)
        localtime = time.asctime(time.localtime(time.time()))
        self.redis_status = True
        print " * [REDIS] End time :", localtime

    def connect_redis(self):

        # Create redis object and connect
        __available = False
        self.redis = redis.ConnectionPool(
            host=self.cfg.get('REDIS_IP', '127.0.0.1'),
            port=self.cfg.get('REDIS_PORT', 6379),
            db=self.cfg.get('REDIS_DB', 0)
        )
        self.redis = redis.Redis(connection_pool=self.redis)
        try:
            self.redis.client_list()
            __available = True
        except redis.ConnectionError:
            self.redis = None

        # Check database is empty
        if __available:
            if self.redis.dbsize() == 0:
                print " * [REDIS] Database empty detected!"
                print " * [REDIS] Cold Init - Started."
                if self.git is None:
                    print " * [REDIS] Cold Init - Stopped."
                    self.redis = "non populated"
                else:
                    self.populate_redis()
                    print " * [REDIS] Cold Init - Finished."
            else:
                self.redis_status = True

# GITLAB (REDIS) ENHANCER API REST

    def api_projects(self):
        if self.redis_status is False:
            return glapi.get_projects(self.git)
        else:
            return glredis.get_projects(self.redis)

    def api_project(self, project_id):
        if self.redis_status is False:
            return glapi.get_project(self.git, project_id)
        else:
            return glredis.get_project(self.redis, project_id)

    def api_project_owner(self, project_id):
        if self.redis_status is False:
            return glapi.get_project_owner(self.git, project_id)
        else:
            return glredis.get_project_owner(self.redis, project_id)

    def api_project_milestones(self, project_id):
        if self.redis_status is False:
            return glapi.get_project_milestones(self.git, project_id)
        else:
            return glredis.get_project_milestones(self.redis, project_id)

    def api_project_milestone(self, project_id, milestone_id):
        if self.redis_status is False:
            return glapi.get_project_milestone(self.git, project_id, milestone_id)
        else:
            return glredis.get_project_milestone(self.redis, project_id, milestone_id)

    def api_project_branches(self, project_id, default_flag):
        if self.redis_status is False:
            return glapi.get_project_branches(
                self.git, project_id, default_flag)
        else:
            return glredis.get_project_branches(
                self.redis, project_id, default_flag)

    def api_project_branch(self, project_id, branch_name):
        if self.redis_status is False:
            return glapi.get_project_branch(
                self.git, project_id, branch_name)
        else:
            return glredis.get_project_branch(
                self.redis, project_id, branch_name)

    def api_project_branch_contributors(self, project_id, branch_name, t_window):
        if self.redis_status is False:
            return glapi.get_project_branch_contributors(
                self.git, project_id, branch_name, t_window)
        else:
            return glredis.get_project_branch_contributors(
                self.redis, project_id, branch_name, t_window)

    def api_project_branch_commits(self, project_id, branch_name, user_id, t_window):
        if self.redis_status is False:
            return glapi.get_project_branch_commits(
                self.git, project_id, branch_name, user_id, t_window)
        else:
            return glredis.get_project_branch_commits(
                self.redis, project_id, branch_name, user_id, t_window)

    def api_project_commits(self, project_id, user_id, t_window):
        if self.redis_status is False:
            return glapi.get_project_commits(
                self.git, project_id, user_id, t_window)
        else:
            return glredis.get_project_commits(
                self.redis, project_id, user_id, t_window)

    def api_project_commit(self, project_id, commit_id):
        if self.redis_status is False:
            return glapi.get_project_commit(
                self.git, project_id, commit_id)
        else:
            return glredis.get_project_commit(
                self.redis, project_id, commit_id)

    def api_project_commit_diff(self, project_id, commit_id):
        if self.redis_status is False:
            return glapi.get_project_commit_diff(
                self.git, project_id, commit_id)
        else:
            return glredis.get_project_commit_diff(
                self.redis, project_id, commit_id)

    def api_project_requests(self, project_id, request_state):
        if self.redis_status is False:
            return glapi.get_project_requests(self.git, project_id, request_state)
        else:
            return glredis.get_project_requests(self.redis, project_id, request_state)

    def api_project_request(self, project_id, request_id):
        if self.redis_status is False:
            return glapi.get_project_request(self.git, project_id, request_id)
        else:
            return glredis.get_project_request(self.redis, project_id, request_id)

    def api_project_request_changes(self, project_id, request_id):
        if self.redis_status is False:
            return glapi.get_project_request_changes(self.git, project_id, request_id)
        else:
            return glredis.get_project_request_changes(self.redis, project_id, request_id)

    def api_project_file_tree(self, project_id, view, branch_name, path):
        return glapi.get_project_file_tree(self.git, project_id, view, branch_name, path)

    def api_project_contributors(self, project_id, t_window):
        if self.redis_status is False:
            return glapi.get_project_contributors(self.git, project_id, t_window)
        else:
            return glredis.get_project_contributors(self.redis, project_id, t_window)

    def api_users(self):
        if self.redis_status is False:
            return glapi.get_users(self.git)
        else:
            return glredis.get_users(self.redis)

    def api_user(self, user_id):
        if self.redis_status is False:
            return glapi.get_user(self.git, user_id)
        else:
            return glredis.get_user(self.redis, user_id)

    def api_user_projects(self, user_id, relation_type, t_window):
        if self.redis_status is False:
            return glapi.get_user_projects(self.git, user_id, relation_type, t_window)
        else:
            return glredis.get_user_projects(self.redis, user_id, relation_type, t_window)

    def api_groups(self):
        if self.redis_status is False:
            return glapi.get_groups(self.git)
        else:
            return glredis.get_groups(self.redis)

    def api_group(self, group_id):
        if self.redis_status is False:
            return glapi.get_group(self.git, group_id)
        else:
            return glredis.get_group(self.redis, group_id)

    def api_group_projects(self, group_id, relation_type, t_window):
        if self.redis_status is False:
            return glapi.get_group_projects(self.git, group_id, relation_type, t_window)
        else:
            return glredis.get_group_projects(self.redis, group_id, relation_type, t_window)

    def api_project_commits_information(self, project_id, branch_name):
        return glapi.get_project_commits_information(self.git, project_id, branch_name)