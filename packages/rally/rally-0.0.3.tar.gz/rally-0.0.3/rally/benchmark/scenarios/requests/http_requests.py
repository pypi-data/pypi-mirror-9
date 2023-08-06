#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import requests

from rally.benchmark.scenarios import base
from rally.common.i18n import _
from rally import exceptions


class WrongStatusException(exceptions.RallyException):
    msg_fmt = _("Requests scenario exception: '%(message)s'")


class Requests(base.Scenario):
    """Benchmark scenarios for HTTP requests."""

    @base.scenario()
    def check_response(self, url, response=None):
        """Standard way to benchmark web services.

        This benchmark is used to GET a URL and check it with expected
        Response.

        :param url: URL to be fetched
        :param response: expected response code
        """
        resp = requests.head(url)
        if response and response != resp.status_code:
            error = "Expected HTTP request code is `%s` actual `%s`" % (
                    response, resp.status_code)
            raise WrongStatusException(error)
