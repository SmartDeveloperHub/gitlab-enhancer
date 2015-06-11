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

import sys
from dateutil import parser

projects = []

# REDIS DATABASE CREATION AND POPULATION


def populate_redis_projects(gl_drainer, gl_redis):
    p = gl_drainer.git.getprojectsall()
    p_number = 1
    print_progress("    Projects", 0)
    for i in p:
        projects.append(i.get('id'))
        if i.get('owner') is None:
            i['owner'] = 'groups:' + str(i.get('namespace').get('id'))
        else:
            i['owner'] = 'users:' + str(i.get('owner').get('id'))

        convert_time_keys(i)
        i['tags'] = map(lambda x: x.get('name').encode('ascii','ignore'),
                        gl_drainer.git.getrepositorytags(i.get('id')))
        parse_info_project(i)
        gl_redis.hmset("projects:" + str(i.get('id')) + ":", i)
        print_progress("    Projects", float(p_number) / len(p))
        p_number += 1
    print ""


def populate_redis_branches(gl_drainer, gl_redis):
    p_number = 1
    print_progress("    Branches (0/" + str(len(projects)) + ")", 0)
    for i in projects:
        b = gl_drainer.git.getbranches(i)
        b_length = len(b)
        b_number = 1
        for j in b:
            if j.get('protected') is False:
                j['protected'] = 'false'
            else:
                j['protected'] = 'true'
            del j['commit']
            gl_redis.hmset("projects:" + str(i) + ":branches:" + j.get('name'), j)
            print_progress("    Branches (" + str(p_number) + "/" + str(len(projects)) +
                           ")", float(b_number) / float(b_length))
            b_number += 1
        p_number += 1
    print ""


def populate_redis_commits(gl_drainer, gl_redis):
    p_number = 0
    list_users = {}
    for i in projects:
        print_progress("    Commits (" + str(p_number) + "/" + str(len(projects)) + ")", 0)
        p_number += 1
        ci = gl_drainer.api_project_commits_information(i, None)
        gl_redis.hset("projects:" + str(i) + ":", 'contributors',
                      ci.get('collaborators'))
        gl_redis.hset("projects:" + str(i) + ":", 'first_commit_at',
                      ci.get('commits')[0].get('created_at'))
        gl_redis.hset("projects:" + str(i) + ":", 'last_commit_at',
                      ci.get('commits')[len(ci.get('commits'))-1].get('created_at'))

        # Insert commits (info and ids) by project
        comm_project_score = []
        comm_project_user = {}
        ci_commits = ci.get('commits')
        for j in ci_commits:
            comm = gl_drainer.api_project_commit(i, j.get('id'))
            comm['parent_ids'] = map(lambda x: x.encode('ascii','ignore'), comm.get('parent_ids'))
            gl_redis.hmset("projects:" + str(i) + ":commits:" + j.get('id'), comm)
            comm_project_score.append("projects:" + str(i) + ":commits:" + j.get('id'))
            comm_project_score.append(j.get('created_at'))
            if comm.get('author') is not comm_project_user:
                comm_project_user[comm.get('author')] = []
            if comm.get('author') is not list_users:
                list_users[comm.get('author')] = {
                    'last': comm.get('created_at'),
                    'first': comm.get('created_at')
                }
            if list_users[comm.get('author')]['first'] > comm.get('created_at'):
                list_users[comm.get('author')]['first'] = comm.get('created_at')
            if list_users[comm.get('author')]['last'] < comm.get('created_at'):
                list_users[comm.get('author')]['last'] = comm.get('created_at')
            comm_project_user[comm.get('author')].append(comm)
        inject_project_commits(gl_redis, str(i), comm_project_score)

        # Insert commits by project's branch
        ci_branches = ci.get('branches')
        for b in ci_branches:
            ci_branch_commits = ci_branches[b].get('commits')
            gl_redis.hset("projects:" + str(i) + ":branches:" + b, 'contributors',
                          ci_branches[b].get('collaborators'))
            gl_redis.hset("projects:" + str(i) + ":branches:" + b, 'created_at',
                          ci_branch_commits[0].get('created_at'))
            gl_redis.hset("projects:" + str(i) + ":branches:" + b, 'last_commit',
                          ci_branch_commits[len(ci_branch_commits)-1].get('id'))
            c_number = 1
            c_length = len(ci_branch_commits)
            com_list_branch = []
            for j in ci_branch_commits:
                com_list_branch.append("projects:" + str(i) + ":commits:" + j.get('id'))
                com_list_branch.append(j.get('created_at'))
            inject_branch_commits(gl_redis, str(i), b, com_list_branch)
            print_progress("    Commits (" + str(p_number) + "/" + str(len(projects)) +
                           ")", float(c_number) / c_length)
            c_number += 1

        # Insert commits by user
        for w in comm_project_user:
            comm_project_user[w].sort(key=lambda j: j.get('created_at'), reverse=False)
            comm_un_project_user = []
            for j in comm_project_user[w]:
                comm_un_project_user.append("projects:" + str(i) + ":commits:" + j.get('id'))
                comm_un_project_user.append(j.get('created_at'))
            inject_user_commits(gl_redis, i, w, comm_un_project_user)

    # Insert user's information
    for i in list_users.keys():
        gl_redis.hset("users:" + str(i) + ":", 'first_commit_at', list_users[i]['first'])
        gl_redis.hset("users:" + str(i) + ":", 'last_commit_at', list_users[i]['last'])

    print ""


def populate_redis_users(gl_drainer, gl_redis):
    pag = 0
    number_page = 50
    git_users_len = -1
    u = {}
    while git_users_len is not 0:
        git_users = gl_drainer.git.getusers(page=pag, per_page=number_page)
        git_users_len = len(git_users)
        for i in git_users:
            if i.get('id') not in u:
                convert_time_keys(i)
                parse_info_user(i)
                u[i.get('id')] = i
        pag += 1
    u_number = 1
    print_progress("    Users", 0)
    for j in u:
        gl_redis.hmset("users:" + str(u[j].get('id')) + ":", u[j])
        print_progress("    Users", float(u_number) / len(u.keys()))
        u_number += 1
    print ""


def populate_redis_groups(gl_drainer, gl_redis):
    g = gl_drainer.git.getgroups()
    g_number = 1
    print_progress("    Groups", 0)
    for j in g:
        if 'projects' in j:
            del j['projects']
        convert_time_keys(j)
        j['members'] = []
        [j['members'].append(x.get('id')) for x in gl_drainer.git.getgroupmembers(j.get('id'))]
        gl_redis.hmset("groups:" + str(j.get('id')) + ":", j)
        print_progress("    Groups", float(g_number) / len(g))
        g_number += 1
    print ""


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
        else:
            pass


def print_progress(label, percent):
    hashes = '#' * int(round(percent * (40 - len(label))))
    spaces = ' ' * ((40 - len(label)) - len(hashes))
    sys.stdout.write("\r" + label + " [{0}] "
                     "{1}%".format(hashes + spaces, int(round(percent * 100))))
    sys.stdout.flush()


def inject_branch_commits(gl_redis, project_id, branch, commits):
    commits_push = []
    c = 0
    for i in commits:
        if c == 10000:
            gl_redis.zadd("projects:" + project_id + ":branches:" + branch + ":commits:", *commits_push)
            commits_push = [i]
            c = 1
        else:
            commits_push.append(i)
            c += 1
    gl_redis.zadd("projects:" + project_id + ":branches:" + branch + ":commits:", *commits_push)


def inject_project_commits(gl_redis, project_id, commits):
    c = 0
    commits_push = []
    for i in commits:
        if c == 10000:
            gl_redis.zadd("projects:" + project_id + ":commits:", *commits_push)
            commits_push = [i]
            c = 1
        else:
            commits_push.append(i)
            c += 1
    gl_redis.zadd("projects:" + project_id + ":commits:", *commits_push)


def inject_user_commits(gl_redis, project_id, user_id, commits):
    c = 0
    commits_push = []
    for i in commits:
        if c == 10000:
            gl_redis.zadd("users:" + str(user_id) + ":projects:" + str(project_id) + ":commits:", *commits_push)
            commits_push = [i]
            c = 1
        else:
            commits_push.append(i)
            c += 1
    gl_redis.zadd("users:" + str(user_id) + ":projects:" + str(project_id) + ":commits:", *commits_push)
