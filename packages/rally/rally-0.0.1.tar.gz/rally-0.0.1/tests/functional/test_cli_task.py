# Copyright 2013: Mirantis Inc.
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

import os
import re
import unittest

import mock

from rally.cmd import envutils
from tests.functional import utils


FAKE_TASK_UUID = '87ab639d-4968-4638-b9a1-07774c32484a'


class TaskTestCase(unittest.TestCase):

    def _get_sample_task_config(self):
        return {
            "Dummy.dummy_random_fail_in_atomic": [
                {
                    "runner": {
                        "type": "constant",
                        "times": 100,
                        "concurrency": 5
                    }
                }
            ]
        }

    def _get_deployment_uuid(self, output):
        return re.search(
            r"Using deployment: (?P<uuid>[0-9a-f\-]{36})",
            output).group("uuid")

    def test_status(self):
        rally = utils.Rally()
        cfg = self._get_sample_task_config()
        config = utils.TaskConfig(cfg)
        rally("task start --task %s" % config.filename)
        self.assertIn("finished", rally("task status"))

    def test_detailed(self):
        rally = utils.Rally()
        cfg = self._get_sample_task_config()
        config = utils.TaskConfig(cfg)
        rally("task start --task %s" % config.filename)
        detailed = rally("task detailed")
        self.assertIn("Dummy.dummy_random_fail_in_atomic", detailed)
        self.assertIn("dummy_fail_test (2)", detailed)
        detailed_iterations_data = rally("task detailed --iterations-data")
        self.assertIn("2. dummy_fail_test (2)", detailed_iterations_data)

    def test_results(self):
        rally = utils.Rally()
        cfg = self._get_sample_task_config()
        config = utils.TaskConfig(cfg)
        rally("task start --task %s" % config.filename)
        self.assertIn("result", rally("task results"))

    def test_results_with_wrong_task_id(self):
        rally = utils.Rally()
        self.assertRaises(utils.RallyCmdError,
                          rally, "task results --uuid %s" % FAKE_TASK_UUID)

    def test_abort_with_wrong_task_id(self):
        rally = utils.Rally()
        self.assertRaises(utils.RallyCmdError,
                          rally, "task abort --uuid %s" % FAKE_TASK_UUID)

    def test_delete_with_wrong_task_id(self):
        rally = utils.Rally()
        self.assertRaises(utils.RallyCmdError,
                          rally, "task delete --uuid %s" % FAKE_TASK_UUID)

    def test_detailed_with_wrong_task_id(self):
        rally = utils.Rally()
        self.assertRaises(utils.RallyCmdError,
                          rally, "task detailed --uuid %s" % FAKE_TASK_UUID)

    def test_report_with_wrong_task_id(self):
        rally = utils.Rally()
        self.assertRaises(utils.RallyCmdError,
                          rally, "task report --tasks %s" % FAKE_TASK_UUID)

    def test_sla_check_with_wrong_task_id(self):
        rally = utils.Rally()
        self.assertRaises(utils.RallyCmdError,
                          rally, "task sla_check --uuid %s" % FAKE_TASK_UUID)

    def test_status_with_wrong_task_id(self):
        rally = utils.Rally()
        self.assertRaises(utils.RallyCmdError,
                          rally, "task status --uuid %s" % FAKE_TASK_UUID)

    def test_report_one_uuid(self):
        rally = utils.Rally()
        cfg = self._get_sample_task_config()
        config = utils.TaskConfig(cfg)
        html_file = "/tmp/test_plot.html"
        rally("task start --task %s" % config.filename)
        if os.path.exists(html_file):
            os.remove(html_file)
        rally("task report --out %s" % html_file)
        self.assertTrue(os.path.exists(html_file))
        self.assertRaises(utils.RallyCmdError,
                          rally, "task report --report %s" % FAKE_TASK_UUID)

    def test_report_bunch_uuids(self):
        rally = utils.Rally()
        cfg = self._get_sample_task_config()
        config = utils.TaskConfig(cfg)
        html_file = "/tmp/test_plot.html"
        if os.path.exists(html_file):
            os.remove(html_file)
        task_uuids = []
        for i in range(3):
            res = rally("task start --task %s" % config.filename)
            for line in res.splitlines():
                if "finished" in line:
                    task_uuids.append(line.split(" ")[1][:-1])
        rally("task report --tasks %s --out %s" % (" ".join(task_uuids),
                                                   html_file))
        self.assertTrue(os.path.exists(html_file))

    def test_report_bunch_files(self):
        rally = utils.Rally()
        cfg = self._get_sample_task_config()
        config = utils.TaskConfig(cfg)
        html_file = "/tmp/test_plot.html"
        if os.path.exists(html_file):
            os.remove(html_file)
        files = list()
        for i in range(3):
            rally("task start --task %s" % config.filename)
            path = "/tmp/task_%d.html" % i
            files.append(path)
            with open(path, "w") as tr:
                tr.write(rally("task results"))

        rally("task report --tasks %s --out %s" % (" ".join(files),
                                                   html_file))
        self.assertTrue(os.path.exists(html_file))

    def test_report_one_uuid_one_file(self):
        rally = utils.Rally()
        cfg = self._get_sample_task_config()
        config = utils.TaskConfig(cfg)
        html_file = "/tmp/test_plot.html"
        rally("task start --task %s" % config.filename)
        if os.path.exists(html_file):
            os.remove(html_file)
        task_result_file = "/tmp/report_42.json"
        with open(task_result_file, "w") as res:
            res.write(rally("task results"))

        task_run_output = rally(
            "task start --task %s" % config.filename).splitlines()
        for line in task_run_output:
            if "is finished" in line:
                task_uuid = line.split(" ")[1]
                break
        else:
            return 1

        rally("task report --tasks"
              " %s %s --out %s" % (task_result_file, task_uuid, html_file))
        self.assertTrue(os.path.exists(html_file))
        self.assertRaises(utils.RallyCmdError,
                          rally, "task report --report %s" % FAKE_TASK_UUID)

    def test_delete(self):
        rally = utils.Rally()
        cfg = self._get_sample_task_config()
        config = utils.TaskConfig(cfg)
        rally("task start --task %s" % config.filename)
        self.assertIn("finished", rally("task status"))
        rally("task delete")
        self.assertNotIn("finishe", rally("task list"))

    def test_list(self):
        rally = utils.Rally()
        cfg = self._get_sample_task_config()
        config = utils.TaskConfig(cfg)
        rally("task start --task %s" % config.filename)
        self.assertIn("finished", rally("task list --deployment MAIN"))
        self.assertIn("There are no tasks",
                      rally("task list --status failed"))
        self.assertIn("finished", rally("task list --status finished"))
        self.assertIn("deployment_name", rally("task list --all-deployments"))
        self.assertRaises(utils.RallyCmdError,
                          rally, "task list --status not_existing_status")

    def test_validate_is_valid(self):
        rally = utils.Rally()
        cfg = self._get_sample_task_config()
        config = utils.TaskConfig(cfg)
        output = rally("task validate --task %s" % config.filename)
        self.assertIn("Task config is valid", output)

    def test_validate_is_invalid(self):
        rally = utils.Rally()
        with mock.patch.dict("os.environ", utils.TEST_ENV):
            deployment_id = envutils.get_global("RALLY_DEPLOYMENT")
        cfg = {"invalid": "config"}
        config = utils.TaskConfig(cfg)
        self.assertRaises(utils.RallyCmdError,
                          rally,
                          ("task validate --task %(task_file)s "
                           "--deployment %(deployment_id)s") %
                          {"task_file": config.filename,
                           "deployment_id": deployment_id})

    def test_start(self):
        rally = utils.Rally()
        with mock.patch.dict("os.environ", utils.TEST_ENV):
            deployment_id = envutils.get_global("RALLY_DEPLOYMENT")
            cfg = self._get_sample_task_config()
            config = utils.TaskConfig(cfg)
            output = rally(("task start --task %(task_file)s "
                            "--deployment %(deployment_id)s") %
                           {"task_file": config.filename,
                            "deployment_id": deployment_id})
        result = re.search(
            r"(?P<task_id>[0-9a-f\-]{36}): started", output)
        self.assertIsNotNone(result)

    # NOTE(oanufriev): Not implemented
    def test_abort(self):
        pass


class SLATestCase(unittest.TestCase):

    def _get_sample_task_config(self, max_seconds_per_iteration=4,
                                max_failure_percent=0):
        return {
            "KeystoneBasic.create_and_list_users": [
                {
                    "args": {
                        "name_length": 10
                    },
                    "runner": {
                        "type": "constant",
                        "times": 5,
                        "concurrency": 5
                    },
                    "sla": {
                        "max_seconds_per_iteration": max_seconds_per_iteration,
                        "max_failure_percent": max_failure_percent,
                    }
                }
            ]
        }

    def test_sla_fail(self):
        rally = utils.Rally()
        cfg = self._get_sample_task_config(max_seconds_per_iteration=0.001)
        config = utils.TaskConfig(cfg)
        rally("task start --task %s" % config.filename)
        self.assertRaises(utils.RallyCmdError, rally, "task sla_check")

    def test_sla_success(self):
        rally = utils.Rally()
        config = utils.TaskConfig(self._get_sample_task_config())
        rally("task start --task %s" % config.filename)
        rally("task sla_check")
        expected = [
            {"benchmark": "KeystoneBasic.create_and_list_users",
             "criterion": "max_seconds_per_iteration",
             "detail": mock.ANY,
             "pos": 0, "status": "PASS"},
            {"benchmark": "KeystoneBasic.create_and_list_users",
             "criterion": "max_failure_percent",
             "detail": mock.ANY,
             "pos": 0, "status": "PASS"},
        ]
        data = rally("task sla_check --json", getjson=True)
        self.assertEqual(expected, data)
