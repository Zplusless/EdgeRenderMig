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



# log.warning('\n\n========new experiment==========\n\n')


# # 开始录屏
# from video_recoder import Recorder
# from threading import Thread

# r = Recorder(config.RTSP_STREAM_1, config.RTSP_STREAM_2, f'srv_mig_{hms()}.mp4', (960, 540), logger=log)
# t=  Thread(target=r.run)
# t.start()

# # 运行几秒钟
# time.sleep(3)

# # 按F2 切换控制权限
# sw.minetest_f2()


# # trigger switch
# #* 此处将log作为参数传进去，在recorder内完成录屏
# r.trigger_switch()




# # switch 窗口
# sw.switch_window()



# # 结束
# time.sleep(5)
# r.close()



