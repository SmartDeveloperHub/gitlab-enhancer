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

from glapi import GlAPI

__author__ = 'Ignacio Molina Cuquerella'


class GRMCollector(object):

    """
        Abstract class GRM Collector

        This class will be used as common interface for each
        Git Repository Management (GRM) as GitLab, GitHub, etc. and therefore
        each GRM should inherit from this class.

        Args:
            url(String): url of the GRM API
            r_servers (dict): pool of redis instances
            username (String): credential id for the GRM account
            password (Optional[String]): credential password for the GRM account
            token (Optional[String]): credential token for the GRM account
            ssl(Optional[bool]): Whether SSL certificates should be validated.

        Attributes:
            url(String): url of the GRM API
            r_servers (dict): pool of redis instances
            username (String): credential id for the GRM account
            password (String): credential password for the GRM account
            token (Optional[String]): credential token for the GRM account
            ssl(Optional[bool]): Whether SSL certificates should be validated.
    """

    def __init__(self, url, r_servers, username=None, password=None, token=None,
                 ssl=False):

        self.url = url
        self.r_servers = r_servers
        self.username = username
        self.password = password
        self.token = token
        self.ssl = ssl
        self.api = self.connect()

    def connect(self):
        pass

    def collect(self):
        pass


class GitLabCollector(GRMCollector):

    def connect(self):

        gl = GlAPI(self.url, token=self.token, ssl=self.ssl)

        return gl

    def collect(self):

        self.update_projects()
        self.update_users()
        self.update_groups()

        # TODO: Methods not implemented on API
        # self.update_requests()
        # TODO: Methods not implemented
        # self.update_milestones()

    def update_projects(self):

        r_projects = self.r_servers.get('projects')

        # Get redis projects list
        old_projects = self._get_ids_list_from_redis(r_projects, 'project')
        current_projects = dict()

        for project in self.api.get_projects():
            if project.get('id'):
                current_projects[str(project.get('id'))] = project

        delete_list = old_projects.difference(set(current_projects))

        # Update current projects (current_projects_list -> redis)
        self._add_to_redis(r_projects, 'project', current_projects)
        # Delete removed projects from redis
        self._remove_from_redis(r_projects, 'project', delete_list)

    def update_users(self):

        r_users = self.r_servers.get('users')

        # Get redis users list
        old_users = self._get_ids_list_from_redis(r_users, 'user')
        current_users = dict()

        for user in self.api.get_users():

            if user.get('id'):
                current_users[str(user.get('id'))] = user

                emails = set()
                emails.add(user.get('email'))
                for email in self.api.get_users_emails_byUid(uid=user.get('id')):
                    emails.add(email.get('email'))
                r_users.sadd('emails:%s' % user['id'], *emails)

        delete_list = set(old_users).difference(set(current_users))

        # Update current users (current_users_list -> redis)
        self._add_to_redis(r_users, 'user', current_users)
        # Delete removed users from redis
        self._remove_from_redis(r_users, 'user', delete_list)
        self._remove_from_redis(r_users, 'emails', delete_list)

    def update_groups(self):

        r_groups = self.r_servers.get('groups')

        # Get redis projects list
        old_groups = self._get_ids_list_from_redis(r_groups, 'group')
        current_groups = dict()

        for group in self.api.get_groups():
            if group.get('id'):
                current_groups[str(group.get('id'))] = group

        delete_list = set(old_groups).difference(set(current_groups))

        # Update current groups (current_groups_list -> redis)
        self._add_to_redis(r_groups, 'group', current_groups)
        # Delete removed group from redis
        self._remove_from_redis(r_groups, 'group', delete_list)

    def update_requests(self):

        r_requests = self.r_servers.get('merge_requests')

        # Get redis requests list
        old_requests = self._get_ids_list_from_redis(r_requests, 'request')
        current_requests = dict()

        for request in self.api.get_projects_merge_requests_byId():
            if request.get('id'):
                current_requests[str(request.get('id'))] = request

        delete_list = set(old_requests).difference(set(current_requests))

        # Update current requests (current_requests_list -> redis)
        self._add_to_redis(r_requests, 'request', current_requests)
        # Delete removed requests from redis
        self._remove_from_redis(r_requests, 'request', delete_list)

    def _add_to_redis(self, r_server, key, list):

        for id in list:
            r_server.hmset('%s:%s' % (key, id), list.get(id))

    def _remove_from_redis(self, r_server, key, list):

        for id in list:
            r_server.delete('%s:%s' % (key, id))

    def _get_ids_list_from_redis(self, r_server, key):

        old_requests = set(
            map(
                lambda id: id.split(':')[1],
                r_server.keys('%s:*' % key)
            )
        )
        return old_requests
