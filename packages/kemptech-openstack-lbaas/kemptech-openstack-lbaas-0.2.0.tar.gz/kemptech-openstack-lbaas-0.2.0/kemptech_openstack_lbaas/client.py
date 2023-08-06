#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.

import abc
from kemptech_openstack_lbaas import constants as kemp_consts
from neutron.common import exceptions
from neutron.openstack.common import log
import requests
import six

LOG = log.getLogger(__name__)


class KempClient(object):

    def __init__(self, address, username, password):
        if (address is None or
            username is None or
            password is None):
            raise KempClientRequestError(msg="Missing URL credentials.")
        else:
            self.loadbalancer = ("https://%s:%s@%s/access/"
                    % (username, password, address))
            self.virtual_services = []
            self.real_servers = []

    def create_virtual_service(self, params):
        virtual_service = VirtualService(self.loadbalancer, params)
        virtual_service.create()
        self.virtual_services.append(virtual_service)

    def update_virtual_service(self, old_params, params, batch_update=False):
        old_virtual_service = VirtualService(self.loadbalancer, old_params)
        virtual_service = VirtualService(self.loadbalancer, params)
        if batch_update:
            pass
        else:
            for service in self.virtual_services:
                if service.id == old_virtual_service.id:
                    service.update(virtual_service.to_dict())
        self.virtual_services.remove(old_virtual_service)
        self.virtual_services.append(virtual_service)

    def delete_virtual_service(self, params):
        virtual_service = VirtualService(self.loadbalancer, params)
        for service in self.virtual_services:
            if service.id == virtual_service.id:
                service.delete()

    def delete_virtual_services(self):
        for virtual_service in self.virtual_services:
            virtual_service.delete()

    def create_real_server(self, params):
        """Attach a real server to a virtual service."""
        real_server = RealServer(self.loadbalancer, params)
        real_server.create()
        self.real_servers.append(real_server)

    def update_real_server(self, old_params, params):
        """Update a real server's parameters on a virtual service."""
        old_real_server = RealServer(self.loadbalancer, old_params)
        real_server = RealServer(self.loadbalancer, params)
        for server in self.real_servers:
            if server.id == old_real_server.id:
                server.update(real_server.to_dict())
        self.real_servers.remove(old_real_server)
        self.real_servers.append(real_server)

    def delete_real_server(self, params):
        """Delete a real server from a virtual service."""
        real_server = RealServer(self.loadbalancer, params)
        for server in self.real_servers:
            if server.id == real_server.id:
                server.delete()

    def update_health_check(self, check_params):
        """Update health check parameters for virtual services."""
        # pop the checker params, call update vs
        # create a health and a vs object
        checkers = {}
        for checker in kemp_consts.CHECKER_OPTS:
            checkers.update(check_params.popitem(checker))
        health_monitor = HealthMonitor(self.loadbalancer, checkers)
        health_monitor.update()
        virtual_service = VirtualService(self.loadbalancer, check_params)
        for service in self.virtual_services:
            if service.id == virtual_service.id:
                service.update(virtual_service.to_dict())


class BaseKempModel(object):
    """A class to build objects based on KEMP RESTful API.

    Subclasses built from this class need to name their parameters
    the same as their RESTful API counterpart in order for this
    class to work.
    """

    API_NAME = ""  # Subclasses must define this.

    def __init__(self, loadbalancer, parameters):
        self.loadbalancer = loadbalancer
        for api_key, api_value in parameters:
            self.__dict__[api_key] = api_value
        if not self.exists:
            self._get_request('add' + self.API_NAME, self.id)

    def create(self):
        if not self.exists:
            self._get_request('add' + self.API_NAME, self.id)

    def update(self, obj):
        if self.exists:
            # Remove the ID parameters and update the attributes.
            for model_id in self.id:
                if model_id in obj.__dict__:
                    obj.__dict__.pop(model_id)
            self.__dict__.update(obj.__dict__)
            self._get_request('mod' + self.API_NAME, self.to_dict())

    def delete(self):
        if self.exists:
            self._get_request('del' + self.API_NAME, self.id)

    @property
    def exists(self):
        return self._get_request('show' + self.API_NAME, self.id) < 300

    @abc.abstractproperty
    def id(self):
        """Must return a dict with unique ID parameters for KEMP API."""
        pass

    @id.setter
    @abc.abstractmethod
    def id(self, value):
        pass

    def to_dict(self):
        """Return a dictionary containing attributes of class.

        Ignore attributes that are set to None or are not a string or int;
        also ignore id as it is not an API thing.
        """
        attributes = {}
        for attr in self.__dict__:
            if (self.__dict__[attr] is not None or
                not self.__dict__[attr] == 'id' or
                not isinstance(self.__dict__[attr], six.string_types) or
                not isinstance(self.__dict__[attr], (int, long))):
                attributes[attr] = self.__dict__[attr]
        return attributes

    def _get_request(self, cmd, params):
        """Perform a HTTP GET.
        Arguments:
            cmd - The command to run.
            params - Dict containing parameters.
        Returns:
            The status code of request
            The response text body.
        """
        cmd_url = self.loadbalancer + cmd + "?"
        LOG.debug("cmd_url: %s" % cmd_url)
        LOG.debug("params: %s" % repr(params))

        try:
            response = requests.request('GET', cmd_url, params=params,
                                        verify=False)
        except requests.exceptions.ConnectionError:
            LOG.error(_LE("A connection error occurred to %s"),
                      self.loadbalancer)
            raise KempClientRequestError(response.status_code, response.text)
        except requests.exceptions.URLRequired:
            LOG.error(_LE("%s is not a valid URL to make a request with."),
                      cmd_url)
            raise KempClientRequestError(response.status_code, response.text)
        except requests.exceptions.TooManyRedirects:
            LOG.error(_LE("Too many redirects with requst to %s"), cmd_url)
            raise KempClientRequestError(response.status_code, response.text)
        except requests.exceptions.Timeout:
            LOG.error(_LE("A connection error occurred to %s"),
                      self.loadbalancer)
            raise KempClientRequestError(response.status_code, response.text)
        except requests.exceptions.RequestException:
            LOG.error(_LE("An uknown error occurred with request to %s"),
                      cmd_url)
            raise KempClientRequestError(response.status_code, response.text)
        return response.status_code, response.text


class VirtualService(BaseKempModel):

    API_NAME = 'vs'

    def __init__(self, loadbalancer, parameters):
        self.id = parameters
        super(VirtualService, self).__init__(loadbalancer, parameters)

    @property
    def id(self):
        return {
            'vs': self.vs,
            'port': self.port,
            'prot': self.prot,
        }

    @id.setter
    def id(self, value):
        self.vs = value['vs']
        self.port = value['port']
        self.prot = value['prot']
        self.rs = value['rs']
        self.rsport = value['rsport']

    def update(self, virtual_service):
        if self.vsport is not None:
            if super(VirtualService, self).update() < 300:
                self.port = self.vsport
                self.vsport = None
        else:
            super(VirtualService, self).update(virtual_service)


class RealServer(BaseKempModel):

    API_NAME = 'rs'

    def __init__(self, loadbalancer, parameters):
        self.id = parameters
        super(RealServer, self).__init__(loadbalancer, parameters)

    @property
    def id(self):
        return {
            'vs': self.vs,
            'port': self.port,
            'prot': self.prot,
            'rs': self.rs,
            'rsport': self.rsport,
        }

    @id.setter
    def id(self, value):
        self.vs = value['vs']
        self.rs = value['rs']
        self.port = value['port']
        self.prot = value['prot']
        self.rsport = value['rsport']


class HealthMonitor(BaseKempModel):

    API_NAME = 'health'

    def __init__(self, parameters):
        self.id = parameters
        super(HealthMonitor, self).__init__(parameters)

    @property
    def id(self):
        """HealthMonitor's do not have a unique ID as they are global"""
        return None

    @id.setter
    def id(self, value):
        self.vs = value['vs']
        self.rs = value['rs']
        self.port = value['port']
        self.prot = value['prot']
        self.rsport = value['rsport']


class KempClientRequestError(exceptions.NeutronException):
    """Raised if HTTP request has failed."""

    def __init__(self, code=None, msg=None):
        if msg is None:
            if code == 400:
                msg = "Mandatory parameter missing from request."
            elif code == 401:
                msg = "Username or password is missing or is incorrect."
            elif code == 403:
                msg = "Incorrect permissions."
            elif code == 404:
                msg = "Not found."
            elif code == 405:
                msg = "Unknown command."
            else:
                msg = "An unknown error has occurred."
        self.message = _("KEMP Client Error: %(code)s; %(msg)s") % (code, msg)
        super(KempClientRequestError, self).__init__()
