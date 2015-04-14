__author__ = 'alejandrofcarrera'

import json

# Repository Web Hooks (glmodule-ce)
# Push (push tags is not included)
# Tags: create / delete
# Issues: create / update / close / reopen
# Merge Request: create / update / merge / close


def hook_specific(event):
    print("hook_specific from glhook")

