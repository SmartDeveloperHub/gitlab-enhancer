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

# keys for transform date to long
str_time_keys = [
    'created_at', 'updated_at', 'last_activity_at',
    'due_date', 'authored_date', 'committed_date',
    'first_commit_at', 'last_commit_at', 'current_sign_in_at'
]


# function to convert time key to long
def convert_time_keys(o):
    for k in o.keys():
        if isinstance(o[k], dict):
            convert_time_keys(o[k])
        elif k in str_time_keys and o[k] != "null":
            o[k] = long(o[k])
        else:
            pass


# function to get user identifier from email
def get_user_identifier(rd, email_b16):
    emails = get_reg_committers_platform(rd)
    if email_b16 in emails:
        return emails[email_b16]
    else:
        return email_b16

# function to get all emails of platform
def get_reg_committers_platform(rd):
    git_emails = {}
    git_users = rd.get("rd_instance_us").keys("u_*")
    for i in git_users:
        git_us_emails = eval(rd.get("rd_instance_us").hgetall(i).get("emails"))
        git_us_id = int(str(i).split("_")[1])
        [git_emails.update({base64.b16encode(x): git_us_id}) for x in git_us_emails]
    return git_emails


# function to get contributors about project
def get_project_contributors(rd, project_id):
    git_branches = rd.get("rd_instance_br").keys("p_" + str(project_id) + ":*")
    git_contributors = set()
    for i in git_branches:
        cont = rd.get("rd_instance_br").hgetall(i).get("contributors")
        if cont is not None:
            git_con_redis = set(eval(
                rd.get("rd_instance_br").hgetall(i).get("contributors")
            ))
            git_contributors = git_contributors.union(git_con_redis)
    if len(git_contributors) > 0:
        git_response = []
        git_emails = get_reg_committers_platform(rd)
        for i in git_emails:
            if i in git_contributors:
                git_response.append(str(git_emails[i]))
        git_contributors -= git_contributors.intersection(set(git_emails.keys()))
        git_response.extend(list(git_contributors))
        return git_response
    else:
        return []


# function to get first and last commit about project
def get_project_commit_at(rd, project_id):
    git_branches = rd.get("rd_instance_br").keys("p_" + str(project_id) + ":*")
    git_co_br = []
    git_response = {
        'first_commit_at': 0,
        'last_commit_at': 0
    }
    for i in git_branches:
        git_f_commit = rd.get("rd_instance_br_co").zrange(i, 0, 0, withscores=True)
        if len(git_f_commit):
            git_co_br.append(git_f_commit[0][1])
        git_f_commit = rd.get("rd_instance_br_co").zrange(i, -1, -1, withscores=True)
        if len(git_f_commit):
            git_co_br.append(git_f_commit[0][1])
    git_co_br.sort()
    if len(git_co_br) > 0:
        git_response['first_commit_at'] = git_co_br[0]
    if len(git_co_br) > 1:
        git_response['last_commit_at'] = git_co_br[-1]
    return git_response


# function to get first and last commit about branch
def get_branch_commit_at(rd, project_id, branch):
    branch_name = "p_" + str(project_id) + ":" + branch
    git_response = {
        'first_commit_at': 0,
        'last_commit_at': 0
    }
    git_co_br = []
    git_f_commit = rd.get("rd_instance_br_co").zrange(branch_name, 0, 0, withscores=True)
    if len(git_f_commit):
        git_co_br.append(git_f_commit[0][1])
    git_f_commit = rd.get("rd_instance_br_co").zrange(branch_name, -1, -1, withscores=True)
    if len(git_f_commit):
        git_co_br.append(git_f_commit[0][1])
    git_co_br.sort()
    if len(git_co_br) > 0:
        git_response['first_commit_at'] = git_co_br[0]
    if len(git_co_br) > 1:
        git_response['last_commit_at'] = git_co_br[-1]
    return git_response


# function to get first and last commit about user
def get_user_commit_at(rd, user_id, is_external, emails):
    git_response = {
        'first_commit_at': 0,
        'last_commit_at': 0
    }
    if is_external:
        git_f_commit = rd.get("rd_instance_us_co").zrange(user_id, 0, 0, withscores=True)
        if len(git_f_commit):
            git_response['first_commit_at'] = git_f_commit[0][1]
        git_f_commit = rd.get("rd_instance_us_co").zrange(user_id, -1, -1, withscores=True)
        if len(git_f_commit):
            git_response['last_commit_at'] = git_f_commit[0][1]
    else:
        git_co_br = []
        for i in emails:
            ikey = base64.b16encode(str(i))
            git_f_commit = rd.get("rd_instance_us_co").zrange(ikey, 0, 0, withscores=True)
            if len(git_f_commit):
                git_co_br.append(git_f_commit[0][1])
            git_f_commit = rd.get("rd_instance_us_co").zrange(ikey, -1, -1, withscores=True)
            if len(git_f_commit):
                git_co_br.append(git_f_commit[0][1])
        git_co_br.sort()
        if len(git_co_br) > 0:
            git_response['first_commit_at'] = git_co_br[0]
        if len(git_co_br) > 1:
            git_response['last_commit_at'] = git_co_br[-1]
    return git_response
