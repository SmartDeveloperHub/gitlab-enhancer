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

import json

# System Web Hooks (glmodule-ce)
# Project: create / destroy
# Project member: add / remove
# User: create / destroy
# Group: create / destroy
# Group member: add / remove


def project_create(event):
    print('project created')


def project_destroy(event):
    print('project destroyed')


def user_add_to_team(event):
    print('user added to team')


def user_remove_from_team(event):
    print('user removed from team')


def user_create(event):
    print('user created')


def user_destroy(event):
    print('user destroyed')


def group_create(event):
    print('group created')


def group_destroy(event):
    print('group destroyed')


def user_add_to_group(event):
    print('user added to group')


def user_remove_from_group(event):
    print('user removed from group')


def hook_system(event):
    if event['event_name'] in globals():
        globals()[event['event_name']](event)