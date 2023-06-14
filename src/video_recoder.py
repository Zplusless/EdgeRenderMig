# sudo apt install libopencv-dev python3-opencv
# using v3.2.0 opencv on ubuntu-18.04, high version like 4.7.0 or 4.5.3 fail to work

import cv2 
import time
# from skimage.measure import  compare_ssim, compare_psnr, compare_mse
from skimage.metrics import structural_similarity as compute_ssim
from logging import Logger
from utils.timmer import current_milli_time


class Recorder:
    def __init__(self, url1, url2, output_file, size=None, logger:Logger=None) -> None:
        self.url1=url1
        self.url2=url2
        self.cap1, self.fps1, self.size1 = self.init_cap(url1)
        self.cap2, self.fps2, self.size2 = self.init_cap(url2)

        self.frame1 = None
        self.frame2 = None


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
        print('start closing process')
        self.end = True

        # cv2.destroyAllWindows()
        print("finished")

    def release_resource(self):
        self.default_cap.release()
        self.copilote_cap.release()
        self.out.release()

    def trigger_switch(self):
        self.on_switching = True
        print('switching enabled')

    def get_downtime(self):
        while self.down_time == None:
            print('switch not finished, wait for switching')
            time.sleep(0.5)
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
                if not self.default_cap.isOpened():
                    time.sleep(1)
                    print('default cap disappear')
                    continue
                # else:
                #     cap = self.cap1
                
                ret1,frame1 = self.default_cap.read()
                self.frame1 = cv2.resize(frame1, self.size)
                if not ret1:
                    if self.default_cap == self.cap1:
                        print('cap1 not recieved yet')
                        continue
                    else:
                        # self.close()
                        print('default cap ends')
                        self.release_resource()
                        break
                

                    
                if self.copilote_cap.isOpened():
                    ret2,frame2 = self.copilote_cap.read()
                    try:
                        self.frame2 = cv2.resize(frame2, self.size)
                    except Exception as e:
                        print(f'\n\n\n\nsize:{self.size}\n\n\n\n')
                        print(e)
                        return -1
                    if not ret2:
                        # break
                        pass
                                               

                


                if self.on_switching and ret1 and ret2:
                    ssim = compute_ssim(frame1, frame2 , channel_axis=2, multichannel=True)
                    print(ssim)
                    if ssim > 0.9:
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
            
                if self.end:
                    print('break normally')
                    self.release_resource()
                    break

        except KeyboardInterrupt:
            print('stop running because of ctrl-c')
            self.release_resource()

        # self.close()




if __name__ == "__main__":
    from threading import Thread
    r = Recorder('rtsp://192.168.1.1:8554/desktop', 'rtsp://192.168.1.2:8554/desktop', 'test_output.mp4') #, (960, 540))
    t=  Thread(target=r.run)
    t.start()


    time.sleep(5)
    r.trigger_switch()



    time.sleep(8)
    r.close()
    # t.join()