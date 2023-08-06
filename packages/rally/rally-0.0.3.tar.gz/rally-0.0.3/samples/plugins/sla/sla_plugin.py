# Copyright 2015: Mirantis Inc.
# All Rights Reserved.
#
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

from rally.benchmark.sla import base
from rally.common.i18n import _


class MaxDurationRange(base.SLA):
    """Maximum allowed duration range in seconds."""
    OPTION_NAME = "max_duration_range"
    CONFIG_SCHEMA = {"type": "number", "minimum": 0.0,
                     "exclusiveMinimum": True}

    @staticmethod
    def check(criterion_value, result):
        durations = [r["duration"] for r in result if not r.get("error")]
        durations_range = max(durations) - min(durations)
        success = durations_range <= criterion_value
        msg = (_("Maximum duration range per iteration %ss, actual %ss")
               % (criterion_value, durations_range))
        return base.SLAResult(success, msg)
