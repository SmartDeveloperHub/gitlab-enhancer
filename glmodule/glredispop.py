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
import datetime

projects = []

# REDIS DATABASE CREATION AND POPULATION


def populate_redis_projects(gl_drainer, gl_redis):
    p = gl_drainer.api_projects(True)
    p_number = 1
    print_progress("    Projects", 0)
    for i in p:
        projects.append(i.get('id'))
        i['owner'] = i.get('owner').get('type') + ":" + str(i.get('owner').get('id'))
        gl_redis.hmset("projects:" + str(i.get('id')) + ":", i)
        print_progress("    Projects", float(p_number) / len(p))
        p_number += 1
    print ""


def populate_redis_branches(gl_drainer, gl_redis):
    p_number = 1
    print_progress("    Branches (0/" + str(len(projects)) + ")", 0)
    for i in projects:
        b = gl_drainer.api_project_branches(i, 'false', True)
        b_length = len(b)
        b_number = 1
        for j in b:
            gl_redis.hmset("projects:" + str(i) + ":branches:" + j.get('name'), j)
            print_progress("    Branches (" + str(p_number) + "/" + str(len(projects)) +
                           ")", float(b_number) / float(b_length))
            b_number += 1
        p_number += 1
    print ""


def populate_redis_commits(gl_drainer, gl_redis):
    p_number = 0
    for i in projects:
        print_progress("    Commits (" + str(p_number) + "/" + str(len(projects)) + ")", 0)
        p_number += 1
        c = gl_drainer.sp_project_commits_by_branch(i, {
            'st_time': long(0),
            'en_time': long(datetime.datetime.now().strftime("%s")) * 1000
        })

        comm_project = c[0]
        bran_project = c[1]
        comm_project_score = []

        # Insert commits by project
        for j in comm_project:
            comm_unique = comm_project[j]
            gl_redis.hmset("projects:" + str(i) + ":commits:" + comm_unique.get('id'), comm_unique)
            comm_project_score.append("projects:" + str(i) + ":commits:" + comm_unique.get('id'))
            comm_project_score.append(comm_unique.get('created_at'))
        inject_project_commits(gl_redis, str(i), comm_project_score)

        # Insert Last and First Commit date (Sorted List by Score)
        gl_redis.hset("projects:" + str(i), 'first_commit_at', gl_redis.zrange("projects:" +
                      str(i) + ":commits:", 0, 0, withscores=True)[0][1])
        gl_redis.hset("projects:" + str(i), 'last_commit_at', gl_redis.zrange("projects:" +
                      str(i) + ":commits:", -1, -1, withscores=True)[0][1])

        # Insert commits by project's branch
        for b in bran_project:
            c_length = len(bran_project[b])
            c_number = 1
            com_list_branch = []
            for j in bran_project[b]:
                com_list_branch.append("projects:" + str(i) + ":commits:" + j)
                com_list_branch.append(comm_project[j].get('created_at'))

                # Insert user additional information
                inject_user_info(gl_redis, i, b, comm_project[j])

            inject_branch_commits(gl_redis, str(i), b, com_list_branch)

            print_progress("    Commits (" + str(p_number) + "/" + str(len(projects)) +
                           ")", float(c_number) / c_length)
            c_number += 1

        # Insert Contributors
        u = map(lambda k: "users:" + str(k.split(':')[1]),
                gl_redis.keys("users:*:projects:" + str(i) + ":commits:"))
        gl_redis.hset("projects:" + str(i), 'contributors', u)

    # Insert user additional information
    pc = gl_redis.keys("users:*:projects:" + str(i) + ":commits:")
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
    for j in u:
        i = gl_drainer.api_user(j)
        gl_redis.hmset("users:" + str(i.get('id')), i)
        gl_redis.set("users:" + str(i.get('id')) + ":email:" + i.get('email'), "")
        print_progress("    Users", float(u_number) / len(u))
        u_number += 1
    print ""


def populate_redis_groups(gl_drainer, gl_redis):
    g = gl_drainer.api_groups()
    g_number = 1
    print_progress("    Groups", 0)
    for j in g:
        i = gl_drainer.api_group(j)
        am = i.get('members')
        [gl_redis.rpush(
            "groups:" + str(i.get('id')) +
            ":members", "users:" + str(x)) for x in am
        ]
        del i['members']
        gl_redis.hmset("groups:" + str(i.get('id')), i)
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


def inject_user_info(gl_redis, project_id, branch, commit):
    b = map(lambda x: int(x.split(':')[1]),
            gl_redis.keys("users:*:email:" + commit.get('author_email')))
    if len(b) == 0:
        return
    b = b[0]

    # Insert commit to Sorted List (project)
    gl_redis.zadd("users:" + str(b) + ":projects:" + str(project_id) + ":commits:",
                  "projects:" + str(project_id) + ":commits:" + commit.get('id'),
                  commit.get('created_at'))

    # Insert commit to Sorted List (branch)
    gl_redis.zadd("users:" + str(b) + ":projects:" + str(project_id) + ":branches:" + branch + ":commits:",
                  "projects:" + str(project_id) + ":commits:" + commit.get('id'),
                  commit.get('created_at'))