import time
import datetime

current_milli_time = lambda: time.time() * 1000  #lambda: int(round(time.time() * 1000))


def hms():
    return datetime.datetime.fromtimestamp(time.time()).strftime("%H:%M:%S.%f")[:8]



if __name__ == "__main__":
    print(hms())