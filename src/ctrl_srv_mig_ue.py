import requests
from utils.call_cmd import cmd
import config
import time
import logging
import socket
from utils.timmer import current_milli_time, hms, wait
import utils.switch_window as sw


from video_recoder import Recorder
from threading import Thread


hostname = socket.gethostname()
logging.basicConfig(
    level=logging.INFO, 
    format= f'%(asctime)s - {hostname} - %(levelname)s - %(message)s', #'%(asctime)s - %(levelname)s - %(message)s',
    filename='node_log/srvMig.log',
    filemode='a',##模式，有w和a，w就是写模式，每次都会重新写日志，覆盖之前的日志
    )
log = logging.getLogger('srvMig_log')




# Edge启动snake游戏 && GA
def start_edge_game(edge_id):
    addr = f'http://192.168.1.{edge_id}:8000/run_game/'
    data = {
        'name': 'srv_mig',
        'ip': config.CLOUD_IP,
        'port': 5500
    }

    res = requests.post(addr, data = data)
    return res.status_code

# 启动GA
def start_edge_ga(edge_id):
    addr = f'http://192.168.1.{edge_id}:8000/run_ga/'
    res = requests.get(addr)
    return res.status_code




def start_stream(dn_id, logfile=None):
    command = f'cd /home/edge/gaminganywhere-master/bin && ./ga-client config/client.abs.conf rtsp://192.168.1.{dn_id}:8554/desktop'
    pid, t, _ = cmd(command, False, logfile=logfile)
    return res

def end_minetest(edge_id):
    addr = f'http://192.168.1.{edge_id}:8000/stop_game/'
    res = requests.get(addr)
    return res.status_code



def measure_start(target = [1,2]):
    ans = [0, 0]
    if isinstance(target, int):
        target = [target]
    if 1 in target:
        url1 = f'http://{config.EDGE_NODE_IP_1}:10800/start/'
        res1 = requests.get(url1)
        ans[0] = res1.status_code
    if 2 in target:
        url2 = f'http://{config.EDGE_NODE_IP_2}:10800/start/'
        res2 = requests.get(url2)
        ans[1] = res2.status_code
    return ans

def measure_end(target = [1,2]):
    ans = [0, 0]
    if isinstance(target, int):
        target = [target]
    if 1 in target:
        url1 = f'http://{config.EDGE_NODE_IP_1}:10800/end/'
        res1 = requests.get(url1)
        ans[0] = res1.status_code
    if 2 in target:
        url2 = f'http://{config.EDGE_NODE_IP_2}:10800/end/'
        res2 = requests.get(url2)
        ans[1] = res2.status_code
    return ans

def measure_insert(msg:str, target=[1,2]):
    ans = [0, 0]

    if isinstance(target, int):
        target = [target]
    if msg not in ['STREAM', 'MIGRATION', 'SWITCH', 'MIGRATION_END', 'STREAM_END']:
        raise Exception('wrong measure insert message')
    if 1 in target:
        url1 = f'http://{config.EDGE_NODE_IP_1}:10800/insert/{msg}/'
        res1 = requests.get(url1)
        ans[0] = res1.status_code
    if 2 in target:
        url2 = f'http://{config.EDGE_NODE_IP_2}:10800/insert/{msg}/'
        res2 = requests.get(url2)
        ans[1] = res2.status_code
    return ans


if __name__ =="__main__":

    # 建立dn1的link
    addr = f'http://100.1.1.254:5000/setup_link/1/'
    ans = requests.get(addr).text
    # print(ans, type(ans))
    if ans != '1':
        raise Exception('link to dn1 failed')
    # ue接入bs1
    pid, t, _ = cmd(f'bash UE/route_init_1.sh', True)



#!##############################################
#   开始推流dn1
#!##############################################
    #?-----------------------------------
    # time.sleep(10)
    if config.IN_MEASUREMENT:
        wait(10, msg='stream dn1')
        measure_insert('STREAM', target=1)
    #?-----------------------------------

    # UE启动dn1上的游戏实例
    res = start_edge_game(1)
    # 启动到dn1的推流
    if res == 200:
        print('start game at edge success!')
        start_stream(1, 'node_log/Stream_log_1.log')
    else:
        print(res)
        raise Exception(f'game start failed at Edge-1')










#!##############################################
#   接入bs2，pre-mig
#!##############################################
    # 建立dn2的link
    addr = f'http://100.1.1.254:5000/setup_link/2/'
    ans = requests.get(addr).text
    if ans != '2':
        raise Exception('link to dn1 failed')
    # ue接入bs2
    pid, t, _ = cmd(f'bash UE/route_init_2-2.sh', True)



#!##############################################
#   开始推流dn2
#!##############################################
    #?-----------------------------------
    # time.sleep(10)
    if config.IN_MEASUREMENT:
        wait(2, msg='stream dn2')
        measure_insert('STREAM', target=2)
    #?-----------------------------------

#!##############################################
#   开始服务迁移
#!##############################################
    #?-----------------------------------
    # time.sleep(10)
    if config.IN_MEASUREMENT:
        wait(5, msg='wait for migtration start')
        measure_insert('MIGRATION')
    #?-----------------------------------
    # =================================
    #! 迁移时间计时点1
    tm1= current_milli_time()
    # =================================

    # UE启动dn2上的游戏实例
    res = start_edge_game(2)
    # 启动到dn2的推流
    if res == 200:
        print('start game at edge success!')
        start_stream(2, 'node_log/Stream_log_2.log')
    else:
        raise Exception(f'game start failed at Edge-2')

    # =================================
    #! 迁移时间计时点1end
    tm1e= current_milli_time()
    # =================================


    # sleep
    wait(5, 'Streaming Game')


    # 切换到dn1的窗口，因为dn2后出来，经常覆盖了dn1，造成主窗口在后，副窗口在前
    sw.switch_window()


    # =================================
    # 开始录屏
    #! 迁移时间计时点2
    tm2= current_milli_time()
    # =================================


    # r = Recorder(config.RTSP_STREAM_1, config.RTSP_STREAM_2, f'ue_log/srv_mig_{hms()}.mp4', (960, 540), logger=log)
    r = Recorder(config.RTSP_STREAM_1, config.RTSP_STREAM_2, f'ue_log/srv_mig_{hms()}.mp4')# , (800, 600))
    t=  Thread(target=r.run)
    t.start()

    # =================================
    #! 迁移时间计时点2end
    tm2e= current_milli_time()
     # =================================







#!##############################################
#   开始switch
#!##############################################
    #?-----------------------------------
    if config.IN_MEASUREMENT:
        wait(10, msg='waiting for switch')
        measure_insert('SWITCH')
    #?-----------------------------------
    # 运行几秒钟
    wait(2, 'Video Recording')

    # =================================
    t1 = current_milli_time()
    # =================================
    # 按F2 切换控制权限
    # sw.minetest_f2()

    # switch 窗口
    # sw.switch_window()

    # 允许视频流切换
    r.trigger_switch()

    # =================================
    t2=current_milli_time()
    # =================================












    # 运行几秒钟,让trigger部分运行起来
    wait(5, 'Triggering Switch')

    # =================================
    tm3 = current_milli_time()
    # =================================
    # 获取downtime
    t = r.get_downtime()
    # =================================
    tm3e = current_milli_time()
    # =================================





#!##############################################
#   服务迁移结束
#!##############################################
    #?-----------------------------------
    if config.IN_MEASUREMENT:
        wait(10, msg='migration end')
        measure_insert('MIGRATION_END')
    #?-----------------------------------

    #         切流   切窗口 
    t_down = t
    # t_down = t +  t2-t1
    # t_down = [t, t2-t1]
    #        连接bs启动游戏    双stream准备    允许切换
    t_mig = (tm1e - tm1) + (tm2e - tm2) + (t2 - t1) + (tm3e - tm3)
    # t_mig = [(tm1e - tm1), (tm2e - tm2), (t2 - t1), (tm3e - tm3)]

    print(f'\nswitching downtime:{t_down}')
    print(f'\ntotal migration time: {t_mig}')



    log.info(f'migration - {t_mig}')
    log.info(f'downtime - {t_down}')
    log.info('\n\n\n====================================')

   
    # 切换后运行一段时间
    wait(10, 'Before Ending')

    # 停止记录
    r.close()
#!##############################################
#   stream结束
#!##############################################
    #?-----------------------------------
    if config.IN_MEASUREMENT:
        wait(2, msg='stream end')
        measure_insert('STREAM_END')
    #?-----------------------------------


#!##############################################
#   推流结束
#!##############################################
    #?-----------------------------------
    if config.IN_MEASUREMENT:
        wait(10, msg='measure end')
        measure_end()
    #?-----------------------------------
    end_minetest(1)


#!##############################################
#   初始化下次测量
#!##############################################
    # #?-----------------------------------
    if config.IN_MEASUREMENT:
        wait(2,msg='init measure for next round')
        measure_start()
    # #?-----------------------------------
