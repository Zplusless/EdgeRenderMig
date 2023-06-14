import requests
from utils.call_cmd import cmd
import config
import time
import logging
import socket
from utils.timmer import current_milli_time, hms, wait
import utils.switch_window as sw



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

def start_stream(dn_id, logfile=None):
    command = f'cd /home/edge/gaminganywhere-master/bin && ./ga-client config/client.abs.conf rtsp://192.168.1.{dn_id}:8554/desktop'
    res, t = cmd(command, False, logfile=logfile)
    return res




if __name__ =="__main__":

    # 建立dn1的link
    addr = f'http://100.1.1.254:5000/setup_link/1/'
    ans = requests.get(addr).text
    print(ans, type(ans))
    if ans != '1':
        raise Exception('link to dn1 failed')


    # ue接入bs1
    res, t = cmd(f'bash UE/route_init_1.sh', True)


    # UE启动dn1上的游戏实例
    res = start_edge_game(1)


    # 启动到dn1的推流
    if res == 200:
        print('start game at edge success!')
        start_stream(1, 'node_log/Stream_log_1.log')
    else:
        raise Exception(f'game start failed at Edge-1')


    # =================================

    # 建立dn2的link
    addr = f'http://100.1.1.254:5000/setup_link/2/'
    ans = requests.get(addr).text
    if ans != '2':
        raise Exception('link to dn1 failed')


    # ue接入bs2
    res, t = cmd(f'bash UE/route_init_2-2.sh', True)


    # UE启动dn2上的游戏实例
    res = start_edge_game(2)


    # 启动到dn2的推流
    if res == 200:
        print('start game at edge success!')
        start_stream(2, 'node_log/Stream_log_2.log')
    else:
        raise Exception(f'game start failed at Edge-2')


    # sleep
    wait(10)


    # 开始录屏
    from video_recoder import Recorder
    from threading import Thread

    # r = Recorder(config.RTSP_STREAM_1, config.RTSP_STREAM_2, f'ue_log/srv_mig_{hms()}.mp4', (960, 540), logger=log)
    r = Recorder(config.RTSP_STREAM_1, config.RTSP_STREAM_2, f'ue_log/srv_mig_{hms()}.mp4')
    t=  Thread(target=r.run)
    t.start()


        
    # 运行几秒钟
    wait(5)

    # 按F2 切换控制权限
    sw.minetest_f2()


    # trigger switch
    r.trigger_switch()


    # # switch 窗口
    # sw.switch_window()

    # t = r.do_switch()
    # print(f'downtime--->:{t}')

    # 切换后运行一段时间
    wait(10)


    # 获取downtime
    t = r.get_downtime()
    print(f'switching downtime:{t}')
   


    # 停止记录
    r.close()


