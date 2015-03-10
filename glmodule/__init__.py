
__author__ = 'alejandrofcarrera'

from flask import request, make_response
import gitlab
import glsystem


class GlDrainer(object):
    def __init__(self, config):
        self.cfg = config
        self.git = None
        self.drainerHost = "%s://%s:%d/system" % (
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

    def hook_system(self, response_hook):
        glsystem.hook_system(response_hook)

    def hook_specific(self, response_hook):
        print("hook_specific")
        #glhook.hook_specific(response_hook.json)

    def api_gitlab(self, name):
        if name == 'projects':
            return self.git.getprojects()

    def link_gitlab(self):
        self.git.addsystemhook(url=self.drainerHost)

    def connect_gitlab(self):
        __linked = False
        __user = self.cfg.get('GITLAB_USER', 'user')
        __pwd = self.cfg.get('GITLAB_PASS', 'password')
        self.git = gitlab.Gitlab(host=self.gitHost)
        self.git.login(user=__user, password=__pwd)
        __hooks = self.git.getsystemhooks()
        for e in __hooks:
            if e['url'] == self.drainerHost:
                __linked = True

        if not __linked:
            self.link_gitlab()
