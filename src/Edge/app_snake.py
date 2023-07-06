from flask import Flask, request
from utils.call_cmd import cmd

edge_app = Flask(__name__)





#******************************
# todo GA脚本启动
#! edge端启动游戏后无法启动GA
#! 要先启动游戏，再启动GA
#******************************




@edge_app.route('/run_game/', methods=['POST'])
def run_game():

    name = request.form.get('name')
    ip = request.form.get('ip')
    port = request.form.get('port')
	
    print(name, ip, port)

    # 启动游戏
    pid, t1, _ = cmd(f'python Edge/Snakepygame.py -n {name} -i {ip} -p {port} &', False)


    return 'done'



@edge_app.route('/run_ga/')
def run_ga():


    # 启动GA
    # todo 修改配置文件，锁定游戏窗口 https://gaminganywhere.org/doc/quick_start.html
    pid, t2, _ = cmd('bash Edge/start_game.sh &', False) # 此处如果为True会一直等待GA运行结束才返回，造成http超时

    return 'done'


if __name__ == '__main__':
    edge_app.run('0.0.0.0', port=8000)
