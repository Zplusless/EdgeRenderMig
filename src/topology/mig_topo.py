#!/usr/bin/python
# -*- coding: UTF-8 -*-

from mininet.topo import Topo
from mininet.util import irange
from mininet.log import error
from mininet.node import Node
from mininet.link import TCIntf
import config
# from base_ip import *

from NF.net_functions import RAN, IUPF, AUPF, UE, DN_CONTROLLER
# import utils


# IUPF采用旁路由模式
class SrvMigTopo(Topo):
    def build(self, ran_num = 2):
        if ran_num>15 or ran_num<1:
            error('invalid ran_num, should be 1~15')
        

        s0 = self.addSwitch('s0')  # 外挂控制网络
        s10 = self.addSwitch('s10') # 外挂dn1
        s20 = self.addSwitch('s20') # 外挂dn2

        s1 = self.addSwitch('s1') # upf-1  ---> ran1
        s2 = self.addSwitch('s2') # upf-2  ---> ran2

        s1001 = self.addSwitch('s1001') # ran1 ---> ue
        s1002 = self.addSwitch('s1002') # ran2 ---> ue



        iupf1 = self.addNode('iupf1', cls=IUPF ,ip = "172.12.1.253/16")
        self.addLink(iupf1, s1, intf=TCIntf, 
                        addr1=f'00:00:00:00:01:fe',
                        params1={'ip':'172.12.1.253/16',
                               'bw':config.BW_NF, 
                                'delay':config.DELAY_NF, 
                                'loss':config.LOSS_NF,
                                'use_htb':True}) 

        iupf2 = self.addNode('iupf2', cls=IUPF ,ip = "172.12.2.253/16")
        self.addLink(iupf2, s2, intf=TCIntf, 
                        addr1=f'00:00:00:00:02:fe',
                        params1={'ip':'172.12.2.253/16',
                               'bw':config.BW_NF, 
                                'delay':config.DELAY_NF, 
                                'loss':config.LOSS_NF,
                                'use_htb':True}) 



        aupf1 = self.addNode('aupf1', cls=AUPF, ip = "172.12.1.254/16")
        self.addLink(aupf1, s1, intf=TCIntf, 
                                intfName1='aupf1-eth0', 
                                addr1=f'00:00:00:00:01:ff',
                                params1={'ip': "172.12.1.254/16", 
                                'bw':config.BW_NF, 
                                'delay':config.DELAY_NF, 
                                'loss':config.LOSS_NF,
                                'use_htb':True})

        self.addLink(aupf1, s10, intf=TCIntf,
                                intfName1='aupf1-eth1', 
                                params1={'ip': "192.168.1.254/24",
                                        'bw':config.BW_NF, 
                                        'delay':config.DELAY_NF, 
                                        'loss':config.LOSS_NF,
                                        'use_htb':True})

        aupf2 = self.addNode('aupf2', cls=AUPF, ip = "172.12.2.254/16")
        self.addLink(aupf2, s2, intf=TCIntf, 
                                intfName1='aupf2-eth0', 
                                addr1=f'00:00:00:00:02:ff',
                                params1={'ip': "172.12.2.254/16", 
                                'bw':config.BW_NF, 
                                'delay':config.DELAY_NF, 
                                'loss':config.LOSS_NF,
                                'use_htb':True})

        self.addLink(aupf2, s20, intf=TCIntf,
                                intfName1='aupf2-eth1', 
                                params1={'ip': "192.168.1.254/24",
                                        'bw':config.BW_NF, 
                                        'delay':config.DELAY_NF, 
                                        'loss':config.LOSS_NF,
                                        'use_htb':True})



        
        ran1 = self.addNode('ran1', cls=RAN,  ip='100.1.1.254/24') # 100.1.1.254
        ran2_1 = self.addNode('ran2_1', cls=RAN,  ip='100.2.1.254/24') # 100.2.1.254
        ran2_2 = self.addNode('ran2_2', cls=RAN,  ip='100.2.1.253/24') # 100.2.1.254

        ue = self.addNode('ue', cls=UE, ip='100.1.1.1/24')


        # ran与ue的连接
        self.addLink(ran1, s1001, intf=TCIntf, 
                                    intfName1='ran1-eth0', 
                                    params1={'ip': '100.1.1.254/24',
                                            'bw':config.BW_UE_RAN, 
                                            'delay':config.DELAY_UE_RAN1, 
                                            'loss':config.LOSS_UE_RAN,
                                            'use_htb':True})  # loss算单条连接

        self.addLink(ran2_1, s1002, intf=TCIntf, 
                                    intfName1='ran2_1-eth0', 
                                    params1={'ip': '100.2.1.254/24',
                                            'bw':config.BW_UE_RAN, 
                                            'delay':config.DELAY_UE_RAN2, 
                                            'loss':config.LOSS_UE_RAN,
                                            'use_htb':True})  # loss算单条连接

        
        self.addLink(ran2_2, s1002, intf=TCIntf, 
                                    intfName1='ran2_2-eth0', 
                                    params1={'ip': '100.2.1.253/24',
                                            'bw':config.BW_UE_RAN, 
                                            'delay':config.DELAY_UE_RAN2, 
                                            'loss':config.LOSS_UE_RAN,
                                            'use_htb':True})  # loss算单条连接



        # ran 与 网元间链路
        self.addLink(ran1, s1, intf=TCIntf, 
                                    intfName1='ran1-eth1', 
                                    addr1=f'00:00:00:00:01:01',
                                    params1={'ip': '172.12.1.1/16',
                                            'bw':config.BW_NF, 
                                            'delay':config.DELAY_NF, 
                                            'loss':config.LOSS_NF,
                                            'use_htb':True})  # loss算单条连接

        
        self.addLink(ran2_1, s2, intf=TCIntf, 
                                    intfName1='ran2-eth1', 
                                    addr1=f'00:00:00:00:02:01',
                                    params1={'ip': '172.12.2.1/16',
                                            'bw':config.BW_NF, 
                                            'delay':config.DELAY_NF, 
                                            'loss':config.LOSS_NF,
                                            'use_htb':True})  # loss算单条连接

        self.addLink(ran2_2, s2, intf=TCIntf, 
                                    intfName1='ran2-eth1', 
                                    addr1=f'00:00:00:00:02:02',
                                    params1={'ip': '172.12.2.2/16',
                                            'bw':config.BW_NF, 
                                            'delay':config.DELAY_NF, 
                                            'loss':config.LOSS_NF,
                                            'use_htb':True})  # loss算单条连接

        

        # ue连接
        self.addLink(ue, s1001, intf=TCIntf, 
                                intfName1='ue-eth0', 
                                params1={'ip': "100.1.1.1/24", 
                                'bw':config.BW_UE_RAN, 
                                'delay':config.DELAY_UE_RAN1, 
                                'loss':config.LOSS_UE_RAN,
                                'use_htb':True})

        self.addLink(ue, s1002, intf=TCIntf,
                                intfName1='ue-eth1', 
                                params1={'ip': "100.2.1.1/24",
                                        'bw':config.BW_UE_RAN, 
                                        'delay':config.DELAY_UE_RAN2, 
                                        'loss':config.LOSS_UE_RAN,
                                        'use_htb':True})


        #* 网元控制链路外挂
        # 10 Mbps, 5ms delay, 2% loss, 1000 packet queue
	    # self.addLink( host, switch, bw=10, delay='5ms', loss=2, max_queue_size=1000, use_htb=True )
        self.addLink(s1, s0,intf=TCIntf,
                            params1={
                                'bw':config.BW_INTER_CLUSTER, 
                                'delay':config.DELAY_INTER_CLUSTER, 
                                'loss':config.LOSS_INTER_CLUSTER,
                                'use_htb':True})

        self.addLink(s2, s0,intf=TCIntf,
                            params1={
                                'bw':config.BW_INTER_CLUSTER, 
                                'delay':config.DELAY_INTER_CLUSTER, 
                                'loss':config.LOSS_INTER_CLUSTER,
                                'use_htb':True})




