from flask import Flask, request
from utils.call_cmd import cmd
import config
import os
import signal
import psutil

edge_app = Flask(__name__)





#******************************
# todo GA脚本启动
#! edge端启动游戏后无法启动GA
#! 要先启动游戏，再启动GA
#******************************

state={'game_pid':None,
       'ga_pid':None}


@edge_app.route('/run_game/', methods=['POST'])
def run_game():

    # name = request.form.get('name')
    # ip = request.form.get('ip')
    # port = request.form.get('port')
	
    # print(name, ip, port)

    # 启动游戏
    res, t1, _ = cmd(f"~/minetest/bin/minetest --address {config.CLOUD_IP} --port 30000 --name {config.GAME_ACCOUNT} --password {config.GAME_PASSWORD} --go", False)
    state['game_pid']=int(res)

    print(f'游戏启动，pid={res}')

    return f'done: game pid:{res}'


@edge_app.route('/stop_game/')
def stop_game():

    # 关闭游戏
    # res, t1 = cmd(f"sudo kill -9 {state['game_pid']}", True)
    # state['game_pid']=res

    os.kill(state['game_pid'], signal.SIGKILL) # 避免出现僵尸进程，这个进程实际不占用资源，pid+1的才是，但下面的kill不包含这个
    # os.kill(state['game_pid']+1, signal.SIGKILL)

    pids = psutil.pids()
    for pid in pids:
        p = psutil.Process(pid)
        # get process name according to pid
        process_name = p.name()
        # kill process "sleep_test1"
        if ('minetest' in process_name) or ('ga-server-periodic'in process_name):
            print("kill specific process: name(%s)-pid(%s)" %(process_name, pid))
            os.kill(pid, signal.SIGKILL)  


    return 'done'


@edge_app.route('/run_ga/')
def run_ga():


    # 启动GA
    # todo 修改配置文件，锁定游戏窗口 https://gaminganywhere.org/doc/quick_start.html
    pid, t2, _ = cmd('bash Edge/start_game.sh &', True)

    return 'done'


if __name__ == '__main__':
    edge_app.run('0.0.0.0', port=8000)