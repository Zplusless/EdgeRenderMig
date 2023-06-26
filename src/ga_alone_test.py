# 本文件用于在dn上直接运行GA并进行in app latency的测试，即在本地进行esc发时延测量
# 用于测量ga本身的menu弹出时延

import config
from utils.call_cmd import cmd
from utils.timmer import wait,hms
import time
from video_recoder import Recorder
from threading import Thread

# 启动游戏
res, t1 = cmd(f"~/minetest/bin/minetest --address {config.CLOUD_IP} --port 30000 --name {config.GAME_ACCOUNT} --password {config.GAME_PASSWORD} --go", False)

# 进行esc录屏
r = Recorder(config.RTSP_STREAM_1, config.RTSP_STREAM_1, f'ue_log/srv_mig_{hms()}.mp4')# , (800, 600))
t=  Thread(target=r.run)
t.start()

wait(15, msg='running')
r.close()
print('end\n\n')
