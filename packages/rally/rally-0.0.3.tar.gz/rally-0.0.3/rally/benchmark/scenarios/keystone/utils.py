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

import uuid

from rally.benchmark.scenarios import base


def is_temporary(resource):
    return resource.name.startswith(KeystoneScenario.RESOURCE_NAME_PREFIX)


class KeystoneScenario(base.Scenario):
    """Base class for Keystone scenarios with basic atomic actions."""

    RESOURCE_NAME_PREFIX = "rally_keystone_"

    @base.atomic_action_timer("keystone.create_user")
    def _user_create(self, name_length=10, email=None, **kwargs):
        """Creates keystone user with random name.

        :param name_length: length of generated (random) part of name
        :param kwargs: Other optional parameters to create users like
                        "tenant_id", "enabled".
        :returns: keystone user instance
        """
        name = self._generate_random_name(length=name_length)
        # NOTE(boris-42): password and email parameters are required by
        #                 keystone client v2.0. This should be cleanuped
        #                 when we switch to v3.
        password = kwargs.pop("password", str(uuid.uuid4()))
        email = email or (name + "@rally.me")
        return self.admin_clients("keystone").users.create(
                    name, password=password, email=email, **kwargs)

    def _resource_delete(self, resource):
        """"Delete keystone resource."""
        r = "keystone.delete_%s" % resource.__class__.__name__.lower()
        with base.AtomicAction(self, r):
            resource.delete()

    @base.atomic_action_timer("keystone.create_tenant")
    def _tenant_create(self, name_length=10, **kwargs):
        """Creates keystone tenant with random name.

        :param name_length: length of generated (random) part of name
        :param kwargs: Other optional parameters
        :returns: keystone tenant instance
        """
        name = self._generate_random_name(length=name_length)
        return self.admin_clients("keystone").tenants.create(name, **kwargs)

    @base.atomic_action_timer("keystone.create_service")
    def _service_create(self, name=None, service_type="rally_test_type",
                        description=None):
        """Creates keystone service with random name.

        :param name: name of the service
        :param service_type: type of the service
        :param description: description of the service
        :returns: keystone service instance
        """
        name = name or self._generate_random_name(prefix="rally_test_service_")
        description = description or self._generate_random_name(
            prefix="rally_test_service_description_")
        return self.admin_clients("keystone").services.create(name,
                                                              service_type,
                                                              description)

    @base.atomic_action_timer("keystone.create_users")
    def _users_create(self, tenant, users_per_tenant, name_length=10):
        """Adds users to a tenant.

        :param tenant: tenant object
        :param users_per_tenant: number of users in per tenant
        :param name_length: length of generated (random) part of name for user
        """
        for i in range(users_per_tenant):
            name = self._generate_random_name(length=name_length)
            password = name
            email = (name + "@rally.me")
            self.admin_clients("keystone").users.create(
                    name, password=password, email=email, tenant_id=tenant.id)

    @base.atomic_action_timer("keystone.create_role")
    def _role_create(self, name_length=5):
        """Creates keystone user role with random name.

        :param name_length: length of generated (random) part of role name
        :returns: keystone user role instance
        """
        role = self.admin_clients("keystone").roles.create(
            self._generate_random_name(length=name_length))
        return role

    @base.atomic_action_timer("keystone.list_users")
    def _list_users(self):
        """List users."""
        return self.admin_clients("keystone").users.list()

    @base.atomic_action_timer("keystone.list_tenants")
    def _list_tenants(self):
        """List tenants."""
        return self.admin_clients("keystone").tenants.list()

    @base.atomic_action_timer("keystone.service_list")
    def _list_services(self):
        """List services."""
        return self.admin_clients("keystone").services.list()

    @base.atomic_action_timer("keystone.get_tenant")
    def _get_tenant(self, tenant_id):
        """Get given tenant.

        :param tenant_id: tenant object
        """
        return self.admin_clients("keystone").tenants.get(tenant_id)

    @base.atomic_action_timer("keystone.get_user")
    def _get_user(self, user_id):
        """Get given user.

        :param user_id: user object
        """
        return self.admin_clients("keystone").users.get(user_id)

    @base.atomic_action_timer("keystone.get_role")
    def _get_role(self, role_id):
        """Get given user role.

        :param role_id: user role object
        """
        return self.admin_clients("keystone").roles.get(role_id)

    @base.atomic_action_timer("keystone.get_service")
    def _get_service(self, service_id):
        """Get service with given service id.

        :param service_id: id for service object
        """
        return self.admin_clients("keystone").services.get(service_id)

    def _get_service_by_name(self, name):
        for i in self._list_services():
            if i.name == name:
                return i

    @base.atomic_action_timer("keystone.delete_service")
    def _delete_service(self, service_id):
        """Delete service.

        :param service_id: service to be deleted
        """
        self.admin_clients("keystone").services.delete(service_id)
