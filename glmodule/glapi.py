__author__ = 'alejandrofcarrera'

import operator


def get_projects(gl):
    """ Get Projects
    :param gl: GitLab Object Instance
    :return: Projects (List)
    """
    return gl.git.getprojectsall()


def get_project(gl, project_id):
    """ Get Project
    :param gl: GitLab Object Instance
    :param project_id: Project Identifier (int)
    :return: Project (Object)
    """
    return gl.git.getproject(project_id)


def get_project_owner(gl, project_id):
    """ Get Project's Owner
    :param gl: GitLab Object Instance
    :param project_id: Project Identifier (int)
    :return: Owner (User Object | Group Object)
    """
    git_project = get_project(gl, project_id)
    if git_project is False:
        return git_project

    # Owner is a group
    if git_project.get('owner') is None:
        git_owner = get_group(gl, git_project.get('namespace').get('id'))
        git_owner['type'] = 'group'

    # Owner is a user
    else:
        git_owner = git_project.get('owner')
        git_owner['type'] = 'user'

    return git_owner


def get_project_milestones(gl, project_id):
    """ Get Project's Milestones
    :param gl: GitLab Object Instance
    :param project_id: Project Identifier (int)
    :return: Milestones (List)
    """
    return gl.git.getmilestones(project_id)


def get_project_milestone(gl, project_id, milestone_id):
    """ Get Project's Milestone
    :param gl: GitLab Object Instance
    :param project_id: Project Identifier (int)
    :param milestone_id: Milestone Identifier (int)
    :return: Milestone (Object)
    """
    return gl.git.getmilestone(project_id, milestone_id)


def get_project_branches(gl, project_id, default_flag):
    """ Get Project's Branches
    :param gl: GitLab Object Instance
    :param project_id: Project Identifier (int)
    :param default_flag: Filter by type (bool)
    :return: Branches (List)
    """
    if default_flag is False:
        return gl.git.getbranches(project_id)
    else:
        git_project = get_project(gl, project_id)
        if git_project is False:
            return git_project
        return [get_project_branch(gl, project_id, git_project.get('default_branch'))]


def get_project_branch(gl, project_id, branch_name):
    """ Get Project's Branch
    :param gl: GitLab Object Instance
    :param project_id: Project Identifier (int)
    :param branch_name: Branch Identifier (string)
    :return: Branch (Object)
    """
    return gl.git.getbranch(project_id, branch_name)


def get_project_branch_contributors(gl, project_id, branch_name):
    """ Get Branch's Contributors
    :param gl: GitLab Object Instance
    :param project_id: Project Identifier (int)
    :param branch_name: Branch Identifier (string)
    :return: Contributors (List)
    """
    return get_contributors_projects(gl, project_id, branch_name)


def get_project_branch_commits(gl, project_id, branch_name, user_id, offset):
    """ Get Branch's Commits
    :param gl: GitLab Object Instance
    :param project_id: Project Identifier (int)
    :param branch_name: Branch Identifier (string)
    :param user_id: Optional User Identifier (int)
    :param offset: Optional Offset parameter (int)
    :return: Commits (List)
    """
    pag = 1
    number_page = 100
    user = None
    if offset is not None:
        pag = 2
        number_page = offset
    ret_commits = []
    git_commits_len = -1
    if user_id is not None:
        user = get_user(gl, user_id)
        if user is False:
            return user
    while git_commits_len is not 0:
        git_commits = gl.git.getrepositorycommits(project_id, branch_name, page=pag, per_page=number_page)
        if git_commits is False:
            return git_commits
        git_commits_len = len(git_commits)
        if user is not None:
            git_ret = []
            for x in git_commits:
                if x.get('author_email') == user.get('email'):
                    git_ret.append(x)
            ret_commits += git_ret
        else:
            ret_commits += git_commits
        pag += 1
    return ret_commits


def get_project_commits(gl, project_id, user_id, offset):
    """ Get Project's Commits
    :param gl: GitLab Object Instance
    :param project_id: Project Identifier (int)
    :param user_id: Optional User Identifier (int)
    :param offset: Optional Offset parameter (int)
    :return: Commits (List)
    """
    pag = 1
    number_page = 100
    user = None
    if offset is not None:
        pag = 2
        number_page = offset
    ret_commits_hash = {}
    ret_commits = []
    if user_id is not None:
        user = get_user(gl, user_id)
        if user is False:
            return user
    git_branches = get_project_branches(gl, project_id)
    if git_branches is False:
        return False
    for i in git_branches:
        git_commits_len = -1
        while git_commits_len is not 0:
            git_commits = gl.git.getrepositorycommits(project_id, i.get('name'), page=pag, per_page=number_page)
            git_commits_len = len(git_commits)
            for x in git_commits:
                if ret_commits_hash.get(x.get('id')) is None:
                    if user is None:
                        ret_commits_hash[x.get('id')] = x
                        ret_commits.append(x)
                    else:
                        if x.get('author_email') == user.get('email'):
                            ret_commits_hash[x.get('id')] = x
                            ret_commits.append(x)
            pag += 1
    return ret_commits


def get_project_commit(gl, project_id, commit_id):
    """ Get Project's Commit
    :param gl: GitLab Object Instance
    :param project_id: Project Identifier (int)
    :param commit_id: Commit Identifier (sha)
    :return: Commit (Object)
    """
    return gl.git.getrepositorycommit(project_id, commit_id)


def get_project_commit_diff(gl, project_id, commit_id):
    """ Get Commit's Differences
    :param gl: GitLab Object Instance
    :param project_id: Project Identifier (int)
    :param commit_id: Commit Identifier (sha)
    :return: Differences (Object)
    """
    return gl.git.getrepositorycommitdiff(project_id, commit_id)


def get_project_requests(gl, project_id, request_state):
    """ Get Project's Merge Requests
    :param gl: GitLab Object Instance
    :param project_id: Project Identifier (int)
    :param request_state: Optional Type Identifier (string)
    :return: Merge Requests (List)
    """
    return gl.git.getmergerequests(project_id=project_id, state=request_state)


def get_project_request(gl, project_id, request_id):
    """ Get Project's Merge Request
    :param gl: GitLab Object Instance
    :param project_id: Project Identifier (int)
    :param request_id: Merge Request Identifier (int)
    :return: Merge Request (Object)
    """
    return gl.git.getmergerequest(project_id, request_id)


def get_project_request_changes(gl, project_id, request_id):
    """ Get Merge Request's Changes
    :param gl: GitLab Object Instance
    :param project_id: Project Identifier (int)
    :param request_id: Merge Request Identifier (int)
    :return: Changes (List)
    """
    return gl.git.getmergerequestchanges(project_id, request_id)


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
    first_step = gl.git.getrepositorytree(project_id, ref_name=branch_name, path=path)
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


def get_project_contributors(gl, project_id):
    """ Get Project's Contributors
    :param gl: GitLab Object Instance
    :param project_id: Project Identifier (int)
    :return: Contributors (List)
    """
    return get_contributors_projects(gl, project_id, None)


def get_users(gl, offset):
    """ Get Users
    :param gl: GitLab Object Instance
    :param offset: Optional Offset parameter (int)
    :return: Users (List)
    """
    pag = 1
    number_page = 50
    if offset is not None:
        pag = 2
        number_page = offset
    ret_users = []
    git_users_len = -1
    while git_users_len is not 0:
        git_users = gl.git.getusers(page=pag, per_page=number_page)
        git_users_len = len(git_users)
        ret_users += git_users
        pag += 1
    return ret_users


def get_user(gl, user_id):
    """ Get User
    :param gl: GitLab Object Instance
    :return: User (Object)
    """
    return gl.git.getuser(user_id)


def get_user_projects(gl, user_id, relation_type):
    """ Get User's Projects
    :param gl: GitLab Object Instance
    :param user_id: User Identifier (int)
    :param relation_type: Relation between User-Project
    :return: Projects (List)
    """
    return get_entity_projects(gl, user_id, relation_type)


def get_groups(gl):
    """ Get Groups
    :param gl: GitLab Object Instance
    :return: Groups (List)
    """
    git_groups = gl.git.getgroups()
    for x in git_groups:
        x['members'] = gl.git.getgroupmembers(x.get('id'))
    return git_groups


def get_group(gl, group_id):
    """ Get Group
    :param gl: GitLab Object Instance
    :param group_id: Group Identifier (int)
    :return: Group (Object)
    """
    git_groups = gl.git.getgroups()
    for x in git_groups:
        if x.get('id') == group_id:
            x['members'] = gl.git.getgroupmembers(x.get('id'))
            return x
    return False


def get_group_projects(gl, group_id, relation_type):
    """ Get Group's Projects
    :param gl: GitLab Object Instance
    :param group_id: Group Identifier (int)
    :param relation_type: Relation between User-Project
    :return: Projects (List)
    """
    return get_entity_projects(gl, group_id, relation_type)


# Functions to help another functions


def get_entity_projects(gl, entity_id, relation_type):

    # Entity (user or group) is not exist
    if get_user(gl, entity_id) is False:
        if get_group(gl, entity_id) is False:
            return False

    # Get Entity's projects
    git_projects = get_projects(gl)
    git_user_projects = []
    for x in git_projects:
        if relation_type == 'owner':
            if entity_id == get_project_owner(gl, x.get('id')).get('id'):
                git_user_projects.append(x)
        else:
            users_list = get_project_contributors(gl, x.get('id'), x.get('default_branch'))
            for j in users_list:
                if entity_id == j.get('id'):
                    git_user_projects.append(x)

    return git_user_projects


def get_contributors_projects(gl, project_id, branch_name):

    # Specific Branch
    if branch_name is not None:
        commits_list = get_project_branch_commits(gl, project_id, branch_name, None, None)

    # Generic Project (all branches)
    else:
        commits_list = get_project_commits(gl, project_id, None, None)
    if commits_list is False:
        return commits_list
    email_list = {}
    ret_users = {}
    for x in commits_list:
        if email_list.get(x.get('author_email')) is None:
            email_list[x.get('author_email')] = 1
    git_users = get_users(gl, None)
    for j in git_users:
        for x in email_list:
            if j.get('email') == x:
                ret_users[x] = j
    return ret_users