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
        self.redis_instance['git'] = \
            self._redis_create_pool(config.REDIS_DB_GIT)
        self.redis_instance['projects'] = \
            self._redis_create_pool(config.REDIS_DB_PROJ)
        self.redis_instance['users'] = \
            self._redis_create_pool(config.REDIS_DB_USER)
        self.redis_instance['groups'] = \
            self._redis_create_pool(config.REDIS_DB_GROUP)
        self.redis_instance['branches'] = \
            self._redis_create_pool(config.REDIS_DB_BRANCH)

        # GitLab Collector instance
        collector_url = '%s://%s' % (config.GITLAB_PROT, config.GITLAB_IP)
        self.collector = GitLabCollector(url=collector_url,
                                         r_servers=self.redis_instance,
                                         token=config.GITLAB_TOKEN,
                                         ssl=config.GITLAB_VER_SSL)
        self.git_collectors = GitCollectorsManager(self.redis_instance['git'])

        file = open(config.GC_FILE, 'r')
        if not file:
            raise EnvironmentError('- GitCollectors list file not found.')

        file_content = file.read()
        if not file_content:
            raise EnvironmentError('- GitCollectors list is empty.')

        try:
            for collector in json.loads(file_content):
                if not self.git_collectors.add_collector(collector):
                    raise EnvironmentError('- Wrong GitCollector format: %s' %
                                           collector)

        except:
            raise EnvironmentError('- GitCollectors list is not a valid json.')

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

        projects = self.git_collectors.get_repositories()

        return [project.get('id') for project in projects]

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
        if repository:
            p_id = self._get_project_id_from_repo(repository)
            project = dict()
            project['id'] = r_id
            project['http_url_to_repo'] = repository.get('url')
            project['web_url'] = repository.get('url').replace('.git', '')
            project['state'] = repository.get('state')

            commits = self.git_collectors.get_commits(repository)
            if commits:
                commits_dict = {commit.get('time'): commit
                                for commit in commits}

                commits_dates = sorted(commits_dict)
                project['created_at'] = commits_dates[0]
                project['first_commit_at'] = commits_dates[0]
                project['last_commit_at'] = commits_dates[-1]
                project['contributors'] = self.get_project_contributors(r_id)

            if p_id:
                r_projects = self.redis_instance.get('projects')
                project.update(r_projects.hgetall('project:%s' % p_id))

                default_branch = project.pop('default_branch')
                branch = map(lambda b: b.get('id'),
                             filter(lambda b: b.get('name') == default_branch,
                                    self.git_collectors.get_branches(repository)
                                    )
                             )
                project['default_branch'] = branch[0] if branch else None
                # deserialize inner structs
                project['tags'] = eval(project.pop('tag_list'))
                project['owner'] = eval(project.pop('owner'))

            return project
        return None

    def _get_project_id_from_repo(self, repository):

        """ Method that combine information from two sources: Git and Redis

        :param repository: information relative to repository
        :return: project with information merged from git collector and redis
        """

        r_projects = self.redis_instance.get('projects')

        projects_id = filter(lambda p_id:
                             r_projects.hget(
                                 p_id,
                                 'http_url_to_repo') == repository.get('url'),
                             r_projects.keys('project:*'))

        return projects_id[0].split(':')[1] if projects_id else None

    def _get_contributors(self, repository):

        """ This method will return a list of the repository contributors from
        GitCollector enriched with redis information

        :param repository: repository information
        :return:
        """

        commiter_list = self.git_collectors.get_commiters(repository)
        contributors = list()

        for commiter in commiter_list:
            author = self._get_contributor(commiter.get('email'))
            if author:
                contributors.append(author)
            else:
                contributors.append(commiter.get('email'))

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
            [user_emails_id.split(':')[1]
             for user_emails_id in r_users.keys('emails:*')])

        return users_id[0] if users_id else None

    def get_project_owner(self, r_id):

        """ Get Project's Owner

        :param r_id: Project Identifier (int)
        :return: Owner (User Object | Group Object)
        """

        repository = self.git_collectors.get_repository(r_id)

        if repository:
            p_id = self._get_project_id_from_repo(repository)

            if p_id:
                r_projects = self.redis_instance.get('projects')
                owner = r_projects.hget('project:%s' % p_id, 'owner')

                return self.get_user(owner['id'])
        return None

    def get_project_contributors(self, r_id):

        """ Get Project's Contributors

        :param r_id: Project Identifier (int)
        :return: Contributors (List)
        """

        repository = self.git_collectors.get_repository(r_id)

        if repository:
            return self._get_contributors(repository)
        return None

    def get_users(self):

        """ Get Users

        :return: Users (List)
        """

        r_users = self.redis_instance.get('users')

        users = [self.get_user(user_id.split(':')[1])
                 for user_id in r_users.keys('user:*')]

        return users

    def _merge_user_information(self, user):

        """ Combine the user information from Git and from Redis.

        :param user: information from redis
        :return: merged user information
        """

        new_user = user.copy()
        first_commit = float('inf')
        last_commit = 0

        for email in user.get('emails'):

            commiter = self.git_collectors.get_commiter(email)
            if commiter:
                first = commiter.get('first_commit_at')
                last = commiter.get('last_commit_at')
                first_commit = first if first_commit > first else first_commit
                last_commit = last if last_commit < last else last_commit

        if last_commit:
            new_user['first_commit_at'] = long(first_commit) * 1000
            new_user['last_commit_at'] = long(last_commit) * 1000
        new_user['id'] = user.get('id')
        if user.get('identities'):
            new_user['identities'] = eval(user['identities'])
        new_user['external'] = user.get('external', False)

        return new_user

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

        r_users = self.redis_instance.get('users')
        user = r_users.hgetall('user:%s' % u_id)

        if user:
            user['emails'] = list(r_users.smembers('emails:%s' % u_id))
            user = self._merge_user_information(user)

        else:  # if user does not exist in Gitlab
            user = self.git_collectors.get_commiter(u_id)
            if user:
                user['external'] = True

        return user

    def get_user_projects(self, u_id, relation):

        """ Get User's Projects

        :param u_id: User Identifier (int)
        :param relation: Relation between User-Project
        :return: Projects (List)
        """

        if relation == 'owner':
            projects = filter(lambda x: x.get('owner').get('id') == u_id,
                              (self.get_project(r_id)
                               for r_id in self.get_projects()))
        else:
            projects = filter(lambda x: u_id in x.get('contributors'),
                              (self.get_project(r_id)
                               for r_id in self.get_projects()))

        return projects

    def get_project_branches(self, r_id, default):

        """ Get Project's Branches

        :param r_id: Project Identifier (int)
        :param default: Filter by type (bool)
        :return: Branches (List)
        """

        repository = self.git_collectors.get_repository(r_id)

        if repository:

            p_id = self._get_project_id_from_repo(repository)

            r_projects = self.redis_instance.get('projects')
            default_branch = r_projects.hget('project:%s' % p_id,
                                             'default_branch')
            branches = filter(lambda b:
                              not default or
                              default and b.get('name') == default_branch,
                              self.git_collectors.get_branches(repository))

            return [branch.get('id') for branch in branches]

        return None

    def get_project_branch(self, r_id, b_id):

        """ Get Project's Branch

        :param r_id: Project Identifier (int)
        :param b_id: Branch Identifier (string)
        :return: Branch (Object)
        """

        # Branch fields
        # "name", "created_at", "protected", "contributors",
        # "last_commit"

        repository = self.git_collectors.get_repository(r_id)

        if repository:
            branch = self.git_collectors.get_branch(repository, b_id)

            if branch:
                p_id = self._get_project_id_from_repo(repository)

                if p_id:
                    r_branches = self.redis_instance.get('branches')
                    protected = r_branches.hget(
                        'branch:%s:%s' % (p_id, branch.get('name')),
                        'protected')
                    branch['protected'] = eval(protected)

                commits = self.git_collectors.get_branches_commits(repository,
                                                                   b_id)
                if commits:
                    commits_dict = {commit.get('time'): commit
                                    for commit in commits}
                    commits_dates = sorted(commits_dict)
                    branch['created_at'] = commits_dates[0]
                    branch['last_commit_at'] = commits_dates[-1]
                    contributors = self.get_project_branch_contributors(r_id,
                                                                        b_id)
                    branch['contributors'] = contributors

                return branch
        return None

    def get_project_branch_contributors(self, r_id, b_id):

        """ Get Branch's Contributors

        :param r_id: Project Identifier (int)
        :param b_id: Branch Identifier (string)
        :return: Contributors (List)
        """

        repository = self.git_collectors.get_repository(r_id)

        return self.git_collectors.get_branch_commiters(repository, b_id)

    def _enhance_commit_information(self, commit):

        """ This method combines commit information from two sources: Git and
        Redis.

        :param commit: data from Git
        :return:
        """

        # "lines_removed", "short_id", "author", "lines_added",
        # "created_at", "title", "parent_ids", "committed_date",
        # "message", "authored_date", "id"

        # GitCollector
        # lines_removed, lines_added, files_changed

        # GitLab
        # short_id, title, author_email, created_at, message, author_name, id

        author_email = commit.get('email')
        author = self._get_contributor(author_email)

        new_commit = commit.copy()
        new_commit.pop('email')
        new_commit['id'] = new_commit.pop('sha')
        new_commit['created_at'] = new_commit.pop('time')
        new_commit['message'] = "%s\n" % commit.get('title')

        if author:
            new_commit['author'] = author
            new_commit['author_name'] = self.get_user(author).get('name')
        new_commit['author_email'] = author_email

        return new_commit

    @staticmethod
    def _filter_commits(commits, u_id, t_window):

        w_start = t_window['st_time'] / 1000
        w_end = t_window['en_time'] / 1000

        filtered_date = filter(lambda commit:
                               w_start < long(commit.get('created_at')) < w_end,
                               commits)

        return filter(lambda x: not u_id or u_id == x.get('author'),
                      filtered_date)

    def get_project_commits(self, r_id, u_id, t_window):

        """ Get Project's Commits
        :param r_id: Project Identifier (int)
        :param u_id: Optional User Identifier (int)
        :param t_window: (Time Window) filter (Object)
        :return: Commits (List)
        """
        # TODO: What we do with 'short_id' and 'message'?

        repository = self.git_collectors.get_repository(r_id)
        filtered_commits = None
        if repository:
            commits = [self._enhance_commit_information(commit)
                       for commit in
                       self.git_collectors.get_commits(repository)]

            filtered_commits = self._filter_commits(commits, u_id, t_window)

        return [commit.get('id') for commit in filtered_commits]

    def get_project_branch_commits(self, r_id, b_id, u_id, t_window):

        """ Get Branch's Commits
        :param r_id: Project Identifier (int)
        :param b_id: Branch Identifier (string)
        :param u_id: Optional User Identifier (int)
        :param t_window: (Time Window) filter (Object)
        :return: Commits (List)
        """

        filtered_commits = None
        repository = self.git_collectors.get_repository(r_id)

        if repository:
            commits = [self._enhance_commit_information(commit)
                       for commit in
                       self.git_collectors.get_branches_commits(repository,
                                                                b_id)]
            filtered_commits = self._filter_commits(commits, u_id, t_window)

        return [commit.get('id') for commit in filtered_commits]

    def get_project_commit(self, r_id, c_id):

        """ Get Project's Commit
        :param r_id: Project Identifier (int)
        :param c_id: Commit Identifier (sha)
        :return: Commit (Object)
        """

        repository = self.git_collectors.get_repository(r_id)

        if repository:

            commit = self.git_collectors.get_commit(repository, c_id)
            if commit:
                return self._enhance_commit_information(commit)

        return None

    def get_groups(self):

        """ Get Groups
        :return: Groups (List)
        """

        r_groups = self.redis_instance.get('groups')

        groups = [group_id.split(':')[1]
                  for group_id in r_groups.keys('group:*')]

        return groups

    def get_group(self, g_id):

        """ Get Group
        :param g_id: Group Identifier (int)
        :return: Group (Object)
        """

        r_groups = self.redis_instance.get('groups')

        group = r_groups.hgetall('group:%s' % g_id)
        group['members'] = list(r_groups.smembers('members:%s' % g_id))
        group['id'] = group.pop('id')

        return group

    def get_group_projects(self, g_id, relation):

        """ Get Group's Projects
        :param g_id: Group Identifier (int)
        :param relation: Relation between Group-Project
        :return: Projects (List)
        """

        projects = list()
        r_groups = self.redis_instance.get('groups')

        for member in r_groups.smembers('members:%s' % g_id):
            projects.extend(self.get_user_projects(int(member), relation))

        return projects

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