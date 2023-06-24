from pynput.keyboard import Key, Controller
import time

import logging
current_milli_time = lambda: time.time() * 1000



# logging.basicConfig(
#     level=logging.INFO, 
#     format= f'%(asctime)s - %(levelname)s - %(message)s', #'%(asctime)s - %(levelname)s - %(message)s',
#     filename='node_log/switch.log',
#     filemode='a',##模式，有w和a，w就是写模式，每次都会重新写日志，覆盖之前的日志
#     )
# switch_log = logging.getLogger('switch_log')


def switch_window():
    '''
    用于模拟窗口切换，默认用于minecraft的迁移切换
    '''

    keyboard = Controller()
    # ts1 = current_milli_time()
    with keyboard.pressed(Key.alt):
        keyboard.press(Key.tab)
        keyboard.release(Key.tab)
    # ts2 = current_milli_time()
    # switch_log.info(ts2-ts1)


def minetest_f2():
    '''
    minetest的迁移切换，包含视频流的切换
    '''
    keyboard = Controller()
    keyboard.press(Key.f2)
    keyboard.release(Key.f2)

def press_esc():
    '''
    minetest中用于按esc跳出菜单栏
    '''
    keyboard = Controller()
    keyboard.press(Key.esc)
    keyboard.release(Key.esc)



if __name__ == "__main__":
    
    t1 = current_milli_time()

    # 按F2 切换控制权限
    # sw.minetest_f2()

    # switch 窗口
    switch_window()
    

    t2=current_milli_time()

    print(t2-t1)