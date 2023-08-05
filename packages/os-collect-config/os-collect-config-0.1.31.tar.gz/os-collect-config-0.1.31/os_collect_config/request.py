# Copyright (c) 2013 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import calendar
import json
import time

from oslo.config import cfg

from os_collect_config import common
from os_collect_config import exc
from os_collect_config.openstack.common import log

CONF = cfg.CONF
logger = log.getLogger(__name__)

opts = [
    cfg.StrOpt('metadata-url',
               help='URL to query for metadata'),
]
name = 'request'


class Collector(object):
    def __init__(self, requests_impl=common.requests):
        self._requests_impl = requests_impl
        self._session = requests_impl.Session()
        self.last_modified = None

    def check_fetch_content(self, headers):
        '''Raises RequestMetadataNotAvailable if metadata should not be
        fetched.
        '''

        # no last-modified header, so fetch
        lm = headers.get('last-modified')
        if not lm:
            return

        last_modified = calendar.timegm(
            time.strptime(lm, '%a, %d %b %Y %H:%M:%S %Z'))

        # first run, so fetch
        if not self.last_modified:
            return last_modified

        if last_modified < self.last_modified:
            logger.warn(
                'Last-Modified is older than previous collection')

        if last_modified <= self.last_modified:
            raise exc.RequestMetadataNotAvailable
        return last_modified

    def collect(self):
        if CONF.request.metadata_url is None:
            logger.warn('No metadata_url configured.')
            raise exc.RequestMetadataNotConfigured
        url = CONF.request.metadata_url
        final_content = {}

        try:
            head = self._session.head(url)
            last_modified = self.check_fetch_content(head.headers)

            content = self._session.get(url)
            content.raise_for_status()
            self.last_modified = last_modified

        except self._requests_impl.exceptions.RequestException as e:
            logger.warn(e)
            raise exc.RequestMetadataNotAvailable
        try:
            value = json.loads(content.text)
        except ValueError as e:
            logger.warn(
                'Failed to parse as json. (%s)' % e)
            raise exc.RequestMetadataNotAvailable
        final_content.update(value)

        return [('request', final_content)]
