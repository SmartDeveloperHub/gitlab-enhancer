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

__author__ = 'Alejandro F. Carrera'

from dateutil import parser


def get_projects(gl, details):
    """ Get Projects
    :param gl: GitLab Object Instance
    :param details: Project details (bool)
    :return: Projects (List)

    """
    p = map(lambda x: int(x.get('id')), gl.getprojectsall())
    p.sort()
    if details is True:
        return map(lambda w: get_project(gl, w), p)
    else:
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
        parse_info_project(git_project)
        convert_time_keys(git_project)
        return git_project


def get_project_owner(gl, project_id):
    """ Get Project's Owner
    :param gl: GitLab Object Instance
    :param project_id: Project Identifier (int)
    :return: Owner (User Object | Group Object)
    """
    git_project = get_project(gl, project_id)
    if git_project is False:
        return False
    if git_project.get('owner').get('type') == 'groups':
        return get_group(gl, git_project.get('owner').get('id'))
    else:
        return get_user(gl, git_project.get('owner').get('id'))


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


def get_project_branches(gl, project_id, default_flag, details):
    """ Get Project's Branches
    :param gl: GitLab Object Instance
    :param project_id: Project Identifier (int)
    :param default_flag: Filter by type (bool)
    :param details: Project details (bool)
    :return: Branches (List)
    """
    if default_flag == 'false':
        gl_b = gl.getbranches(project_id)
        if gl_b is False:
            return False
        if details is True:
            for x in gl_b:
                x['last_commit'] = x.get('commit').get('id')
                if x.get('protected') is False:
                    x['protected'] = 'false'
                else:
                    x['protected'] = 'true'
                del x['commit']
            return gl_b
        else:
            return map(lambda w: w.get('name'), gl_b)
    else:
        git_project = get_project(gl, project_id)
        if git_project is False:
            return False
        else:
            if details is False:
                return [git_project.get('default_branch')]
            else:
                return [get_project_branch(gl, project_id, git_project.get('default_branch'))]


def get_project_branch(gl, project_id, branch_name):
    """ Get Project's Branch
    :param gl: GitLab Object Instance
    :param project_id: Project Identifier (int)
    :param branch_name: Branch Identifier (string)
    :return: Branch (Object)
    """
    gl_branch = gl.getbranch(project_id, branch_name)
    if gl_branch is False:
        return gl_branch
    else:
        gl_branch['last_commit'] = gl_branch.get('commit').get('id')
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


def get_project_branch_commits(gl, project_id, branch_name, user_id, offset, t_window, details):
    """ Get Branch's Commits
    :param gl: GitLab Object Instance
    :param project_id: Project Identifier (int)
    :param branch_name: Branch Identifier (string)
    :param user_id: Optional User Identifier (int)
    :param offset: Optional Offset parameter (int)
    :param t_window: (Time Window) filter (Object)
    :param details: Commit details (bool)
    :return: Commits (List)
    """
    pag = 0
    number_page = 10000
    user = None
    if offset is not None:
        pag = 1
        number_page = offset
    ret_commits = []
    git_commits_len = -1
    if user_id is not None:
        user = get_user(gl, user_id)
        if user is False:
            return False
    if get_project_branch(gl, project_id, branch_name) is False:
        return False
    while git_commits_len is not 0:
        git_commits = gl.getrepositorycommits(project_id, branch_name, page=pag, per_page=number_page)
        git_commits_len = len(git_commits)
        [convert_time_keys(x) for x in git_commits]

        # Filter by time
        git_commits_time = []
        [git_commits_time.append(x) for x in git_commits if
         t_window.get('st_time') <= x.get('created_at') <= t_window.get('en_time')]

        # Filter by user
        if user is None:
            ret_commits += git_commits_time
        else:
            git_commits_user = []
            [git_commits_user.append(x) for x in git_commits_time if
             x.get('author_email') == user.get('email')]
            ret_commits += git_commits_user
        pag += 1

    # Sort and return ids
    ret_commits.sort(key=lambda w: w.get('created_at'), reverse=False)
    if details is False:
        return map(lambda k: k.get('id'), ret_commits)
    else:
        return ret_commits


def get_project_commits(gl, project_id, user_id, offset, t_window, details):
    """ Get Project's Commits
    :param gl: GitLab Object Instance
    :param project_id: Project Identifier (int)
    :param user_id: Optional User Identifier (int)
    :param offset: Optional Offset parameter (int)
    :param t_window: (Time Window) filter (Object)
    :param details: Project details (bool)
    :return: Commits (List)
    """
    ret_commits_hash = {}
    git_branches = get_project_branches(gl, project_id, 'false', False)
    if git_branches is False:
        return False
    for i in git_branches:
        c = get_project_branch_commits(gl, project_id, i, user_id, offset, t_window, False)
        [ret_commits_hash.update({x: '1'}) for x in c if (x not in ret_commits_hash)]
    if details is False:
        return ret_commits_hash.keys()
    else:
        [ret_commits_hash.update({x: get_project_commit(gl, project_id, x)}) for x in ret_commits_hash.keys()]
        return ret_commits_hash


def get_project_commit(gl, project_id, commit_id):
    """ Get Project's Commit
    :param gl: GitLab Object Instance
    :param project_id: Project Identifier (int)
    :param commit_id: Commit Identifier (sha)
    :return: Commit (Object)
    """
    gl_commit = gl.getrepositorycommit(project_id, commit_id)
    convert_time_keys(gl_commit)
    cd = gl.getrepositorycommitdiff(project_id, commit_id)
    add_lines_j = []
    rem_lines_j = []
    if cd is not False:
        for x in cd:
            j = x.get('diff').split("@@ ")
            if len(j) == 2:
                j = [j[1].splitlines()]
            elif len(j) == 3:
                j = [j[2].splitlines()]
            elif len(j) > 3:
                j = j[2:]
                j = j[::2]
                j = map(lambda w: w.splitlines(), j)
            for i in j:
                for item in i:
                    if item != "":
                        if item[0] == '+':
                            add_lines_j.append(1)
                        elif item[0] == '-':
                            rem_lines_j.append(1)
    gl_commit['lines_added'] = len(add_lines_j)
    gl_commit['lines_removed'] = len(rem_lines_j)
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


def get_users(gl, offset):
    """ Get Users
    :param gl: GitLab Object Instance
    :param offset: Optional Offset parameter (int)
    :return: Users (List)
    """
    pag = 0
    number_page = 50
    if offset is not None:
        pag = 1
        number_page = offset
    ret_users = []
    git_users_len = -1
    while git_users_len is not 0:
        git_users = gl.getusers(page=pag, per_page=number_page)
        git_users_len = len(git_users)
        git_users_id = []
        [git_users_id.append(x.get('id')) for x in git_users]
        ret_users += git_users_id
        pag += 1
    ret_users_unique = []
    [ret_users_unique.append(x) for x in ret_users if x not in ret_users_unique]
    return ret_users_unique


def get_user(gl, user_id):
    """ Get User
    :param gl: GitLab Object Instance
    :return: User (Object)
    """
    gl_user = gl.getuser(user_id)
    if gl_user is False:
        return False
    parse_info_user(gl_user)
    convert_time_keys(gl_user)
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


def sp_project_commits_by_branch(gl, project_id, t_window):
    git_branches = get_project_branches(gl, project_id, 'false', False)
    if git_branches is False:
        return False
    ret_commits_hash = {}
    ret_commits_project = {}
    for i in git_branches:
        cb = get_project_branch_commits(gl, project_id, i, None, None, t_window, False)
        [ret_commits_project.update({x: '1'}) for x in cb if (x not in ret_commits_project)]
        ret_commits_hash[i] = cb
    [ret_commits_project.update({x: get_project_commit(gl, project_id, x)}) for x in ret_commits_project.keys()]
    return [ret_commits_project, ret_commits_hash]


time_keys = [
    'created_at', 'updated_at', 'last_activity_at',
    'due_date', 'authored_date', 'committed_date'
]


def convert_time_keys(o):
    for k in o.keys():
        if isinstance(o[k], dict):
            convert_time_keys(o[k])
        else:
            if k in time_keys:
                o[k] = long(
                    parser.parse(o.get(k)).strftime("%s")
                ) * 1000


def parse_info_user(o):
    del o['bio']
    del o['can_create_group']
    del o['can_create_project']
    del o['color_scheme_id']
    del o['identities']
    del o['is_admin']
    del o['projects_limit']
    del o['theme_id']


def parse_info_project(o):
    del o['namespace']
    del o['wiki_enabled']
    del o['merge_requests_enabled']
    del o['snippets_enabled']
    del o['issues_enabled']
    del o['path_with_namespace']
    del o['ssh_url_to_repo']
    del o['path']
    del o['visibility_level']
    del o['permissions']
    del o['name_with_namespace']
    for k in o.keys():
        if o[k] is None:
            o[k] = 'null'
        elif o[k] is False:
            o[k] = 'false'
        elif o[k] is True:
            o[k] = 'true'
        else:
            pass


# TODO: Source Code - Language (Language Mapping)
# "projects:id:commits:sha[language]" = {'language': 'number_files'}
#     "projects:id:branches:name[language]" = {'language': 'number_files'}
#     "projects:id[language]" = top_language_value in project
#     "users:id[favourite_language]" = top_language_value
def get_language_by_extension(ext):
    return "code"


def get_entity_projects(gl, entity_id, relation_type, user_type, t_window):

    # Get Entity's projects
    git_projects_details = get_projects(gl, True)
    git_ret = []
    if relation_type == 'owner':
        [git_ret.append(k.get('id')) for k in git_projects_details
         if k.get('owner').get('type') == user_type and k.get('owner').get('id') == entity_id]
    else:
        for x in git_projects_details:
            users_list = get_contributors_projects(gl, x.get('id'), None, t_window)

            # Search through group's members
            if user_type == 'groups':
                g_m = get_group(gl, entity_id).get('members')
                [git_ret.append(x.get('id')) for j in g_m if j in users_list]

            # Search about user
            else:
                [git_ret.append(x.get('id')) for k in users_list if k == entity_id]
    if user_type == 'groups':
        git_ret_un = []
        [git_ret_un.append(x) for x in git_ret if x not in git_ret_un]
        git_ret_un.sort()
        git_ret = git_ret_un
    return git_ret


def get_contributors_projects(gl, project_id, branch_name, t_window):

    # Specific Branch
    email_list = {}
    if branch_name is not None:
        commits_list = get_project_branch_commits(gl, project_id, branch_name, None, None, t_window, True)

    # Generic Project (all branches)
    else:
        commits_list = get_project_commits(gl, project_id, None, None, t_window, True)
        commits_list = map(lambda w: commits_list[w], commits_list.keys())

    if commits_list is False:
        return False
    else:
        [email_list.update({x.get('author_email'): '1'}) for x in commits_list]
        email_list = email_list.keys()
        git_users = get_users(gl, None)
        ret_users = []
        [ret_users.append(i) for i in git_users if get_user(gl, i).get('email') in email_list]
        ret_users.sort()
        return ret_users
