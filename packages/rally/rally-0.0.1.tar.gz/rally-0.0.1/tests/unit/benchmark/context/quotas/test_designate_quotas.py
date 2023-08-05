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

import mock

from rally.benchmark.context.quotas import designate_quotas
from tests.unit import test


class DesignateQuotasTestCase(test.TestCase):

    @mock.patch("rally.benchmark.context.quotas.quotas.osclients.Clients")
    def test_update(self, client_mock):
        quotas = designate_quotas.DesignateQuotas(client_mock)
        tenant_id = mock.MagicMock()
        quotas_values = {
            "domains": 5,
            "domain_recordsets": 20,
            "domain_records": 20,
            "recordset_records": 20,
        }
        quotas.update(tenant_id, **quotas_values)
        client_mock.designate().quotas.update.assert_called_once_with(
            tenant_id, quotas_values)

    @mock.patch("rally.benchmark.context.quotas.quotas.osclients.Clients")
    def test_delete(self, client_mock):
        quotas = designate_quotas.DesignateQuotas(client_mock)
        tenant_id = mock.MagicMock()
        quotas.delete(tenant_id)
        client_mock.designate().quotas.reset.assert_called_once_with(
            tenant_id)
