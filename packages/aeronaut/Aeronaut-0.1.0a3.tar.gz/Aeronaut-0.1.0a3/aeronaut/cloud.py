from os.path import expanduser, exists, join
import re
import requests
import yaml

from aeronaut.resource.cloud.resource import RootElementNotFoundError
from aircraft.response import Response


# ==========
# EXCEPTIONS
# ==========

class AuthenticationError(Exception):

    def __init__(self, response):
        message = 'Can\'t authenticate against {remote}. ' \
                  'Server returned HTTP status {code}'.format(
                      remote=response.url, code=response.status_code)
        super(AuthenticationError, self).__init__(message)

        self.response = response


class NotAuthenticatedError(Exception):

    def __init__(self, response):
        message = 'The operation requires authentication beforehand'
        super(AuthenticationError, self).__init__(message)


class OperationForbiddenError(Exception):

    def __init__(self, status):
        message = "The server responded with a 403: Forbidden error. " \
                  "{code}: {details}".format(code=status.result_code,
                                             details=status.result_detail)
        super(OperationForbiddenError, self).__init__(message)

        self.status = status


class UnauthorizedError(Exception):

    def __init__(self):
        message = "Unable to complete the request due to authorization " \
                  "error. The session has likely expired. Please check " \
                  "and re-authenticate as needed."
        super(UnauthorizedError, self).__init__(message)


# ================
# CONNECTION CLASS
# ================

class CloudConnection(object):
    """Represents a connection to a DiData Cloud provider"""

    def __init__(self, endpoint, api_version='v0.9'):
        """
        :param str endpoint: The endpoint to connect to when
            :meth:`~aeronaut.cloud.CloudConnection.authenticate` is called.

        :param str api_version: Optional. The API version to use.
            Defaults to v0.9 when not provided. Note that the default may
            be updated to a later API version in future releases.
        """
        self._endpoint = endpoint
        self._api_version = api_version
        self._my_account = None

    # =================
    # PUBLIC PROPERTIES
    # =================

    @property
    def api_version(self):
        return self._api_version

    @property
    def base_url(self):
        return 'https://{}'.format(self.endpoint)

    @property
    def endpoint(self):
        return self._endpoint

    @property
    def is_authenticated(self):
        return self.my_account is not None

    @property
    def my_account(self):
        return self._my_account

    # ==================
    # PRIVATE PROPERTIES
    # ==================

    @property
    def _dotfile_credentials(self):
        """
        Gets the applicable credentials from ~/.aeronaut when available. If
        not available, None will be returned.
        """
        path = join(expanduser('~'), '.aeronaut')

        if not exists(path):
            return None

        if not hasattr(self, '__dotfile_credentials__'):
            with open(path, 'r') as dotfile:
                d = yaml.load(dotfile)
                if self.endpoint not in d:
                    return None
                self.__dotfile_credentials__ = d[self.endpoint]

        return self.__dotfile_credentials__

    @property
    def _http_session(self):
        if not hasattr(self, '__http_session__'):
            self.__http_session__ = requests.Session()

        return self.__http_session__

    # ==============
    # PUBLIC METHODS
    # ==============

    def add_storage_to_server(self, server_id, size_gb, disk_speed_id=None,
                              org_id=None):
        """Creates an additional disk/volume for an existing server

        :param str server_id: The ID of the server to add storage to.

        :param int size_gb: The size of the disk in GB.

        :param str disk_speed_id: Optional. The id of the disk speed to use. This
            can be obtained via :meth:`aeronaut.resource.cloud.data_center.DataCenter.hypervisor.disk_speeds`.
            See the sample usage below for guidance.

        :param str org_id: Optional. The organization ID that owns the
            server. Defaults to the current user's :py:attr:`~aeronaut.resource.cloud.account.Account.org_id`
            if not provided.

        :returns: The status of the operation.
        :rtype: :class:`aeronaut.resource.cloud.server.AddStorageToServerStatus`

        Sample usage:

        .. code-block:: python

            import aeronaut.cloud

            conn = aeronaut.cloud.connect('api-na.dimensiondata.com')

            filters = [
                ['name', '==', 'myserver01']
            ]

            servers = conn.list_servers(filters=filters)
            server = servers[0]

            dc = next(dc for dc in conn.list_data_centers() if dc.is_default)
            speed = dc.hypervisor.disk_speeds[0]

            # The disk_speed_id argument below is optional
            result = conn.add_storage_to_server(server_id=server.id,
                                                size_gb=13,
                                                disk_speed_id=speed.id)

            print result.is_success
            print result.result_detail
        """  # NOQA
        params = {
            'org_id': self._ensure_org_id(org_id),
            'server_id': server_id,
            'size_gb': size_gb,
            'disk_speed_id': disk_speed_id
        }
        response = self.request('add_storage_to_server', params=params)
        self._raise_if_unauthorized(response)
        return self._deserialize('server.AddStorageToServerStatus',
                                 response.body)

    def authenticate(self):
        """Authenticates against the endpoint provided during initialization

        To successfully authenticate against the given endpoint, the method
        will look for a file in the path ``~/.aeronaut`` with a section name
        matching the same endpoint. The file must be valid YAML with the
        following structure::

            api-na.dimensiondata.com:
                username: myuser
                password: mypassword

            another.endpoint.com:
                username: myotheruser
                password: mypasswordtoo!

        If the backend server does not return an HTTP status code of 200 or
        201, the method will raise
        :class:`aeronaut.cloud.AuthenticationError`
        """
        kwargs = {}

        if self._dotfile_credentials is not None:
            credentials = self._dotfile_credentials
            username = credentials['username']
            password = credentials['password']
            kwargs['auth'] = (username, password)

        # The server does pre-emptive basic authentication and self.request()
        # Provides basic auth data when available. So calling any method will
        # automatically authenticate us. We just happen to choose the
        # 'get_my_account' request for this process so that we will have a copy
        # of the account in memory.
        response = self.request('get_my_account', **kwargs)

        if response.status_code in [200, 201]:
            self._my_account = self._deserialize('my_account.MyAccount',
                                                 response.body)
        else:
            raise AuthenticationError(response)

    def clean_failed_server_deployment(self, server_id, org_id=None):
        """Removes a failed server deployment from the list of pending
        deployed servers

        :param str server_id: The id of the server you wish to remove.

        :param str org_id: Optional. The organization ID that owns the
            server. Defaults to the current user's
            :py:attr:`~aeronaut.resource.cloud.account.Account.org_id` if not
            provided.

        :returns: The status of the operation
        :rtype: :class:`aeronaut.resource.cloud.server.CleanFailedServerDeploymentStatus`
        """  # NOQA
        params = {
            'org_id': self._ensure_org_id(org_id),

            'server_id': server_id
        }
        response = self.request('clean_failed_server_deployment',
                                params=params)
        self._raise_if_unauthorized(response)
        return self._deserialize('server.CleanFailedServerDeploymentStatus',
                                 response.body)

    def create_acl_rule(self, network_id, name, position, action, protocol,
                        type, source_ip=None, source_netmask=None,
                        dest_ip=None, dest_netmask=None, from_port=None,
                        to_port=None, org_id=None):
        """Creates an ACL Rule

        :param str network_id: The id of the network where the ACL rule
            is to be created.

        :param str name: The name of the ACL rule.

        :param int position: The position of the ACL rule. Valid range
            is 100-500 inclusive.

        :param str action: One of PERMIT or DENY.

        :param str protocol: One of IP, ICMP, TCP, UDP.

        :param str type: For inbound rules, provide OUTSIDE_ACL. For
            outbound rules, provide INSIDE_ACL.

        :param str source_ip: Optional. IP address of the traffic
            source.

        :param str source_netmaks: Optional. Netmask for the source IP.

        :param str dest_ip: Optional. IP address of the traffic
            destination.

        :param str dest_netmask: Optional. for the destination IP.

        :param int from_port: Optional. Valid range is 1-65535
            inclusive

        :param int to_port: Optional. Valid range is 1-65535 inclusive

        :param str org_id: Optional. The organization ID that owns the
            network. Defaults to the current user's
            :py:attr:`~aeronaut.resource.cloud.account.Account.org_id` if not
            provided.

        :returns: The status of the operation
        :rtype: :class:`aeronaut.resource.cloud.acl.CreateAclRuleStatus`
        """
        org_id = self._ensure_org_id(org_id)

        params = {
            'type': type,
            'action': action,
            'dest_ip': dest_ip,
            'dest_netmask': dest_netmask,
            'from_port': from_port,
            'name': name,
            'network_id': network_id,
            'org_id': org_id,
            'position': position,
            'protocol': protocol,
            'source_ip': source_ip,
            'source_netmask': source_netmask,
            'to_port': to_port
        }

        response = self.request('create_acl_rule', params=params)
        self._raise_if_unauthorized(response)

        # The underlying REST API is inconsistent. When succesful, it returns
        # an AclRule element, otherwise it returns a Status element. This is an
        # attempt to make our own return value consistent.
        try:
            return self._deserialize('acl.CreateAclRuleStatus', response.body)
        except RootElementNotFoundError:
            xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <ns6:Status xmlns:ns6="http://oec.api.opsource.net/schemas/general">
                <ns6:operation>Add ACL Rule</ns6:operation>
                <ns6:result>SUCCESS</ns6:result>
                <ns6:resultDetail>ACL Rule created succesfully</ns6:resultDetail>
                <ns6:resultCode>REASON_0</ns6:resultCode>
            </ns6:Status>
            """  # NOQA
            return self._deserialize('acl.CreateAclRuleStatus', xml)

    def create_network(self, location, name, org_id=None, description=None):
        """Creates a network with the given name in the given location

        :param str location: The data center where the network is to be
            created.

        :param str name: The name of the network

        :param str org_id: Optional. The organization ID that owns the
            network. Defaults to the current user's
            :py:attr:`~aeronaut.resource.cloud.account.Account.org_id` if not
            provided.

        :returns: The status of the operation
        :rtype: :class:`aeronaut.resource.cloud.network.CreateNetworkStatus`
        """
        org_id = self._ensure_org_id(org_id)

        params = {
            'org_id': org_id,
            'location': location,
            'name': name
        }

        if description:
            params['description'] = description

        response = self.request('create_network', params=params)
        self._raise_if_unauthorized(response)

        return self._deserialize('network.CreateNetworkStatus', response.body)

    def delete_acl_rule(self, network_id, rule_id, org_id=None):
        """Deletes the given rule from the given network

        :param str network_id: The ID of the network associated with
            the ACL rule.

        :param str rule_id: The ID of the ACL rule.

        :param str org_id: Optional. The organization ID that owns the
            network. Defaults to the current user's
            :py:attr:`~aeronaut.resource.cloud.account.Account.org_id` if not
            provided.

        :returns: The status of the operation
        :rtype: :class:`aeronaut.resource.cloud.acl.DeleteAclRuleStatus`
        """
        org_id = self._ensure_org_id(org_id)

        params = {
            'org_id': org_id,
            'network_id': network_id,
            'rule_id': rule_id
        }

        response = self.request('delete_acl_rule', params=params)
        self._raise_if_unauthorized(response)

        return self._deserialize('acl.DeleteAclRuleStatus', response.body)

    def delete_server(self, server_id, org_id=None):
        """Delete the given server. Note that a Server must be stopped before
        it can be deleted

        :param str server_id: The ID of the server to delete.

        :param str org_id: Optional. The organization ID that owns the
            server. Defaults to the current user's
            :py:attr:`~aeronaut.resource.cloud.account.Account.org_id` if not
            provided.

        :returns: The status of the operation
        :rtype: :mod:`aeronaut.resource.cloud.server.DeleteServerStatus`
        """
        params = {
            'org_id': self._ensure_org_id(org_id),
            'server_id': server_id
        }

        response = self.request('delete_server', params=params)
        self._raise_if_unauthorized(response)
        return self._deserialize('server.DeleteServerStatus', response.body)

    def deploy_server(self, name, image_id, org_id=None, **kwargs):
        """Deploys a new server from an existing customer or base image

        :param str name: Human-friendly name of the server.

        :param str image_id: ID of the image to use for this server.

        :param str org_id: Optional. The organization ID that owns the
            server. Defaults to the current user's
            :py:attr:`~aeronaut.resource.cloud.account.Account.org_id` if not
            provided. authenticated user's account will be used.

        Additional arguments are listed in the source code of
        :class:`aeronaut.request.cloud.v0_9.deploy_server.DeployServer`

        :returns: The status of the operation
        :rtype: :class:`aeronaut.resource.cloud.server.DeployServerStatus`

        Sample usage:

        .. code-block:: python

            import aeronaut.cloud

            conn = aeronaut.cloud.connect('api-na.dimensiondata.com')

            dcs = conn.list_data_centers()
            dc = next(dc for dc in dcs if dc.is_default)

            images = conn.list_base_images(filters=filters)
            image = images[0]

            networks = conn.list_networks(location=dc.location)
            network = networks[0]

            status = conn.deploy_server(name='My new server',
                                        description='A new deployment',
                                        image_id=image.id,
                                        start=True,
                                        admin_password='asdfkjhw',
                                        network_id=network.id)
            print status.is_success

        Note how there is no argument for adding disks above. To add one,
        you need to call :meth:`~aeronaut.cloud.CloudConnection.add_storage_to_server`
        """  # NOQA
        kwargs['org_id'] = self._ensure_org_id(org_id)
        kwargs['name'] = name
        kwargs['image_id'] = image_id

        response = self.request('deploy_server', params=kwargs)
        self._raise_if_unauthorized(response)

        return self._deserialize('server.DeployServerStatus', response.body)

    def does_image_name_exist(self, image_name, location, org_id=None):
        """Returns True if the given image name exists in the data center

        :param str image_name: The name of the image

        :param str location: Location where the image is expected to exist.
            This can be taken from the `location` property of the
            :class:`~aeronaut.resource.cloud.data_center.DataCenter` resource
            object.

        :param str org_id: Optional. The organization ID that owns the
            image. Defaults to the current user's
            :py:attr:`~aeronaut.resource.cloud.account.Account.org_id` if not
            provided.

        :returns: :class:`True` if the image_name exists. :class:`False` if
            otherwise.
        :rtype: :class:`bool`
        """
        org_id = self._ensure_org_id(org_id)

        params = {
            'org_id': org_id,
            'image_name': image_name,
            'location': location
        }

        response = self.request('does_image_name_exist', params=params)
        self._raise_if_unauthorized(response)
        exists = self._deserialize('image.ImageNameExists', response.body)

        return exists.is_true

    def get_server_image(self, image_id, org_id=None):
        """Returns a full description of the indicated server image

        :param str image_id: The id of the image to retrieve

        :param str org_id: Optional. The organization ID that owns the
            image. Defaults to the current user's
            :py:attr:`~aeronaut.resource.cloud.account.Account.org_id` if not
            provided.

        :returns: The image with the given ID
        :rtype: :class:`aeronaut.resource.cloud.image.Image`
        """
        params = {
            'org_id': self._ensure_org_id(org_id),
            'image_id': image_id
        }

        response = self.request('get_server_image', params=params)
        self._raise_if_unauthorized(response)
        image = self._deserialize('image.ServerImage', response.body)

        return image

    def list_acl_rules(self, network_id, org_id=None):
        """Returns a list of ACL rules

        :param str network_id: The ID of the network whose ACL rules you want
            to retrieve.

        :param str org_id: Optional. The organization ID that owns the
            network. Defaults to the current user's
            :py:attr:`~aeronaut.resource.cloud.account.Account.org_id` if not
            provided.

        :returns: A list of ACL rules in the given network
        :rtype: :class:`aeronaut.resource.cloud.acl.AclRuleList`
        """
        if not org_id:
            org_id = self.my_account.org_id

        params = {
            'network_id': network_id,
            'org_id': org_id
        }

        response = self.request('list_acl_rules', params=params)
        self._raise_if_unauthorized(response)

        return self._deserialize('acl.AclRuleList', response.body)

    def list_base_images(self, filters=None, page_size=None, page_number=None,
                         sort=None):
        """Returns a list of base images

        :param list filters: A list of 3-element lists specifying the filters
            to apply when retrieving the base images.

        :param int page_size: The maximum number of items per page

        :param int page_number: The page number to return

        :param list sort: A list of strings specifying the order of the list.

        :rtype: :class:`aeronaut.resource.cloud.image.ImageList`

        Here is an example usage with the above parameters included:

        .. code-block:: python

            filters = [
                ["location", "==", "NA5"],
                ["location", "==", "NA3"],
                ["name", "like", "Windows*"]
            ]

            page_size = 5
            page_number = 1

            sort = [
                "location ASC",
                "name DESC"
            ]

            images = conn.list_base_images(filters=filters,
                                           sort=sort,
                                           page_size=page_size,
                                           page_number=page_number)

            print images.page_number, "of", images.total_pages
            print images.page_size
            print images.total_count
            print len(images)
            for image in images:
                print image.id, image.name
        """
        return self.list_images('base',
                                filters=filters,
                                page_size=page_size,
                                page_number=page_number,
                                sort=sort)

    def list_customer_images(self, org_id=None, filters=None, page_size=None,
                             page_number=None, sort=None):
        """Returns a list of customer images

        :rtype: :class:`aeronaut.resource.cloud.image.ImageList`
        """
        return self.list_images(self._ensure_org_id(org_id),
                                filters=filters,
                                page_size=page_size,
                                page_number=page_number,
                                sort=sort)

    def list_data_centers(self, org_id=None, filters=None, page_size=None,
                          page_number=None, sort=None):
        """Returns a list of data centers

        :rtype: :class:`aeronaut.resource.cloud.data_center.DataCenterList`
        """
        params = {
            'org_id': self._ensure_org_id(org_id),
            'filters': filters,
            'page_size': page_size,
            'page_number': page_number,
            'sort': sort
        }
        response = self.request('list_data_centers', params=params)
        self._raise_if_unauthorized(response)
        return self._deserialize('data_center.DataCenterList', response.body)

    def list_images(self, base_or_org_id, **kwargs):
        """Returns a list of base or customer images. While this is available,
        you are better off calling either
        :meth:`~aeronaut.cloud.CloudConnection.list_customer_images` or
        :meth:`~aeronaut.cloud.CloudConnection.list_base_images`

        :rtype: :class:`aeronaut.resource.cloud.image.ImageList`
        """
        kwargs['base_or_org_id'] = base_or_org_id

        response = self.request('list_images', params=kwargs)
        self._raise_if_unauthorized(response)
        images = self._deserialize('image.ImageList', response.body)

        return images

    def list_networks(self, org_id=None, location=None):
        """Returns a list of networks

        :param str org_id: Optional. The organization ID that owns the
            networks. Defaults to the current user's
            :py:attr:`~aeronaut.resource.cloud.account.Account.org_id` if not
            provided.

        :param str location: Location where the image is expected to exist.
            This can be taken from the `location` property of the
            :class:`~aeronaut.resource.cloud.data_center.DataCenter` resource
            object.

        :rtype: :class:`aeronaut.resource.cloud.network.NetworkList`
        """
        org_id = self._ensure_org_id(org_id)

        params = {'org_id': org_id}

        if isinstance(location, str):
            params['location'] = location

        response = self.request('list_networks', params=params)
        self._raise_if_unauthorized(response)

        return self._deserialize('network.NetworkList', response.body)

    def list_servers(self, org_id=None, filters=None, page_size=None,
                     page_number=None, sort=None):
        """Returns a list of servers

        :param str org_id: Optional. The organization ID that owns the
            server. Defaults to the current user's
            :py:attr:`~aeronaut.resource.cloud.account.Account.org_id` if not
            provided.

        :rtype: :class:`aeronaut.resource.cloud.server.ServerList`
        """
        params = {
            'org_id': self._ensure_org_id(org_id),
            'filters': filters,
            'page_size': page_size,
            'page_number': page_number,
            'sort': sort
        }

        response = self.request('list_servers', params=params)
        self._raise_if_unauthorized(response)
        return self._deserialize('server.ServerList', response.body)

    def modify_server(self, server_id, name=None, description=None,
                      cpu_count=None, memory=None, org_id=None):
        """Changes the name, description, CPU, or RAM profile of an existing
        deployed server.

        :param str org_id: Optional. The organization ID that owns the
            server. Defaults to the current user's
            :py:attr:`~aeronaut.resource.cloud.account.Account.org_id` if not
            provided.

        :param str name: Optional. New name of the server.

        :param str description: Optional. New description of the server.

        :param int cpu_count: Optional. New number of virtual CPUs.

        :param int memory: Optional. New total memory in MB. Value must be a
                multiple of 1024.

        :param str server_id: The ID of the server to modify.

        :rtype: :class:`aeronaut.resource.cloud.server.ModifyServerStatus`
        """
        params = {
            'org_id': self._ensure_org_id(org_id),
            'server_id': server_id
        }

        for var in ['name', 'description', 'cpu_count', 'memory']:
            if eval(var):
                params[var] = eval(var)

        response = self.request('modify_server', params=params)
        self._raise_if_unauthorized(response)
        return self._deserialize('server.ModifyServerStatus', response.body)

    def poweroff_server(self, server_id, org_id=None):
        """Forcefully power off the server

        :param str server_id: The ID of the server you want to power off.

        :param str org_id: Optional. The organization ID that owns the
            server. Defaults to the current user's
            :py:attr:`~aeronaut.resource.cloud.account.Account.org_id` if not
            provided.

        :rtype: :class:`aeronaut.resource.cloud.server.PoweroffServerStatus`
        """
        params = {
            'org_id': self._ensure_org_id(org_id),
            'server_id': server_id
        }

        response = self.request('poweroff_server', params=params)
        self._raise_if_unauthorized(response)
        return self._deserialize('server.PoweroffServerStatus', response.body)

    def reboot_server(self, server_id, org_id=None):
        """Gracefully reboot a server

        :param str server_id: The ID of the server you want to power off.

        :param str org_id: Optional. The organization ID that owns the
            server. Defaults to the current user's
            :py:attr:`~aeronaut.resource.cloud.account.Account.org_id` if not
            provided.

        :rtype: :class:`aeronaut.resource.cloud.server.RebootServerStatus`
        """
        params = {
            'org_id': self._ensure_org_id(org_id),
            'server_id': server_id
        }

        response = self.request('reboot_server', params=params)
        self._raise_if_unauthorized(response)
        return self._deserialize('server.RebootServerStatus', response.body)

    def reset_server(self, server_id, org_id=None):
        """Forcefully power cycle the server.

        :param str server_id: The ID of the server you want to power off.

        :param str org_id: Optional. The organization ID that owns the
            server. Defaults to the current user's
            :py:attr:`~aeronaut.resource.cloud.account.Account.org_id` if not
            provided.

        :rtype: :class:`aeronaut.resource.cloud.server.ResetServerStatus`
        """
        params = {
            'org_id': self._ensure_org_id(org_id),
            'server_id': server_id
        }

        response = self.request('reset_server', params=params)
        self._raise_if_unauthorized(response)
        return self._deserialize('server.ResetServerStatus', response.body)

    def shutdown_server(self, server_id, org_id=None):
        """Gracefully stop a server

        :param str server_id: The ID of the server you want to power off.

        :param str org_id: Optional. The organization ID that owns the
            server. Defaults to the current user's
            :py:attr:`~aeronaut.resource.cloud.account.Account.org_id` if not
            provided.

        :rtype: :class:`aeronaut.resource.cloud.server.ShutdownServerStatus`
        """
        params = {
            'org_id': self._ensure_org_id(org_id),
            'server_id': server_id
        }

        response = self.request('shutdown_server', params=params)
        self._raise_if_unauthorized(response)
        return self._deserialize('server.ShutdownServerStatus', response.body)

    def start_server(self, server_id, org_id=None):
        """Powers on an existing server

        :param str server_id: The ID of the server you want to power off.

        :param str org_id: Optional. The organization ID that owns the
            server. Defaults to the current user's
            :py:attr:`~aeronaut.resource.cloud.account.Account.org_id` if not
            provided.

        :rtype: :class:`aeronaut.resource.cloud.server.StartServerStatus`
        """
        params = {
            'org_id': self._ensure_org_id(org_id),
            'server_id': server_id
        }

        response = self.request('start_server', params=params)
        self._raise_if_unauthorized(response)
        return self._deserialize('server.StartServerStatus', response.body)

    def request(self, req_name, api_version=None, params={}, auth=None):
        """Sends a request to the provider. This is a low-level method used by
        all other operations exposed by this class. You do not need to call
        it directly but it's here anyway in case you really want to use it.

        :param str req_name: The name of the request. For a list of available
            requests, see :mod:`aeronaut.request.cloud`

        :param str api_version: The API version to use.

        :param dict params: Parameters to be supplied to the request. This can
            vary between requests.

        :param tuple auth: A tuple of two strings, username and password, to
            use should the server require authentication.

        Example:

        .. code-block:: python

            params = {
                'cpu_count': 2,
                'memory': 2048
            }

            response = self.request('modify_server',
                                    api_version='v0.9',
                                    params=params)
            print response.status_code

        The above call results in the class
        :class:`aeronaut.request.cloud.v0_9.modify_server.ModifyServer`
        being used to send a request to the provider.

        * The version ``v0_9`` is inferred from the ``api_version`` argument
        * The class ``ModifyServer`` is inferred from the first argument,
          ``modify_server``
        * What values go into the params argument is determined by whatever
          the :meth:`~aeronaut.cloud.request.v0_9.modify_server.ModifyServer.params`
          method of the request class returns.

        Note that this method returns a raw response object, not an object
        representation of the XML returned by the server.
        """  # NOQA
        if api_version is None:
            api_version = self.api_version

        request = self._build_request(req_name, api_version, params)
        kwargs = {}

        if auth is not None:
            kwargs['auth'] = auth

        if request.http_method() in ['post', 'put'] \
                and request.body() is not None:
            kwargs['data'] = request.body()

        if request.headers():
            kwargs['headers'] = request.headers()

        http_method = getattr(self._http_session, request.http_method())
        return Response(http_method(request.build_url(), **kwargs), request)

    # ===============
    # PRIVATE METHODS
    # ===============

    def _build_request(self, req_name, api_version, params):
        classname = ''.join([s.capitalize() for s in req_name.split('_')])
        api_version = re.sub('\.', '_', api_version)
        modname = 'aeronaut.request.cloud.{api_version}.{req_name}' \
                  .format(api_version=api_version,
                          req_name=req_name)

        try:
            mod = __import__(modname, fromlist=[classname])
        except ImportError:
            raise ImportError("no module named {}.{}"
                              .format(modname, classname))

        klass = getattr(mod, classname)
        return klass(base_url=self.base_url, params=params)

    def _deserialize(self, classname, xml):
        modname, classname = classname.split('.')
        modname = 'aeronaut.resource.cloud.{}'.format(modname)

        try:
            mod = __import__(modname, fromlist=[classname])
        except ImportError:
            raise ImportError("Cannot import module named {}.{}"
                              .format(modname, classname))

        klass = getattr(mod, classname)
        return klass(xml=xml)

    def _ensure_org_id(self, org_id):
        if org_id:
            return org_id
        else:
            if not self.my_account:
                raise NotAuthenticatedError()

            return self.my_account.org_id

    def _raise_if_unauthorized(self, response):
        if response.status_code == 401:
            raise UnauthorizedError()
        elif response.status_code == 403:
            status = self._deserialize('resource.Status', response.body)
            raise OperationForbiddenError(status)


def connect(endpoint):
    """Creates a new connection to a DiData Cloud Server or DiData Cloud
    Network provider. Multiple calls to :py:func:`~aeronaut.cloud.connect` can
    be made to establish connections to multiple providers.

    :param str endpoint: The endpoint to connect to. For example:
        ``api-na.dimensiondata.com``

    :return: An authenticated connection to the cloud provider
    :rtype: :class:`~aeronaut.cloud.CloudConnection`

    Here is a simple usage example::

        from aeronaut.cloud import connect

        conn = connect('api-na.dimensiondata.com')
        servers = aeronaut.list_servers()

    To successfully authenticate against the given endpoint, the function will
    look for a file in the path ``~/.aeronaut`` with a section name matching
    the same endpoint. The file must be valid YAML with the following
    structure::

        api-na.dimensiondata.com:
            username: myuser
            password: mypassword

        another.endpoint.com:
            username: myotheruser
            password: mypasswordtoo!

    Note that this function is really just syntactic sugar that wraps in a
    single step the act of instantiating a
    :class:`~aeronaut.cloud.CloudConnection` object and calling
    :meth:`~aeronaut.cloud.CloudConnection.authenticate` against it. To learn
    more about the authentication process,
    see :meth:`aeronaut.cloud.CloudConnection.authenticate`.

    Here is a more detailed usage example::

        from aeronaut.cloud import connect

        cloud = connect('api-na.dimensiondata.com')

        images = cloud.list_base_images()
        image = images[0]

        networks = cloud.list_networks()
        network = networks[0]

        status = conn.deploy_server(name='My New Server',
                                    description='First server deployment',
                                    image_id=image.id,
                                    start=True,
                                    admin_password='32456sdkddd',
                                    network_id=network.id)

        print status.is_success

    All requests such as :meth:`~aeronaut.cloud.CloudConnection.deploy_server`
    and :meth:`~aeronaut.cloud.CloudConnection.list_base_images` are delegated
    to request classes under the :mod:`aeronaut.request.cloud` package. Whereas
    the return values are instances of classes under the
    :mod:`aeronaut.resource.cloud` package. Documentation is currently sparse
    in both packages so you are required to read the source code to fully
    understand what the request and resource objects do.
    """
    conn = CloudConnection(endpoint=endpoint)
    conn.authenticate()
    return conn
