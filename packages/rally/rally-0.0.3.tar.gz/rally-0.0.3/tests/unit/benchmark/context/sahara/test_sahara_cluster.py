# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import mock
from oslo_config import cfg

from rally.benchmark.context.sahara import sahara_cluster
from rally import exceptions
from tests.unit import test

CONF = cfg.CONF

BASE_CTX = "rally.benchmark.context"
CTX = "rally.benchmark.context.sahara"
SCN = "rally.benchmark.scenarios"


class SaharaClusterTestCase(test.TestCase):

    def setUp(self):
        super(SaharaClusterTestCase, self).setUp()
        self.tenants_num = 2
        self.users_per_tenant = 2
        self.users = self.tenants_num * self.users_per_tenant
        self.task = mock.MagicMock()

        self.tenants = dict()
        self.users_key = list()

        for i in range(self.tenants_num):
            self.tenants[str(i)] = {"id": str(i), "name": str(i),
                                    "sahara_image": "42"}
            for j in range(self.users_per_tenant):
                self.users_key.append({"id": "%s_%s" % (str(i), str(j)),
                                       "tenant_id": str(i),
                                       "endpoint": "endpoint"})

        CONF.set_override("cluster_check_interval", 0, "benchmark")

    @property
    def context_without_cluster_keys(self):
        return {
            "config": {
                "users": {
                    "tenants": self.tenants_num,
                    "users_per_tenant": self.users_per_tenant,
                },
                "sahara_cluster": {
                    "flavor_id": "test_flavor",
                    "workers_count": 2,
                    "plugin_name": "test_plugin",
                    "hadoop_version": "test_version"
                }
            },
            "admin": {"endpoint": mock.MagicMock()},
            "task": mock.MagicMock(),
            "users": self.users_key,
            "tenants": self.tenants
        }

    @mock.patch("%s.sahara_cluster.resource_manager.cleanup" % CTX)
    @mock.patch("%s.sahara_cluster.utils.SaharaScenario._launch_cluster" % CTX,
                return_value=mock.MagicMock(id=42))
    @mock.patch("%s.sahara_cluster.osclients" % CTX)
    def test_setup_and_cleanup(self, mock_osclients,
                               mock_launch, mock_cleanup):

        mock_sahara = mock_osclients.Clients(mock.MagicMock()).sahara()

        ctx = self.context_without_cluster_keys
        sahara_ctx = sahara_cluster.SaharaCluster(ctx)

        launch_cluster_calls = []

        for i in self.tenants:
            launch_cluster_calls.append(mock.call(
                plugin_name="test_plugin",
                hadoop_version="test_version",
                flavor_id="test_flavor",
                workers_count=2,
                image_id=ctx["tenants"][i]["sahara_image"],
                floating_ip_pool=None,
                volumes_per_node=None,
                volumes_size=1,
                auto_security_group=True,
                security_groups=None,
                node_configs=None,
                cluster_configs=None,
                enable_anti_affinity=False,
                wait_active=False
            ))

        mock_sahara.clusters.get.side_effect = [
            mock.MagicMock(status="not-active"),
            mock.MagicMock(status="active")]
        sahara_ctx.setup()

        mock_launch.assert_has_calls(launch_cluster_calls)
        sahara_ctx.cleanup()
        mock_cleanup.assert_called_once_with(names=["sahara.clusters"],
                                             users=ctx["users"])

    @mock.patch("%s.sahara_cluster.utils.SaharaScenario._launch_cluster" % CTX,
                return_value=mock.MagicMock(id=42))
    @mock.patch("%s.sahara_cluster.osclients" % CTX)
    def test_setup_and_cleanup_error(self, mock_osclients, mock_launch):

        mock_sahara = mock_osclients.Clients(mock.MagicMock()).sahara()

        ctx = self.context_without_cluster_keys
        sahara_ctx = sahara_cluster.SaharaCluster(ctx)

        launch_cluster_calls = []

        for i in self.tenants:
            launch_cluster_calls.append(mock.call(
                plugin_name="test_plugin",
                hadoop_version="test_version",
                flavor_id="test_flavor",
                workers_count=2,
                image_id=ctx["tenants"][i]["sahara_image"],
                floating_ip_pool=None,
                volumes_per_node=None,
                volumes_size=1,
                auto_security_groups=True,
                security_groups=None,
                node_configs=None,
                cluster_configs=None,
                wait_active=False
            ))

        mock_sahara.clusters.get.side_effect = [
            mock.MagicMock(status="not-active"),
            mock.MagicMock(status="error")]

        self.assertRaises(exceptions.SaharaClusterFailure, sahara_ctx.setup)
