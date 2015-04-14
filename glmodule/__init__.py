
__author__ = 'alejandrofcarrera'

from glmodule import glsystem, glhook, glapi
from flask import make_response
import gitlab, json


class GlDrainer(object):
    def __init__(self, config):
        self.cfg = config
        self.git = None
        self.drainerHost = "%s://%s:%d/system" % (
            self.cfg.get('DRAINER_PROT', 'http'),
            self.cfg.get('DRAINER_IP', '127.0.0.1'),
            self.cfg.get('DRAINER_PORT', 8080)
        )
        self.hookHost = "%s://%s:%d/hook" % (
            self.cfg.get('DRAINER_PROT', 'http'),
            self.cfg.get('DRAINER_IP', '127.0.0.1'),
            self.cfg.get('DRAINER_PORT', 8080)
        )
        self.gitHost = "%s://%s:%d" % (
            self.cfg.get('GITLAB_PROT', 'http'),
            self.cfg.get('GITLAB_IP', '127.0.0.1'),
            self.cfg.get('GITLAB_PORT', 80)
        )
        self.connect_gitlab()

    @property
    def config(self):
        return self.cfg

# GITLAB HOOKS

    def hook_system(self, response_hook):
        glsystem.hook_system(response_hook)

    def hook_specific(self, response_hook):
        glhook.hook_specific(response_hook)

# GITLAB CONNECTION

    def link_gitlab(self):
        self.git.addsystemhook(url=self.drainerHost)

    def link_repositories(self):

        # Get Git projects (visible to admin)
        __projects = self.git.getprojects()
        for e in __projects:

            # Check Hooks and Link with Git Projects
            __hooks = self.git.getprojecthooks(project_id=e['id'])
            __linked = False
            for j in __hooks:
                if j['url'] == self.hookHost:
                    __linked = True
            if not __linked:
                self.git.addprojecthook(project_id=e['id'], url=self.hookHost)

    def connect_gitlab(self):

        # Create git object and connect
        __linked = False
        __available = False
        __user = self.cfg.get('GITLAB_USER', 'user')
        __pwd = self.cfg.get('GITLAB_PASS', 'password')
        self.git = gitlab.Gitlab(host=self.gitHost)
        try:
            self.git.login(user=__user, password=__pwd)
            __available = True
        except Exception as e:
            self.git = None

        # Check Hooks and Link with Git Admin Area
        if __available:
            __hooks = self.git.getsystemhooks()
            for e in __hooks:
                if e['url'] == self.drainerHost:
                    __linked = True
            if not __linked:
                self.link_gitlab()

            # Check Projects instead of admin area
            self.link_repositories()

# GITLAB ENHANCER API REST

    def api_projects(self):
        response = make_response(json.dumps(glapi.get_projects(self)))
        return response

    def api_project(self, project_id):
        response = make_response(json.dumps(glapi.get_project(self, project_id)))
        return response

    def api_project_owner(self, project_id):
        response = make_response(json.dumps(glapi.get_project_owner(project_id)))
        return response