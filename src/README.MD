# 需要修改配置的点
1. config 下的  
```python
CLOUD_IP 
CLUSTER_INTF
DN_INTF_1
DN_INTF_2
```
2. 修改Edge/start_game.sh使里面的路径与conf文件匹配

# Edge配置
1. 安装gaming-anywhere
2. 在Edge端拉取本项目，在src路径下启动 `start_dnc.py`
3. 将Edge/server.snake.conf拷贝到GA路径下的`bin/config`目录下，作为启动GA的配置文件（已经在Edge/start_game.sh中）


   

# 需要注意的点

1. DN节点需要添加route命令

   `sudo ip r add 10.0.0.0/8 via 192.168.254`

   或在netplan的配置文件中：
   ```bash
      ens38:
            addresses:
               - 192.168.1.1/24
            dhcp4: false
            routes:
               - to: 100.0.0.0/8
               via: 192.168.1.254
   ```







# 存在算法的点
1. 中心控制节点
   1. 什么时间操作容器
   2. 选择在什么地点开关容器
   3. 每个用户建立gtp隧道的a-upf选择在哪里，即服务卸载到哪里
2. dnc节点-->port分配
   1. 端口过程包含了edge内部的负载均衡

# 端口设置

UE--->6600

NF--->5000

dnc--->8000

dn-ffmpeg-server--->5600



server端

8xyz--->x为srv_id, y为containeri_d, z为port的动态分配id



# ID映射规则

server id--->a000

srv id --->b, b属于[1,9]

container_id--->abc0, c为congtainer的动态分配号，范围0~9

port--->8bcd, b c对应上面的，d为动态分配，d=0为ue的控制交互端口，d=1~9为业务端口.  注意不论是在哪个server上，port最左边都是8。

