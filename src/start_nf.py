#!/usr/bin/python
# -*- coding: UTF-8 -*-

from flask import Flask
import subprocess
import logging

import argparse
from NF.nf_cls import RAN, AUPF, IUPF
import config

nf_app = Flask(__name__)

# parser = argparse.ArgumentParser()
# parser.add_argument('-n', '--name', 
#                     help='the name of current node')
# args = parser.parse_args()

# # 构架命令行，使得node启动时自动启动app.py对外监听
# nf = args.name


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)



def get_node_name():
    res = subprocess.getoutput('ifconfig|grep eth0')
    ans = res.split('-')
    return ans[0]



nf = get_node_name()
op = None
if 'ran' in nf:
    op = RAN(nf)
    print(f'\n*** using RAN operator @ {nf}\n')
elif 'iupf' in nf:
    op = IUPF(nf)
    print(f'\n*** using IUPF operator @ {nf}\n')
elif 'aupf' in nf:
    op = AUPF(nf)
    print(f'\n*** using AUPF operator @ {nf}\n')
else:
    raise Exception('{} is not a valid nf operator type'.format(nf))


# 对外的http接口
@nf_app.route('/add_tunnel/<ue>/<int:dn_cluster_id>/<int:tunnel_id>/')
def add_tunnel(ue, dn_cluster_id, tunnel_id):
    try:
        log.debug(f'start adding tunnel between ue-{ue} and dn_cluster-{dn_cluster_id}')
        op.addTunnel(ue, dn_cluster_id, tunnel_id)
    except Exception as e:
        log.debug(f'add tunnel for ue-{ue} to cluster-{dn_cluster_id} failed')
        return e, 500
    ans = "No.{}:\t{} add tunnel between {} and dn{}\n".format(tunnel_id,op.name, ue, dn_cluster_id)
    log.info(ans)
    return ans, 200

@nf_app.route('/del_tunnel/<int:tunnel_id>/')
def del_tunnel(tunnel_id):
    try:
        log.debug(f'start deleting tunnel-{tunnel_id}')
        op.delTunnel(tunnel_id)
    except Exception as e:
        log.debug(f'del tunnel-{tunnel_id} failed')
        return e, 500
    ans = "No.{}: tunnel has been deleted\n".format(tunnel_id)
    log.info(ans)
    return ans, 200

@nf_app.route('/add_ue/<ue>/<log_name>/')
def add_ue(ue, log_name):
    if isinstance(op, RAN):
        try:
            status_code = op.addUE(ue, log_name, srv=config.UE_SRV_ID)
        except Exception as e:
            log.debug(f'start ue-{ue} service request faled')
            return e, 500
        ans = "ue {} start requiring service ---> {}\n".format(ue, status_code)
        log.info(ans)
        return ans, 200
    else:
        ans = 'not calling a RAN\n'
        log.debug(ans)
        return ans, 500

@nf_app.route('/add_ue/<ue>/<log_name>/<int:t>/')
def add_ue_t(ue, log_name, t):
    if isinstance(op, RAN):
        try:
            status_code = op.addUE(ue, log_name, srv=config.UE_SRV_ID, t=t)
        except Exception as e:
            log.debug(f'start ue-{ue} service request faled')
            return e, 500
        ans = "ue {} start requiring service ---> {}\n".format(ue, status_code)
        log.info(ans)
        return ans, 200
    else:
        ans = 'not calling a RAN\n'
        log.debug(ans)
        return ans, 500

@nf_app.route('/del_ue/<ue>/')
def del_ue(ue):
    if isinstance(op, RAN):
        try:
            res = op.delUE(ue)
        except Exception as e:
            log.debug(f'stop ue-{ue} failed, got Exception')
            return e, 500
        if res.status_code == 200:  # 只有200才分正常运行和broken pipe
            info = f"ue {ue} stopped"
            log.info(info)
            return  res.text, 200 
        else:
            info = "\nfailed to stop ue {},  ---> {}\n".format(ue, res.text)
            log.debug(info)
            return info, res.status_code
    else:
        info = 'not calling a RAN\n'
        log.debug(info)
        return info, 500



if __name__=='__main__':
    print('*** starting NF operator')
    nf_app.run(host='0.0.0.0', port=5000)
