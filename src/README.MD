# 控制逻辑
1. 控制器只负责：开关容器（resource scheduling），建立gtp隧道（workload dispatching）

2. 容器的开关通过dnc的接口代理实现

3. gtp隧道的建立基于网元控制接口实现

4. 每个UE的请求都默认到192.168.1.252，即dnc节点去请求server的ip和端口，由dnc来负责返回

5. UE根据分配给的ip和端口请求响应的服务

   

# 需要注意的点

1. DN节点需要添加route命令

   `sudo ip r add 10.0.0.0/8 via 192.168.254`








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

