#!/usr/bin/python
# -*- coding: UTF-8 -*-


import re
import sys

from mininet.cli import CLI
from mininet.log import setLogLevel, info, error
from mininet.net import Mininet
from mininet.node import OVSSwitch, Controller, RemoteController
from mininet.link import TCLink

import config

# from topology.my_topo import Edge5GTopo
from topology.mig_topo import SrvMigTopo
from utils.intf import *
# from NF.net_functions import NF


c0 = Controller( 'c0', port=6634 )
# c1 = RemoteController( 'c1', ip=config.HOST_IP, port=6633 )

# class MultiSwitch( OVSSwitch ):
#     "Custom Switch() subclass that connects to different controllers"
#     def map_controller(self, switch_name):
#         if switch_name == 's888':
#             return c1 if config.DN_LB else c0
#         else:
#             return c0
    
#     def start( self, controllers ):
#         return OVSSwitch.start( self, [self.map_controller(self.name)])



if __name__ == '__main__':
    setLogLevel( 'info' )

    
    # info( '*** Creating controler\n' )
    # c0 = RemoteController('c0', ip='127.0.0.1', port=6633 )

    info( '*** Creating network\n' )
    # net = Mininet( topo=MultiIntfHostTopo() , controller = c0)
    net = Mininet(  topo=SrvMigTopo(2) , 
                    # switch=c0, 
                    # link=TCLink, 
                    # autoStaticArp=True,
                    build=False)
    
    # for c in [c0, c1]:
    #     net.addController(c)
    
    net.addController(c0)
    
    net.build()

    s0 = net.nameToNode['s0']
    s10 = net.nameToNode['s10']
    s20 = net.nameToNode['s20']
    # link_Intf(config.CLUSTER_INTF, s0)  # 绑定外部网络  服务迁移实验中只用到一个cluster，故注释掉，否则需要额外绑定网卡
    link_Intf(config.DN_INTF_1, s10)
    link_Intf(config.DN_INTF_2, s20)

    net.start()
    
    CLI( net )
    net.stop()
