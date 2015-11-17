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

import base64

__author__ = 'Alejandro F. Carrera'


def get_projects(rd):
    """ Get Projects
    :param rd: Redis Object Instance
    :return: Projects (List)
    """
    red_p = map(lambda w: int(w.split(':')[1]), rd.keys("projects:*:"))
    p = []
    [p.append(x) for x in red_p if x not in p]
    p.sort()
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
        git_project['owner'] = {
            'type': git_project.get('owner').split(":")[0],
            'id': int(git_project.get('owner').split(":")[1]),
        }
        git_project['id'] = int(git_project.get('id'))
        if git_project.get('tags'):
            git_project['tags'] = eval(git_project.get('tags'))
        if git_project.get('contributors'):
            git_project['contributors'] = eval(git_project.get('contributors'))
        convert_time_keys(git_project)
        git_project['default_branch_name'] = git_project['default_branch']
        git_project['default_branch'] = base64.b16encode(git_project['default_branch'])
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
        u = get_group(rd, git_project.get('owner').get('id'))
        u['type'] = 'group'
    else:
        u = get_user(rd, git_project.get('owner').get('id'))
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


def get_project_branches(rd, project_id, default_flag):
    """ Get Project's Branches
    :param rd: Redis Object Instance
    :param project_id: Project Identifier (int)
    :param default_flag: Filter by type (bool)
    :return: Branches (List)
    """
    if default_flag == 'false':
        gl_b = rd.keys("projects:" + str(project_id) + ":branches:*")
        gl_b = map(lambda w: base64.b16encode(w.split(":")[3]), gl_b)
        if len(gl_b) == 0:
            return False
        gl_b_un = []
        [gl_b_un.append(x) for x in gl_b if x not in gl_b_un]
        return gl_b_un
    else:
        git_project = get_project(rd, project_id)
        if git_project is False:
            return False
        else:
            return [base64.b16encode(git_project.get('default_branch'))]


def get_project_branch(rd, project_id, branch_name):
    """ Get Project's Branch
    :param rd: Redis Object Instance
    :param project_id: Project Identifier (int)
    :param branch_name: Branch Identifier (string)
    :return: Branch (Object)
    """
    branch_name = base64.b16decode(branch_name)
    git_branch = rd.hgetall("projects:" + str(project_id) + ":branches:" + branch_name)
    if bool(git_branch) is False:
        return False
    else:
        convert_time_keys(git_branch)
        git_branch['contributors'] = eval(git_branch.get('contributors'))
        return git_branch


def get_project_branch_contributors(rd, project_id, branch_name, t_window):
    """ Get Branch's Contributors
    :param rd: Redis Object Instance
    :param project_id: Project Identifier (int)
    :param branch_name: Branch Identifier (string)
    :param t_window: (Time Window) filter (Object)
    :return: Contributors (List)
    """
    return get_contributors_projects(rd, project_id, branch_name, t_window)


def get_project_branch_commits(rd, project_id, branch_name, user_id, t_window):
    """ Get Branch's Commits
    :param rd: Redis Object Instance
    :param project_id: Project Identifier (int)
    :param branch_name: Branch Identifier (string)
    :param user_id: Optional User Identifier (int)
    :param t_window: (Time Window) filter (Object)
    :return: Commits (List)
    """
    user = None
    if user_id is not None:
        user = get_user(rd, user_id)
        if user is False:
            return False
    if get_project_branch(rd, project_id, branch_name) is False:
        return False

    branch_name = base64.b16decode(branch_name)
    # Search and Filter by time
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

    return map(lambda k: k.get('id'), git_commits)


def get_project_commits(rd, project_id, user_id, t_window):
    """ Get Project's Commits
    :param rd: Redis Object Instance
    :param project_id: Project Identifier (int)
    :param user_id: Optional User Identifier (int)
    :param t_window: (Time Window) filter (Object)
    :return: Commits (List)
    """
    user = None
    if user_id is not None:
        user = get_user(rd, user_id)
        if user is False:
            return False

    # Search and Filter by time
    git_commits = rd.zrange("projects:" + str(project_id) + ":commits:",
                            t_window.get('st_time'), t_window.get('en_time'))
    git_commits = map(lambda w: rd.hgetall(w), git_commits)

    # Filter by user
    if user is not None:
        git_commits_user = []
        for x in git_commits:
            if x.get('author_email') == user.get('email'):
                git_commits_user.append(x)
        git_commits = git_commits_user

    return map(lambda k: k.get('id'), git_commits)


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
        git_commit['lines_removed'] = int(git_commit.get('lines_removed'))
        git_commit['lines_added'] = int(git_commit.get('lines_added'))
        git_commit['author'] = int(git_commit.get('author'))
        git_commit['parent_ids'] = eval(git_commit.get('parent_ids'))
        convert_time_keys(git_commit)
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


def get_users(rd):
    """ Get Users
    :param rd: Redis Object Instance
    :return: Users (List)
    """
    red_u = map(lambda w: int(w.split(':')[1]), rd.keys("users:*:"))
    u = []
    [u.append(x) for x in red_u if x not in u]
    u.sort()
    return u


def get_user(rd, user_id):
    """ Get User
    :param rd: Redis Object Instance
    :return: User (Object)
    """
    git_user = rd.hgetall("users:" + str(user_id) + ":")
    if bool(git_user) is False:
        return False
    else:
        git_user['id'] = int(git_user.get('id'))
        convert_time_keys(git_user)
        return git_user


def get_user_projects(rd, user_id, relation_type, t_window):
    """ Get User's Projects
    :param rd: Redis Object Instance
    :param user_id: User Identifier (int)
    :param relation_type: Relation between User-Project
    :param t_window: (Time Window) filter (Object)
    :return: Projects (List)
    """
    git_user = rd.hgetall("users:" + str(user_id) + ":")
    if bool(git_user) is False:
        return False
    return get_entity_projects(rd, user_id, relation_type, 'users', t_window)


def get_groups(rd):
    """ Get Groups
    :param rd: Redis Object Instance
    :return: Groups (List)
    """
    red_g = map(lambda w: int(w.split(':')[1]), rd.keys("groups:*:"))
    g = []
    [g.append(x) for x in red_g if x not in g]
    return g


def get_group(rd, group_id):
    """ Get Group
    :param rd: Redis Object Instance
    :param group_id: Group Identifier (int)
    :return: Group (Object)
    """
    git_group = rd.hgetall("groups:" + str(group_id) + ":")
    if bool(git_group) is False:
        return False
    else:
        git_group['id'] = int(git_group.get('id'))
        git_group['members'] = eval(git_group.get('members'))
        return git_group


def get_group_projects(rd, group_id, relation_type, t_window):
    """ Get Group's Projects
    :param rd: Redis Object Instance
    :param group_id: Group Identifier (int)
    :param relation_type: Relation between User-Project
    :param t_window: (Time Window) filter (Object)
    :return: Projects (List)
    """
    git_group = rd.hgetall("groups:" + str(group_id) + ":")
    if bool(git_group) is False:
        return False
    return get_entity_projects(rd, group_id, relation_type, 'groups', t_window)


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
                    if o[k].find(".", 0, len(o[k])) > 0:
                        o[k] = o[k].split(".")[0]
                    o[k] = long(o[k])


def get_entity_projects(rd, entity_id, relation_type, user_type, t_window):

    # Get Entity's projects
    git_projects = get_projects(rd)

    git_ret = []
    if user_type == 'groups':
        g_m = get_group(rd, entity_id).get('members')
    if relation_type == 'owner':
        user_type = user_type[:-1]

    for k in git_projects:
        if relation_type == 'owner':
            o = get_project_owner(rd, k)
            if o.get('type') == user_type and o.get('id') == entity_id:
                git_ret.append(k)
        else:
            c = get_project_contributors(rd, k, t_window)
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


def get_contributors_projects(rd, project_id, branch_name, t_window):

    ret_users = {}

    # Search and Filter by time
    if branch_name is not None:
        branch_name = base64.b16decode(branch_name)
        git_commits = rd.zrange("projects:" + str(project_id) + ":branches:" + branch_name + ":commits:",
                                t_window.get('st_time'), t_window.get('en_time'))
    else:
        git_commits = rd.zrange("projects:" + str(project_id) + ":commits:",
                                t_window.get('st_time'), t_window.get('en_time'))
    git_commits = map(lambda j: rd.hgetall(j), git_commits)

    # Get Users emails and identifiers
    git_users = get_users(rd)

    for w in git_commits:
        if int(w.get('author')) in git_users:
            ret_users[w.get('author')] = '1'

    ret_users = ret_users.keys()
    ret_users = map(lambda x: int(x), ret_users)
    ret_users.sort()
    return ret_users
