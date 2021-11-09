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
    res, t1 = cmd(f'cd Edge/minecraft && java -jar HMCL-3.3.188.jar', False)


    return 'done'



@edge_app.route('/run_ga/')
def run_ga():


    # 启动GA
    # todo 修改配置文件，锁定游戏窗口 https://gaminganywhere.org/doc/quick_start.html
    res, t2 = cmd('bash Edge/start_game.sh &', True)

    return 'done'


if __name__ == '__main__':
    edge_app.run('0.0.0.0', port=8000)