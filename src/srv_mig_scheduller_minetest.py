# 在UE直连的bs上运行


import requests
import time

from utils.call_cmd import cmd
import utils.switch_window as sw
from utils.timmer import current_milli_time, hms
from corenet_controller import Scheduller
import config
import logging
import socket

hostname = socket.gethostname()





logging.basicConfig(
    level=logging.INFO, 
    format= f'%(asctime)s - {hostname} - %(levelname)s - %(message)s', #'%(asctime)s - %(levelname)s - %(message)s',
    filename='node_log/srvMig.log',
    filemode='a',##模式，有w和a，w就是写模式，每次都会重新写日志，覆盖之前的日志
    )
log = logging.getLogger('srvMig_log')


s = Scheduller()


# UE 初始化
def init_bs(bs_id):

    print(f'init bs-{bs_id}')

    if bs_id not in ['1','2-1','2-2']:
        raise Exception('Wrong bs id')
    addr = f'http://100.1.1.1:6600/init_bs/{bs_id}/'
    t = requests.get(addr)

    return float(t.text)


# UE 切换
def switch_bs(bs_id):
    
    print(f'switch bs to: {bs_id}')


    if bs_id not in ['1','2']:
        raise Exception('Wrong bs id')
    addr = f'http://100.1.1.1:6600/switch_bs/{bs_id}/'
    t = requests.get(addr)

    return float(t.text)

# UE 启动GA
def ue_run_GA(dn_id):

    print(f'calling GA of edge-{dn_id} at ue')

    if dn_id not in [1,2]:
        raise Exception('Wrong bs id')
    addr = f'http://100.1.1.1:6600/run_client/{dn_id}/'
    t = requests.get(addr)

    return float(t.text)



if __name__ == "__main__":

#*==========阶段1================
    # 建立到dn1的隧道
    tunnel_1 = s.add_tunnel(1001001, 1, 0)

    # dn1启动game和GA
    # start_edge(1)

    # ue接入bs1
    t1 = init_bs('1')
    print(f'init bs 1, done ---> t = {t1}')

    time.sleep(1)

    # UE启动GA客户端，开始接受服务
    t2 = ue_run_GA(1)
    print(f'start game and GA at ue, done ---> t = {t2}')

    time.sleep(5)

# #*==========bs切换================
    # # 建立经过bs_2-1到dn1的隧道
    # tunnel_2 = s.add_tunnel(2001001, 1, 0)

    # # bs切换
    # # switch_bs('2')

    # time.sleep(3)

# #*==========新session建立================
    
    t1 = current_milli_time()
    # 建立经过bs_2-2到dn2的隧道
    tunnel_3 = s.add_tunnel(2001001, 2, 1)

    # ue接入bs_2-2
    init_bs('2-2')

    # UE启动GA客户端，开始接受服务
    ue_run_GA(dn_id=2)
    t2 = current_milli_time()
    log.info('\n\n\n %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
    log.info(f"migration - {t2-t1}")

# #*==========关闭旧链接================
#     s.del_tunnel(tunnel_1)
#     s.del_tunnel(tunnel_2)


# #*==========切换窗口================

time.sleep(10) # 等待两个窗口都出现



log.warning('\n\n========new experiment==========\n\n')


# 开始录屏
addr = f'http://100.1.1.1:6600/start_record/'
ans = requests.get(addr)


# 运行几秒钟
time.sleep(5)

# 按F2 切换控制权限
sw.minetest_f2()


# trigger switch
addr = f'http://100.1.1.1:6600/trigger_switch/'
ans = requests.get(addr)


# switch 窗口
sw.switch_window()



# 结束
time.sleep(10)


# 获取downtime
addr = f'http://100.1.1.1:6600/get_downtime/'
t = requests.get(addr)

dt = float(t.text)
# dt = int(requests.get(addr).text)
log.info(f"switch - {dt}")


# r.close()
addr = f'http://100.1.1.1:6600/close_recorder/'
ans = requests.get(addr)


