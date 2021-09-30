# -*- coding: UTF-8 -*-

"""
This is a simulation of the apps running on UE.
Functions like srv_1() are different client apps 
whose server side are running at DN.

run_srv() controls which client app will run.
"""

import time
import logging
from flask import Flask, request
# from multiprocessing import Process

# from UE.Snakepygame import SnakeClient
from utils.call_cmd import cmd
import asyncio

import requests

import config




current_milli_time = lambda: int(round(time.time() * 1000))

ue_app = Flask(__name__)

# 关闭flask的log
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)



logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

TEMP = {'client':None}

def run_client(client):
    asyncio.get_event_loop().run_until_complete(client.game())

# Edge启动snake游戏 && GA
def start_edge(edge_id):
    addr = f'http://192.168.1.{edge_id}:8000/run_game/'
    data = {
        'name': 'srv_mig',
        'ip': config.CLOUD_IP,
        'port': 5500
    }

    res = requests.post(addr, data = data)
    return res.status_code



@ue_app.route('/run_client/<dn_id>/')
def run_client(dn_id):

    # 让edge端启动
    res = start_edge(dn_id)
    if res == 200:
        # dn = request.form.get('dn_id')
        command = f'cd /home/edge/gaminganywhere-master/bin && ./ga-client config/client.abs.conf rtsp://192.168.1.{dn_id}:8554/desktop'
        t = cmd(command, True)
    else:
        raise Exception(f'game start failed at Edge-{dn_id}')

    return str(t)

@ue_app.route('/switch_bs/<target_bs>/')
def switch_bs(target_bs):
    t = cmd(f'bash UE/route_to_{target_bs}.sh', True)

    return str(t)

@ue_app.route('/init_bs/<bs_id>/')
def init_bs(bs_id):
    t = cmd(f'bash UE/route_init_{bs_id}.sh', True)

    return str(t)

if __name__ == "__main__":
    ue_app.run(host='0.0.0.0', port=6600)







# @ue_app.route('/run_srv/<log_name>/<int:srv_id>/')
# def run_srv(log_name, srv_id):
#     srv_cls = SRVS[srv_id]
#     CURRENT_STATE['srv_id'] = srv_id

#     log.debug(CURRENT_STATE)

#     if srv_cls.log_name: # 如果非空，表示本UE已经在运行
#         raise Exception('Current UE is running, why start it again?')

#     return srv_cls.start(log_name=log_name)


# @ue_app.route('/run_srv/<log_name>/<int:srv_id>/<int:t>/')
# def run_srv_with_time(log_name, srv_id, t):
#     srv_cls = SRVS[srv_id]
#     CURRENT_STATE['srv_id'] = srv_id

#     log.debug(CURRENT_STATE)

#     if srv_cls.log_name: # 如果非空，表示本UE已经在运行
#         raise Exception('Current UE is running, why start it again?')

#     return srv_cls.start(log_name=log_name, max_time=t)


# @ue_app.route('/stop_srv/')
# def stop_srv():
#     srv_id = CURRENT_STATE['srv_id']
#     srv_cls = SRVS[srv_id]
#     if srv_cls:
        
#         if not srv_cls.is_BrokenPipe: # 如果没有broken pipe
#             res = srv_cls.stop()
#             log.info('a working UE stopped')
#             return '0'  #! 关闭了一个正常的UE
#         else: # 如果broken pipe
#             srv_cls.stop()
#             log.info('Broken Pipe UE stopped')
#             ans = srv_cls.force_del_dnc_record()
#             if ans ==0:
#                 finish()
#                 log.info('a broken pipe UE stopped and finished\n\n\n')
#                 return '-1' #! 关闭了一个broken pipe UE
#             else:
#                 log.info('****** Failed to del dnc record of broken pipe UE ******')
#                 # raise Exception # 按说不应该发生
#                 return '-2' #! 关闭broken pipe UE 失败， 按说不应该发生
#     else:
#         return 'no ue running'
        

# @ue_app.route('/record_t/', methods=['POST'])
# def recieve_data():
#     srv_id = CURRENT_STATE['srv_id']
#     srv_cls = SRVS[srv_id]
#     # if len(srv_cls.t_remote)<=len(srv_cls.t_local):

#     #! 虽然很奇怪，BrokenPipe后ue不记录time stamp后还会受到server端的time stamp
#     #! 目前这个问题原因还没找到，但是先在这里一刀切屏蔽了
#     if srv_cls.is_BrokenPipe:
#         return 'Broken Pipe, no need to record'
#     else:

#         frame = int(request.form.get('frame'))
#         t2 = int(request.form.get('t2'))
#         t3 = int(request.form.get('t3'))
#         t4 = int(request.form.get('t4'))
#         t5 = current_milli_time()
#         # print(f'got frame--->{frame}')
#         srv_cls.record([frame, t2, t3, t4, t5])

#         return 'done'

# @ue_app.route('/finish/')
# def finish():
    
#     ip = request.remote_addr
#     log.debug(f'finish invoked by {ip}\n\n\n')

#     srv_id = CURRENT_STATE['srv_id']
#     srv_cls = SRVS[srv_id]

#     if not srv_cls.started:
#         # 写入远端数据
#         csv_name1 = config.BASE_LOG_PATH + f'{srv_cls.log_name}_t2345_log.csv'
#         with open(csv_name1, 'w', newline='') as result_file:
#             wr = csv.writer(result_file, dialect='excel')
#             wr.writerows(srv_cls.t_remote)

#         # 状态初始化
#         srv_cls.init()
#         CURRENT_STATE['srv_id'] = None

#         log.info('UE finished!')

#         return 'done'
    
#     else:
#         #! # fixme UE 端process.stdin.close()后，server端也会推出，触发对ue端finish的请求
#         #! 故出现没有stop就finish的情况  逻辑暂时无法优化，只能在这里做一个判断
#         log.info('出现对没有stop的UE调用finish')
#         return 'not stopped yet, cannot finish\n\n\n\n'


# @ue_app.route('/ue_stamps/')
# def get_time_stamps():
#     srv_id = CURRENT_STATE['srv_id']
#     srv_cls = SRVS[srv_id]

#     #! 如果brokenPipe，直接返回空的数据，让识别成brokenPipe就行了
#     if srv_cls.is_BrokenPipe:
#         upload_data = {
#             'host': srv_cls.ip,
#             'timestamp': []   # [[t1,t2,t3,t4,t5], [t1,t2,t3,t4,t5]...]
#         }
#         return upload_data
#     else:
#         dict_frames = srv_cls.get_new_stamps()
#         return dict_frames

