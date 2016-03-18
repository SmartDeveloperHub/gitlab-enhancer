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

import os
import logging

__author__ = 'Alejandro F. Carrera'

# Enhancer Package Configuration
NAME = "gl-enhancer"
VERSION = "1.0.4"
DEBUGGER = True
LONGNAME = "Gitlab Enhancer"

# Enhancer Configuration to create Flask API
ENHANCER_LISTEN_PROT = os.environ.get("ENH_LISTEN_PROT", "http")
ENHANCER_LISTEN_PORT = int(os.environ.get("ENH_LISTEN_PORT", 5000))
ENHANCER_LISTEN_IP = os.environ.get("ENH_LISTEN_IP", "0.0.0.0")

# Redis Configuration to set data
REDIS_IP = os.environ.get("ENH_REDIS_IP", "127.0.0.1")
REDIS_PORT = int(os.environ.get("ENH_REDIS_PORT", 6379))
REDIS_PASS = os.environ.get("ENH_REDIS_PASS", None)

# Redis Configuration (Main Entities)
REDIS_DB_PR = int(os.environ.get("COLL_REDIS_DB_PROJECT", 0))
REDIS_DB_BR = int(os.environ.get("COLL_REDIS_DB_BRANCH", 1))
REDIS_DB_CO = int(os.environ.get("COLL_REDIS_DB_COMMIT", 2))
REDIS_DB_US = int(os.environ.get("COLL_REDIS_DB_USER", 3))

# Redis Configuration (Relations)
REDIS_DB_BR_CO = int(os.environ.get("COLL_REDIS_DB_BRANCH_COMMIT", 4))
REDIS_DB_US_CO = int(os.environ.get("COLL_REDIS_DB_COMMITTER_COMMIT", 5))


def print_message(msg):
    if DEBUGGER:
        logging.warn("[DEBUG] %s" % msg)
    else:
        logging.info("[INFO] %s" % msg)


def print_error(msg):
    if DEBUGGER:
        logging.warn("[ERROR] %s" % msg)
    else:
        logging.info("[ERROR] %s" % msg)
