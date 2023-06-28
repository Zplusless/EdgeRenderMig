# 本文件用于在dn上直接对mintest进行in app latency的测试，即在本地进行esc发时延测量
# 总时延=网络时延+GA时延+minetest时延，本文测量结果仅包含minetest的时延
# 用于测量ga的本身的menu弹出时延


#! 由于此处videoGet不是io操作，而是cpu密集的，因此会收到GIL的限制，录屏帧率上不去。
# 多进程分享数据，使用多进程的Queue传递数据
# https://docs.python.org/3.6/library/multiprocessing.html#exchanging-objects-between-processes
# 使用Value传递数据https://blog.csdn.net/bqw18744018044/article/details/104739000

#todo 帧率仍然上不去




import numpy as np
from PIL import ImageGrab
import cv2
import time
from threading import Thread
from multiprocessing import Process, Queue, Value, Manager

from utils.call_cmd import cmd
from utils.timmer import wait,hms
import utils.switch_window as sw
import config

class VideoGet:
    """
    Class that continuously gets frames from a VideoCapture object
    with a dedicated thread.
    """

    def __init__(self, fps:int, length):
        self.length = Value('d', length)

        im = ImageGrab.grab()
        self.size = im.size

        self.max_fps = self.test_max_fps()
        if 0<fps<=self.max_fps:
            self.fps = fps
        else:
            self.fps = self.max_fps
        print(f'实际录屏帧率：{self.fps}')
        # self.frame = cv2.cvtColor(np.array(im), cv2.COLOR_BGR2RGB)
        self.frame_queue = Manager().Queue() 

        # self.stream = cv2.VideoCapture(src)
        # (self.grabbed, self.frame) = self.stream.read()
        self.stopped = Value('i', 0) #! 使用进程共享的变量，否则后面stop失效
        
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
        self.start_time = Value('d', time.time())
        Process(target=self.get, args=()).start()
        return self, self.fps, self.size

    def get(self):
        ptime = time.time()
        while self.stopped.value!=1:
            # nowtime = time.time()
            # # if (nowtime-ptime)>= 1/(self.fps*2): # 以2倍fps进行采样
            # if (nowtime-ptime)>=1/(self.fps*1.2):
            #     self.frame = self.next_frame()
            #     self.frame_queue.put(self.frame)
            #     ptime = nowtime
            self.frame = self.next_frame()
            self.frame_queue.put(self.frame)

            if time.time() - self.start_time.value > self.length.value:
                break
            
        print('Screen recording process stopped!')
  

    def read(self):
        return self.frame_queue.get()
            

    def stop(self):
        self.stopped.value = 1





class LocalRecorder:
    def __init__(self, path:str, length=20, fps=120) -> None:
        fourcc = cv2.VideoWriter_fourcc(*'avc1')  # 设置视频编码格式
        # self.fps = fps # 设置帧率
        # init只是给出期望帧率，VideoGet返回的是实际帧率
        self.capture, self.fps, self.size = VideoGet(fps, length=length).start()
        self.writer = cv2.VideoWriter(path, fourcc, self.fps, self.size)
        self.length = length
        self.is_running=True
        self.show_text = False
        

    def run(self):
        ptime = time.time()
        t_start = ptime
        in_app_ptime = ptime
        count = 0
        print(f'self.fps={self.fps}')
        while self.is_running:  # 开始录制
            # im = ImageGrab.grab()
            # im_cv = cv2.cvtColor(np.array(im), cv2.COLOR_BGR2RGB)
            # 图像写入
            nowtime = time.time()
            if (nowtime-ptime)>=1/(self.fps*1.2):
                frame = self.capture.read()
                if nowtime - in_app_ptime > config.IN_APP_LATENCY_INTERVAL:
                    # print(nowtime - in_app_ptime)
                    sw.press_esc()
                    self.show_text = (self.show_text==False)  # True False交替出现
                    in_app_ptime = time.time()
                if self.show_text:
                    # https://docs.opencv.org/4.x/d6/d6e/group__imgproc__draw.html#ga5126f47f883d730f633d74f07456c576   
                    cv2.putText(frame, 'ESC Pressed', (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 3.0, (255, 255, 0), thickness = 5)
            
                self.writer.write(frame)
                count+=1
                ptime=nowtime
            
            if time.time()-t_start>=self.length:  # 当某某条件满足中断循环
                break
        tt = time.time()-t_start
        print(f'录制结束，共录制{tt}秒, 总帧数为{count}, 实际fps{count/tt}')
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