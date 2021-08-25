#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
定义网元类，用于mininet中网元的启动，规定了启动时的初始化操作
"""

# toto: custom hosts in mininet
# cluster.py consoles.py controllers.py !!nodelib.py

from mininet.node import Node
import config
import time




class NF( Node ):
    "A Node with IP forwarding enabled."
    def config( self, **params ):
        super(NF, self).config( **params )
        # Enable forwarding on the router
        self.cmd( 'sysctl net.ipv4.ip_forward=1' )


    def terminate( self ):
        self.cmd( 'sysctl net.ipv4.ip_forward=0' )
        # self.cmdPrint( 'sudo gtp5g-link del gtp5gtest')
        super( NF, self ).terminate()


class RAN(NF):

    def config( self, **params ):
        super(RAN, self).config( **params )
        # Enable forwarding on the router
        # self.cmd( 'sysctl net.ipv4.ip_forward=1' )
        self.cmdPrint( 'sudo gtp5g-link add gtp5gtest --ran &')
        self.cmd( 'sleep 0.2')
        self.cmdPrint( 'sudo ip r add {} dev gtp5gtest'.format(config.DN_CIDR))

        # 启动flask监听
        if config.IN_DEPLOYMENT:
            self.cmdPrint(f'gunicorn -b 0.0.0.0:5000 start_nf:nf_app > node_log/{self.name}.log 2>&1 &')
        else:
            self.cmdPrint(f'python start_nf.py > node_log/{self.name}.log 2>&1 &')
        # self.cmdPrint('python nf_app.py -n {} {} > nf_logs/{}/{}.log'.format(self.name, 
        #                                                                         debug_flag, 
        #                                                                         time.time()[0:9],
        #                                                                         self.name))

        
    def terminate( self ):
        # self.cmd( 'sysctl net.ipv4.ip_forward=0' )
        self.cmdPrint( 'sudo gtp5g-link del gtp5gtest --ran')
        super(RAN, self ).terminate()



class IUPF(NF):

    def config( self, **params ):
        super(IUPF, self).config( **params )
        # Enable forwarding on the router
        # self.cmd( 'sysctl net.ipv4.ip_forward=1' )
        self.cmdPrint( 'sudo gtp5g-link add gtp5gtest &')
        # self.cmd( 'sleep 0.1')
        # self.cmdPrint( 'sudo ip r add {} dev gtp5gtest'.format(config.DN_CIDR))

        # 启动flask监听
        if config.IN_DEPLOYMENT:
            self.cmdPrint(f'gunicorn -b 0.0.0.0:5000 start_nf:nf_app > node_log/{self.name}.log 2>&1 &')
        else:
            self.cmdPrint(f'python start_nf.py > node_log/{self.name}.log 2>&1 &')
        # self.cmdPrint('python nf_app.py -n {} {} > nf_logs/{}/{}.log'.format(self.name, 
        #                                                                         debug_flag, 
        #                                                                         time.time()[0:9],
        #                                                                         self.name))
    
    def terminate( self ):
        # self.cmd( 'sysctl net.ipv4.ip_forward=0' )
        self.cmdPrint( 'sudo gtp5g-link del gtp5gtest')
        super( IUPF, self ).terminate()



class AUPF(NF):

    def config( self, **params ):
        super(AUPF, self).config( **params )
        # Enable forwarding on the router
        # self.cmd( 'sysctl net.ipv4.ip_forward=1' )
        self.cmdPrint( 'sudo gtp5g-link add gtp5gtest &')
        self.cmd( 'sleep 0.1')
        self.cmdPrint( 'sudo ip r add {} dev gtp5gtest src {}'.format(config.UE_CIDR, config.DN_CONTROLLER_IP.split('/')[0]))

        # 启动flask监听
        if config.IN_DEPLOYMENT:
            self.cmdPrint(f'gunicorn -b 0.0.0.0:5000 start_nf:nf_app > node_log/{self.name}-NF.log 2>&1 &')
        else:
            self.cmdPrint(f'python start_nf.py > node_log/{self.name}-NF.log 2>&1 &')
        
        
        # 启动dnc控制, 在AUPF启动，避免dnc不在控制的网段内
        # if config.IN_DEPLOYMENT:
        #     self.cmdPrint(f'gunicorn -b 0.0.0.0:8000 start_dnc:dn_app > node_log/{self.name}-dnc.log 2>&1 &')
        # else:
        #     self.cmdPrint(f'python start_dnc.py > node_log/{self.name}-dnc.log 2>&1 &')

        
    def terminate( self ):
        # self.cmd( 'sysctl net.ipv4.ip_forward=0' )
        self.cmdPrint( 'sudo gtp5g-link del gtp5gtest')
        super( AUPF, self ).terminate()


class UE(Node):
    # When ue start up, ue_app will run automatically.
    def config( self, **params ):
        super(UE, self).config( **params )
        if config.IN_DEPLOYMENT:
            self.cmdPrint(f'gunicorn -b 0.0.0.0:6600 start_ue:ue_app > node_log/{self.name}.log 2>&1 &')
        else:
            self.cmdPrint(f'python start_ue.py > node_log/{self.name}.log 2>&1 &')


    # def terminate(self):
    #     self.t.
    #     super(UE, self).terminate()


class DN_CONTROLLER(Node):
    # When ue start up, ue_app will run automatically.
    def config( self, **params ):
        super(DN_CONTROLLER, self).config( **params )
        self.cmdPrint('python start_dnc.py &')



class HTTP_SERVER(Node):
    # When dn start up, ue_app will run automatically.
    def config( self, **params ):
        super(HTTP_SERVER, self).config( **params )
        self.cmdPrint('python -m SimpleHTTPServer 80 &')

if __name__ == "__main__":
    pass