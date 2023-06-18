# sudo apt install libopencv-dev python3-opencv
# using v3.2.0 opencv on ubuntu-18.04, high version like 4.7.0 or 4.5.3 fail to work

import cv2 
import time
# from skimage.measure import  compare_ssim, compare_psnr, compare_mse
from skimage.metrics import structural_similarity as compute_ssim
from logging import Logger
from utils.timmer import current_milli_time, wait
import config


class Recorder:
    def __init__(self, url1, url2, output_file, size=None, logger:Logger=None) -> None:
        self.url1=url1
        self.url2=url2
        self.cap1, self.fps1, self.size1 = self.init_cap(self.url1)
        self.cap2, self.fps2, self.size2 = self.init_cap(self.url2)

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
        self.default_cap = self.cap1
        self.copilote_cap = self.cap2
        
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
        print('Set self.end=True')
        self.end = True

        # cv2.destroyAllWindows()
        # print("finished")

    def release_resource(self):
        print('Releasing captures')
        self.default_cap.release()
        self.copilote_cap.release()
        self.out.release()
        print('Releasing End')

    def trigger_switch(self):
        self.on_switching = True
        print('switching enabled')

    def get_downtime(self):
        while self.down_time == None:
            print(f'switch not finished, wait for switching: ssim={self.ssim}, on_switching = {self.on_switching}')
            if self.ssim == None:
                print(len(self.frame1), len(self.frame2), compute_ssim(self.frame1, self.frame2 , channel_axis=2, multichannel=True))
            time.sleep(2) 
            if self.end:
                print('record has finished, no switching, exit')
                return -1

        t = self.down_time
        self.down_time = None
        return t


    # def do_switch(self):
    #     print('start switching')
    #     while True:
    #         if self.default_cap.isOpened() and self.copilote_cap.isOpened():
    #             ssim = compute_ssim(self.frame1, self.frame2 , channel_axis=2, multichannel=True)
    #             print(ssim)
    #             if ssim > 0.9:
    #                 print(f'before switching {id(self.default_cap)}<--->{id(self.copilote_cap)}')
    #                 self.t1 = current_milli_time()

    #                 temp = self.copilote_cap
    #                 self.copilote_cap = self.default_cap
    #                 self.default_cap = temp


    #                 self.t2 = current_milli_time()
    #                 self.down_time = self.t2-self.t1
    #                 # if self.log:
    #                 #     self.log.info(f"switch - {self.down_time}")

    #                 # self.on_switching = False
    #                 print("\n\n========trigger switch!!=====")
    #                 print(f'after switching {id(self.default_cap)}<--->{id(self.copilote_cap)}')
                    
    #                 break
    #         else:
    #             time.sleep(0.5)
    #     return self.down_time


    def run(self):
        try:
            # cap = None
            while True:

                #! 一定要先判断是否end，否则容易出现中途continue导致运行不到end的判断这一步
                if self.end:
                    print('break normally')
                    self.release_resource()
                    break

                # 首先保证cap都是开的
                de_cap_ready = self.default_cap.isOpened()
                co_cap_ready = self.copilote_cap.isOpened()
                if not (de_cap_ready and co_cap_ready):
                    de_cap = "cap1" if self.default_cap == self.cap1 else "cap2"
                    co_cap = "cap2" if self.copilote_cap == self.cap2 else "cap1"
                    print('Not all caps are ready')
                    print(f'default_cap ---> {de_cap},  copilot_cap ---> {co_cap}')
                    time.sleep(1)
                    continue
                
                
                
                # 保证都读到了frame
                ret1,frame1 = self.default_cap.read()
                ret2,frame2 = self.copilote_cap.read()


                #! 重置capture--->https://stackoverflow.com/a/56379034
                if not (ret1 and ret2):
                    
                    self.cap1, self.fps1, self.size1 = self.init_cap(self.url1)
                    self.cap2, self.fps2, self.size2 = self.init_cap(self.url2)

                    # 判断cap是否已经交换过
                    is_changed = (self.default_cap == self.cap2) 

                    if is_changed:
                        de_cap = "cap2"
                        co_cap = "cap1"
                        self.default_cap = self.cap2
                        self.copilote_cap = self.cap1

                    
                    else:
                        de_cap = "cap1"
                        co_cap = "cap2"     
                        self.default_cap = self.cap1
                        self.copilote_cap = self.cap2                   

                    print('Reading from video capture failed')
                    print(f'default_cap({de_cap}) --->{ret1},  copilot_cap({co_cap}) --->{ret2}')
                    time.sleep(1)
                    continue



                self.frame1 = cv2.resize(frame1, self.size)
                self.frame2 = cv2.resize(frame2, self.size)

                if self.on_switching:
                    self.ssim = compute_ssim(self.frame1, self.frame2 , channel_axis=2, multichannel=True)
                    print(self.ssim)
                    if self.ssim > config.SSIM_THRESHOLD:
                        print(f'before switching {id(self.default_cap)}<--->{id(self.copilote_cap)}')
                        self.t1 = current_milli_time()

                        temp = self.copilote_cap
                        self.copilote_cap = self.default_cap
                        self.default_cap = temp
                        frame1 = frame2

                        self.t2 = current_milli_time()
                        self.down_time = self.t2-self.t1
                        if self.log:
                            self.log.info(f"switch - {self.down_time}")

                        self.on_switching = False
                        print("\n\n========trigger switch!!=====")
                        print(f'after switching {id(self.default_cap)}<--->{id(self.copilote_cap)}')

                
                self.out.write(self.frame1)
                print('-', end='')


                # cv2.imshow("frame",frame1)


                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print('break with key_q pressed')
                    break
            


        except KeyboardInterrupt:
            print('stop running because of ctrl-c')
            self.release_resource()

        # self.close()




if __name__ == "__main__":
    from threading import Thread
    from utils.timmer import wait
    r = Recorder('rtsp://192.168.5.81:8554/desktop', 'rtsp://192.168.5.61:8554/desktop', 'test_output.mp4') #, (960, 540))
    # r = Recorder('rtsp://192.168.1.1:8554/desktop', 'rtsp://192.168.1.2:8554/desktop', 'test_output.mp4') #, (960, 540))
    t=  Thread(target=r.run)
    t.start()


    wait(5)
    r.trigger_switch()
    
    print(r.get_downtime())


    wait(8)
    r.close()
    # t.join()