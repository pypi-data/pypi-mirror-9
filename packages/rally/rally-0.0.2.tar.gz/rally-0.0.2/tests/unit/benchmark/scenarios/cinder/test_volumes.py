# Copyright 2013 Huawei Technologies Co.,LTD.
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

from rally.benchmark.scenarios.cinder import volumes
from tests.unit import fakes
from tests.unit import test

CINDER_VOLUMES = "rally.benchmark.scenarios.cinder.volumes.CinderVolumes"


class fake_type(object):
    name = "fake"


class CinderServersTestCase(test.TestCase):

    def test_create_and_list_volume(self):
        scenario = volumes.CinderVolumes()
        scenario._create_volume = mock.MagicMock()
        scenario._list_volumes = mock.MagicMock()
        scenario.create_and_list_volume(1, True, fakearg="f")
        scenario._create_volume.assert_called_once_with(1, fakearg="f")
        scenario._list_volumes.assert_called_once_with(True)

    def test_list_volumes(self):
        scenario = volumes.CinderVolumes()
        scenario._list_volumes = mock.MagicMock()
        scenario.list_volumes(True)
        scenario._list_volumes.assert_called_once_with(True)

    def test_create_and_delete_volume(self):
        fake_volume = mock.MagicMock()

        scenario = volumes.CinderVolumes()
        scenario._create_volume = mock.MagicMock(return_value=fake_volume)
        scenario.sleep_between = mock.MagicMock()
        scenario._delete_volume = mock.MagicMock()

        scenario.create_and_delete_volume(size=1, min_sleep=10, max_sleep=20,
                                          fakearg="f")

        scenario._create_volume.assert_called_once_with(1, fakearg="f")
        scenario.sleep_between.assert_called_once_with(10, 20)
        scenario._delete_volume.assert_called_once_with(fake_volume)

    def test_create_volume(self):
        fake_volume = mock.MagicMock()
        scenario = volumes.CinderVolumes()
        scenario._create_volume = mock.MagicMock(return_value=fake_volume)

        scenario.create_volume(1, fakearg="f")
        scenario._create_volume.assert_called_once_with(1, fakearg="f")

    def test_create_and_extend_volume(self):
        fake_volume = mock.MagicMock()

        scenario = volumes.CinderVolumes()
        scenario._create_volume = mock.MagicMock(return_value=fake_volume)
        scenario._extend_volume = mock.MagicMock(return_value=fake_volume)
        scenario.sleep_between = mock.MagicMock()
        scenario._delete_volume = mock.MagicMock()

        scenario.create_and_extend_volume(1, 2, 10, 20, fakearg="f")
        scenario._create_volume.assert_called_once_with(1, fakearg="f")
        self.assertTrue(scenario._extend_volume.called)
        scenario.sleep_between.assert_called_once_with(10, 20)
        scenario._delete_volume.assert_called_once_with(fake_volume)

    def test_create_from_image_and_delete_volume(self):
        fake_volume = mock.MagicMock()
        scenario = volumes.CinderVolumes()
        scenario._create_volume = mock.MagicMock(return_value=fake_volume)
        scenario._delete_volume = mock.MagicMock()

        scenario.create_and_delete_volume(1, image="fake_image")
        scenario._create_volume.assert_called_once_with(1,
                                                        imageRef="fake_image")

        scenario._delete_volume.assert_called_once_with(fake_volume)

    def test_create_volume_from_image(self):
        fake_volume = mock.MagicMock()
        scenario = volumes.CinderVolumes()
        scenario._create_volume = mock.MagicMock(return_value=fake_volume)

        scenario.create_volume(1, image="fake_image")
        scenario._create_volume.assert_called_once_with(1,
                                                        imageRef="fake_image")

    def test_create_volume_from_image_and_list(self):
        fake_volume = mock.MagicMock()
        scenario = volumes.CinderVolumes()
        scenario._create_volume = mock.MagicMock(return_value=fake_volume)
        scenario._list_volumes = mock.MagicMock()

        scenario.create_and_list_volume(1, True, "fake_image")
        scenario._create_volume.assert_called_once_with(1,
                                                        imageRef="fake_image")
        scenario._list_volumes.assert_called_once_with(True)

    def test_create_from_volume_and_delete_volume(self):
        fake_volume = mock.MagicMock()
        vol_size = 1
        scenario = volumes.CinderVolumes(
            context={"user": {"tenant_id": "fake"},
                     "tenant": {"id": "fake", "name": "fake",
                                "volumes": [{"id": "uuid"}]}})
        scenario._create_volume = mock.MagicMock(return_value=fake_volume)
        scenario._delete_volume = mock.MagicMock()

        scenario.create_from_volume_and_delete_volume(vol_size)
        scenario._create_volume.assert_called_once_with(1, source_volid="uuid")
        scenario._delete_volume.assert_called_once_with(fake_volume)

    def test_create_and_delete_snapshot(self):
        fake_snapshot = mock.MagicMock()
        scenario = volumes.CinderVolumes(
            context={"user": {"tenant_id": "fake"},
                     "tenant": {"id": "fake", "name": "fake",
                                "volumes": [{"id": "uuid"}]}})

        scenario._create_snapshot = mock.MagicMock(return_value=fake_snapshot)
        scenario.sleep_between = mock.MagicMock()
        scenario._delete_snapshot = mock.MagicMock()

        scenario.create_and_delete_snapshot(False, 10, 20, fakearg="f")

        scenario._create_snapshot.assert_called_once_with("uuid", force=False,
                                                          fakearg="f")
        scenario.sleep_between.assert_called_once_with(10, 20)
        scenario._delete_snapshot.assert_called_once_with(fake_snapshot)

    def test_create_and_list_snapshots(self):
        fake_snapshot = mock.MagicMock()
        scenario = volumes.CinderVolumes(
            context={"user": {"tenant_id": "fake"},
                     "tenant": {"id": "fake", "name": "fake",
                                "volumes": [{"id": "uuid"}]}})

        scenario._create_snapshot = mock.MagicMock(return_value=fake_snapshot)
        scenario._list_snapshots = mock.MagicMock()
        scenario.create_and_list_snapshots(False, True, fakearg="f")
        scenario._create_snapshot.assert_called_once_with("uuid", force=False,
                                                          fakearg="f")
        scenario._list_snapshots.assert_called_once_with(True)

    def test_create_and_attach_volume(self):
        fake_volume = mock.MagicMock()
        fake_server = mock.MagicMock()
        scenario = volumes.CinderVolumes()

        scenario._attach_volume = mock.MagicMock()
        scenario._detach_volume = mock.MagicMock()

        scenario._boot_server = mock.MagicMock(return_value=fake_server)
        scenario._delete_server = mock.MagicMock()
        scenario._create_volume = mock.MagicMock(return_value=fake_volume)
        scenario._delete_volume = mock.MagicMock()

        scenario.create_and_attach_volume(10, "img", "0")
        scenario._attach_volume.assert_called_once_with(fake_server,
                                                        fake_volume)
        scenario._detach_volume.assert_called_once_with(fake_server,
                                                        fake_volume)

        scenario._delete_volume.assert_called_once_with(fake_volume)
        scenario._delete_server.assert_called_once_with(fake_server)

    def test_create_and_upload_volume_to_image(self):
        fake_volume = mock.Mock()
        fake_image = mock.Mock()
        scenario = volumes.CinderVolumes()

        scenario._create_volume = mock.MagicMock(return_value=fake_volume)
        scenario._upload_volume_to_image = mock.MagicMock(
                return_value=fake_image)
        scenario._delete_volume = mock.MagicMock()
        scenario._delete_image = mock.MagicMock()

        scenario.create_and_upload_volume_to_image(2,
                                                   container_format="fake",
                                                   disk_format="disk",
                                                   do_delete=False)

        scenario._create_volume.assert_called_once_with(2)
        scenario._upload_volume_to_image.assert_called_once_with(fake_volume,
                                                                 False,
                                                                 "fake",
                                                                 "disk")
        scenario._create_volume.reset_mock()
        scenario._upload_volume_to_image.reset_mock()

        scenario.create_and_upload_volume_to_image(1, do_delete=True)

        scenario._create_volume.assert_called_once_with(1)
        scenario._upload_volume_to_image.assert_called_once_with(fake_volume,
                                                                 False,
                                                                 "bare",
                                                                 "raw")
        scenario._delete_volume.assert_called_once_with(fake_volume)
        scenario._delete_image.assert_called_once_with(fake_image)

    def test_create_snapshot_and_attach_volume(self):
        fake_volume = mock.MagicMock()
        fake_snapshot = mock.MagicMock()
        fake_server = mock.MagicMock()

        context = {"user": {"tenant_id": "fake"},
                   "users": [{"tenant_id": "fake", "users_per_tenant": 1}],
                   "tenant": {"id": "fake", "name": "fake", "servers": [1]}}

        scenario = volumes.CinderVolumes(context)

        scenario._attach_volume = mock.MagicMock()
        scenario._detach_volume = mock.MagicMock()
        scenario._boot_server = mock.MagicMock(return_value=fake_server)
        scenario._delete_server = mock.MagicMock()
        scenario._create_volume = mock.MagicMock(return_value=fake_volume)
        scenario._delete_volume = mock.MagicMock()
        scenario._create_snapshot = mock.MagicMock(return_value=fake_snapshot)
        scenario._delete_snapshot = mock.MagicMock()

        scenario.clients = mock.MagicMock()
        scenario.clients("nova").servers.get = mock.MagicMock(
            return_value=fake_server)

        scenario.create_snapshot_and_attach_volume()

        self.assertTrue(scenario._create_volume.called)
        scenario._create_snapshot.assert_called_once_with(fake_volume.id,
                                                          False)
        scenario._delete_snapshot.assert_called_once_with(fake_snapshot)
        scenario._attach_volume.assert_called_once_with(fake_server,
                                                        fake_volume)
        scenario._detach_volume.assert_called_once_with(fake_server,
                                                        fake_volume)
        scenario._delete_volume.assert_called_once_with(fake_volume)

    def test_create_snapshot_and_attach_volume_use_volume_type(self):
        fake_volume = mock.MagicMock()
        fake_snapshot = mock.MagicMock()
        fake_server = mock.MagicMock()
        context = {"user": {"tenant_id": "fake"},
                   "users": [{"tenant_id": "fake", "users_per_tenant": 1}],
                   "tenant": {"id": "fake", "name": "fake", "servers": [1]}}

        scenario = volumes.CinderVolumes(context)

        scenario._attach_volume = mock.MagicMock()
        scenario._detach_volume = mock.MagicMock()
        scenario._boot_server = mock.MagicMock(return_value=fake_server)
        scenario._delete_server = mock.MagicMock()
        scenario._create_volume = mock.MagicMock(return_value=fake_volume)
        scenario._delete_volume = mock.MagicMock()
        scenario._create_snapshot = mock.MagicMock(return_value=fake_snapshot)
        scenario._delete_snapshot = mock.MagicMock()
        fake = fake_type()

        scenario.clients = mock.MagicMock()
        scenario.clients("cinder").volume_types.list = mock.MagicMock(
            return_value=[fake])
        scenario.clients("nova").servers.get = mock.MagicMock(
            return_value=fake_server)

        scenario.create_snapshot_and_attach_volume(volume_type=True)

        # Make sure create volume's second arg was the correct volume type.
        # fake or none (randomly selected)
        self.assertTrue(scenario._create_volume.called)
        vol_type = scenario._create_volume.call_args_list[0][1]["volume_type"]
        self.assertTrue(vol_type is fake.name or vol_type is None)
        scenario._create_snapshot.assert_called_once_with(fake_volume.id,
                                                          False)
        scenario._delete_snapshot.assert_called_once_with(fake_snapshot)
        scenario._attach_volume.assert_called_once_with(fake_server,
                                                        fake_volume)
        scenario._detach_volume.assert_called_once_with(fake_server,
                                                        fake_volume)
        scenario._delete_volume.assert_called_once_with(fake_volume)

    def test_create_nested_snapshots_and_attach_volume(self):
        fake_volume = mock.MagicMock()
        fake_snapshot = mock.MagicMock()
        fake_clients = fakes.FakeClients()
        fake_server = fake_clients.nova().servers.create("test_server",
                                                         "image_id_01",
                                                         "flavor_id_01")
        scenario = volumes.CinderVolumes(

            context={"user": {"tenant_id": "fake"},
                     "users": [{"tenant_id": "fake", "users_per_tenant": 1}],
                     "tenant": {"id": "fake", "name": "fake",
                                "servers": [fake_server.uuid]}})

        scenario._attach_volume = mock.MagicMock()
        scenario._detach_volume = mock.MagicMock()
        scenario._delete_server = mock.MagicMock()
        scenario._create_volume = mock.MagicMock(return_value=fake_volume)
        scenario._delete_volume = mock.MagicMock()
        scenario._create_snapshot = mock.MagicMock(return_value=fake_snapshot)
        scenario._delete_snapshot = mock.MagicMock()

        scenario._clients = fake_clients

        scenario.create_nested_snapshots_and_attach_volume()

        volume_count = scenario._create_volume.call_count
        snapshots_count = scenario._create_snapshot.call_count
        attached_count = scenario._attach_volume.call_count

        self.assertEqual(scenario._delete_volume.call_count, volume_count)
        self.assertEqual(scenario._delete_snapshot.call_count, snapshots_count)
        self.assertEqual(scenario._detach_volume.call_count, attached_count)

    def test_create_nested_snapshots_calls_order(self):
        fake_volume1 = mock.MagicMock()
        fake_volume2 = mock.MagicMock()
        fake_snapshot1 = mock.MagicMock()
        fake_snapshot2 = mock.MagicMock()
        fake_clients = fakes.FakeClients()
        fake_server = fake_clients.nova().servers.create("test_server",
                                                         "image_id_01",
                                                         "flavor_id_01")
        scenario = volumes.CinderVolumes(

            context={"user": {"tenant_id": "fake"},
                     "users": [{"tenant_id": "fake", "users_per_tenant": 1}],
                     "tenant": {"id": "fake", "name": "fake",
                                "servers": [fake_server.uuid]}})

        scenario._attach_volume = mock.MagicMock()
        scenario._detach_volume = mock.MagicMock()
        scenario._delete_server = mock.MagicMock()
        scenario._create_volume = mock.MagicMock(
            side_effect=[fake_volume1, fake_volume2])
        scenario._delete_volume = mock.MagicMock()
        scenario._create_snapshot = mock.MagicMock(
            side_effect=[fake_snapshot1, fake_snapshot2])
        scenario._delete_snapshot = mock.MagicMock()
        scenario._clients = fake_clients

        scenario.create_nested_snapshots_and_attach_volume(
            nested_level={"min": 2, "max": 2})

        vol_delete_calls = [mock.call(fake_volume2), mock.call(fake_volume1)]
        snap_delete_calls = [mock.call(fake_snapshot2),
                             mock.call(fake_snapshot1)]

        scenario._delete_volume.assert_has_calls(vol_delete_calls)
        scenario._delete_snapshot.assert_has_calls(snap_delete_calls)
