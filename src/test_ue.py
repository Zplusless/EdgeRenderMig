from utils.call_cmd import cmd

command = f'cd /home/edge/gaminganywhere-master/bin && ./ga-client config/client.abs.conf rtsp://192.168.1.1:8554/desktop'
res, t = cmd(command, True)

print(t)
print(res)

