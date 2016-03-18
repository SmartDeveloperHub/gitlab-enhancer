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
from threading import Timer

import redis

from grm_collectors import GitLabCollector

__author__ = 'Ignacio Molina Cuquerella'


class Enhancer:

    """
        Enhancer class

        This class will mix the information gathered by Git Collector service
        and the GitLab collector to enrich the Git Protocol information.

        Args:
            config (setting.py): configuration from settings.py
    """

    def __init__(self, config):

        self.gc_url = 'http://%s:%s' % (config.GIT_IP, config.GIT_PORT)
        self.schedule = config.GE_SCHEDULE
        self.redis_config = {'ip': config.REDIS_IP, 'port': config.REDIS_PORT,
                            'password': config.REDIS_PASS}

        # redis instances
        self.redis_instance = dict()
        self.redis_instance['projects'] = self._redis_create_pool(config.REDIS_DB_PROJ)
        self.redis_instance['users'] = self._redis_create_pool(config.REDIS_DB_USER)
        self.redis_instance['groups'] = self._redis_create_pool(config.REDIS_DB_GROUP)
        self.redis_instance['merge_requests'] = self._redis_create_pool(config.REDIS_DB_MERGE)

        # GitLab Collector instance
        collector_url = '%s://%s' % (config.GITLAB_PROT, config.GITLAB_IP)
        self.collector = GitLabCollector(url=collector_url,
                                         r_servers= self.redis_instance,
                                         token=config.GITLAB_TOKEN,
                                         ssl=config.GITLAB_VER_SSL)

    def _redis_create_pool(self, database):
        """
            Method that creates a redis instance

        :param database (int): name of the database
        :return: redis instance connection
        """

        connection_pool = redis.ConnectionPool(
            host=self.redis_config.get('ip'),
            port=self.redis_config.get('port'),
            db=database,
            password=self.redis_config.get('password')
        )

        redis_pool = redis.Redis(connection_pool=connection_pool)

        try:
            redis_pool.client_list()
            return redis_pool
        except Exception as e:
            raise EnvironmentError("- Configuration is not valid or Redis is not online")


    def start(self):

        """ Starts Collector and set a scheduler for next activations of the
        collector.
        """

        logging.info('Started GitLab Collector')
        self.collector.collect()
        logging.info('Finish GitLab Collector')
        Timer(self.schedule, self.start).start()

    def get_projects(self):

        """ Get Projects
            :return: Projects (List)
        """

        r_projects = self.redis_instance.get('projects')
        projects_id = r_projects.keys('project:*')

        projects = list()

        for id in projects_id:
            projects.append(json.loads(r_projects.get(id)))

        return projects

    def get_project(self, p_id):

        """ Get Project
        :param p_id: Project Identifier (int)
        :return: Project (Object)
        """
        # Repository fields
        # "first_commit_at", "archived", "last_activity_at", "name",
        # "contributors", "tags", "created_at", "default_branch",
        # "id", "http_url_to_repo", "web_url", "owner", "last_commit_at",
        # "public", "avatar_url"
        pass

    def get_project_owner(self, p_id):

        """ Get Project's Owner
        :param p_id: Project Identifier (int)
        :return: Owner (User Object | Group Object)
        """

        return None

    def get_users(self):

        """ Get Users
        :return: Users (List)
        """

        return list()

    def get_user(self, u_id):

        """ Get User
        :param u_id: User or Committer identifier
        :return: User (Object)
        """

        # User fields
        # "username", "first_commit_at", "name", "created_at",
        # "email", "state", "avatar_url", "last_commit_at", "id",
        # "external"

        # Commiter fields
        # "first_commit_at", "email", "last_commit_at", "id",
        # "external"

        return None

    def get_user_projects(self, u_id, relation):

        """ Get User's Projects
        :param u_id: User Identifier (int)
        :param relation: Relation between User-Project
        :return: Projects (List)
        """

        return list()

    def get_project_branches(self, p_id, default):

        """ Get Project's Branches
        :param p_id: Project Identifier (int)
        :param default: Filter by type (bool)
        :return: Branches (List)
        """

        return list()

    def get_project_branch(self, p_id, b_id):

        """ Get Project's Branch
        :param p_id: Project Identifier (int)
        :param b_id: Branch Identifier (string)
        :return: Branch (Object)
        """

        # Branch fields
        # "name", "created_at", "protected", "contributors",
        # "last_commit"

        return None

    def get_project_branch_contributors(self, p_id, b_id):

        """ Get Branch's Contributors
        :param p_id: Project Identifier (int)
        :param b_id: Branch Identifier (string)
        :return: Contributors (List)
        """

        return list()

    def get_project_branch_commits(self, p_id, b_id, u_id, t_window):

        """ Get Branch's Commits
        :param p_id: Project Identifier (int)
        :param b_id: Branch Identifier (string)
        :param u_id: Optional User Identifier (int)
        :param t_window: (Time Window) filter (Object)
        :return: Commits (List)
        """

        return list()

    def get_project_commits(self, p_id, u_id, t_window):

        """ Get Project's Commits
        :param p_id: Project Identifier (int)
        :param u_id: Optional User Identifier (int)
        :param t_window: (Time Window) filter (Object)
        :return: Commits (List)
        """

        return list()

    def get_project_commit(self, p_id, c_id):

        """ Get Project's Commit
        :param p_id: Project Identifier (int)
        :param c_id: Commit Identifier (sha)
        :return: Commit (Object)
        """

        # "lines_removed", "short_id", "author", "lines_added",
        # "created_at", "title", "parent_ids", "committed_date",
        # "message", "authored_date", "id"

        return None

    def get_project_milestones(self, p_id):

        """ Get Project's Milestones
        :param p_id: Project Identifier (int)
        :return: Milestones (List)
        """

        return list()

    def get_project_milestone(self, p_id, m_id):

        """ Get Project's Milestone
        :param p_id: Project Identifier (int)
        :param m_id: Milestone Identifier (int)
        :return: Milestone (Object)
        """

        return None

    def get_project_requests(self, p_id, r_state):

        """ Get Project's Merge Requests
        :param p_id: Project Identifier (int)
        :param r_state: Optional Type Identifier (string)
        :return: Merge Requests (List)
        """

        return list()

    def get_project_request(self, p_id, r_id):

        """ Get Project's Merge Request
        :param p_id: Project Identifier (int)
        :param r_id: Merge Request Identifier (int)
        :return: Merge Request (Object)
        """

        return None

    def get_project_request_changes(self, p_id, r_id):

        """ Get Merge Request's Changes
        :param p_id: Project Identifier (int)
        :param r_id: Merge Request Identifier (int)
        :return: Changes (List)
        """

        return list()

    def get_project_contributors(self, p_id):

        """ Get Project's Contributors
        :param p_id: Project Identifier (int)
        :return: Contributors (List)
        """

        return list()

    def get_groups(self):

        """ Get Groups
        :return: Groups (List)
        """

        return list()

    def get_group(self, g_id):

        """ Get Group
        :param group_id: Group Identifier (int)
        :return: Group (Object)
        """

        return None

    def get_group_projects(self, g_id, relation):

        """ Get Group's Projects
        :param g_id: Group Identifier (int)
        :param relation: Relation between User-Project
        :return: Projects (List)
        """

        return list()