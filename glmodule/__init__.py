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

from glmodule import glredis
import redis

__author__ = 'Alejandro F. Carrera'


class GlEnhancer(object):

    """GitLab Enhancer Class

    Args:
        config (dict): configuration from settings.py

    Attributes:
        cfg (dict): same as config arg
        redis (Redis): Redis object from redis module
        rd_host (string): url for Redis Host
    """

    def __init__(self, config):
        self.cfg = config
        self.git = None
        self.redis = None
        self.rd_host = "%s:%d" % (
            self.cfg.get("REDIS_IP"),
            self.cfg.get("REDIS_PORT")
        )
        self.connect_redis()

    @property
    def config(self):
        return self.cfg

# REDIS CONNECTION

    def test_connection_redis(self):

        if self.redis is not None:
            try:
                self.redis.client_list()
                return True
            except Exception as e:
                return False

    def connect_redis(self):

        # Create redis object and connect
        __available = False
        self.redis = redis.ConnectionPool(
            host=self.cfg.get("REDIS_IP"),
            port=self.cfg.get("REDIS_PORT"),
            db=self.cfg.get("REDIS_DB"),
            password=self.cfg.get("REDIS_PASS")
        )
        self.redis = redis.Redis(connection_pool=self.redis)

# GITLAB (REDIS) ENHANCER API REST

    def api_ping(self):
        return {
            "api": "ok",
            "redis": 'ok' if self.test_connection_redis() is True else 'Not connected'
        }

    def api_projects(self):
        if self.test_connection_redis():
            return glredis.get_projects(self.redis)
        else:
            return False

    def api_project(self, project_id):
        if self.test_connection_redis():
            return glredis.get_project(self.redis, project_id)
        else:
            return False

    def api_project_owner(self, project_id):
        if self.test_connection_redis():
            return glredis.get_project_owner(self.redis, project_id)
        else:
            return False

    def api_project_milestones(self, project_id):
        if self.test_connection_redis():
            return glredis.get_project_milestones(self.redis, project_id)
        else:
            return False

    def api_project_milestone(self, project_id, milestone_id):
        if self.test_connection_redis():
            return glredis.get_project_milestone(self.redis, project_id, milestone_id)
        else:
            return False

    def api_project_branches(self, project_id, default_flag):
        if self.test_connection_redis():
            return glredis.get_project_branches(self.redis, project_id, default_flag)
        else:
            return False

    def api_project_branch(self, project_id, branch_name):
        if self.test_connection_redis():
            return glredis.get_project_branch(self.redis, project_id, branch_name)
        else:
            return False

    def api_project_branch_contributors(self, project_id, branch_name, t_window):
        if self.test_connection_redis():
            return glredis.get_project_branch_contributors(self.redis, project_id, branch_name, t_window)
        else:
            return False

    def api_project_branch_commits(self, project_id, branch_name, user_id, t_window):
        if self.test_connection_redis():
            return glredis.get_project_branch_commits(self.redis, project_id, branch_name, user_id, t_window)
        else:
            return False

    def api_project_commits(self, project_id, user_id, t_window):
        if self.test_connection_redis():
            return glredis.get_project_commits(self.redis, project_id, user_id, t_window)
        else:
            return False

    def api_project_commit(self, project_id, commit_id):
        if self.test_connection_redis():
            return glredis.get_project_commit(self.redis, project_id, commit_id)
        else:
            return False

    def api_project_commit_diff(self, project_id, commit_id):
        if self.test_connection_redis():
            return glredis.get_project_commit_diff(self.redis, project_id, commit_id)
        else:
            return False

    def api_project_requests(self, project_id, request_state):
        if self.test_connection_redis():
            return glredis.get_project_requests(self.redis, project_id, request_state)
        else:
            return False

    def api_project_request(self, project_id, request_id):
        if self.test_connection_redis():
            return glredis.get_project_request(self.redis, project_id, request_id)
        else:
            return False

    def api_project_request_changes(self, project_id, request_id):
        if self.test_connection_redis():
            return glredis.get_project_request_changes(self.redis, project_id, request_id)
        else:
            return False

    def api_project_contributors(self, project_id, t_window):
        if self.test_connection_redis():
            return glredis.get_project_contributors(self.redis, project_id, t_window)
        else:
            return False

    def api_users(self):
        if self.test_connection_redis():
            return glredis.get_users(self.redis)
        else:
            return False

    def api_user(self, user_id):
        if self.test_connection_redis():
            return glredis.get_user(self.redis, user_id)
        else:
            return False

    def api_user_projects(self, user_id, relation_type, t_window):
        if self.test_connection_redis():
            return glredis.get_user_projects(self.redis, user_id, relation_type, t_window)
        else:
            return False

    def api_groups(self):
        if self.test_connection_redis():
            return glredis.get_groups(self.redis)
        else:
            return False

    def api_group(self, group_id):
        if self.test_connection_redis():
            return glredis.get_group(self.redis, group_id)
        else:
            return False

    def api_group_projects(self, group_id, relation_type, t_window):
        if self.test_connection_redis():
            return glredis.get_group_projects(self.redis, group_id, relation_type, t_window)
        else:
            return False
