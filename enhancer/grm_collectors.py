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

__author__ = 'Ignacio Molina Cuquerella'


class GRMCollector:

    """
        Abstract class GRM Collector

        This class will be used as common interface for each
        Git Repository Management (GRM) as GitLab, GitHub, etc. and therefore
        each GRM should inherit from this class.

        Args:
            url(String): url of the GRM API
            username (String): credential id for the GRM account
            password (Optional[String]): credential password for the GRM account

        Attributes:
            url(String): url of the GRM API
            username (String): credential id for the GRM account
            password (String): credential password for the GRM account
            kwargs (dict): additional data fields
    """

    def __init__(self, url, username, password=None):

        self.url = url
        self.username = username
        self.password = password

    def collect(self):
        pass


class GitLabCollector(GRMCollector):

    def collect(self):
        pass


class GitHubCollector(GRMCollector):

    def collect(self):
        pass
