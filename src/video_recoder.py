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

        fps = max(self.fps1, self.fps2)
        self.out = cv2.VideoWriter(output_file, cv2.VideoWriter_fourcc(*'XVID'), fps, self.size2)

        self.on_switching = False # 在True期间会判断是否要切换cap
        self.default_cap = self.cap1
        self.copilote_cap = self.cap2
        self.size = size

        # 计时模块
        self.log = logger
        self.t1 = None
        self.t2 = None

        self.running = True


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
        self.running = False
        self.default_cap.release()
        self.copilote_cap.release()
        self.out.release()
        cv2.destroyAllWindows()
        print("finished")

    def trigger_switch(self):
        self.on_switching = True
        print('switching enabled')

    def run(self):
        try:
            # cap = None
            while self.running:
                if not self.default_cap.isOpened():
                    time.sleep(1)
                    continue
                # else:
                #     cap = self.cap1
                
                ret1,frame1 = self.default_cap.read()
                if not ret1:
                    if self.default_cap == self.cap1:
                        print('cap1 not recieved yet')
                        continue
                    else:
                        # self.close()
                        print('default cap ends')
                        break
                if self.size:
                    frame1 = cv2.resize(frame1, self.size)

                    
                if self.copilote_cap.isOpened():
                    ret2,frame2 = self.copilote_cap.read()
                    if not ret2:
                        # break
                        pass
                    
                    else:
                        if self.size:
                            frame2 = cv2.resize(frame2, self.size)

                


                if self.on_switching and ret1 and ret2:
                    ssim = compute_ssim(frame1, frame2 , channel_axis=2, multichannel=True)
                    print(ssim)
                    if ssim > 0.9:

                        self.t1 = current_milli_time()

                        temp = self.copilote_cap
                        self.copilote_cap = self.default_cap
                        self.default_cap = temp
                        frame1 = frame2

                        self.t2 = current_milli_time()
                        if self.log:
                            self.log.info(f"switch - {self.t2-self.t1}")

                        self.on_switching = False
                        print("\n\n========trigger switch!!=====")

                self.out.write(frame1)
                cv2.imshow("frame",frame1)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        except KeyboardInterrupt:
            self.close()

        self.close()




if __name__ == "__main__":
    from threading import Thread
    r = Recorder('input.mp4', 'concat_output.mp4', 'test_output.mp4', (960, 540))
    t=  Thread(target=r.run)
    t.start()
    

    time.sleep(5)
    r.trigger_switch()
    time.sleep(15)
    r.close()
    # t.join()