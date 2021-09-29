#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
定义网元的操作，用于在网元启动后，用于调用，进行建立隧道等操作
"""

# toto: custom hosts in mininet
# cluster.py consoles.py controllers.py !!nodelib.py

# from mininet.node import Node
import config
import subprocess
import requests as r 
import logging
# import utils

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)


class NF( object ):

    def get_IDs(self, ue_id):
        cluster = ue_id//1000000
        ran = ue_id//1000%1000
        ue_ip = ue_id%1000

        return cluster, ran, ue_ip

    def getNodeIP(self, ue, dn_cluster_ID, sub_ran = 0):
        ue = int(ue.replace('ue',''))
        ue_cluster, ran_id, ue_id = self.get_IDs(ue)

        ue_ip = config.BASE_UE_IP.format(ue_cluster, ran_id, ue_id).split('/')[0]
        if not dn_cluster_ID:
            return ue_ip
        else:
            ran_ip = config.BASE_RAN_IUPF_IP.format(ue_cluster,ran_id+sub_ran).split('/')[0]
            iupf_ip = config.BASE_IUPF_WAN_IP.format(ue_cluster).split('/')[0]
            aupf_ip = config.BASE_AUPF_WAN_IP.format(dn_cluster_ID).split('/')[0]
            return {'ue':ue_ip,'ran':ran_ip, 'iupf':iupf_ip, 'aupf':aupf_ip}   
    
    def getUEip(self, ue):
        return self.getNodeIP(ue, None)

    def getTEID(self, tunnel_id):
        TEID = {}
        base_teid = tunnel_id*10
        for nf in ['ran', 'iupf', 'aupf']:
            TEID[nf] = {}
        TEID['ran']['iupf'] = base_teid+1
        TEID['iupf']['aupf'] = base_teid+2
        TEID['aupf']['iupf'] = base_teid+3
        TEID['iupf']['ran'] = base_teid+4
        return TEID
    
    def cmdPrint(self, cmd):
        res = subprocess.call(cmd, shell=True)
        if res !=0:
            print("COMMAND FAILED--->\'{}\'".format(cmd))

class RAN(NF):

    def __init__(self, name):
        self.name = name

    def addTunnel(self, ue, dn_cluster_id, tunnel_id, sub_ran):

        node_ip = self.getNodeIP(ue, dn_cluster_id, sub_ran)

        up_tunnel_id = tunnel_id*10
        down_tunnel_id = up_tunnel_id + 1
        
        teid = self.getTEID(tunnel_id)

        # 添加下行流量
        self.cmdPrint('sudo gtp5g-tunnel add far gtp5gtest {} --action 2'.format(down_tunnel_id))
        self.cmdPrint('sudo gtp5g-tunnel add pdr gtp5gtest {} --pcd 1 --hdr-rm 0 --ue-ipv4 {} --f-teid {} {} --far-id {}'.format(down_tunnel_id,
                                                                                                                                node_ip['ue'], 
                                                                                                                                teid['iupf']['ran'], 
                                                                                                                                node_ip['ran'], 
                                                                                                                                down_tunnel_id))
        log.debug(f'downstream tunnel for ue-{ue} set up')


        # 添加上行流量
        self.cmdPrint('sudo gtp5g-tunnel add far gtp5gtest {} --action 2 --hdr-creation 0 {} {} 2152'.format(up_tunnel_id, 
                                                                                                            teid['ran']['iupf'],
                                                                                                            node_ip['iupf']))
        self.cmdPrint('sudo gtp5g-tunnel add pdr gtp5gtest {} --pcd 2 --ue-ipv4 {} --far-id {} --gtpu-src-ip={}'.format(up_tunnel_id,
                                                                                                                        node_ip['ue'], 
                                                                                                                        up_tunnel_id,
                                                                                                                        node_ip['ran']))
        log.debug(f'upstream tunnel for ue-{ue} set up')


    def delTunnel(self, tunnel_id):
        up_tunnel_id = tunnel_id*10
        down_tunnel_id = up_tunnel_id + 1

        # 删除下行流量
        self.cmdPrint('sudo gtp5g-tunnel del far gtp5gtest {}'.format(down_tunnel_id))
        self.cmdPrint('sudo gtp5g-tunnel del pdr gtp5gtest {}'.format(down_tunnel_id))
        log.debug(f'downstream tunnel for tunnel-{tunnel_id} deleted')

        # 删除上行流量
        self.cmdPrint('sudo gtp5g-tunnel del far gtp5gtest {}'.format(up_tunnel_id))
        self.cmdPrint('sudo gtp5g-tunnel del pdr gtp5gtest {}'.format(up_tunnel_id))
        log.debug(f'upstream tunnel for tunnel-{tunnel_id} deleted')

    def addUE(self, ue, log_name, srv, t=None):
        ue_ip = self.getUEip(ue)
        print('\n\n{}\n\n'.format(ue_ip))
        if t:
            ans = r.get('http://{}:6600/run_srv/{}/{}/{}'.format(ue_ip, log_name, srv, t), timeout=3)
        else:
            ans = r.get('http://{}:6600/run_srv/{}/{}'.format(ue_ip, log_name, srv), timeout=3)
        return ans.status_code

    def delUE(self, ue):
        ue_ip = self.getUEip(ue)
        print('\n\n{}\n\n'.format(ue_ip))
        ans = r.get('http://{}:6600/stop_srv/'.format(ue_ip), timeout=3)
        return ans


class IUPF(NF):

    def __init__(self, name):
        self.name = name

    def addTunnel(self, ue, dn_cluster_id, tunnel_id, sub_ran):
        
        node_ip=self.getNodeIP(ue, dn_cluster_id, sub_ran)

        up_tunnel_id = tunnel_id*10
        down_tunnel_id = up_tunnel_id + 1
        
        teid = self.getTEID(tunnel_id)

        # 添加下行流量
        self.cmdPrint('sudo gtp5g-tunnel add far gtp5gtest {} --action 2 --hdr-creation 0 {} {} 2152'.format(down_tunnel_id, 
                                                                                                            teid['iupf']['ran'], 
                                                                                                            node_ip['ran']))
        self.cmdPrint('sudo gtp5g-tunnel add pdr gtp5gtest {} --pcd 2 --hdr-rm 0 --f-teid {} {} --far-id {} --gtpu-src-ip={}'.format(down_tunnel_id, 
                                                                                                                                    teid['aupf']['iupf'],
                                                                                                                                    node_ip['iupf'], 
                                                                                                                                    down_tunnel_id,
                                                                                                                                    node_ip['iupf']))
        
        # 添加上行流量
        self.cmdPrint('sudo gtp5g-tunnel add far gtp5gtest {} --action 2 --hdr-creation 0 {} {} 2152'.format(up_tunnel_id, 
                                                                                                            teid['iupf']['aupf'], 
                                                                                                            node_ip['aupf']))
        self.cmdPrint('sudo gtp5g-tunnel add pdr gtp5gtest {} --pcd 1 --hdr-rm 0 --ue-ipv4 {} --f-teid {} {} --far-id {} --gtpu-src-ip={}'.format(up_tunnel_id,
                                                                                                                                                node_ip['ue'],
                                                                                                                                                teid['ran']['iupf'], 
                                                                                                                                                node_ip['iupf'], 
                                                                                                                                                up_tunnel_id, 
                                                                                                                                                node_ip['iupf']))

    def delTunnel(self, tunnel_id):
        up_tunnel_id = tunnel_id*10
        down_tunnel_id = up_tunnel_id + 1

        # 删除下行流量
        self.cmdPrint('sudo gtp5g-tunnel del far gtp5gtest {}'.format(down_tunnel_id))
        self.cmdPrint('sudo gtp5g-tunnel del pdr gtp5gtest {}'.format(down_tunnel_id))
        
        # 删除上行流量
        self.cmdPrint('sudo gtp5g-tunnel del far gtp5gtest {}'.format(up_tunnel_id))
        self.cmdPrint('sudo gtp5g-tunnel del pdr gtp5gtest {}'.format(up_tunnel_id))


class AUPF(NF):

    def __init__(self, name):
        self.name = name

    def addTunnel(self, ue, dn_cluster_id, tunnel_id, sub_ran):

        node_ip=self.getNodeIP(ue,dn_cluster_id,sub_ran)

        up_tunnel_id = tunnel_id*10
        down_tunnel_id = up_tunnel_id + 1
        
        teid = self.getTEID(tunnel_id)

        # 添加上行流量
        self.cmdPrint('sudo gtp5g-tunnel add far gtp5gtest {} --action 2'.format(up_tunnel_id))
        self.cmdPrint('sudo gtp5g-tunnel add pdr gtp5gtest {} --pcd 1 --hdr-rm 0 --ue-ipv4 {} --f-teid {} {} --far-id {}'.format(up_tunnel_id,
                                                                                                                                node_ip['ue'], 
                                                                                                                                teid['iupf']['aupf'], 
                                                                                                                                node_ip['aupf'], 
                                                                                                                                up_tunnel_id))
        
        # 添加下行流量
        self.cmdPrint('sudo gtp5g-tunnel add far gtp5gtest {} --action 2 --hdr-creation 0 {} {} 2152'.format(down_tunnel_id, 
                                                                                                            teid['aupf']['iupf'],
                                                                                                            node_ip['iupf']))
        self.cmdPrint('sudo gtp5g-tunnel add pdr gtp5gtest {} --pcd 2 --ue-ipv4 {} --far-id {} --gtpu-src-ip={}'.format(down_tunnel_id,
                                                                                                                        node_ip['ue'], 
                                                                                                                        down_tunnel_id, 
                                                                                                                        node_ip['aupf']))

    def delTunnel(self, tunnel_id):
        up_tunnel_id = tunnel_id*10
        down_tunnel_id = up_tunnel_id + 1

        # 删除下行流量
        self.cmdPrint('sudo gtp5g-tunnel del far gtp5gtest {}'.format(down_tunnel_id))
        self.cmdPrint('sudo gtp5g-tunnel del pdr gtp5gtest {}'.format(down_tunnel_id))
        
        # 删除上行流量
        self.cmdPrint('sudo gtp5g-tunnel del far gtp5gtest {}'.format(up_tunnel_id))
        self.cmdPrint('sudo gtp5g-tunnel del pdr gtp5gtest {}'.format(up_tunnel_id))


if __name__ == "__main__":
    nf = NF()
    ips = nf.getNodeIP('ue1001001', 1)
    ips = nf.getNodeIP('ue1001002')
    print()