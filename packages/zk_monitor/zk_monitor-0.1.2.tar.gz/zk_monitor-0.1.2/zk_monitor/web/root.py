# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Copyright 2013 Nextdoor.com, Inc

"""
Handles generating the root index page for web requests.
"""

from tornado import web

from zk_monitor.version import __version__ as VERSION

__author__ = 'matt@nextdoor.com (Matt Wise)'


class RootHandler(web.RequestHandler):
    """Serves up the main / index page"""

    def initialize(self):
        """Log the initialization of this root handler"""
        self.state = {'version': VERSION}

    def get(self):
        self.write(self.state)
