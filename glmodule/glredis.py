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


def get_projects(rd, details):
    """ Get Projects
    :param rd: Redis Object Instance
    :param details: Project details (bool)
    :return: Projects (List)
    """
    red_p = map(lambda w: int(w.split(':')[1]), rd.keys("projects:*:"))
    p = []
    [p.append(x) for x in red_p if x not in p]
    p.sort()
    if details is True:
        return map(lambda w: get_project(rd, w), p)
    else:
        return p


def get_project(rd, project_id):
    """ Get Project
    :param rd: Redis Object Instance
    :param project_id: Project Identifier (int)
    :return: Project (Object)
    """
    git_project = rd.hgetall("projects:" + str(project_id) + ":")
    if bool(git_project) is False:
        return False
    else:
        o = {
            'type': git_project.get('owner').split(":")[0],
            'id': git_project.get('owner').split(":")[1],
        }
        git_project['owner'] = o
        return git_project


def get_project_owner(rd, project_id):
    """ Get Project's Owner
    :param rd: Redis Object Instance
    :param project_id: Project Identifier (int)
    :return: Owner (User Object | Group Object)
    """
    git_project = get_project(rd, project_id)
    if git_project is False:
        return False
    if git_project.get('owner').get('type') == 'groups':
        return get_group(rd, git_project.get('owner').get('id'))
    else:
        return get_user(rd, git_project.get('owner').get('id'))


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


def get_project_branches(rd, project_id, default_flag, details):
    """ Get Project's Branches
    :param rd: Redis Object Instance
    :param project_id: Project Identifier (int)
    :param default_flag: Filter by type (bool)
    :param details: Project details (bool)
    :return: Branches (List)
    """
    if default_flag == 'false':
        gl_b = rd.keys("projects:" + str(project_id) + ":branches:*")
        gl_b = map(lambda w: w.split(":")[3], gl_b)
        if len(gl_b) == 0:
            return False
        gl_b_un = []
        [gl_b_un.append(x) for x in gl_b if x not in gl_b_un]
        gl_b = gl_b_un
        if details is True:
            return map(lambda w: get_project_branch(rd, project_id, w), gl_b)
        else:
            return gl_b
    else:
        git_project = get_project(rd, project_id)
        if git_project is False:
            return False
        else:
            if details is False:
                return [git_project.get('default_branch')]
            else:
                return [get_project_branch(rd, project_id, git_project.get('default_branch'))]


def get_project_branch(rd, project_id, branch_name):
    """ Get Project's Branch
    :param rd: Redis Object Instance
    :param project_id: Project Identifier (int)
    :param branch_name: Branch Identifier (string)
    :return: Branch (Object)
    """
    gl_branch = rd.hgetall("projects:" + str(project_id) + ":branches:" + branch_name)
    if bool(gl_branch) is False:
        return False
    else:
        return gl_branch


def get_project_branch_contributors(rd, project_id, branch_name, t_window):
    """ Get Branch's Contributors
    :param rd: Redis Object Instance
    :param project_id: Project Identifier (int)
    :param branch_name: Branch Identifier (string)
    :param t_window: (Time Window) filter (Object)
    :return: Contributors (List)
    """
    return get_contributors_projects(rd, project_id, branch_name, t_window)


def get_project_branch_commits(rd, project_id, branch_name, user_id, offset, t_window, details):
    """ Get Branch's Commits
    :param rd: Redis Object Instance
    :param project_id: Project Identifier (int)
    :param branch_name: Branch Identifier (string)
    :param user_id: Optional User Identifier (int)
    :param offset: Optional Offset parameter (int)
    :param t_window: (Time Window) filter (Object)
    :param details: Commit details (bool)
    :return: Commits (List)
    """
    user = None
    if user_id is not None:
        user = get_user(rd, user_id)
        if user is False:
            return False
    if get_project_branch(rd, project_id, branch_name) is False:
        return False
    git_commits = rd.zrange("projects:" + str(project_id) + ":branches:" + branch_name + ":commits:",
                            t_window.get('st_time'), t_window.get('en_time'))
    git_commits = map(lambda w: rd.hgetall(w), git_commits)

    # Filter by user
    if user is not None:
        git_commits_user = []
        for x in git_commits:
            if x.get('author_email') == user.get('email'):
                git_commits_user.append(x)
        git_commits = git_commits_user

    # Offset and Return ids
    if offset is not None:
        return git_commits[offset:]
    if details is False:
        return map(lambda k: k.get('id'), git_commits)
    else:
        return git_commits


def get_project_commits(rd, project_id, user_id, offset, t_window, details):
    """ Get Project's Commits
    :param rd: Redis Object Instance
    :param project_id: Project Identifier (int)
    :param user_id: Optional User Identifier (int)
    :param offset: Optional Offset parameter (int)
    :param t_window: (Time Window) filter (Object)
    :param details: Project details (bool)
    :return: Commits (List)
    """
    ret_commits_hash = {}
    git_branches = get_project_branches(rd, project_id, 'false', False)
    if git_branches is False:
        return False
    for i in git_branches:
        c = get_project_branch_commits(rd, project_id, i, user_id, offset, t_window, False)
        [ret_commits_hash.update({x: '1'}) for x in c if (x not in ret_commits_hash)]
    if details is False:
        return ret_commits_hash.keys()
    else:
        [ret_commits_hash.update({x: get_project_commit(rd, project_id, x)}) for x in ret_commits_hash.keys()]
        return ret_commits_hash


def get_project_commit(rd, project_id, commit_id):
    """ Get Project's Commit
    :param rd: Redis Object Instance
    :param project_id: Project Identifier (int)
    :param commit_id: Commit Identifier (sha)
    :return: Commit (Object)
    """
    git_commit = rd.hgetall("projects:" + str(project_id) + ":commits:" + commit_id)
    if bool(git_commit) is False:
        return False
    else:
        return git_commit


def get_project_requests(rd, project_id, request_state):
    """ Get Project's Merge Requests
    :param rd: Redis Object Instance
    :param project_id: Project Identifier (int)
    :param request_state: Optional Type Identifier (string)
    :return: Merge Requests (List)
    """
    return False


def get_project_request(rd, project_id, request_id):
    """ Get Project's Merge Request
    :param rd: Redis Object Instance
    :param project_id: Project Identifier (int)
    :param request_id: Merge Request Identifier (int)
    :return: Merge Request (Object)
    """
    return False


def get_project_request_changes(rd, project_id, request_id):
    """ Get Merge Request's Changes
    :param rd: Redis Object Instance
    :param project_id: Project Identifier (int)
    :param request_id: Merge Request Identifier (int)
    :return: Changes (List)
    """
    return False


def get_project_contributors(rd, project_id, t_window):
    """ Get Project's Contributors
    :param rd: Redis Object Instance
    :param project_id: Project Identifier (int)
    :param t_window: (Time Window) filter (Object)
    :return: Contributors (List)
    """
    return get_contributors_projects(rd, project_id, None, t_window)


def get_users(rd, offset):
    """ Get Users
    :param rd: Redis Object Instance
    :param offset: Optional Offset parameter (int)
    :return: Users (List)
    """
    red_u = map(lambda w: int(w.split(':')[1]), rd.keys("users:*"))
    u = []
    [u.append(x) for x in red_u if x not in u]
    if offset is not None:
        return u[offset:]
    else:
        return u


def get_user(rd, user_id):
    """ Get User
    :param rd: Redis Object Instance
    :return: User (Object)
    """
    git_user = rd.hgetall("users:" + str(user_id))
    if bool(git_user) is False:
        return False
    else:
        return git_user


def get_user_projects(rd, user_id, relation_type, t_window):
    """ Get User's Projects
    :param rd: Redis Object Instance
    :param user_id: User Identifier (int)
    :param relation_type: Relation between User-Project
    :param t_window: (Time Window) filter (Object)
    :return: Projects (List)
    """
    git_user = rd.hgetall("users:" + str(user_id))
    if bool(git_user) is False:
        return False
    return get_entity_projects(rd, user_id, relation_type, 'users', t_window)


def get_groups(rd):
    """ Get Groups
    :param rd: Redis Object Instance
    :return: Groups (List)
    """
    red_g = map(lambda w: int(w.split(':')[1]), rd.keys("groups:*"))
    g = []
    [g.append(x) for x in red_g if x not in g]
    if len(g) == 0:
        return False
    else:
        return g


def get_group(rd, group_id):
    """ Get Group
    :param rd: Redis Object Instance
    :param group_id: Group Identifier (int)
    :return: Group (Object)
    """
    git_group = rd.hgetall("groups:" + str(group_id))
    if bool(git_group) is False:
        return False
    else:
        g_m = rd.lrange("groups:2:members", 0, -1)
        git_group['members'] = map(lambda x: x.split(":")[1], g_m)
        return git_group


def get_group_projects(rd, group_id, relation_type, t_window):
    """ Get Group's Projects
    :param rd: Redis Object Instance
    :param group_id: Group Identifier (int)
    :param relation_type: Relation between User-Project
    :param t_window: (Time Window) filter (Object)
    :return: Projects (List)
    """
    git_group = rd.hgetall("groups:" + str(group_id))
    if bool(git_group) is False:
        return False
    return get_entity_projects(rd, group_id, relation_type, 'groups', t_window)


# Functions to help another functions


# TODO: Source Code - Language (Language Mapping)
# "projects:id:commits:sha[language]" = {'language': 'number_files'}
#     "projects:id:branches:name[language]" = {'language': 'number_files'}
#     "projects:id[language]" = top_language_value in project
#     "users:id[favourite_language]" = top_language_value
def get_language_by_extension(ext):
    return "code"


def get_entity_projects(rd, entity_id, relation_type, user_type, t_window):

    # Get Entity's projects
    git_projects_details = get_projects(rd, True)
    git_ret = []
    if relation_type == 'owner':
        [git_ret.append(k.get('id')) for k in git_projects_details
         if k.get('owner').get('type') == user_type and k.get('owner').get('id') == str(entity_id)]
    else:
        for x in git_projects_details:
            users_list = get_contributors_projects(rd, x.get('id'), None, t_window)

            # Search through group's members
            if user_type == 'groups':
                g_m = get_group(rd, entity_id).get('members')
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


def get_contributors_projects(rd, project_id, branch_name, t_window):
    user_unique = []
    u = get_users(rd, None)
    user_temp = []
    for i in u:

        # Specific Branch
        if branch_name is not None:
            c = rd.zrange("users:" + str(i) + ":projects:" + str(project_id) + ":branches:" + branch_name + ":commits:",
                          t_window.get('st_time'), t_window.get('en_time'))

        # Generic Project (all branches)
        else:
            c = rd.zrange("users:" + str(i) + ":projects:" + str(project_id) + ":commits:",
                          t_window.get('st_time'), t_window.get('en_time'))
        if len(c) > 0:
            user_temp.append(i)

    [user_unique.append(k) for k in user_temp if k not in user_unique]
    user_unique.sort()
    return user_unique