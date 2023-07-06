# import os 
import time
from subprocess import Popen, PIPE


current_milli_time = lambda: int(round(time.time() * 1000))

def cmd(cmd, record_time:bool, logfile:str=None):
    """
    call system shell

    Args:
        cmd (str): shell command
        record_time (bool): wheter wait the process of shell command and record time used 

    Raises:
        Exception: invalid cmd

    Returns:
        ans: stdout of shell command if record_time=True, else return pid
        t: miliseconds used to execute the cmd 
    """
    
    if not isinstance(cmd, str):
        raise Exception('invalid cmd, it should be a str')
    t1 = time.time()*1000
    # ans = os.popen(cmd, buffering=-1).read()
    if logfile:
        target = open(logfile, 'w')
        
    elif record_time:
        target = PIPE
    else:
        target = None
    print(f'CMD:  {cmd}')
    proc = Popen(cmd, bufsize=-1, stdout=target, stderr=target, shell=True)


    if record_time:
        ans,_ = proc.communicate()
        t2 = time.time()*1000
        if logfile:
            target.close()
        return proc.pid, t2-t1, ans
    else:
        if logfile:
            target.close()
        return proc.pid, -1, ''


if __name__ == '__main__':
    pid, t, _ = cmd('sleep 4 && ls', record_time=False, logfile='ue_log/test.txt')
    # ans, t = cmd('sleep 4 && ls', record_time=True)
    print(t)
    # Popen('ls', shell = True)