__author__ = 'Alejandro F. Carrera'

import json

# System Web Hooks (gitlab-ce)
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
    if globals() in event['event_name']:
        globals()[event['event_name']](event)