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

""" Rally command: use """

import os

from rally.cmd import cliutils
from rally.common import fileutils
from rally import db
from rally import exceptions


class UseCommands(object):
    """Set of commands that allow you to set an active deployment and task.

    Active deployment and task allow you not to specify deployment UUID and
    task UUID in the commands requiring this parameter.
    """

    def _update_openrc_deployment_file(self, deployment, endpoint):
        openrc_path = os.path.expanduser('~/.rally/openrc-%s' % deployment)
        # NOTE(msdubov): In case of multiple endpoints write the first one.
        with open(openrc_path, 'w+') as env_file:
            env_file.write('export OS_AUTH_URL=%(auth_url)s\n'
                           'export OS_USERNAME=%(username)s\n'
                           'export OS_PASSWORD=%(password)s\n'
                           'export OS_TENANT_NAME=%(tenant_name)s\n'
                           % endpoint)
            if endpoint.get('region_name'):
                env_file.write('export OS_REGION_NAME=%(region_name)s\n'
                               % endpoint)
        expanded_path = os.path.expanduser('~/.rally/openrc')
        if os.path.exists(expanded_path):
            os.remove(expanded_path)
        os.symlink(openrc_path, expanded_path)

    def _update_attribute_in_global_file(self, attribute, value):
        expanded_path = os.path.expanduser('~/.rally/globals')
        fileutils.update_env_file(expanded_path, attribute, '%s\n' % value)

    def _ensure_rally_configuration_dir_exists(self):
        if not os.path.exists(os.path.expanduser('~/.rally/')):
            os.makedirs(os.path.expanduser('~/.rally/'))

    @cliutils.deprecated_args(
        "--uuid", dest="deployment", type=str,
        required=False, help="UUID of the deployment.")
    @cliutils.deprecated_args(
        "--name", dest="deployment", type=str,
        required=False, help="Name of the deployment.")
    @cliutils.args('--deployment', type=str, dest='deployment',
                   help='UUID or name of the deployment')
    def deployment(self, deployment=None):
        """Set active deployment.

        :param deployment: UUID or name of a deployment
        """

        try:
            deploy = db.deployment_get(deployment)
            print('Using deployment: %s' % deploy['uuid'])
            self._ensure_rally_configuration_dir_exists()
            self._update_attribute_in_global_file('RALLY_DEPLOYMENT',
                                                  deploy['uuid'])
            self._update_openrc_deployment_file(
                deploy['uuid'], deploy.get('admin') or deploy.get('users')[0])
            print ('~/.rally/openrc was updated\n\nHINTS:\n'
                   '* To get your cloud resources, run:\n\t'
                   'rally show [flavors|images|keypairs|networks|secgroups]\n'
                   '\n* To use standard OpenStack clients, set up your env by '
                   'running:\n\tsource ~/.rally/openrc\n'
                   '  OpenStack clients are now configured, e.g run:\n\t'
                   'glance image-list')
        except exceptions.DeploymentNotFound:
            print('Deployment %s is not found.' % deployment)
            return 1

    @cliutils.args('--uuid', type=str, dest='task_id', required=False,
                   help='UUID of the task')
    def task(self, task_id):
        """Set active task.

        :param task_id: a UUID of task
        """
        print('Using task: %s' % task_id)
        self._ensure_rally_configuration_dir_exists()
        db.task_get(task_id)
        self._update_attribute_in_global_file('RALLY_TASK', task_id)

    @cliutils.args("--uuid", type=str, dest="verification_id", required=False,
                   help="UUID of the verification")
    def verification(self, verification_id):
        """Set active verification.

        :param verification_id: a UUID of verification
        """
        print('Verification UUID: %s' % verification_id)
        self._ensure_rally_configuration_dir_exists()
        db.verification_get(verification_id)
        self._update_attribute_in_global_file('RALLY_VERIFICATION',
                                              verification_id)
