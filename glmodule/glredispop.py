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
import json
import time

# REDIS DATABASE CREATION AND POPULATION


def populate_redis_projects(gl_drainer, gl_redis):
    p = gl_drainer.api_projects()
    p_number = 1
    print_progress("    Projects", 0)
    for i in p:
        o = gl_drainer.api_project_owner(i.get('id'))
        gl_redis.hmset("projects:" + str(i.get('id')) + ":", {
            'id': i.get('id'),
            'name': i.get('name'),
            'description': i.get('description'),
            'created_at': i.get('created_at'),
            'http_url_to_repo': i.get('http_url_to_repo'),
            'public': i.get('public'),
            'avatar_url': i.get('avatar_url'),
            'tags': json.dumps(i.get('tags', [])),
            'archived': i.get('archived'),
            'owner': o.get('type') + "s:" + str(o.get('id')),
            'default_branch': i.get('default_branch')
        })
        print_progress("    Projects", float(p_number) / len(p))
        p_number += 1
    print ""


def populate_redis_branches(gl_drainer, gl_redis):
    p = map(lambda x: int(x.split(':')[1]), gl_redis.keys("projects:*:"))
    p_number = 1
    print_progress("    Branches (0/" + str(len(p)) + ")", 0)
    for i in p:
        b = gl_drainer.api_project_branches(i, 'false')
        b_length = len(b)
        b_number = 1
        for j in b:
            id_com = j.get('commit').get('id')
            gl_redis.hmset("projects:" + str(i) + ":branches:" + j.get('name'), {
                'name': j.get('name'),
                'protected': j.get('protected'),
                'last_commit': "projects:" + str(i) + ":commits:" + id_com
            })
            print_progress("    Branches (" + str(p_number) + "/" + str(len(p)) +
                           ")", float(b_number) / float(b_length))
            b_number += 1
        p_number += 1
    print ""


# TODO: Filter by branch
#     "projects:id:branches:name:commits" = Sorted List
#     "projects:id:branches:name[contributors]" = Keys List

# TODO: Lines added and removed (Git Log)
#     "projects:id:commits:sha[lines_added]" = value
#     "projects:id:commits:sha[lines_removed]" = value

# TODO: Source Code - Language (Language Mapping)
#     "projects:id:commits:sha[language]" = {'language': 'number_files'}
#     "projects:id:branches:name[language]" = {'language': 'number_files'}
#     "projects:id[language]" = top_language_value in project
#     "users:id[favourite_language]" = top_language_value

def populate_redis_commits(gl_drainer, gl_redis):
    p = map(lambda x: int(x.split(':')[1]), gl_redis.keys("projects:*:"))
    p_number = 0
    for i in p:
        print_progress("    Commits (" + str(p_number) + "/" + str(len(p)) + ")", 0)
        p_number += 1
        c = gl_drainer.api_project_branch_commits(i, 'master', None, None)
        c_length = len(c)
        c_number = 1
        for j in c:

            # Insert commit information
            gl_redis.hmset("projects:" + str(i) + ":commits:" + j.get('id'), {
                'id': j.get('id'),
                'author_email': j.get('author_email'),
                'author_name': j.get('author_name'),
                'created_at': j.get('created_at'),
                'message': j.get('message'),
                'title': j.get('title')
            })

            # Insert commit to Sorted List (project)
            gl_redis.zadd("projects:" + str(i) + ":commits:",
                          "projects:" + str(i) + ":commits:" + j.get('id'),
                          j.get('created_at'))

            # Insert commit additional information
            # Time without this execution - 2 min
            # Time with this execution - 1 hour 24 min
            # inject_commit_info(gl_drainer, gl_redis, i, j.get('id'))

            # Insert user additional information
            inject_user_info(gl_redis, i, j)

            print_progress("    Commits (" + str(p_number) + "/" + str(len(p)) +
                           ")", float(c_number) / c_length)
            c_number += 1

        # Insert Contributors
        u = map(lambda w: "users:" + str(w.split(':')[1]),
                gl_redis.keys("users:*:projects:" + str(i) + ":commits"))
        gl_redis.hset("projects:" + str(i), 'contributors', u)

        # Insert Last and First Commit date (Sorted List by Score)
        gl_redis.hset("projects:" + str(i), 'first_commit_at', gl_redis.zrange("projects:" +
                      str(i) + ":commits:", 0, 0, withscores=True)[0][1])
        gl_redis.hset("projects:" + str(i), 'last_commit_at', gl_redis.zrange("projects:" +
                      str(i) + ":commits:", -1, -1, withscores=True)[0][1])

    # Insert user additional information
    pc = gl_redis.keys("users:*:projects:" + str(i) + ":commits")
    users_temp = {}
    for i in pc:
        f = gl_redis.zrange(i, 0, 0, withscores=True)[0][1]
        l = gl_redis.zrange(i, -1, -1, withscores=True)[0][1]
        user_id = "users:" + i.split(':')[1]
        if user_id in users_temp:
            if l > users_temp[user_id]["last"]:
                users_temp[user_id]["last"] = l
            if f < users_temp[user_id]["first"]:
                users_temp[user_id]["first"] = f
        else:
            users_temp[user_id] = {}
            users_temp[user_id]["last"] = l
            users_temp[user_id]["first"] = f
    for i in users_temp.keys():
        gl_redis.hset(i, 'first_commit_at', users_temp[i]['first'])
        gl_redis.hset(i, 'last_commit_at', users_temp[i]['last'])

    print ""


def populate_redis_users(gl_drainer, gl_redis):
    u = gl_drainer.api_users(None)
    u_number = 1
    print_progress("    Users", 0)
    for i in u:
        gl_redis.hmset("users:" + str(i.get('id')), {
            'id': i.get('id'),
            'name': i.get('name'),
            'email': i.get('email'),
            'created_at': i.get('created_at'),
            'skype': i.get('skype'),
            'linkedin': i.get('linkedin'),
            'twitter': i.get('twitter'),
            'website_url': i.get('website_url'),
            'user_url': gl_drainer.gitHost + "/u/" + i.get('username'),
            'avatar_url': i.get('avatar_url')
        })
        gl_redis.set("users:" + str(i.get('id')) + ":email:" + i.get('email'), "")
        print_progress("    Users", float(u_number) / len(u))
        u_number += 1
    print ""


def populate_redis_groups(gl_drainer, gl_redis):
    g = gl_drainer.api_groups()
    g_number = 1
    print_progress("    Groups", 0)
    for i in g:
        am = i.get('members')
        for x in am:
            gl_redis.rpush("groups:" + str(i.get('id')) +
                           ":members", "users:" + str(x.get('id')))
        gl_redis.hmset("groups:" + str(i.get('id')), {
            'id': i.get('id'),
            'name': i.get('name'),
            'path': i.get('path'),
            'description': i.get('description')
        })
        print_progress("    Groups", float(g_number) / len(g))
        g_number += 1
    print ""


# Functions to help another functions


def print_progress(label, percent):
    hashes = '#' * int(round(percent * (40 - len(label))))
    spaces = ' ' * ((40 - len(label)) - len(hashes))
    sys.stdout.write("\r" + label + " [{0}] "
                     "{1}%".format(hashes + spaces, int(round(percent * 100))))
    sys.stdout.flush()


def get_language_by_extension(ext):
    return "code"


def inject_user_info(gl_redis, project_id, commit):
    b = map(lambda x: int(x.split(':')[1]),
            gl_redis.keys("users:*:email:" + commit.get('author_email')))
    if len(b) == 0:
        return
    b = b[0]

    # Insert commit to Sorted List
    gl_redis.zadd("users:" + str(b) + ":projects:" + str(project_id) + ":commits:",
                  "projects:" + str(project_id) + ":commits:" + commit.get('id'),
                  commit.get('created_at'))


def inject_commit_info(gl_drainer, gl_redis, project_id, commit_sha):
    c = gl_drainer.api_project_commit(project_id, commit_sha)
    gl_redis.hset("projects:" + str(project_id) + ":commits:" + commit_sha, "commited_date",
                  c.get("commited_date"))
    gl_redis.hset("projects:" + str(project_id) + ":commits:" + commit_sha, "parent_ids",
                  c.get("parent_ids"))

    cd = gl_drainer.api_project_commit_diff(project_id, commit_sha)
    languages = {}
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
                j_temp = []
                x_n = 0
                for w in j:
                    if x_n > 0 and x_n % 2 == 0:
                        j_temp.append(w.splitlines())
                    x_n += 1
                j = j_temp
            for i in j:
                [add_lines_j.append(item) for item in i if item[0] == '+']
                [rem_lines_j.append(item) for item in i if item[0] == '-']
            if x.get('deleted_file') is False:
                l = get_language_by_extension(x.get('new_path'))
                if languages.get(l):
                    languages[l] += 1
                else:
                    languages[l] = 1

    gl_redis.hset("projects:" + str(project_id) + ":commits:" + commit_sha, "lines_added",
                  len(add_lines_j))
    gl_redis.hset("projects:" + str(project_id) + ":commits:" + commit_sha, "lines_removed",
                  len(rem_lines_j))
    gl_redis.hset("projects:" + str(project_id) + ":commits:" + commit_sha, "language",
                  languages)