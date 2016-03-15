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
import utils

__author__ = 'Alejandro F. Carrera'


def get_projects(rd):
    """ Get Projects
    :param rd: Redis Object Instance
    :return: Projects (List)
    """
    red_p = map(lambda w: int(w.split('_')[1]), rd.get("rd_instance_pr").keys("*"))
    red_p.sort()
    return red_p


def get_project(rd, project_id):
    """ Get Project
    :param rd: Redis Object Instance
    :param project_id: Project Identifier (int)
    :return: Project (Object)
    """

    # Repository fields
    # "first_commit_at", "archived", "last_activity_at", "name",
    # "contributors", "tags", "created_at", "default_branch",
    # "id", "http_url_to_repo", "web_url", "owner", "last_commit_at",
    # "public", "avatar_url"

    git_project = rd.get("rd_instance_pr").hgetall("p_" + str(project_id))
    if bool(git_project) is False:
        return False
    else:
        git_project['owner'] = {
            'type': "user" if str(git_project['owner']).startswith("u_") else "group" ,
            'id': int(git_project.get('owner').split("_")[1]),
        }
        git_project['id'] = int(git_project.get('id'))
        if git_project.get('tags'):
            git_project['tags'] = eval(git_project.get('tags'))
        git_project['contributors'] = utils.get_project_contributors(rd, project_id)
        git_commit_at = utils.get_project_commit_at(rd, project_id)
        git_project['first_commit_at'] = git_commit_at.get('first_commit_at')
        git_project['last_commit_at'] = git_commit_at.get('last_commit_at')
        if 'default_branch' in git_project:
            git_project['default_branch'] = base64.b16encode(git_project.get('default_branch'))
        utils.convert_time_keys(git_project)
        return git_project


def get_project_owner(rd, project_id):
    """ Get Project's Owner
    :param rd: Redis Object Instance
    :param project_id: Project Identifier (int)
    :return: Owner (User Object | Group Object)
    """
    git_project = rd.get("rd_instance_pr").hgetall("p_" + str(project_id))
    if bool(git_project) is False:
        return False
    else:
        owner_id = int(git_project.get('owner').split("_")[1])
        if str(git_project['owner']).startswith("u_"):
            u = get_user(rd, owner_id)
            u['type'] = 'user'
        else:
            u = get_group(rd, owner_id)
            u['type'] = 'group'
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
        gl_b = rd.get("rd_instance_br").keys("p_" + str(project_id) + ":*")
        gl_b = map(lambda w: w.split(":")[1], gl_b)
        if len(gl_b) == 0:
            return False
        return gl_b
    else:
        git_project = get_project(rd, project_id)
        if git_project is False:
            return False
        else:
            return [git_project.get('default_branch')]


def get_project_branch(rd, project_id, branch_name):
    """ Get Project's Branch
    :param rd: Redis Object Instance
    :param project_id: Project Identifier (int)
    :param branch_name: Branch Identifier (string)
    :return: Branch (Object)
    """

    # Branch fields
    # "name", "created_at", "protected", "contributors",
    # "last_commit"

    git_branch = rd.get("rd_instance_br").hgetall("p_" + str(project_id) + ":" + branch_name)
    if bool(git_branch) is False:
        return False
    else:
        git_commit_at = utils.get_branch_commit_at(rd, project_id, branch_name)
        git_branch['created_at'] = git_commit_at.get('first_commit_at')
        git_branch['last_commit_at'] = git_commit_at.get('last_commit_at')
        git_branch['contributors'] = eval(git_branch.get('contributors'))
        utils.convert_time_keys(git_branch)
        return git_branch


def get_project_branch_contributors(rd, project_id, branch_name):
    """ Get Branch's Contributors
    :param rd: Redis Object Instance
    :param project_id: Project Identifier (int)
    :param branch_name: Branch Identifier (string)
    :return: Contributors (List)
    """
    git_branch = get_project_branch(rd, project_id, branch_name)
    if git_branch is False:
        return False
    else:
        return git_branch.get("contributors")


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

    # Search and Filter by time
    git_commits = rd.get("rd_instance_br_co").zrange(
        "p_" + str(project_id) + ":" + branch_name,
        t_window.get('st_time'), t_window.get('en_time')
    )

    # Filter by user
    if user is not None:
        emails = user.get("emails")
        emails = map(lambda w: base64.b16encode(w), emails)
        git_commits_val = map(lambda w: rd.get("rd_instance_co").hgetall(w), git_commits)
        git_commits_dict = dict(zip(git_commits, git_commits_val))
        git_commits_user = set()
        for x in git_commits_dict.keys():
            if git_commits_dict[x].get('author') in emails:
                git_commits_user.add(x)
        git_commits = list(git_commits_user)

    # Clean commits' id
    return map(lambda w: str(w).split(":")[1], git_commits)


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
    if get_project(rd, project_id) is False:
        return False

    # Search and Filter by time
    git_branches = get_project_branches(rd, project_id, 'false')
    if git_branches is False:
        return []
    br_co = set()
    for i in git_branches:
        br_co = br_co.union(set(get_project_branch_commits(rd, project_id, i, user_id, t_window)))
    return list(br_co)


def get_project_commit(rd, project_id, commit_id):
    """ Get Project's Commit
    :param rd: Redis Object Instance
    :param project_id: Project Identifier (int)
    :param commit_id: Commit Identifier (sha)
    :return: Commit (Object)
    """

    # "lines_removed", "short_id", "author", "lines_added",
    # "created_at", "title", "parent_ids", "committed_date",
    # "message", "authored_date", "id"

    git_commit = rd.get("rd_instance_co").hgetall("p_" + str(project_id) + ":" + commit_id)
    if bool(git_commit) is False:
        return False
    else:
        git_commit['lines_removed'] = int(git_commit.get('lines_removed'))
        git_commit['lines_added'] = int(git_commit.get('lines_added'))
        git_commit['files_changed'] = int(git_commit.get('files_changed'))
        git_commit['author'] = str(utils.get_user_identifier(rd, git_commit['author']))
        utils.convert_time_keys(git_commit)
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


def get_project_contributors(rd, project_id):
    """ Get Project's Contributors
    :param rd: Redis Object Instance
    :param project_id: Project Identifier (int)
    :return: Contributors (List)
    """
    return get_project(rd, project_id).get("contributors")


def get_users(rd):
    """ Get Users
    :param rd: Redis Object Instance
    :return: Users (List)
    """
    red_u = map(lambda w: int(w.split('_')[1]), rd.get("rd_instance_us").keys("u_*"))
    red_u.sort()
    return red_u


def get_user(rd, user_id):
    """ Get User
    :param rd: Redis Object Instance
    :param user_id: User or Committer identifier
    :return: User (Object)
    """

    # User fields
    # "username", "first_commit_at", "name", "created_at",
    # "email", "state", "avatar_url", "last_commit_at", "id",
    # "external"

    # Commiter fields
    # "first_commit_at", "email", "last_commit_at", "id",
    # "external"

    git_user = rd.get("rd_instance_us").hgetall("u_" + str(user_id))
    if bool(git_user) is False:
        git_user = rd.get("rd_instance_us_co").keys(str(user_id))
        if len(git_user) > 0:
            git_user = {
                'email': base64.b16decode(str(user_id)),
                'emails': [base64.b16decode(str(user_id))],
                'id': str(user_id),
                'external': True
            }
            user_commit_at = utils.get_user_commit_at(rd, user_id, True, None)
            git_user['first_commit_at'] = user_commit_at.get('first_commit_at')
            git_user['last_commit_at'] = user_commit_at.get('last_commit_at')
            utils.convert_time_keys(git_user)
            return git_user
        else:
            return False
    else:
        git_user['email'] = str(git_user.get('primary_email'))
        git_user['id'] = str(git_user.get('id'))
        git_user['emails'] = eval(git_user['emails'])
        git_user['external'] = False
        user_commit_at = utils.get_user_commit_at(rd, None, False, git_user['emails'])
        git_user['first_commit_at'] = user_commit_at.get('first_commit_at')
        git_user['last_commit_at'] = user_commit_at.get('last_commit_at')
        del git_user['primary_email']
        utils.convert_time_keys(git_user)
        return git_user


def get_user_projects(rd, user_id, relation_type):
    """ Get User's Projects
    :param rd: Redis Object Instance
    :param user_id: User Identifier (int)
    :param relation_type: Relation between User-Project
    :return: Projects (List)
    """
    if relation_type == 'contributor':
        git_ret = set()
        git_projects = get_projects(rd)
        for k in git_projects:
            o = get_project(rd, k)
            if str(user_id) in o.get("contributors"):
                git_ret.add(k)
        return list(git_ret)
    else:
        git_user = rd.get("rd_instance_us").hgetall("u_" + str(user_id))
        if bool(git_user) is False:
            return False
        else:
            git_ret = set()
            git_projects = get_projects(rd)
            for k in git_projects:
                o = get_project_owner(rd, k)
                if str(user_id) == str(o.get("id")) and str(o.get('type')) == 'user':
                    git_ret.add(k)
            return list(git_ret)


def get_groups(rd):
    """ Get Groups
    :param rd: Redis Object Instance
    :return: Groups (List)
    """
    red_g = map(lambda w: int(w.split('_')[1]), rd.get("rd_instance_us").keys("g_*"))
    red_g.sort()
    return red_g


def get_group(rd, group_id):
    """ Get Group
    :param rd: Redis Object Instance
    :param group_id: Group Identifier (int)
    :return: Group (Object)
    """
    git_group = rd.get("rd_instance_us").hgetall("g_" + str(group_id))
    if bool(git_group) is False:
        return False
    else:
        git_group['id'] = int(git_group.get('id'))
        m = eval(git_group.get('members'))
        new_m = []
        for i in m:
            new_m.append(str(i).replace("u_", ""))
        git_group['members'] = new_m
        return git_group


def get_group_projects(rd, group_id, relation_type):
    """ Get Group's Projects
    :param rd: Redis Object Instance
    :param group_id: Group Identifier (int)
    :param relation_type: Relation between User-Project
    :return: Projects (List)
    """
    group = get_group(rd, group_id)
    if group is False:
        return False
    if relation_type == 'contributor':
        git_ret = set()
        for i in group.get('members'):
            g = get_user_projects(rd, i, 'contributor')
            git_ret.union(set(g))
        return list(git_ret)
    else:
        git_ret = set()
        git_projects = get_projects(rd)
        for k in git_projects:
            o = get_project_owner(rd, k)
            if str(group_id) == str(o.get("id")) and str(o.get('type')) == 'group':
                git_ret.add(k)
        return list(git_ret)
