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
import logging
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
        self.collectors = dict()

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
            collector = dict()
            collector['id'] = c_id
            collector['url'] = url
            collector['security'] = security
            collector['password'] = password
            self.collectors[c_id] = collector

            return c_id

        return None

    def get_notifications_config(self):

        notifications = list()

        for collector_id in self.collectors:
            api = self._request_to_collector('', collector_id)
            collector = api.get('Notifications')
            if collector:
                collector['instance'] = self.collectors[collector_id].get('url')
                notifications.append(collector)

        return notifications

    def get_repositories(self):

        """ This method return a list of repositories from all the
        GitCollectors.

        :return: list of repositories
        """

        repositories = list()

        for collector_id in self.collectors:

            for repository in self._request_to_collector('/repositories',
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

        repositories = filter(lambda repository: repository.get('id') == r_id,
                              self.get_repositories())

        return repositories[0] if repositories else None

    def get_commits(self, repository):

        """ This method gets the repository commits.

        :param repository: information relative to a repository
        :return: list of the repository commits
        """

        path = '/repositories/%s/commits' % repository.get('id')
        collector_id = repository.get('collector')

        commits = map(lambda commit_id: self.get_commit(repository, commit_id),
                      self._request_to_collector(path, collector_id))

        return commits

    def get_commit(self, repository, cid):

        """ This method return an specific commit from a repository

        :param repository: information relative to a repository
        :param cid: commit identifier
        :return: commit information from a repository
        """

        path = '/repositories/%s/commits/%s' % (repository.get('id'), cid)

        commit = self._request_to_collector(path, repository.get('collector'))
        commit['time'] = long(commit.pop('time')) * 1000
        commit['lines_removed'] = int(commit.pop('lines_removed'))
        commit['lines_added'] = int(commit.pop('lines_added'))
        commit['files_changed'] = int(commit.pop('files_changed'))

        return commit

    def get_commiters(self, repository):

        """ Returns a commiters list of a repository.

        :param repository: information relative to a repository
        :return: commiter emails list of a repository.
        """

        path = '/repositories/%s/contributors' % repository.get('id')

        return map(lambda commiter_id:
                   self._get_commiter(repository, commiter_id).get('email'),
                   self._request_to_collector(path,
                                              repository.get('collector')))

    def _get_commiter(self, repository, commiter_id):

        """ Returns commiter information

        :param repository: information relative to repository
        :param commiter_id:
        :return: commiter information
        """

        path = '/contributors/%s' % commiter_id

        commiter = self._request_to_collector(path, repository.get('collector'))

        commiter['commits'] = int(commiter.pop('commits'))
        commiter['first_commit_at'] = long(commiter.pop('first_commit_at'))
        commiter['first_commit_at'] *= 1000
        commiter['last_commit_at'] = long(commiter.pop('last_commit_at'))
        commiter['last_commit_at'] *= 1000

        return commiter

    def get_commiter_by_id(self, commiter_id):

        commiter = None
        for repository in self.get_repositories():
            try:
                commiter = self._get_commiter(repository, commiter_id)
                break
            except StandardError:
                pass

        return commiter

    def get_commiter(self, email):

        """ Returns commiter information regardless its repository

        :param email:
        :return: commiter information
        """

        path = '/contributors'

        commiter = dict()
        commiter['commits'] = 0L
        for repository in self.get_repositories():

            collector_id = repository.get('collector')
            contributors = self._request_to_collector(path, collector_id)
            for contributor_id in contributors:
                contributor = self._get_commiter(repository, contributor_id)
                if contributor.get('email') == email:
                    commiter['email'] = contributor.get('email')
                    commiter['commits'] += contributor.get('commits')
                    commiter['last_commit_at'] = max(
                        contributor['last_commit_at'],
                        commiter.get('last_commit_at',
                                     contributor['last_commit_at']))
                    commiter['first_commit_at'] = min(
                        contributor['first_commit_at'],
                        commiter.get('first_commit_at',
                                     contributor['first_commit_at']))

        return commiter if commiter.get('email') else None

    def get_branches(self, repository):

        """ Returns a branches list of a repository

        :param repository:  information relative to a repository
        :return: branches list of a repository
        """

        path = '/repositories/%s/branches' % repository.get('id')
        collector_id = repository.get('collector')

        branches = filter(lambda branch: branch is not None,
                          (self.get_branch(repository, identifier)
                           for identifier in
                           self._request_to_collector(path, collector_id)))

        return branches

    def get_branch(self, repository, b_id):

        """ Returns branch information

        :param repository: information relative to repository
        :param b_id: branch identifier
        :return: branch information from repository
        """
        # "Name", "contributors" = []
        path = '/repositories/%s/branches/%s' % (repository.get('id'), b_id)
        collector_id = repository.get('collector')

        branch = self._request_to_collector(path, collector_id)

        if branch and not branch.get('Error'):

            contributors = list()
            for contributor in branch.pop('contributors'):

                commiter = self._get_commiter(repository, contributor)
                contributors.append(commiter.get('email'))
            branch['contributors'] = contributors
            branch['id'] = b_id

            return branch
        return None

    def get_branch_commiters(self, repository, b_id):

        """ This method returns a list of commiters email.

        :param repository: information relative to repository
        :param b_id: branch identifier
        :return: list of commiters email
        """

        r_id = repository.get('id')
        collector_id = repository.get('collector')
        path = '/repositories/%s/branches/%s/contributors' % (r_id,
                                                                  b_id)

        return map(lambda c_id:
                   self._get_commiter(repository, c_id).get('email'),
                   self._request_to_collector(path, collector_id))

    def get_branches_commits(self, repository, b_id):

        """ Returns commit list of an specific branch

        :param repository: information relative to repository
        :param b_id: branch identifier
        :return: commits list from a branch
        """
        path = '/repositories/%s/branches/%s/commits' % (
            repository.get('id'), b_id)
        collector_id = repository.get('collector')

        return map(lambda commit_id: self.get_commit(repository, commit_id),
                   self._request_to_collector(path, collector_id))

    def _request_to_collector(self, path, collector_id):

        """ Makes a request to the API of a collector using an specific path

        :param path: path of the API request
        :param collector_id: collector identifier
        :return: request response or an empty dict if request fails
        """

        collector = self.collectors.get(collector_id)

        if collector:
            headers = dict()
            headers['Accept'] = 'application/json'

            if collector.get('security'):
                headers['X-GC-PWD'] = '%s' % collector.get('password')

            try:
                return requests.get('%s%s' % (collector.get('url'), path),
                                    headers=headers).json()
            except IOError:
                logging.error('Error: when trying request to GitCollector '
                              '(%s%s)' % (collector.get('url'), path))
                return dict()
        return dict()
