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
from flask import Flask, make_response, jsonify
from flask_negotiate import produces, consumes
import json

__author__ = 'Ignacio Molina Cuquerella'


class GitEnhancer:

    """
        Git Enhancer class

        This class will mix the information gathered by Git Collector service
        and the different GRM if any to enrich the Git Protocol information;
        and then deploy a RESTFul API service to offer the outcome.

        Args:
            config (setting.py): configuration from settings.py

        Attributes:
            app(Flask): Flask service for deploying endpoints
    """

    def __init__(self, config):

        self.app = Flask(__name__)

        # Root path (same as /api)
        @self.app.route('/', methods=['GET'])
        @produces('application/json')
        def root():
            return api()

        # Get information about Git Enhancer
        @self.app.route('/api', methods=['GET'])
        @produces('application/json')
        def api():
            return jsonify(Name=config.GE_LONGNAME,
                           Version=config.GE_VERSION)
