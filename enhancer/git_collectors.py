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
        if collector:
            collector['id'] = c_id

        return collector

    def get_collectors(self):

        """ This method returns a list of the GitCollectors that are been
        used by service.

        :return: List of GitCollectors
        """

        collector_list = list()

        for key in self.r_server.keys('collector:*'):

            collector = self.r_server.hgetall(key)
            collector['id'] = key.split(':')[1]
            collector_list.append(collector)

        return collector_list

    def add_collector(self, params):

        """ This method allow to add a GitCollector to the services.

        :param params: GitCollector access information
        :return: GitCollector id or None if params are not right.
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

            return c_id

        return None

    def remove_collector(self, c_id):

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

        for key in self.r_server.keys('collector:*'):

            collector_id = key.split(':')[1]
            for repository in self._request_to_collector('/api/repositories',
                                                         collector_id):

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

        path = '/api/repositories/%s/commits' % repository.get('id')
        collector_id = repository.get('collector')

        commits = list()
        for commit_id in self._request_to_collector(path, collector_id):

            commits.append(self.get_commit(repository, commit_id))

        return commits

    def get_commit(self, repository, cid):

        """ This method return an specific commit from a repository

        :param repository: information relative to a repository
        :param cid: commit identifier
        :return: commit information from a repository
        """

        path = '/api/repositories/%s/commits/%s' % (repository.get('id'), cid)

        return self._request_to_collector(path, repository.get('collector'))

    def get_commiters(self, repository):

        """
        Returns a commiters list of a repository.

        :param repository: information relative to a repository
        :return: commiters list of a repository.
        """

        path = '/api/repositories/%s/contributors' % repository.get('id')
        commiters = list()

        for id in self._request_to_collector(path, repository.get('collector')):
            commiters.append(self._get_commiter(repository, id))

        return commiters

    def _get_commiter(self, repository, commiter_id):

        """
        Returns commiter information
        :param repository: information relative to repository
        :param commiter_id:
        :return: commiter information
        """

        path = '/api/contributors/%s' % commiter_id

        return self._request_to_collector(path, repository.get('collector'))

    def get_commiter(self, email):
        """
        Returns commiter information regardless its repository
        :param commiter_id:
        :return: commiter information
        """
        pass

    def get_branches(self, repository):

        """
        Returns a branches list of a repository
        :param repository:  information relative to a repository
        :return: branches list of a repository
        """
        # TODO:
        path = '/api/repositories/%s/branches' % repository.get('id')
        collector_id = repository.get('collector')
        branches = list()
        for id in self._request_to_collector(path, collector_id):

            branch = self.get_branch(repository, id)
            if branch:
                branches.append(branch)

        return branches

    def get_branch(self, repository, b_id):

        """
        Returns branch information
        :param repository: information relative to repository
        :param b_id: branch identifier
        :return: branch information from repository
        """
        # "Name", "contributors" = []
        path = '/api/repositories/%s/branches/%s' % (repository.get('id'), b_id)
        collector_id = repository.get('collector')

        branch = self._request_to_collector(path, collector_id)

        if branch and not branch.get('Error'):

            contributors = list()
            for contributor in eval(branch.pop('contributors')):

                commiter = self._get_commiter(repository, contributor)
                contributors.append(commiter.get('email'))
            branch['contributors'] = contributors
            branch['id'] = b_id

            return branch
        return None


    def get_branches_commits(self, repository, b_id):

        path = '/api/repositories/%s/branches/%s/commits' % (
            repository.get('id'), b_id)
        collector_id = repository.get('collector')

        commits = list()
        for commit_id in self._request_to_collector(path, collector_id):
            commits.append(self.get_commit(repository, commit_id))

        return commits

    def _request_to_collector(self, path, collector_id):

        collector = self.r_server.hgetall('collector:%s' %
                                          collector_id)

        if collector:
            headers = dict()
            headers['Accept'] = 'application/json'
            headers['Content-Type'] = 'application/json'

            if collector.get('security'):
                headers['X-GC-PWD'] = '%s' % collector.get('password')

            return requests.get('%s%s' % (collector.get('url'), path),
                                headers=headers).json()
        return None