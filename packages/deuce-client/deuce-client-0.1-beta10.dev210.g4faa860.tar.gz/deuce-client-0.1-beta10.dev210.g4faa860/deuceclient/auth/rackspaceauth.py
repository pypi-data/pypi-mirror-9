"""
Deuce Rackspace Authentication API
"""
import logging

import deuceclient.auth
import deuceclient.auth.openstackauth


def get_identity_apihost(datacenter):
    if datacenter in ('us', 'uk', 'lon', 'iad', 'dfw', 'ord'):
        return 'https://identity.api.rackspacecloud.com/v2.0'
    elif datacenter in ('hkg', 'syd'):
        return'https://{0:}.identity.api.rackspacecloud.com/v2.0'.\
            format(datacenter)
    else:
        raise deuceclient.auth.AuthenticationError(
            'Unknown Data Center: {0:}'.format(datacenter))


class RackspaceAuthentication(
        deuceclient.auth.openstackauth.OpenStackAuthentication):
    """Rackspace Identity Authentication Support

    Only difference between this and OpenStackAuthentication is that this
    can know the servers without one being specified.
    """

    def __init__(self, userid=None, usertype=None,
                 credentials=None, auth_method=None,
                 datacenter=None, auth_url=None):

        # If an authentication url is not provided then create one using
        # Rackspace's Identity Service for the specified datacenter
        if auth_url is None:
            if datacenter is None:
                raise deuceclient.auth.AuthenticationError(
                    'Required Parameter, datacenter, not specified.')

            auth_url = get_identity_apihost(datacenter)
            log = logging.getLogger(__name__)
            log.debug('No AuthURL specified. Using {0:}'.format(auth_url))

        super(RackspaceAuthentication, self).__init__(userid=userid,
                                                      usertype=usertype,
                                                      credentials=credentials,
                                                      auth_method=auth_method,
                                                      datacenter=datacenter,
                                                      auth_url=auth_url)

    @staticmethod
    def _management_url(*args, **kwargs):
        # NOTE(TheSriram): kwarg region_name is the datacenter supplied
        # when instantiating RackspaceAuthentication class
        return get_identity_apihost(kwargs['region_name'])

    @staticmethod
    def patch_management_url():
        from keystoneclient.service_catalog import ServiceCatalog
        ServiceCatalog.url_for = RackspaceAuthentication._management_url

    def get_client(self):
        """Retrieve the Rackspace Client
        """
        # NOTE(TheSriram): The exceptions thrown if any, would still
        # bear OpenstackAuthentication class in the message.
        RackspaceAuthentication.patch_management_url()
        return super(RackspaceAuthentication, self).get_client()
