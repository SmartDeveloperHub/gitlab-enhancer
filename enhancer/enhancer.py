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
from datetime import datetime
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
        self.redis_instance['commits'] = \
            self._redis_create_pool(config.REDIS_DB_COMMIT)
        self.redis_instance['merge_requests'] = \
            self._redis_create_pool(config.REDIS_DB_MERGE)

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

        project = self._match_repo_with_project(repository)

        if project:

            commits = self.git_collectors.get_commits(repository)
            if commits:
                project['first_commit_at'] = \
                    self._format_date(commits[0].get('time'))
                project['last_commit_at'] = \
                    self._format_date(commits[-1].get('time'))

            project['contributors'] = self._get_contributors(repository)
            project['id'] = repository.get('id')

            return project

        return None

    def _match_repo_with_project(self, repository):

        """ Method that combine information from two sources: Git and Redis

        :param repository: information relative to repository
        :return: project with information merged from git collector and redis
        """

        r_projects = self.redis_instance.get('projects')

        projects = filter(lambda x:
                          x.get('http_url_to_repo') == repository.get('url'),
                          [r_projects.hgetall(p_id)
                           for p_id in r_projects.keys('project:*')])

        if projects:

            project = projects[0]
            # deserialize inner structs
            project['owner'] = eval(project.get('owner'))
            project['namespace'] = eval(project.get('namespace'))

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
            contributors.append(self._get_contributor(commiter.get('email')))

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

        return int(users_id[0]) if users_id else None

    def get_project_owner(self, r_id):

        """ Get Project's Owner

        :param r_id: Project Identifier (int)
        :return: Owner (User Object | Group Object)
        """

        repository = self.git_collectors.get_repository(r_id)
        project = None

        if repository:
            project = self._match_repo_with_project(repository)

        if project:
            owner = project.get('owner')
            return self.get_user(owner['id'])

        return None

    def get_project_contributors(self, r_id):

        """ Get Project's Contributors

        :param r_id: Project Identifier (int)
        :return: Contributors (List)
        """

        project = self.get_project(r_id)

        if project:
            return project.get('contributors')

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
            new_user['first_commit_at'] = self._format_date(first_commit)
            new_user['last_commit_at'] = self._format_date(last_commit)
        new_user['id'] = int(user.get('id'))
        if user.get('identities'):
            new_user['identities'] = eval(user['identities'])

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
            # TODO: external

        return user

    def get_user_projects(self, u_id, relation):

        """ Get User's Projects

        :param u_id: User Identifier (int)
        :param relation: Relation between User-Project
        :return: Projects (List)
        """

        if relation == 'owner':
            projects = filter(lambda x: x.get('owner').get('id') == u_id,
                              self.get_projects())
        else:
            projects = filter(lambda x: u_id in x.get('contributors'),
                              self.get_projects())

        return projects

    def _merge_branch_information(self, p_id, branch):

        """ Returns the branch information with additional fields

        :param p_id: Redis project id
        :param branch: branch information from Git protocol
        :return: branch enhanced branch information
        """

        r_branches = self.redis_instance.get('branches')
        merged_branch = r_branches.hgetall('branch:%s:%s' % (p_id,
                                                             branch.get('name'))
                                           )

        if merged_branch:

            # Change name of key
            merged_branch['last_commit'] = eval(merged_branch.pop('commit'))
            contributors = list()
            for contributor in branch.get('contributors'):
                contributors.append(self._get_contributor(contributor))

            merged_branch['contributors'] = contributors
            merged_branch['id'] = branch.get('id')
            return merged_branch

    def get_project_branches(self, r_id, default):

        """ Get Project's Branches

        :param r_id: Project Identifier (int)
        :param default: Filter by type (bool)
        :return: Branches (List)
        """
        # TODO: use default param
        branches = list()
        repository = self.git_collectors.get_repository(r_id)

        if repository:

            p_id =  self._match_repo_with_project(repository).get('id')
            for b in self.git_collectors.get_branches(repository):
                branch = self._merge_branch_information(p_id, b)
                if branch:
                    branches.append(branch)

        return branches

    def get_project_branch(self, r_id, b_id):

        """ Get Project's Branch

        :param r_id: Project Identifier (int)
        :param b_id: Branch Identifier (string)
        :return: Branch (Object)
        """

        # Branch fields
        # "name", "created_at", "protected", "contributors",
        # "last_commit"

        branch = None
        repository = self.git_collectors.get_repository(r_id)

        if repository:
            b = self.git_collectors.get_branch(repository, b_id)
            p_id = self._match_repo_with_project(repository).get('id')

            if b:
                branch = self._merge_branch_information(p_id, b)

        return branch

    def get_project_branch_contributors(self, r_id, b_id):

        """ Get Branch's Contributors

        :param r_id: Project Identifier (int)
        :param b_id: Branch Identifier (string)
        :return: Contributors (List)
        """

        branch = self.get_project_branch(r_id, b_id)
        if branch:
            return branch.get('contributors')
        return None

    def _merge_commit_information(self, p_id, commit):

        """ This method combines commit information from two sources: Git and
        Redis.

        :param p_id: Redis project id
        :param commit: data from Git
        :return:
        """

        # "lines_removed", "short_id", "author", "lines_added",
        # "created_at", "title", "parent_ids", "committed_date",
        # "message", "authored_date", "id"

        r_commits = self.redis_instance.get('commits')
        r_commit = r_commits.hgetall('commit:%s:%s' % (p_id, commit.get('sha')))

        # GitCollector
        # lines_removed, lines_added, files_changed

        # GitLab
        # short_id, title, author_email, created_at, message, author_name, id

        author_email = commit.get('email')
        author = self._get_contributor(author_email)

        if r_commit:
            new_commit = r_commit.copy()
            new_commit['lines_removed'] = commit.get('lines_removed')
            new_commit['lines_added'] = commit.get('lines_added')
            new_commit['files_changed'] = commit.get('files_changed')

        else:
            new_commit = commit.copy()
            new_commit.pop('email')
            new_commit['id'] = new_commit.pop('sha')
            new_commit['created_at'] = self._format_date(new_commit.pop('time'))
            new_commit['message'] = "%s\n" % commit.get('title')

        new_commit['author'] = author
        new_commit['author_email'] = author_email
        new_commit['author_name'] = self.get_user(author).get('name')

        return new_commit

    def _filter_commits(self, repository, commits, u_id, t_window):

        """ This method filter commits regarding user id and a time window.

        :param repository: information relative to a repository
        :param commits: list of commits from Git
        :param u_id: user id
        :param t_window: time window within commits have been created.
        :return: list of commits satisfying filter params
        """

        # Milliseconds to seconds
        w_start = t_window['st_time'] / 1000
        w_end = t_window['en_time'] / 1000
        co = filter(lambda x: w_start < long(x.get('time')) < w_end,
                    commits)

        p_id = self._match_repo_with_project(repository).get('id')

        return filter(lambda x: not u_id or u_id == x.get('author'),
                      (self._merge_commit_information(p_id, commit)
                       for commit in co))

    def get_project_commits(self, r_id, u_id, t_window):

        """ Get Project's Commits
        :param r_id: Project Identifier (int)
        :param u_id: Optional User Identifier (int)
        :param t_window: (Time Window) filter (Object)
        :return: Commits (List)
        """

        repository = self.git_collectors.get_repository(r_id)
        commits = None
        if repository:
            raw_commits = self.git_collectors.get_commits(repository)
            commits = self._filter_commits(repository, raw_commits, u_id,
                                           t_window)

        return commits

    def get_project_branch_commits(self, r_id, b_id, u_id, t_window):

        """ Get Branch's Commits
        :param r_id: Project Identifier (int)
        :param b_id: Branch Identifier (string)
        :param u_id: Optional User Identifier (int)
        :param t_window: (Time Window) filter (Object)
        :return: Commits (List)
        """

        commits = None
        repository = self.git_collectors.get_repository(r_id)

        if repository:
            raw_commits = self.git_collectors.get_branches_commits(repository,
                                                                   b_id)
            commits = self._filter_commits(repository, raw_commits, u_id,
                                           t_window)

        return commits

    def get_project_commit(self, r_id, c_id):

        """ Get Project's Commit
        :param r_id: Project Identifier (int)
        :param c_id: Commit Identifier (sha)
        :return: Commit (Object)
        """

        repository = self.git_collectors.get_repository(r_id)

        if repository:

            p_id = self._match_repo_with_project(repository).get('id')
            commit = self.git_collectors.get_commit(repository, c_id)
            if commit:
                return self._merge_commit_information(p_id, commit)

        return None

    def get_groups(self):

        """ Get Groups
        :return: Groups (List)
        """

        r_groups = self.redis_instance.get('groups')

        groups = [self.get_group(group_id.split(':')[1])
                  for group_id in r_groups.keys('group:*')]

        return groups

    def get_group(self, g_id):

        """ Get Group
        :param g_id: Group Identifier (int)
        :return: Group (Object)
        """

        r_groups = self.redis_instance.get('groups')

        group = r_groups.hgetall('group:%s' % g_id)
        group['id'] = int(group.pop('id'))

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

    def _format_date(self, timestamp):

        # Example: 2012-09-20T09:06:12+03:00
        return datetime.utcfromtimestamp(float(timestamp))\
                .strftime('%Y-%m-%dT%H:%M:%S%z')