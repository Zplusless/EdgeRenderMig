# 实验步骤

1. 在Corenet节点利用env_setup里的脚本，配置miniEdgeCore

2. 在Edge服务器上配置[gaminganywhere](https://github.com/GamingAnywhere/gaminganywhere)

3. 在Edge服务器上也拉取本项目，并且`python start_dnc`

4. Edge服务器的的config.py文件需要修改以下项目

   ```python
   CLOUD_IP = '10.112.145.90' # game server的ip,跑游戏的云端server
   
5. Corenet节点修改一下参数
   # =============================================
   # 新装机必须修改的参数
   CLUSTER_INTF = 'enp1s0'      # 用于cluster通信的网卡,走gtp隧道
   DN_INTF_1 = 'enp5s0'           # 连接edge server 1的网卡
   DN_INTF_2 = 'enp3s0'           # 连接edge server 2的网卡
   HOST_IP = '192.168.50.135'  # mini5Gedge本机上网网卡的ip
   ```

   

5. 

