# -*- coding: utf-8 -*-

import os
from heatclient import client as heat_client
from keystoneclient.v2_0 import client as ksclient

import logging
global LOG
LOG = logging.getLogger('cloudutils')


def get_ksclient(**kwargs):
    """Get an endpoint and auth token from Keystone.

    :param username: name of user
    :param password: user's password
    :param tenant_id: unique identifier of tenant
    :param tenant_name: name of tenant
    :param auth_url: endpoint to authenticate against
    :param token: token to use instead of username/password
    """
    kc_args = {'auth_url': kwargs.get('auth_url'),
               'insecure': kwargs.get('insecure'),
               'cacert': kwargs.get('cacert')}

    if kwargs.get('tenant_id'):
        kc_args['tenant_id'] = kwargs.get('tenant_id')
    else:
        kc_args['tenant_name'] = kwargs.get('tenant_name')

    if kwargs.get('token'):
        kc_args['token'] = kwargs.get('token')
    else:
        kc_args['username'] = kwargs.get('username')
        kc_args['password'] = kwargs.get('password')

    return ksclient.Client(**kc_args)


# Magic function: gets keystone endpoints from environment without requiring admin privileges

def get_endpoint(client, **kwargs):
    """Get an endpoint using the provided keystone client."""
    if kwargs.get('region_name'):
        return client.service_catalog.url_for(
            service_type=kwargs.get('service_type') or 'orchestration',
            attr='region',
            filter_value=kwargs.get('region_name'),
            endpoint_type=kwargs.get('endpoint_type') or 'publicURL')
    return client.service_catalog.url_for(
        service_type=kwargs.get('service_type') or 'orchestration',
        endpoint_type=kwargs.get('endpoint_type') or 'publicURL')

# Get Keystone credentials from environment

keystone_kwargs = {
        'username': os.environ['OS_USERNAME'],
        'password': os.environ['OS_PASSWORD'],
        'tenant_name': os.environ['OS_TENANT_NAME'],
        'auth_url': os.environ['OS_AUTH_URL']
}

# Authenticate with keystone

# Heat

#ksclient = get_ksclient(**keystone_kwargs)
#endpoint = get_endpoint(ksclient, **keystone_kwargs)

#client = heat_client.Client('1', endpoint, token=ksclient.auth_ref['token']['id'], **keystone_kwargs)

#fields = {'stack_id': argv[1]}
#stack = client.stacks.get(**fields)

#print "%s - %s" % (stack.stack_status, stack.stack_status_reason)

