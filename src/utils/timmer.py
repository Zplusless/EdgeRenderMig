import time
import datetime
from tqdm import trange

current_milli_time = lambda: time.time() * 1000  #lambda: int(round(time.time() * 1000))


def hms():
    return datetime.datetime.fromtimestamp(time.time()).strftime("%H:%M:%S.%f")[:8]


def wait(t, msg=''):
    for i in trange(t*2, desc=f'{msg} wait {t}s', ncols=80):
        time.sleep(0.5)
    



if __name__ == "__main__":
    print(hms())
    wait(5)