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

__author__ = 'Alejandro F. Carrera'

DEBUGGER = True

ENHANCER_LISTEN_PROT = os.environ.get("ENH_LISTEN_PROT", "http")
ENHANCER_LISTEN_PORT = int(os.environ.get("ENH_LISTEN_PORT", 5000))
ENHANCER_LISTEN_IP = os.environ.get("ENH_LISTEN_IP", "0.0.0.0")

# GITLAB_PASS = '5iveL!fe'

REDIS_IP = os.environ.get("ENH_REDIS_IP", "127.0.0.1")
REDIS_PORT = int(os.environ.get("ENH_REDIS_PORT", 6379))
REDIS_PASS = os.environ.get("ENH_REDIS_PASS", None)
REDIS_DB = int(os.environ.get("ENH_REDIS_DB", 0))
