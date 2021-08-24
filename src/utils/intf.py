#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from mininet.link import Intf
from mininet.util import quietRun
from mininet.log import setLogLevel, info, error
import re



def checkIntf( intf ):
    "Make sure intf exists and is not configured."
    config = quietRun( 'ifconfig %s 2>/dev/null' % intf, shell=True )
    if not config:
        error( 'Error:', intf, 'does not exist!\n' )
        exit( 1 )
    ips = re.findall( r'\d+\.\d+\.\d+\.\d+', config )
    if ips:
        error( 'Error:', intf, 'has an IP address,'
               'and is probably in use!\n' )
        exit( 1 )

def link_Intf(h_intf, s_intf):
    '''
    h_intf--->hardware interface
    s_intf--->software interface
    dhcp---> make software interface get ip from outside dhcp server
    '''
    
    # try to get hw intf from the command line; by default, use eth1
    # intfName = sys.argv[ 1 ] if len( sys.argv ) > 1 else 'ens39'
    info( '*** Connecting to hw intf: %s\n' % h_intf )

    info( '*** Checking', h_intf, '\n' )
    checkIntf( h_intf )

    info( '*** Adding hardware interface', h_intf, 'to switch',
          s_intf.name, '\n' )
    _intf = Intf( h_intf, node=s_intf )

    # info( '*** Note: you may need to reconfigure the interfaces for '
    #       'the Mininet hosts:\n', s_intf, '\n' )

def dhclient_up(nodes):
    _nodes = []
    if not isinstance(nodes, list):
        _nodes.append(nodes)
    else:
        _nodes = nodes

    for host in _nodes:
        print('enable dhcp for {}'.format(host.defaultIntf().name))
        host.cmd('dhclient '+host.defaultIntf().name)

