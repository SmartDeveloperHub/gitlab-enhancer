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
import logging


import redis
import threading
import time

from enhancer.grm_collectors import GitLabCollector

__author__ = 'Ignacio Molina Cuquerella'


class CollectorsManager:

    """
        Class Collectors Manager

        This class will manage each GRM Collector using independent threads.
        The manager will start threads based on schedule.

        Args:
            r_server(redis): redis instance
            schedule (int): time between collectors
    """

    def __init__(self, r_server, schedule):

        self.r_server = r_server
        self.schedule = schedule

    def _start_collector(self, name, data):

        if 'gitlab' in name:

            collector = GitLabCollector(data.url, data.username, data.password)

        else:
            collector = None

        if collector:
            threading.Thread(target=collector.collect)\
                .start()
        else:
            logging.error("No found \'%s\' collector module.", name)

    def start(self):

        while True:

            grms = self.r_server.smembers('grms:set')
            for grm_name in grms:

                grm_data = self.r_server.get('%s:data' % grm_name)

                logging.info('Launching \'%s\' collector.', grm_name)
                self._start_collector(grm_name, grm_data)

            logging.info('Sleeping for %d seconds.', self.schedule)
            time.sleep(self.schedule)