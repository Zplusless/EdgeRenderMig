# 在UE直连的bs上运行


import requests
import time

from utils.call_cmd import cmd
from corenet_controller import Scheduller
import config

s = Scheduller()

# Edge启动snake游戏 && GA
def start_edge(edge_id):
    addr = f'http://192.168.1.{edge_id}:8000/run_game/'
    data = {
        'name': 'srv_mig',
        'ip': config.CLOUD_IP,
        'port': 5500
    }

    requests.post(addr, data = data)


# UE 初始化
def init_bs(bs_id):
    if bs_id not in ['1','2-1','2-2']:
        raise Exception('Wrong bs id')
    addr = f'http://100.1.1.1:6600/init_bs/{bs_id}/'
    t = requests.get(addr)

    return int(t)


# UE 切换
def switch_bs(bs_id):
    if bs_id not in ['1','2']:
        raise Exception('Wrong bs id')
    addr = f'http://100.1.1.1:6600/switch_bs/{bs_id}/'
    t = requests.get(addr)

    return int(t)

# UE 启动GA
def ue_run_GA(dn_id):
    if dn_id not in [1,2]:
        raise Exception('Wrong bs id')
    addr = f'http://100.1.1.1:6600/run_client/{dn_id}/'
    t = requests.get(addr)

    return int(t)



if __name__ == "__main__":

#*==========阶段1================
    # 建立到dn1的隧道
    # tunnel_1 = s.add_tunnel(1001001, 1, 0)

    # dn1启动game和GA
    start_edge(1)

#     # ue接入bs1
#     init_bs('1')

#     time.sleep(1)

#     # UE启动GA客户端，开始接受服务
#     ue_run_GA(1)

#     time.sleep(10)

# #*==========bs切换================
#     # 建立经过bs_2-1到dn1的隧道
#     tunnel_2 = s.add_tunnel(2001001, 1, 0)

#     # bs切换
#     switch_bs('2')

#     time.sleep(3)

# #*==========新session建立================
#     # 建立经过bs_2-2到dn2的隧道
#     tunnel_3 = s.add_tunnel(2001001, 2, 1)

#     # ue接入bs_2-2
#     init_bs('2-2')

#     # UE启动GA客户端，开始接受服务
#     ue_run_GA(dn_id=2)

# #*==========关闭旧链接================
#     s.del_tunnel(tunnel_1)
#     s.del_tunnel(tunnel_2)
