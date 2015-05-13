__author__ = 'alejandrofcarrera'

from dateutil import parser


def get_projects(gl):
    """ Get Projects
    :param gl: GitLab Object Instance
    :return: Projects (List)
    """
    git_projects = gl.getprojectsall()
    for x in git_projects:
        convert_time_keys(x)
        if x.get('owner'):
            del x['owner']
    return git_projects


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

    # Owner is a group
    if git_project.get('owner') is None:
        git_owner = get_group(gl, git_project.get('namespace').get('id'))
        git_owner['type'] = 'group'

    # Owner is a user
    else:
        git_owner = get_user(gl, git_project.get('owner').get('id'))
        git_owner['type'] = 'user'

    return git_owner


def get_project_milestones(gl, project_id):
    """ Get Project's Milestones
    :param gl: GitLab Object Instance
    :param project_id: Project Identifier (int)
    :return: Milestones (List)
    """
    git_miles = gl.getmilestones(project_id)
    if git_miles is False:
        return False
    else:
        for x in git_miles:
            convert_time_keys(x)
        return git_miles


def get_project_milestone(gl, project_id, milestone_id):
    """ Get Project's Milestone
    :param gl: GitLab Object Instance
    :param project_id: Project Identifier (int)
    :param milestone_id: Milestone Identifier (int)
    :return: Milestone (Object)
    """
    git_mile = gl.getmilestone(project_id, milestone_id)
    if git_mile is False:
        return False
    else:
        convert_time_keys(git_mile)
        return git_mile


def get_project_branches(gl, project_id, default_flag):
    """ Get Project's Branches
    :param gl: GitLab Object Instance
    :param project_id: Project Identifier (int)
    :param default_flag: Filter by type (bool)
    :return: Branches (List)
    """
    if default_flag == 'false':
        gl_branches = gl.getbranches(project_id)
        if gl_branches is False:
            return False
        else:
            for x in gl_branches:
                convert_time_keys(x)
            return gl_branches
    else:
        git_project = get_project(gl, project_id)
        if git_project is False:
            return False
        else:
            gl_branches = get_project_branch(gl, project_id, git_project.get('default_branch'))
            if gl_branches is False:
                return False
            else:
                return [gl_branches]


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
        convert_time_keys(gl_branch)
        return gl_branch


def get_project_branch_contributors(gl, project_id, branch_name, st_time, en_time):
    """ Get Branch's Contributors
    :param gl: GitLab Object Instance
    :param project_id: Project Identifier (int)
    :param branch_name: Branch Identifier (string)
    :param st_time: Start (Time Window) filter (long)
    :param en_time: End (Time Window) filter (long)
    :return: Contributors (List)
    """
    return get_contributors_projects(gl, project_id, branch_name, st_time, en_time)


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
    if get_project_branch(gl, project_id, branch_name) is False:
        return False
    while git_commits_len is not 0:
        git_commits = gl.getrepositorycommits(project_id, branch_name, page=pag, per_page=number_page)
        git_commits_len = len(git_commits)
        git_ret = []
        for x in git_commits:
            convert_time_keys(x)
            if user is not None:
                if x.get('author_email') == user.get('email'):
                    git_ret.append(x)
            else:
                git_ret.append(x)
        ret_commits += git_ret
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
    git_branches = get_project_branches(gl, project_id, False)
    if git_branches is False:
        return False
    for i in git_branches:
        git_commits_len = -1
        while git_commits_len is not 0:
            git_commits = gl.getrepositorycommits(project_id, i.get('name'), page=pag, per_page=number_page)
            git_commits_len = len(git_commits)
            for x in git_commits:
                convert_time_keys(x)
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
    gl_commit = gl.getrepositorycommit(project_id, commit_id)
    convert_time_keys(gl_commit)
    return gl_commit


def get_project_commit_diff(gl, project_id, commit_id):
    """ Get Commit's Differences
    :param gl: GitLab Object Instance
    :param project_id: Project Identifier (int)
    :param commit_id: Commit Identifier (sha)
    :return: Differences (Object)
    """
    return gl.getrepositorycommitdiff(project_id, commit_id)


def get_project_requests(gl, project_id, request_state):
    """ Get Project's Merge Requests
    :param gl: GitLab Object Instance
    :param project_id: Project Identifier (int)
    :param request_state: Optional Type Identifier (string)
    :return: Merge Requests (List)
    """
    gl_requests = gl.getmergerequests(project_id=project_id, state=request_state)
    for x in gl_requests:
        convert_time_keys(x)
    return gl_requests


def get_project_request(gl, project_id, request_id):
    """ Get Project's Merge Request
    :param gl: GitLab Object Instance
    :param project_id: Project Identifier (int)
    :param request_id: Merge Request Identifier (int)
    :return: Merge Request (Object)
    """
    gl_request = gl.getmergerequest(project_id, request_id)
    convert_time_keys(gl_request)
    return gl_request


def get_project_request_changes(gl, project_id, request_id):
    """ Get Merge Request's Changes
    :param gl: GitLab Object Instance
    :param project_id: Project Identifier (int)
    :param request_id: Merge Request Identifier (int)
    :return: Changes (List)
    """
    gl_request = gl.getmergerequestchanges(project_id, request_id)
    convert_time_keys(gl_request)
    return gl_request


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


def get_project_contributors(gl, project_id, st_time, en_time):
    """ Get Project's Contributors
    :param gl: GitLab Object Instance
    :param project_id: Project Identifier (int)
    :param st_time: Start (Time Window) filter (long)
    :param en_time: End (Time Window) filter (long)
    :return: Contributors (List)
    """
    return get_contributors_projects(gl, project_id, None, st_time, en_time)


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
        git_users = gl.getusers(page=pag, per_page=number_page)
        for x in git_users:
            convert_time_keys(x)
        git_users_len = len(git_users)
        ret_users += git_users
        pag += 1
    return ret_users


def get_user(gl, user_id):
    """ Get User
    :param gl: GitLab Object Instance
    :return: User (Object)
    """
    gl_user = gl.getuser(user_id)
    convert_time_keys(gl_user)
    return gl_user


def get_user_projects(gl, user_id, relation_type):
    """ Get User's Projects
    :param gl: GitLab Object Instance
    :param user_id: User Identifier (int)
    :param relation_type: Relation between User-Project
    :return: Projects (List)
    """
    return get_entity_projects(gl, user_id, relation_type, 'user')


def get_groups(gl):
    """ Get Groups
    :param gl: GitLab Object Instance
    :return: Groups (List)
    """
    git_groups = gl.getgroups()
    for x in git_groups:
        convert_time_keys(x)
        x['members'] = gl.getgroupmembers(x.get('id'))
    return git_groups


def get_group(gl, group_id):
    """ Get Group
    :param gl: GitLab Object Instance
    :param group_id: Group Identifier (int)
    :return: Group (Object)
    """
    git_groups = gl.getgroups()
    for x in git_groups:
        if x.get('id') == group_id:
            convert_time_keys(x)
            x['members'] = gl.getgroupmembers(x.get('id'))
            return x
    return False


def get_group_projects(gl, group_id, relation_type):
    """ Get Group's Projects
    :param gl: GitLab Object Instance
    :param group_id: Group Identifier (int)
    :param relation_type: Relation between User-Project
    :return: Projects (List)
    """
    return get_entity_projects(gl, group_id, relation_type, 'group')


# Functions to help another functions

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


def get_entity_projects(gl, entity_id, relation_type, user_type):

    # Get Entity's projects
    git_projects = get_projects(gl)
    git_user_projects = []
    for x in git_projects:
        if relation_type == 'owner':
            user_type_project = 'group'
            if x.get('owner') is not None:
                user_type_project = 'user'
            if user_type == user_type_project:
                if entity_id == get_project_owner(gl, x.get('id')).get('id'):
                    git_user_projects.append(x)
        else:
            users_list = get_project_branch_contributors(gl, x.get('id'), x.get('default_branch'))
            for j in users_list:
                if entity_id == j.get('id'):
                    git_user_projects.append(x)

    return git_user_projects


def get_contributors_projects(gl, project_id, branch_name, st_time, en_time):

    # Specific Branch
    if branch_name is not None:
        commits_list = get_project_branch_commits(gl, project_id, branch_name, None, None)

    # Generic Project (all branches)
    else:
        commits_list = get_project_commits(gl, project_id, None, None)
    if commits_list is False:
        return commits_list
    email_list = {}
    ret_users = []
    for x in commits_list:
        if st_time is not None and en_time is not None:
            if x.get('created_at') >= st_time and x.get('created_at') <= en_time:
                if email_list.get(x.get('author_email')) is None:
                    email_list[x.get('author_email')] = 1
        else:
            if email_list.get(x.get('author_email')) is None:
                email_list[x.get('author_email')] = 1
    git_users = get_users(gl, None)
    for j in git_users:
        for x in email_list:
            if j.get('email') == x:
                ret_users.append(j)
    return ret_users