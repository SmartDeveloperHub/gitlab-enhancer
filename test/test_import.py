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

import time
import sys
from random import randint
import hashlib

import gitlab

from drainer.settings import *

if __name__ == '__main__':
    for arg in sys.argv:
        print arg
    print "--"
    git = gitlab.Gitlab(
        host="%s://%s:%d" % (
            GITLAB_PROT, GITLAB_IP, GITLAB_PORT
        ))
    git.login(user=GITLAB_USER, password=GITLAB_PASS)

    git_users_json = {}
    git_users_em_id = {}

    print "Creating Group: jenkins"
    group = git.creategroup("jenkins", "jenkins")
    time.sleep(15)
    print " - Done"

    visibility_levels = ['public', 'private', 'internal']
    projects = [
        {
            'git': "https://github.com/jenkinsci/jenkins.git",
            'name': 'jenkins',
        },
        {
            'git': "https://github.com/jenkinsci/pom.git",
            'name': 'pom',
        },
        {
            'git': "https://github.com/jenkinsci/maven-interceptors.git",
            'name': 'maven-interceptors',
        },
        {
            'git': "https://github.com/jenkinsci/maven-hpi-plugin.git",
            'name': 'maven-hpi-plugin',
        },
        {
            'git': "https://github.com/jenkinsci/backend-extension-indexer.git",
            'name': 'backend-extension-indexer',
        }
    ]

    for i in projects:
        print "Creating Project: " + i.get('name')
        v = randint(0, 2)
        if randint(0, 1) == 0:
            project = git.createproject(
                name=i.get('name'), visibility_level=visibility_levels[v], import_url=i.get('git')
            )
        else:
            project = git.createproject(
                name=i.get('name'), visibility_level=visibility_levels[v], import_url=i.get('git'), namespace_id=group.get('id')
            )
        time.sleep(45)
        git_branches = git.getbranches(project.get('id'))
        total_commits = 0
        total_users = 0
        git_commits_hash = {}
        print " - Branches: " + str(len(git_branches))
        for x in git_branches:
            pag = 0
            number_page = 10000
            git_commits_len = -1
            while git_commits_len is not 0:
                git_commits = git.getrepositorycommits(project.get('id'), x.get('name'), page=pag, per_page=number_page)
                git_commits_len = len(git_commits)
                total_commits += git_commits_len
                for w in git_commits:
                    if w.get('id') not in git_commits_hash:
                        git_commits_hash[w.get('id')] = '1'
                        if w.get('author_email') not in git_users_em_id:
                            git_users_em_id[w.get('author_email')] = '1'
                            u = hashlib.md5()
                            u.update(w.get('author_email'))
                            u = u.hexdigest()
                            git_users_json[u] = {
                                "username": w.get('author_email').split("@")[0],
                                "email": w.get('author_email')
                            }
                            r = git.createuser(u, u, "pass12345", u + "@c.com")
                            time.sleep(10)
                            if r is False:
                                print "Error: " + u + ' - ' + w.get('author_email')
                            else:
                                print "Created: " + u + ' - ' + w.get('author_email')
                                total_users += 1
                pag += 1
        print " - Commits (All Branches): " + str(total_commits)
        print " - Commits (Unique): " + str(len(git_commits_hash.keys()))
        print " - New Users: " + str(total_users)
        print " - Done"

        import json
        with open('json_users.json', 'w') as outfile:
            json.dump(git_users_json, outfile)
