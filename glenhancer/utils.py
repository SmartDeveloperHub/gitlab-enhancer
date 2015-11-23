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

# keys for transform date to long
str_time_keys = [
    'created_at', 'updated_at', 'last_activity_at',
    'due_date', 'authored_date', 'committed_date',
    'first_commit_at', 'last_commit_at', 'current_sign_in_at'
]


# function to convert time key to long
def convert_time_keys(o):
    for k in o.keys():
        if isinstance(o[k], dict):
            convert_time_keys(o[k])
        else:
            if k in str_time_keys and o[k] != "null":
                if o[k].find(".", 0, len(o[k])) > 0:
                    o[k] = o[k].split(".")[0]
                o[k] = long(o[k])