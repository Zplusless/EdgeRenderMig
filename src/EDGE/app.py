from flask import Flask, request
from utils.call_cmd import cmd

edge_app = Flask(__name__)


@edge_app.route('/run_game/', methods=['POST'])
def run_game():

    name = request.form.get('name')
    ip = request.form.get('ip')
    port = request.form.get('port')

    # 启动游戏
    t1 = cmd(f'python ./Snakepygame.py -n {name} -i {ip} -p {port}', True)

    # 启动GA
    t2 = cmd('bash ./start_game.sh', True)

    return 'done'


if __name__ == '__main__':
    edge_app.run('0.0.0.0', port=8000)