from pynput.keyboard import Key, Controller
import time

import logging
# current_milli_time = lambda: time.time() * 1000



# logging.basicConfig(
#     level=logging.INFO, 
#     format= f'%(asctime)s - %(levelname)s - %(message)s', #'%(asctime)s - %(levelname)s - %(message)s',
#     filename='node_log/switch.log',
#     filemode='a',##模式，有w和a，w就是写模式，每次都会重新写日志，覆盖之前的日志
#     )
# switch_log = logging.getLogger('switch_log')


def switch_window():

    keyboard = Controller()
    # ts1 = current_milli_time()
    with keyboard.pressed(Key.alt):
        keyboard.press(Key.tab)
        keyboard.release(Key.tab)
    # ts2 = current_milli_time()
    # switch_log.info(ts2-ts1)
