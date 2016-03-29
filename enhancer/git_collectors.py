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
import base64
import requests


class GitCollectorsManager(object):

    """
        GitCollectorManager class.

        Class for manage all the git collector instances.

        Args:
            r_server: Redis instances where git collectors information are.
    """

    def __init__(self, r_server):

        self.r_server = r_server

    def get_collector(self, c_id):

        """ This methods returns the settings of a collector with id.

        :param c_id: GitCollector id
        :return: information relative to the GitCollector.
        """

        collector = self.r_server.hgetall('collector:%s' % c_id)

        return collector

    def get_collectors(self):

        """ This method returns a list of the GitCollectors that are been
        used by service.

        :return: List of GitCollectors
        """

        collector_list = list()

        for collector in self.r_server.keys('collector:*'):
            collector_list.append(self.r_server.get(collector))

        return collector_list

    def add_collector(self, params):

        """ This method allow to add a GitCollector to the services.

        :param params: GitCollector access information
        :return: return GitCollector id or None if params are not right.
        """

        if params.get('url'):

            url = params['url']
            security = False
            password = ''

            if params.get('security') and params.get('password'):

                security = True
                password = params.get('password')

            c_id = base64.b16encode(url)
            self.r_server.hset('collector:%s' % c_id, 'url', url)
            self.r_server.hset('collector:%s' % c_id, 'security', security)
            self.r_server.hset('collector:%s' % c_id, 'password', password)

            return id

        return None

    def delete_collector(self, c_id):

        """ This method remove the specified GitCollector from the services.

        :param c_id: GitCollector id.
        """

        if self.r_server.delete('collector:%s' % c_id):
            return True

        return False

    def get_repositories(self):

        """ This method return a list of repositories from all the
        GitCollectors.

        :return: list of repositories
        """

        repositories = list()

        for collector_id in self.r_server.keys('collector:*'):

            collector = self.r_server.hgetall(collector_id)
            headers = dict()
            headers['Accept'] = 'application/json',
            headers['Content-Type'] = 'application/json'

            if collector.get('security'):
                headers['X-GC-PWD'] = '%s' % collector.get('password')

            url = '%s/api/repositories' % collector.get('url')
            for repository in requests.get(url,
                                           headers=headers).json():
                repository['collector'] = collector_id
                repositories.append(repository)

        return repositories

    def get_repository(self, r_id):

        """ This methods return the information relative a repository that
        match r_id, with its GitCollector id.

        :param r_id: repository identifier.
        :return: repository information.
        """

        repositories = filter(lambda x: x.get('id') == r_id,
                              self.get_repositories())

        return repositories[0] if repositories else None

    def get_commits(self, repository):

        """ This method gets the repository commits.

        :param repository: information relative to a repository
        :return: list of the repository commits
        """
        # TODO:
        pass

    def get_commiters(self, repository):

        """
        Returns a commiters list of a repository.

        :param repository: information relative to a repository
        :return: commiters list of a repository.
        """
        # TODO:
        pass

    def _get_commiter(self, repository, commiter_id):

        """
        Returns commiter information
        :param repository: information relative to repository
        :param commiter_id:
        :return: commiter information
        """

        # "commits", "first_commit_at", "last_commit_at", "email",
        # TODO:
        pass