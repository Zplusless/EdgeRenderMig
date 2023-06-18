# sudo apt install libopencv-dev python3-opencv
# using v3.2.0 opencv on ubuntu-18.04, high version like 4.7.0 or 4.5.3 fail to work

import cv2 
import time
# from skimage.measure import  compare_ssim, compare_psnr, compare_mse
from skimage.metrics import structural_similarity as compute_ssim
from logging import Logger
from utils.timmer import current_milli_time, wait
import queue
import socket
import logging

hostname = socket.gethostname()
logging.basicConfig(
    level=logging.INFO, 
    format= f'%(asctime)s - {hostname} - %(levelname)s - %(message)s', #'%(asctime)s - %(levelname)s - %(message)s',
    filename='node_log/video_recoder',
    filemode='a',##模式，有w和a，w就是写模式，每次都会重新写日志，覆盖之前的日志
    )
log = logging.getLogger('video_recoder')



class Recorder:
    def __init__(self, url1, url2, output_file, size=None, logger:Logger=None) -> None:
        self.url1=url1
        self.url2=url2
        self.cap1, self.fps1, self.size1 = self.init_cap(self.url1)
        self.cap2, self.fps2, self.size2 = self.init_cap(self.url2)

        self.queue1 = queue.Queue()
        self.queue2 = queue.Queue()

        self.frame1 = None
        self.frame2 = None
        self.ssim = None


        # * write的size一定要一致
        # https://blog.csdn.net/daixiangzi/article/details/86165129
        if size:
            self.size = size
        else:
            self.size = self.size1

        fps = max(self.fps1, self.fps2)
        # self.out = cv2.VideoWriter(output_file, cv2.VideoWriter_fourcc(*"MJPG"), fps, self.size)
        self.out = cv2.VideoWriter(output_file, cv2.VideoWriter_fourcc(*"mp4v"), fps, self.size)

        self.on_switching = False # 在True期间会判断是否要切换cap

        self.default_queue = self.queue1
        self.copilot_queue = self.queue2
        
        # 计时模块
        self.log = logger
        self.t1 = None
        self.t2 = None
        self.down_time = None

        self.end = False



    def init_cap(self, url):

        cap = cv2.VideoCapture(url)

        fps = int(cap.get(cv2.CAP_PROP_FPS))  
        # 分辨率-宽度
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        # 分辨率-高度
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        return cap, fps, (width, height)

    def close(self):
        log.info('Set self.end=True')
        self.end = True

        # cv2.destroyAllWindows()
        # log.info("finished")

    def release_resource(self):
        log.info('Releasing captures')
        self.cap1.release()
        self.cap2.release()
        self.out.release()
        log.info('Releasing End')

    def trigger_switch(self):
        self.on_switching = True
        log.info('switching enabled')

    def get_downtime(self):
        while self.down_time == None:
            log.info(f'switch not finished, wait for switching: ssim={self.ssim}, on_switching = {self.on_switching}')
            if self.ssim == None:
                log.info(len(self.frame1), len(self.frame2), compute_ssim(self.frame1, self.frame2 , channel_axis=2, multichannel=True))
            time.sleep(2) 
            if self.end:
                log.info('record has finished, no switching, exit')
                return -1

        t = self.down_time
        self.down_time = None
        return t


    #! 接收和处理分离 https://stackoverflow.com/a/63413453
    def run_recieve(self):
        try:
            # cap = None
            while True:

                #! 一定要先判断是否end，否则容易出现中途continue导致运行不到end的判断这一步
                if self.end:
                    log.info('break normally')
                    self.release_resource()
                    break

                # 首先保证cap都是开的
                cap1_ready = self.cap1.isOpened()
                cap2_ready = self.cap2.isOpened()
                if not (cap1_ready and cap2_ready):
                    # de_cap = "cap1" if self.default_cap == self.cap1 else "cap2"
                    # co_cap = "cap2" if self.copilote_cap == self.cap2 else "cap1"
                    log.info('Not all caps are ready')
                    log.info(f'cap1 ---> {cap1_ready},  cap2 ---> {cap2_ready}')
                    time.sleep(1)


                    #! 重置capture--->https://stackoverflow.com/a/56379034
                    log.info('reset captures')
                    self.cap1, self.fps1, self.size1 = self.init_cap(self.url1)
                    self.cap2, self.fps2, self.size2 = self.init_cap(self.url2)
                    log.info('captue reset done')
                    continue
                    continue
                
                
                
                # 保证都读到了frame
                ret1,frame1 = self.cap1.read()
                ret2,frame2 = self.cap2.read()

                if not (ret1 and ret2):
                    # de_cap = "cap1" if self.default_cap == self.cap1 else "cap2"
                    # co_cap = "cap2" if self.copilote_cap == self.cap2 else "cap1"
                    log.info('Reading from video capture failed')
                    log.info(f'cap1 --->{ret1},  cap2 --->{ret2}')
                    time.sleep(1)


                    #! 重置capture--->https://stackoverflow.com/a/56379034
                    log.info('reset captures')
                    self.cap1, self.fps1, self.size1 = self.init_cap(self.url1)
                    self.cap2, self.fps2, self.size2 = self.init_cap(self.url2)
                    log.info('captue reset done')
                    continue



                frame1 = cv2.resize(frame1, self.size)
                frame2 = cv2.resize(frame2, self.size)

                self.queue1.put(frame1)
                self.queue2.put(frame2)
        
        except KeyboardInterrupt:
            log.info('stop running because of ctrl-c')
            self.release_resource()

    
    
    def run_record(self):

        while True:
            if  self.queue1.empty()  or self.queue2.empty():
                log.info('frame queue empty, exit')
                break

            self.frame1 = self.default_queue.get()
            self.frame2 = self.copilot_queue.get()

            if self.on_switching:
                self.ssim = compute_ssim(self.frame1, self.frame2 , channel_axis=2, multichannel=True)
                log.info(self.ssim)
                if self.ssim > 0.95:
                    log.info(f'before switching {id(self.default_queue)}<--->{id(self.copilot_queue)}')
                    self.t1 = current_milli_time()

                    temp = self.copilot_queue
                    self.copilot_queue = self.default_queue
                    self.default_queue = temp


                    self.t2 = current_milli_time()
                    self.down_time = self.t2-self.t1
                    if self.log:
                        self.log.info(f"switch - {self.down_time}")

                    self.on_switching = False
                    log.info("\n\n========trigger switch!!=====")
                    log.info(f'after switching {id(self.default_queue)}<--->{id(self.copilot_queue)}')

            
            self.out.write(self.frame1)
            log.info('-', end='')


                # cv2.imshow("frame",frame1)


                # if cv2.waitKey(1) & 0xFF == ord('q'):
                #     log.info('break with key_q pressed')
                #     break
            




if __name__ == "__main__":
    from threading import Thread
    from utils.timmer import wait
    r = Recorder('rtsp://192.168.5.81:8554/desktop', 'rtsp://192.168.5.61:8554/desktop', 'test_output.mp4') #, (960, 540))
    # r = Recorder('rtsp://192.168.1.1:8554/desktop', 'rtsp://192.168.1.2:8554/desktop', 'test_output.mp4') #, (960, 540))
    t1=  Thread(target=r.run_recieve())
    t2= Thread(target=r.run_recieve)
    t1.start()
    t2.start()


    wait(5)
    r.trigger_switch()
    
    log.info(r.get_downtime())


    wait(8)
    r.close()
    # t.join()