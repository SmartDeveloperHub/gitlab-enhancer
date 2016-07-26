"""
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=#
  This file is part of the Smart Developer Hub Project:
    http://www.smartdeveloperhub.org
  Center for Open Middleware
        http://www.centeropenmiddleware.com/
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=#
  Copyright (C) 2016 Center for Open Middleware.
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

import os

__author__ = 'Ignacio Molina Cuquerella'

# Enhancer Package Configuration
GE_NAME = "gitlab-enhancer"
GE_VERSION = "2.0.0"
GE_LONGNAME = "Git Enhancer"

# Enhancer execution Configuration
GE_SCHEDULE = int(os.environ.get("ENH_SCHEDULE", 60 * 60 * 3))

# Enhancer Configuration to create Flask API
GE_LISTEN_PROT = os.environ.get("ENH_LISTEN_PROT", "http")
GE_LISTEN_PORT = int(os.environ.get("ENH_LISTEN_PORT", 5000))
GE_LISTEN_IP = os.environ.get("ENH_LISTEN_IP", "0.0.0.0")

# Gitlab Configuration to get data
GITLAB_PROT = os.environ.get("COLL_GITLAB_PROT", "http")
GITLAB_IP = os.environ.get("COLL_GITLAB_IP", "127.0.0.1")
GITLAB_PORT = int(os.environ.get("COLL_GITLAB_PORT", 80))
GITLAB_TOKEN = os.environ.get("COLL_GITLAB_TOKEN", "")

GITLAB_VER_SSL = bool(os.environ.get("COLL_GITLAB_VERIFY_SSL", False))
GC_FILE = os.environ.get("GIT_COLL_FILE", "../git_collectors.json")

# Redis Configuration to set data
REDIS_IP = os.environ.get("GE_REDIS_IP", "127.0.0.1")
REDIS_PORT = int(os.environ.get("GE_REDIS_PORT", 6379))
REDIS_PASS = os.environ.get("GE_REDIS_PASS", None)

# Redis Configuration (Main Entities)
REDIS_DB_GIT = int(os.environ.get("COLL_REDIS_DB_GIT", 0))
REDIS_DB_PROJ = int(os.environ.get("COLL_REDIS_DB_PROJECT", 1))
REDIS_DB_USER = int(os.environ.get("COLL_REDIS_DB_USER", 2))
REDIS_DB_GROUP = int(os.environ.get("COLL_REDIS_DB_GROUP", 3))
REDIS_DB_BRANCH = int(os.environ.get("COLL_REDIS_DB_BRANCH", 4))
REDIS_DB_COMMIT = int(os.environ.get("COLL_REDIS_DB_COMMIT", 5))
REDIS_DB_MERGE = int(os.environ.get("COLL_REDIS_DB_MERGE", 6))