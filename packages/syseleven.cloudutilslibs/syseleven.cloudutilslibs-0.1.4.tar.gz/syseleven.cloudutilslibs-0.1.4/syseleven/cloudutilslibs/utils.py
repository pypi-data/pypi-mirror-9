#!/usr/bin/env python


from neutronclient.common.exceptions import NotFound as neutronclientNotFound
from novaclient.exceptions import NotFound as novaclientNotFound
from heatclient.exc import HTTPNotFound as heatclientHTTPNotFound

from copy import deepcopy
import sys


import logging
global LOG
LOG = logging.getLogger('cloudutils')

def get_floating_ip_from_heat_nova_neutron(stack, heatclient, neutronclient, novaclient):
    """ gets floating IPs from a heat stack and returns (name, floatingip) as tuple """
    ret = []
    fields = {'stack_id': stack.stack_name}
    stack_resources = heatclient.resources.list(**fields)

    for stack_resource in stack_resources:
        port_id = False
        floatingip_address = False

        # get floatingip_address and port_id
        if stack_resource.resource_type == 'OS::Neutron::FloatingIP':
            try:
                floatingip = neutronclient.show_floatingip(stack_resource.physical_resource_id)['floatingip']
            except neutronclientNotFound:
                continue
            floatingip_address = floatingip['floating_ip_address']
            port_id = floatingip['port_id']

        elif stack_resource.resource_type.startswith('sys11::floatport'):
            try:
              heat_ret = heatclient.stacks.get(stack_id=stack_resource.physical_resource_id).to_dict().get('outputs', [])
            except heatclientHTTPNotFound:
                continue
            for output in heat_ret:
                if output['output_key'] == 'floating_ip_address':
                    floatingip_address = output['output_value']
                elif output['output_key'] == 'port':
                    port_id = output['output_value']

        if port_id and floatingip_address:
            port = neutronclient.show_port(port_id)['port']
            device_id = port['device_id']
            try:
                server = novaclient.servers.get(device_id)
            except novaclientNotFound:
                continue
            ret.append((server, floatingip_address))

    return ret


def dict_merge(a, b):
    '''recursively merges dict's. not just simple a['key'] = b['key'], if
    both a and bhave a key who's value is a dict then dict_merge is called
    on both values and the result stored in the returned dictionary.'''

    if not isinstance(b, dict):
        return b
    result = deepcopy(a)
    for k, v in b.iteritems():
        if k in result and isinstance(result[k], dict):
                result[k] = dict_merge(result[k], v)
        else:
            result[k] = deepcopy(v)
    return result

def drilldownchoices(input, formatter=lambda x: str(x), always_keep_first=False, **keywords):
    """ take list of hashs
        ask user interactively which hash it wants
        returns selected hash
    """
    LOG.debug('drilldownchoices() %s', repr(input))

    if 'last' in keywords:
        last = keywords['last']
        LOG.info('Only showing last %d entries.', last)
    else:
        last = None

    counter = 0
    results = list()

    if len(input) == 1:
        return input[0]

    # TODO -1 for exit

    print '-1) exit'

    for x in input:
        if last:
            if (len(input) - counter) < last:
                print (' %d) %s' % (counter, formatter(x)))
        else:
            print (' %d) %s' % (counter, formatter(x)))

        counter += 1

    user_input = get_input(' >')

    if user_input == '-1':
        sys.exit(-1)
    elif user_input.isdigit() and int(user_input) < counter:
        results += [(input[int(user_input)])]
    else:
        for x in input:
            if user_input.lower() in formatter(x).lower():
                results += [x]
    if always_keep_first:
        results = [input[0]] + results

    LOG.debug(repr(results))
    LOG.debug(repr(len(results)))

    if len(results) > 1:
        return drilldownchoices(results, formatter=formatter, always_keep_first=always_keep_first)
    elif len(results) == 0:
        return drilldownchoices(input, formatter=formatter, always_keep_first=always_keep_first)

    # TODO if zero then do something
    LOG.debug(results)
    #LOG.info('Choice %s', repr(results[0]))
    return results[0]

def safe_unicode(value, encoding='utf-8'):
    """Converts a value to unicode, even it is already a unicode string.
       >>> from sys11.helpers import safe_unicode
       >>> safe_unicode('spam')
       u'spam'
       >>> safe_unicode(u'spam')
       u'spam'
       >>> safe_unicode(u'spam'.encode('utf-8'))
       u'spam'
       >>> safe_unicode('\xc6\xb5')
       u'\u01b5'
       >>> safe_unicode(u'\xc6\xb5'.encode('iso-8859-1'))
       u'\u01b5'
       >>> safe_unicode('\xc6\xb5', encoding='ascii')
       u'\u01b5'
       >>> safe_unicode(1)
       1
       >>> print safe_unicode(None)
       None
    """
    if isinstance(value, unicode):
        return value
    elif isinstance(value, basestring):
        try:
            value = unicode(value, encoding)
        except (UnicodeDecodeError):
            value = value.decode('utf-8', 'replace')
    return value


def convert_to_str(value):
    """ Converts value to string.
    Using safe_unicode, if value is basestring"""
    if isinstance(value, basestring):
        return safe_unicode(value)
    else:
        return str(value)




def get_input(value=u''):
    """ Returns raw_input as type unicode """
    input_ = raw_input('%s ' % value)
    if input_:
        return safe_unicode(input_)
    else:
        LOG.debug('No input given')
        return ''
