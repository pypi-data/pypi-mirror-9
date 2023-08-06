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

import abc

import jsonschema
import six

from rally.common.i18n import _
from rally.common import log as logging
from rally.common import utils
from rally import consts
from rally.deploy.serverprovider import provider
from rally import exceptions


LOG = logging.getLogger(__name__)


@six.add_metaclass(abc.ABCMeta)
class EngineFactory(object):
    """Base class of all deployment engines.

    It's a base class with self-discovery of subclasses. Each subclass
    has to implement deploy() and cleanup() methods. By default, each engine
    located as a submodule of the package rally.deploy.engines is
    auto-discovered.

    Example of usage with a simple engine:

    # Add new engine with __name__ == "A"
    class A(EngineFactory):
        def __init__(self, deployment):
            # do something

        def deploy(self):
            # Make a deployment and return OpenStack endpoints.
            # The endpoints may have either admin or ordinary users
            # permissions (depending on how the deploy engine has been
            # initialized).
            return [endpoint_1, endpoint_2, ...]

        def cleanup(self):
            # Destroy OpenStack deployment and free resource

    An instance of this class used as a context manager on any unsafe
    operations to a deployment. Any unhandled exceptions bring a status
    of the deployment to the inconsistent state.

    with EngineFactory.get_engine("A", deployment) as deploy:
        # deploy is an instance of the A engine
        # perform all usage operations on your cloud
    """
    def __init__(self, deployment):
        self.deployment = deployment
        self.config = deployment["config"]

    def validate(self):
        # TODO(sskripnick): remove this checking when config schema
        # is done for all available engines
        if hasattr(self, "CONFIG_SCHEMA"):
            jsonschema.validate(self.config, self.CONFIG_SCHEMA)

    def get_provider(self):
        if "provider" in self.config:
            return provider.ProviderFactory.get_provider(
                self.config["provider"], self.deployment)

    @staticmethod
    def get_by_name(name):
        """Return Engine class by name."""
        for engine in utils.itersubclasses(EngineFactory):
            if name == engine.__name__:
                return engine
        raise exceptions.NoSuchEngine(engine_name=name)

    @staticmethod
    def get_engine(name, deployment):
        """Returns instance of a deploy engine with corresponding name."""
        try:
            engine_cls = EngineFactory.get_by_name(name)
            return engine_cls(deployment)
        except exceptions.NoSuchEngine:
            LOG.error(_("Deployment %(uuid)s: Deploy engine for %(name)s "
                        "does not exist.") %
                      {"uuid": deployment["uuid"], "name": name})
            deployment.update_status(consts.DeployStatus.DEPLOY_FAILED)
            raise exceptions.NoSuchEngine(engine_name=name)

    @staticmethod
    def get_available_engines():
        """Returns a list of names of available engines."""
        return [e.__name__ for e in utils.itersubclasses(EngineFactory)]

    @abc.abstractmethod
    def deploy(self):
        """Deploy OpenStack cloud and return endpoints."""

    @abc.abstractmethod
    def cleanup(self):
        """Cleanup OpenStack deployment."""

    @utils.log_deploy_wrapper(LOG.info, _("OpenStack cloud deployment."))
    def make_deploy(self):
        self.deployment.set_started()
        endpoints = self.deploy()
        self.deployment.set_completed()
        return endpoints

    @utils.log_deploy_wrapper(LOG.info,
                              _("Destroy cloud and free allocated resources."))
    def make_cleanup(self):
        self.deployment.update_status(consts.DeployStatus.CLEANUP_STARTED)
        self.cleanup()
        provider = self.get_provider()
        if provider:
            provider.destroy_servers()
        self.deployment.update_status(consts.DeployStatus.CLEANUP_FINISHED)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if exc_type is not None:
            exc_info = None
            if not issubclass(exc_type, exceptions.InvalidArgumentsException):
                exc_info = (exc_type, exc_value, exc_traceback)
            LOG.error(_("Deployment %(uuid)s: Error has occurred into context "
                        "of the deployment"),
                      {"uuid": self.deployment["uuid"]},
                      exc_info=exc_info)
            status = self.deployment["status"]
            if status in (consts.DeployStatus.DEPLOY_INIT,
                          consts.DeployStatus.DEPLOY_STARTED):
                self.deployment.update_status(
                    consts.DeployStatus.DEPLOY_FAILED)
            elif status == consts.DeployStatus.DEPLOY_FINISHED:
                self.deployment.update_status(
                    consts.DeployStatus.DEPLOY_INCONSISTENT)
            elif status == consts.DeployStatus.CLEANUP_STARTED:
                self.deployment.update_status(
                    consts.DeployStatus.CLEANUP_FAILED)
