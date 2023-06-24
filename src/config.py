#!/usr/bin/python
# -*- coding: UTF-8 -*-


# 是否使用gunicorn，使用ctrl_srv_mig_ue.py控制时，gunicorn报错
IN_DEPLOYMENT = False # True为实际部署，用gunicorn运行；False使用flask自带的webserver


# 是否测量edge测的cpu和带宽
IN_MEASUREMENT = False

# 是否测试in app 时延
IN_APP_LATENCY = False
IN_APP_LATENCY_INTERVAL = 0.5 # 秒

# =============================================
# Game配置
SSIM_THRESHOLD = 0.85
# 经过多少帧完成video record过程中视频帧加权平均的切换
TRANSITION_STEPS = 12 #! 最小为1，取1的时候不加平滑



# =============================================
# Game配置
CLOUD_IP = '192.168.5.63'  # server ip
GAME_ACCOUNT = 'test'  # for game login
GAME_PASSWORD = 'test' # for game login

EDGE_NODE_IP_1 = '192.168.1.1'
EDGE_NODE_IP_2 = '192.168.1.2'

RTSP_STREAM_1 = f'rtsp://{EDGE_NODE_IP_1}:8554/desktop'
RTSP_STREAM_2 = f'rtsp://{EDGE_NODE_IP_2}:8554/desktop'


# =============================================
RAN_NUM = 2 # topo中有多少个基站


# =============================================
# 新装机必须修改的参数
CLUSTER_INTF = 'enp0s31f6'      # 用于cluster通信的网卡,走gtp隧道
DN_INTF_1 = 'enp4s0f0'           # 用于5G接入DN的网卡
DN_INTF_2 = 'enp4s0f1'           # 用于5G接入DN的网卡
HOST_IP = '192.168.5.82'  # mini5Gedge本机上网网卡的ip
CLUSTER_ID = 3              # cluster id, 不同cluster不能重复


UE_SRV_ID = 3 # *从dnc的ctl_config.py中找到对应服务
UE_SRV_TIME = 999 # UE默认最大服务时间
UE_SRV_INTERVAL = 0.5

FRAME_SLOT = 10 # 每多少帧统计一次时延


# =============================================
# UE记录时延log的基础路径
BASE_LOG_PATH = './ue_log/'

# UE上传视频文件的路径
UE_UPLOAD_FILE = './UE/example.mp4'


# =============================================
# 连接时延参数, 带宽参数
# 此处的时延为单向时延，等于RTT的一半
# 时延参数太小的时候会不准
DELAY_UE_RAN = '1ms'
BW_UE_RAN = 1000  # 200 # Mbps
LOSS_UE_RAN = None # 0.01%

DELAY_NF = '1ms'
BW_NF = 1000 #Mbps
LOSS_NF = None

# INTER_CLUSTER 专指 s1与s0之间的时延 
DELAY_INTER_CLUSTER = '3ms'
BW_INTER_CLUSTER = 1000 # Mbps
LOSS_INTER_CLUSTER = None




# =============================================
# network config
UE_CIDR = "100.0.0.0/8"
DN_CIDR = "192.168.1.0/24"


# 10.X.Y.Z--->X=CLUSTER ID  Y=RAN ID  Z=UE ID PER RAN
BASE_UE_IP="100.{}.{}.{}/24" 
BASE_RAN_UE_IP="100.{}".format(CLUSTER_ID)+".{}.254/24"

# 172.12.X.Y--->X=CLUSTER ID    Y=RAN ID
BASE_RAN_IUPF_IP = "172.12.{}.{}/16"
BASE_IUPF_WAN_IP = "172.12.{}.253/16"
BASE_AUPF_WAN_IP = "172.12.{}.254/16"


# 192.168.1.K--->   K=254, for AUPF, 
#                   K=252, for dn controller
#                   K=1, for load balance gateway
#                   K=1~250, for server in DN
BASE_AUPF_DN_IP = "192.168.1.254/24"

#fixme 部署时修改
DN_CONTROLLER_IP = "192.168.1.254/24" #"127.0.0.1/24"# 
DN_CONTROLLER_PORT = 8000


