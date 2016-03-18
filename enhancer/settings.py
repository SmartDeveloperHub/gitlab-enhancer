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
GE_NAME = "git-enhancer"
GE_VERSION = "1.0.0"
GE_LONGNAME = "Git Enhancer"

# Enhancer execution Configuration
GE_SCHEDULE = int(os.environ.get("ENH_SCHEDULE", 60 * 60 * 3))

# Enhancer Configuration to create Flask API
GE_LISTEN_PROT = os.environ.get("ENH_LISTEN_PROT", "http")
GE_LISTEN_PORT = int(os.environ.get("ENH_LISTEN_PORT", 5000))
GE_LISTEN_IP = os.environ.get("ENH_LISTEN_IP", "0.0.0.0")

# Gitlab Configuration to get data
# GITLAB_PROT = os.environ.get("COLL_GITLAB_PROT", "http")
# GITLAB_IP = os.environ.get("COLL_GITLAB_IP", "127.0.0.1")
# GITLAB_PORT = int(os.environ.get("COLL_GITLAB_PORT", 8000))
# GITLAB_USER = os.environ.get("COLL_GITLAB_USER", "root")
# GITLAB_PASS = os.environ.get("COLL_GITLAB_PASS", "12345678")
# GITLAB_VER_SSL = bool(os.environ.get("COLL_GITLAB_VERIFY_SSL", False))

GITLAB_PROT = os.environ.get("COLL_GITLAB_PROT", "http")
GITLAB_IP = os.environ.get("COLL_GITLAB_IP", "vps164.cesvima.upm.es")
# GITLAB_USERNAME = os.environ.get("COLL_GITLAB_USERNAME", "root")
# GITLAB_PASSWORD = os.environ.get("COLL_GITLAB_PASSWORD", "123456sdh")
GITLAB_TOKEN = os.environ.get("COLL_GITLAB_TOKEN", "jy3BsgxBQhU1x4hk49z-")
# GITLAB_PROT = os.environ.get("COLL_GITLAB_PROT", "https")
# GITLAB_IP = os.environ.get("COLL_GITLAB_IP", "repo.conwet.fi.upm.es")
# GITLAB_TOKEN = os.environ.get("COLL_GITLAB_TOKEN", "1Ur_VZD8VjDysXSjFeux")
GITLAB_VER_SSL = bool(os.environ.get("COLL_GITLAB_VERIFY_SSL", False))

# Git Collector Configuration
GIT_IP = os.environ.get("GIT_COLL_IP", "127.0.0.1")
GIT_PORT = int(os.environ.get("GIT_COLL_PORT", 5001))

# Redis Configuration to set data
REDIS_IP = os.environ.get("GE_REDIS_IP", "127.0.0.1")
REDIS_PORT = int(os.environ.get("GE_REDIS_PORT", 6379))
REDIS_PASS = os.environ.get("GE_REDIS_PASS", None)

# Redis Configuration (Main Entities)
REDIS_DB_PROJ = int(os.environ.get("COLL_REDIS_DB_PROJECT", 0))
REDIS_DB_USER = int(os.environ.get("COLL_REDIS_DB_USER", 1))
REDIS_DB_GROUP = int(os.environ.get("COLL_REDIS_DB_GROUP", 2))
REDIS_DB_MERGE = int(os.environ.get("COLL_REDIS_DB_MERGE", 3))