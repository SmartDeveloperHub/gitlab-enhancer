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

import logging
from threading import Timer

import redis

from git_collectors import GitCollectorsManager
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

        self.schedule = config.GE_SCHEDULE
        self.redis_config = {'ip': config.REDIS_IP,
                             'port': config.REDIS_PORT,
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
                                         r_servers=self.redis_instance,
                                         token=config.GITLAB_TOKEN,
                                         ssl=config.GITLAB_VER_SSL)
        self.git_collectors = GitCollectorsManager(self.redis_instance['git'])

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
        except Exception:
            raise EnvironmentError("- Configuration is not valid or Redis is "
                                   "not online")

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
        projects = list()

        for repository in self.git_collectors.get_repositories():

            project = self._get_project_from_repo(repository)
            if project:
                projects.append(project)

        return projects

    def get_project(self, r_id):

        """ Get Project
        :param r_id: repository identifier (int)
        :return: Project (Object)
        """
        # Repository fields
        # "first_commit_at", "archived", "last_activity_at", "name",
        # "contributors", "tags", "created_at", "default_branch",
        # "id", "http_url_to_repo", "web_url", "owner", "last_commit_at",
        # "public", "avatar_url"

        repository = self.git_collectors.get_repository(r_id)

        return self._get_project_from_repo(repository) if repository else None

    def _get_project_from_repo(self, repository):

        """ This method will search and find a project with the specified URL

        :param repository: repository information of the project sought
        :return: project information
        """

        r_projects = self.redis_instance.get('projects')

        projects = filter(lambda x:
                          x.get('http_url_to_repo') == repository.get('url'),
                          [r_projects.hgetall(p_id)
                           for p_id in r_projects.keys('project:*')])

        if projects:

            project = projects[0]
            commits = self.git_collectors.get_commits(repository)
            project['first_commit_at'] = commits[0].time
            project['last_commit_at'] = commits[-1].time

            project['contributors'] = self._get_contributors(repository)

            return project

        return None

    def _get_contributors(self, repository):

        """ This method will return a list of the repository contributors from
        GitCollector enriched with redis information

        :param repository: repository information
        :return:
        """

        commiter_list = self.git_collectors.get_commiters(repository)
        contributors = list()

        for commiter in commiter_list:
            contributors.append(self._get_contributor(commiter.email))

        return contributors

    def _get_contributor(self, email):

        """ This method return a user from redis with the specified email
        address.

        :param email: email used by the user.
        :return: user information from redis
        """

        r_users = self.redis_instance.get('users')

        users_id = filter(
            lambda x: email in r_users.smembers('emails:%s' % x),
            [user_emails_id.split(':')[0]
             for user_emails_id in r_users.keys('emails:*')])

        if users_id:

            return r_users.hgetall('user:%s' % users_id[0])

        return None

    def get_project_owner(self, r_id):

        """ Get Project's Owner
        :param r_id: Project Identifier (int)
        :return: Owner (User Object | Group Object)
        """

        return None

    def get_users(self):

        """ Get Users
        :return: Users (List)
        """
        # TODO:
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
        # TODO:
        return None

    def get_user_projects(self, u_id, relation):

        """ Get User's Projects
        :param u_id: User Identifier (int)
        :param relation: Relation between User-Project
        :return: Projects (List)
        """
        # TODO:
        return list()

    def get_project_branches(self, r_id, default):

        """ Get Project's Branches
        :param r_id: Project Identifier (int)
        :param default: Filter by type (bool)
        :return: Branches (List)
        """
        # TODO:
        return list()

    def get_project_branch(self, r_id, b_id):

        """ Get Project's Branch
        :param r_id: Project Identifier (int)
        :param b_id: Branch Identifier (string)
        :return: Branch (Object)
        """

        # Branch fields
        # "name", "created_at", "protected", "contributors",
        # "last_commit"
        # TODO:
        return None

    def get_project_branch_contributors(self, r_id, b_id):

        """ Get Branch's Contributors
        :param r_id: Project Identifier (int)
        :param b_id: Branch Identifier (string)
        :return: Contributors (List)
        """
        # TODO:
        return list()

    def get_project_branch_commits(self, r_id, b_id, u_id, t_window):

        """ Get Branch's Commits
        :param r_id: Project Identifier (int)
        :param b_id: Branch Identifier (string)
        :param u_id: Optional User Identifier (int)
        :param t_window: (Time Window) filter (Object)
        :return: Commits (List)
        """
        # TODO:
        return list()

    def get_project_commits(self, r_id, u_id, t_window):

        """ Get Project's Commits
        :param r_id: Project Identifier (int)
        :param u_id: Optional User Identifier (int)
        :param t_window: (Time Window) filter (Object)
        :return: Commits (List)
        """
        # TODO:
        return list()

    def get_project_commit(self, r_id, c_id):

        """ Get Project's Commit
        :param r_id: Project Identifier (int)
        :param c_id: Commit Identifier (sha)
        :return: Commit (Object)
        """

        # "lines_removed", "short_id", "author", "lines_added",
        # "created_at", "title", "parent_ids", "committed_date",
        # "message", "authored_date", "id"
        # TODO:
        return None

    def get_project_milestones(self, r_id):

        """ Get Project's Milestones
        :param r_id: Project Identifier (int)
        :return: Milestones (List)
        """
        # TODO:
        return list()

    def get_project_milestone(self, r_id, m_id):

        """ Get Project's Milestone
        :param r_id: Project Identifier (int)
        :param m_id: Milestone Identifier (int)
        :return: Milestone (Object)
        """
        # TODO:
        return None

    def get_project_requests(self, r_id, r_state):

        """ Get Project's Merge Requests
        :param r_id: Project Identifier (int)
        :param r_state: Optional Type Identifier (string)
        :return: Merge Requests (List)
        """
        # TODO:
        return list()

    def get_project_request(self, r_id, mr_id):

        """ Get Project's Merge Request
        :param r_id: Project Identifier (int)
        :param mr_id: Merge Request Identifier (int)
        :return: Merge Request (Object)
        """
        # TODO:
        return None

    def get_project_request_changes(self, r_id, mr_id):

        """ Get Merge Request's Changes
        :param r_id: Project Identifier (int)
        :param mr_id: Merge Request Identifier (int)
        :return: Changes (List)
        """
        # TODO:
        return list()

    def get_project_contributors(self, r_id):

        """ Get Project's Contributors
        :param r_id: Project Identifier (int)
        :return: Contributors (List)
        """
        # TODO:
        return list()

    def get_groups(self):

        """ Get Groups
        :return: Groups (List)
        """
        # TODO:
        return list()

    def get_group(self, g_id):

        """ Get Group
        :param g_id: Group Identifier (int)
        :return: Group (Object)
        """
        # TODO:
        return None

    def get_group_projects(self, g_id, relation):

        """ Get Group's Projects
        :param g_id: Group Identifier (int)
        :param relation: Relation between User-Project
        :return: Projects (List)
        """
        # TODO:
        return list()