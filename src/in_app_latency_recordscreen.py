# 本文件用于在dn上直接对mintest进行in app latency的测试，即在本地进行esc发时延测量
# 总时延=网络时延+GA时延+minetest时延，本文测量结果仅包含minetest的时延
# 用于测量ga的本身的menu弹出时延


#todo 由于此处videoGet不是io操作，而是cpu密集的，因此会收到GIL的限制，录屏帧率上不去。
#todo 多进程分享数据，参考https://blog.csdn.net/weixin_41457494/article/details/103637858
# https://towardsdatascience.com/python-concurrency-multiprocessing-327c02544a5a


import numpy as np
from PIL import ImageGrab
import cv2
import time
from threading import Thread

from utils.call_cmd import cmd
from utils.timmer import wait,hms
import utils.switch_window as sw
import config

class VideoGet:
    """
    Class that continuously gets frames from a VideoCapture object
    with a dedicated thread.
    """

    def __init__(self, fps:int):
        im = ImageGrab.grab()
        self.size = im.size

        self.max_fps = self.test_max_fps()
        if 0<fps<=self.max_fps:
            self.fps = fps
        else:
            self.fps = self.max_fps
        print(f'实际录屏帧率：{self.fps}')
        self.frame = cv2.cvtColor(np.array(im), cv2.COLOR_BGR2RGB)

        # self.stream = cv2.VideoCapture(src)
        # (self.grabbed, self.frame) = self.stream.read()
        self.stopped = False
        
        # self.fps = int(self.stream.get(cv2.CAP_PROP_FPS)) 
        # print(f'fps:--->{self.fps}')

    def test_max_fps(self):
        t1 = time.time()
        im = ImageGrab.grab()
        im_cv = cv2.cvtColor(np.array(im), cv2.COLOR_BGR2RGB)
        t = time.time()-t1
        return 1/t

    def next_frame(self):
        im = ImageGrab.grab()
        im_cv = cv2.cvtColor(np.array(im), cv2.COLOR_BGR2RGB)
        return im_cv

    def start(self):    
        Thread(target=self.get, args=()).start()
        return self, self.fps, self.size

    def get(self):
        ptime = time.time()
        while not self.stopped:
            nowtime = time.time()
            # if (nowtime-ptime)>= 1/(self.fps*2): # 以2倍fps进行采样
            if (nowtime-ptime)>=1/(self.fps*1.2):
                self.frame = self.next_frame()
                ptime = nowtime
  
    def stop(self):
        self.stopped = True

class LocalRecorder:
    def __init__(self, path:str, length=20, fps=24) -> None:
        fourcc = cv2.VideoWriter_fourcc(*'avc1')  # 设置视频编码格式
        # self.fps = fps # 设置帧率
        # init只是给出期望帧率，VideoGet返回的是实际帧率
        self.capture, self.fps, self.size = VideoGet(fps).start()
        self.writer = cv2.VideoWriter(path, fourcc, self.fps, self.size)
        self.length = length
        self.is_running=True
        self.show_text = False
        

    def run(self):
        ptime = time.time()
        t_start = ptime
        in_app_ptime = ptime
        count = 0
        while self.is_running:  # 开始录制
            # im = ImageGrab.grab()
            # im_cv = cv2.cvtColor(np.array(im), cv2.COLOR_BGR2RGB)
            # 图像写入
            nowtime = time.time()
            if (nowtime-ptime)>=1/(self.fps*1.2):
                frame = self.capture.frame
                if nowtime - in_app_ptime > config.IN_APP_LATENCY_INTERVAL:
                    sw.press_esc()
                    self.show_text = (self.show_text==False)  # True False交替出现
                    self.in_app_ptime = time.time()
                if self.show_text:
                    # https://docs.opencv.org/4.x/d6/d6e/group__imgproc__draw.html#ga5126f47f883d730f633d74f07456c576   
                    cv2.putText(frame, 'ESC Pressed', (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 3.0, (255, 255, 0), thickness = 5)
            
                self.writer.write(frame)
                count+=1
                ptime=nowtime
            
            if time.time()-t_start>=self.length:  # 当某某条件满足中断循环
                break
        
        print(f'录制结束，共录制{time.time()-t_start}秒, 总帧数为{count}')
        self.release()

    def release(self):
        self.writer.release()
        self.capture.stop()
        print('release cv writer, end!')

    def close(self):
        self.is_running=False


if __name__ == "__main__":
    # 启动游戏
    res, t1 = cmd(f"~/minetest/bin/minetest --address {config.CLOUD_IP} --port 30000 --name {config.GAME_ACCOUNT} --password {config.GAME_PASSWORD} --go", False, logfile='ue_log/minetest.log')
    time.sleep(3)
    r = LocalRecorder(f'ue_log/srv_mig_{hms()}.mp4', fps=120)
    t = Thread(target=r.run)
    t.start()

    # wait(15, msg='running')
    time.sleep(15)
    r.close()
    print('end\n\n')