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

from dateutil import parser
import base64

__author__ = 'Alejandro F. Carrera'


def get_projects(gl):
    """ Get Projects
    :param gl: GitLab Object Instance
    :return: Projects (List)

    """
    p = map(lambda x: int(x.get('id')), gl.getprojectsall())
    p.sort()
    return p


def get_project(gl, project_id):
    """ Get Project
    :param gl: GitLab Object Instance
    :param project_id: Project Identifier (int)
    :return: Project (Object)
    """
    git_project = gl.getproject(project_id)
    if git_project is False:
        return False
    else:

        ci = get_project_information(gl, project_id, None)

        # Owner
        if git_project.get('owner') is None:
            git_owner = {
                'type': 'groups',
                'id': git_project.get('namespace').get('id')
            }
            git_project['owner'] = git_owner
        else:
            git_owner = {
                'type': 'users',
                'id': git_project.get('owner').get('id')
            }
            git_project['owner'] = git_owner
        convert_time_keys(git_project)

        # Tags
        git_project['tags'] = map(lambda x: x.get('name'), gl.getrepositorytags(project_id))

        # First and last commits
        if len(ci.get('commits')) > 0:
            git_project['first_commit_at'] = ci.get('commits')[0].get('created_at')
            git_project['last_commit_at'] = ci.get('commits')[-1].get('created_at')

        # Contributors
        git_project['contributors'] = ci.get('collaborators')

        # Remove and transform fields
        parse_info_project(git_project)
        git_project['default_branch_name'] = git_project['default_branch']
        git_project['default_branch'] = base64.b16encode(git_project['default_branch'])
        return git_project


def get_project_owner(gl, project_id):
    """ Get Project's Owner
    :param gl: GitLab Object Instance
    :param project_id: Project Identifier (int)
    :return: Owner (User Object | Group Object)
    """
    git_project = gl.getproject(project_id)
    if git_project is False:
        return False
    if git_project.get('owner') is None:
        u = get_group(gl, git_project.get('namespace').get('id'))
        u['type'] = 'group'
    else:
        u = get_user(gl, git_project.get('owner').get('id'))
        u['type'] = 'user'
    return u


def get_project_milestones(gl, project_id):
    """ Get Project's Milestones
    :param gl: GitLab Object Instance
    :param project_id: Project Identifier (int)
    :return: Milestones (List)
    """
    return False


def get_project_milestone(gl, project_id, milestone_id):
    """ Get Project's Milestone
    :param gl: GitLab Object Instance
    :param project_id: Project Identifier (int)
    :param milestone_id: Milestone Identifier (int)
    :return: Milestone (Object)
    """
    return False


def get_project_branches(gl, project_id, default_flag):
    """ Get Project's Branches
    :param gl: GitLab Object Instance
    :param project_id: Project Identifier (int)
    :param default_flag: Filter by type (bool)
    :return: Branches (List)
    """
    if default_flag == 'false':
        gl_b = gl.getbranches(project_id)
        if gl_b is False:
            return False
        return map(lambda w: base64.b16encode(w.get('name')), gl_b)
    else:
        git_project = get_project(gl, project_id)
        if git_project is False:
            return False
        else:
            return [base64.b16encode(git_project['default_branch'])]


def get_project_branch(gl, project_id, branch_name):
    """ Get Project's Branch
    :param gl: GitLab Object Instance
    :param project_id: Project Identifier (int)
    :param branch_name: Branch Identifier (string)
    :return: Branch (Object)
    """
    branch_name = base64.b16decode(branch_name)
    gl_branch = gl.getbranch(project_id, branch_name)
    if gl_branch is False:
        return False
    else:
        cm = get_project_information(gl, project_id, branch_name)
        gl_branch['created_at'] = cm.get('commits')[0].get('created_at')
        gl_branch['last_commit'] = cm.get('commits')[-1].get('id')
        gl_branch['contributors'] = cm.get('collaborators')
        if gl_branch.get('protected') is False:
            gl_branch['protected'] = 'false'
        else:
            gl_branch['protected'] = 'true'
        del gl_branch['commit']
        return gl_branch


def get_project_branch_contributors(gl, project_id, branch_name, t_window):
    """ Get Branch's Contributors
    :param gl: GitLab Object Instance
    :param project_id: Project Identifier (int)
    :param branch_name: Branch Identifier (string)
    :param t_window: (Time Window) filter (Object)
    :return: Contributors (List)
    """
    return get_contributors_projects(gl, project_id, branch_name, t_window)


def get_project_branch_commits(gl, project_id, branch_name, user_id, t_window):
    """ Get Branch's Commits
    :param gl: GitLab Object Instance
    :param project_id: Project Identifier (int)
    :param branch_name: Branch Identifier (string)
    :param user_id: Optional User Identifier (int)
    :param t_window: (Time Window) filter (Object)
    :return: Commits (List)
    """
    user = None
    if user_id is not None:
        user = gl.getuser(user_id)
        if user is False:
            return False
        else:
            user = user.get('email')
    if gl.getbranch(project_id, base64.b16decode(branch_name)) is False:
        return False
    ci = get_project_information(gl, project_id, branch_name)
    ci_commits = ci.get('commits')
    git_commits_time = []

    # Filter by time
    [git_commits_time.append(x) for x in ci_commits if
        t_window.get('st_time') <= x.get('created_at') <= t_window.get('en_time')]

    # Filter by user
    if user is None:
        ret_commits = git_commits_time
    else:
        git_commits_user = []
        [git_commits_user.append(x) for x in git_commits_time if
            x.get('author_email') == user.get('email')]
        ret_commits = git_commits_user

    return map(lambda k: k.get('id'), ret_commits)


def get_project_commits(gl, project_id, user_id, t_window):
    """ Get Project's Commits
    :param gl: GitLab Object Instance
    :param project_id: Project Identifier (int)
    :param user_id: Optional User Identifier (int)
    :param t_window: (Time Window) filter (Object)
    :return: Commits (List)
    """
    user = None
    if user_id is not None:
        user = gl.getuser(user_id)
        if user is False:
            return False
        else:
            user = user.get('email')

    ci = get_project_information(gl, project_id, None)
    ci_commits = ci.get('commits')
    git_commits_time = []

    # Filter by time
    [git_commits_time.append(x) for x in ci_commits if
        t_window.get('st_time') <= x.get('created_at') <= t_window.get('en_time')]

    # Filter by user
    if user is None:
        ret_commits = git_commits_time
    else:
        git_commits_user = []
        [git_commits_user.append(x) for x in git_commits_time if
            x.get('author_email') == user.get('email')]
        ret_commits = git_commits_user

    return map(lambda k: k.get('id'), ret_commits)


def get_project_commit(gl, project_id, commit_id):
    """ Get Project's Commit
    :param gl: GitLab Object Instance
    :param project_id: Project Identifier (int)
    :param commit_id: Commit Identifier (sha)
    :return: Commit (Object)
    """
    gl_commit = gl.getrepositorycommit(project_id, commit_id)
    if gl_commit is False:
        return False
    convert_time_keys(gl_commit)
    cd = gl.getrepositorycommitdiff(project_id, commit_id)
    add_lines_j = []
    rem_lines_j = []
    if cd is not False:

        def split_cd(cd_commit):
            cd_line = cd_commit.get('diff').split('@@')
            if len(cd_line) == 1:
                return
            elif len(cd_line) == 2:
                cd_line = [cd_line[1].splitlines()]
            elif len(cd_line) == 3:
                cd_line = [cd_line[2].splitlines()]
            elif len(cd_line) > 3:
                cd_line = cd_line[2:]
                cd_line = cd_line[::2]
                cd_line = map(lambda w: w.splitlines(), cd_line)

            [add_lines_j.append(1) for w in cd_line[0] if w != "" and w[0] == '+']
            [rem_lines_j.append(1) for w in cd_line[0] if w != "" and w[0] == '-']

        [split_cd(i) for i in cd]

    gl_commit['lines_added'] = len(add_lines_j)
    gl_commit['lines_removed'] = len(rem_lines_j)
    git_users = get_users(gl)
    git_users = map(lambda w: gl.getuser(w), git_users)
    [gl_commit.update({'author': x.get('id')}) for x in git_users
        if x.get('email') == gl_commit.get('author_email').lower()]
    del gl_commit['author_email']
    del gl_commit['author_name']
    return gl_commit


def get_project_requests(gl, project_id, request_state):
    """ Get Project's Merge Requests
    :param gl: GitLab Object Instance
    :param project_id: Project Identifier (int)
    :param request_state: Optional Type Identifier (string)
    :return: Merge Requests (List)
    """
    return False


def get_project_request(gl, project_id, request_id):
    """ Get Project's Merge Request
    :param gl: GitLab Object Instance
    :param project_id: Project Identifier (int)
    :param request_id: Merge Request Identifier (int)
    :return: Merge Request (Object)
    """
    return False


def get_project_request_changes(gl, project_id, request_id):
    """ Get Merge Request's Changes
    :param gl: GitLab Object Instance
    :param project_id: Project Identifier (int)
    :param request_id: Merge Request Identifier (int)
    :return: Changes (List)
    """
    return False


def get_project_file_tree(gl, project_id, view, branch_name, path):
    """ Get Project's File Tree
    :param gl: GitLab Object Instance
    :param project_id: Project Identifier (int)
    :param view: Representation (string)
    :param branch_name: Optional Branch Identifier (string)
    :param path: Optional Start Path (string)
    :return: File Tree (Object)
    """
    if branch_name is None:
        git_project = get_project(gl, project_id)
        if git_project is False:
            return git_project
        else:
            branch_name = git_project.get('default_branch')
            branch_name = base64.b16decode(branch_name)
    first_step = gl.getrepositorytree(project_id, ref_name=branch_name, path=path)
    if view == 'simple' or first_step is False:
        return first_step
    else:
        ret_tree = {}
        for x in first_step:
            if x.get('type') == 'tree':
                if path is not None:
                    new_path = path + '/' + x.get('name')
                else:
                    new_path = x.get('name')
                ret_tree[x.get('name')] = x
                ret_tree_git = get_project_file_tree(gl, project_id, 'full', branch_name, new_path)
                if ret_tree_git is not False:
                    ret_tree[x.get('name')]['tree'] = ret_tree_git
            else:
                ret_tree[x.get('name')] = x
        if len(ret_tree) == 0:
            return False
        else:
            return ret_tree


def get_project_contributors(gl, project_id, t_window):
    """ Get Project's Contributors
    :param gl: GitLab Object Instance
    :param project_id: Project Identifier (int)
    :param t_window: (Time Window) filter (Object)
    :return: Contributors (List)
    """
    return get_contributors_projects(gl, project_id, None, t_window)


def get_users(gl):
    """ Get Users
    :param gl: GitLab Object Instance
    :return: Users (List)
    """
    pag = 0
    number_page = 50
    git_users_len = -1
    git_users_id = {}
    while git_users_len is not 0:
        git_users = gl.getusers(page=pag, per_page=number_page)
        git_users_len = len(git_users)
        [git_users_id.update({x.get('id'): '1'}) for x in git_users
            if x.get('id') not in git_users_id]
        pag += 1
    git_users_id = git_users_id.keys()
    git_users_id.sort()
    return git_users_id


def get_user(gl, user_id):
    """ Get User
    :param gl: GitLab Object Instance
    :return: User (Object)
    """
    gl_user = gl.getuser(user_id)
    if gl_user is False:
        return False
    convert_time_keys(gl_user)
    git_projects = get_projects(gl)
    f_commit = -1
    l_commit = -1
    for i in git_projects:
        gpc = get_project_information(gl, i, None)
        if gl_user.get('id') in gpc.get('collaborators'):
            for j in gpc.get('commits'):
                if f_commit == -1 and \
                   j.get('author_email').lower() == gl_user.get('email'):
                    f_commit = j.get('created_at')
                if l_commit == -1 and \
                   j.get('author_email').lower() == gl_user.get('email'):
                    l_commit = j.get('created_at')
                if f_commit > j.get('created_at') and \
                   j.get('author_email').lower() == gl_user.get('email'):
                    f_commit = j.get('created_at')
                if l_commit < j.get('created_at') and \
                   j.get('author_email').lower() == gl_user.get('email'):
                    l_commit = j.get('created_at')
    if f_commit != -1:
        gl_user['first_commit_at'] = f_commit
    if l_commit != -1:
        gl_user['last_commit_at'] = l_commit
    parse_info_user(gl_user)
    return gl_user


def get_user_projects(gl, user_id, relation_type, t_window):
    """ Get User's Projects
    :param gl: GitLab Object Instance
    :param user_id: User Identifier (int)
    :param relation_type: Relation between User-Project
    :param t_window: (Time Window) filter (Object)
    :return: Projects (List)
    """
    gl_user = gl.getuser(user_id)
    if gl_user is False:
        return False
    return get_entity_projects(gl, user_id, relation_type, 'users', t_window)


def get_groups(gl):
    """ Get Groups
    :param gl: GitLab Object Instance
    :return: Groups (List)
    """
    gl_g = gl.getgroups()
    if gl_g is False:
        return []
    return map(lambda x: int(x.get('id')), gl_g)


def get_group(gl, group_id):
    """ Get Group
    :param gl: GitLab Object Instance
    :param group_id: Group Identifier (int)
    :return: Group (Object)
    """
    git_group = gl.getgroups(group_id)
    if git_group is False:
        return False
    else:
        if 'projects' in git_group:
            del git_group['projects']
        convert_time_keys(git_group)
        git_group['members'] = []
        [git_group['members'].append(x.get('id')) for x in gl.getgroupmembers(git_group.get('id'))]
        return git_group


def get_group_projects(gl, group_id, relation_type, t_window):
    """ Get Group's Projects
    :param gl: GitLab Object Instance
    :param group_id: Group Identifier (int)
    :param relation_type: Relation between User-Project
    :param t_window: (Time Window) filter (Object)
    :return: Projects (List)
    """
    git_group = gl.getgroups(group_id)
    if git_group is False:
        return False
    return get_entity_projects(gl, group_id, relation_type, 'groups', t_window)


# Functions to help another functions


time_keys = [
    'created_at', 'updated_at', 'last_activity_at',
    'due_date', 'authored_date', 'committed_date',
    'first_commit_at', 'last_commit_at'
]


def convert_time_keys(o):
    for k in o.keys():
        if isinstance(o[k], dict):
            convert_time_keys(o[k])
        else:
            if k in time_keys:
                if o[k] != "null":
                    o[k] = long(
                        parser.parse(o.get(k)).strftime("%s")
                    ) * 1000


def parse_info_user(o):
    k_users = [
        "username", "name", "twitter", "created_at",
        "linkedin", "email", "state", "avatar_url",
        "skype", "id", "website_url", "first_commit_at",
        "last_commit_at"
    ]
    for k in o.keys():
        if k not in k_users:
            del o[k]
        elif o[k] is None or o[k] == '':
            del o[k]
        else:
            pass


def parse_info_project(o):
    k_projects = [
        "first_commit_at", "contributors", "http_url_to_repo", "web_url",
        "owner", "id", "archived", "public", "description", "default_branch",
        "last_commit_at", "last_activity_at", "name", "created_at", "avatar_url",
        "tags"
    ]
    for k in o.keys():
        if k not in k_projects:
            del o[k]
        elif o[k] is None or o[k] == '':
            del o[k]
        elif o[k] is False:
            o[k] = 'false'
        elif o[k] is True:
            o[k] = 'true'
        elif isinstance(o[k], list):
            if len(o[k]) == 0:
                del o[k]
        else:
            pass


def get_entity_projects(gl, entity_id, relation_type, user_type, t_window):

    # Get Entity's projects
    git_projects = get_projects(gl)

    git_ret = []
    g_m = None
    if user_type == 'groups':
        g_m = get_group(gl, entity_id).get('members')
    if relation_type == 'owner':
        user_type = user_type[:-1]

    for k in git_projects:
        if relation_type == 'owner':
            o = get_project_owner(gl, k)
            if o.get('type') == user_type and o.get('id') == entity_id:
                git_ret.append(k)
        else:
            c = get_project_contributors(gl, k, t_window)
            if user_type == 'groups':
                [git_ret.append(k) for j in c if j in g_m]
            else:
                [git_ret.append(k) for j in c if j == entity_id]

    if user_type == 'groups':
        git_ret_un = []
        [git_ret_un.append(x) for x in git_ret if x not in git_ret_un]
        git_ret_un.sort()
        git_ret = git_ret_un
    return git_ret


def get_contributors_projects(gl, project_id, branch_name, t_window):

    ret_users = {}

    # Get Commits
    ci = get_project_information(gl, project_id, branch_name)
    ci_commits = []
    [ci_commits.append(w) for w in ci.get('commits') if
        t_window.get('st_time') <= w.get('created_at') <= t_window.get('en_time')]

    # Get Users emails and identifiers
    pag = 0
    number_page = 100
    git_users_len = -1
    git_users_em_id = {}
    while git_users_len is not 0:
        git_users = gl.getusers(page=pag, per_page=number_page)
        git_users_len = len(git_users)
        [git_users_em_id.update({x.get('email'): x.get('id')}) for x in git_users]
        pag += 1

    for w in ci_commits:
        w['author_email'] = w.get('author_email').lower()
        if w.get('author_email') in git_users_em_id:
            if w.get('author_email') not in ret_users:
                ret_users[w.get('author_email')] = git_users_em_id[w.get('author_email')]

    ret_users = ret_users.values()
    ret_users.sort()
    return ret_users


def get_project_information(gl, project_id, branch_name):

    # Detect possible failures
    git_project = gl.getproject(project_id)
    if git_project is False:
        return False
    if branch_name is not None:
        try:
            branch_name = base64.b16decode(branch_name)
        except Exception as e:
            pass
        if gl.getbranch(project_id, branch_name) is False:
            return False
        git_branches = [branch_name]
    else:
        git_branches = get_project_branches(gl, project_id, 'false')
        git_branches = map(lambda j: base64.b16decode(j), git_branches)

    # Get Users emails and identifiers
    pag = 0
    number_page = 100
    git_users_len = -1
    git_users_em_id = {}
    while git_users_len is not 0:
        git_users = gl.getusers(page=pag, per_page=number_page)
        git_users_len = len(git_users)
        [git_users_em_id.update({x.get('email'): x.get('id')}) for x in git_users]
        pag += 1

    information = {
        'branches': {},
        'collaborators': {},
        'commits': []
    }
    commits_hash = {}
    for i in git_branches:
        information['branches'][i] = {
            'commits': None,
            'collaborators': {}
        }
        pag = 0
        number_page = 10000
        ret_commits = []
        git_commits_len = -1
        while git_commits_len is not 0:
            git_commits = gl.getrepositorycommits(project_id, i, page=pag, per_page=number_page)
            git_commits_len = len(git_commits)
            for w in git_commits:
                convert_time_keys(w)
                w['author_email'] = w.get('author_email').lower()
                if w.get('author_email') in git_users_em_id:
                    collaborator_id = git_users_em_id[w.get('author_email')]
                    information['branches'][i]['collaborators'][collaborator_id] = '1'
                    information['collaborators'][collaborator_id] = '1'
                    if w.get('id') not in commits_hash:
                        commits_hash[w.get('id')] = '1'
                        information['commits'].append(w)
            ret_commits += git_commits
            pag += 1

        ret_commits.sort(key=lambda j: j.get('created_at'), reverse=False)
        information['branches'][i]['commits'] = ret_commits
        information['branches'][i]['collaborators'] = information['branches'][i]['collaborators'].keys()

    information['commits'].sort(key=lambda j: j.get('created_at'), reverse=False)
    information['collaborators'] = information['collaborators'].keys()
    return information
