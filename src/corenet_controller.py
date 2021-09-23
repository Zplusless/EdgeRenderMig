#!/usr/bin/python
# -*- coding: UTF-8 -*-

import requests as r
import time

BASE_IP = 'http://{}:5000/'

class Tunnel(object):
    def __init__(self, ue_id, dn_cluster_id, tunnel_id, start_time = None):
        self.ue = ue_id
        self.dn_cluster_id = dn_cluster_id
        self.start_time = start_time
        self.tunnel_id = tunnel_id

class Scheduller(object):
    def __init__(self):
        self.working_tunnel={} # {tunnel_id: Tunnel(ue_id, dn_cluster_id, tunnel_id)}
        self.ue_has_tunnel = {}  # {ueid:tunnel_id}
        self.history_tunnel = {} # 暂时没用到
        self.next_tunnel_id = 1 # 用于tunnel_id计数

        # 在请求服务的ue
        self.working_ue = set()  # 正在请求服务的ue_id的集合

        # 启动的container
        self.working_container = {} # 正在工作的container的id集合


    def check_waiting_ue(self, ue_id, ueip):
        tunnel_id = self.ue_has_tunnel[ue_id]
        tunnel:Tunnel = self.working_tunnel[tunnel_id]
        dn_cluster_id = tunnel.dn_cluster_id
        url = f'http://172.12.{dn_cluster_id}.254:8000/port/check_release/'
        data = {'ueip':ueip}
        res = r.post(url, data = data, timeout=3)
        if res.text == 'True':
            return True
        else:
            return False


    def reset(self):
        for ue in self.working_ue:
            self.del_ue(ue)
        
        for tunnel in self.working_tunnel.copy().keys():
            self.del_tunnel(tunnel)
        
        for key, container_id in self.working_container.items():
            self.remove_container(key[0], key[1], container_id)

        self.working_tunnel={}
        self.ue_has_tunnel = {}  # 建立隧道的ue
        self.history_tunnel = {}
        self.next_tunnel_id = 1

        # 在请求服务的ue
        self.working_ue = set()

        # 已经下达del命令但还没有得到dnc确认的ue
        self.waiting_del_ue = set()

        # 启动的container
        self.working_container = {}


    def get_node_ips(self, ue_id, dn_cluster_id):
        
        id_ran = ue_id//1000%1000
        # id_ue = ue_id%1000
        current_cluster = ue_id//1000000
        ran_ip = '172.12.{}.{}'.format(current_cluster, id_ran)
        if not dn_cluster_id:    
            return ran_ip
        else:
            iupf_ip = '172.12.{}.253'.format(current_cluster)
            aupf_ip = '172.12.{}.254'.format(dn_cluster_id)
            return ran_ip, iupf_ip, aupf_ip

    def get_ran_ip(self, ue_id):
        return self.get_node_ips(ue_id, dn_cluster_id=None)

    def list_tunnel(self):
        print('\n************Working Tunnels**********')
        for id, tunnel in self.working_tunnel.items():
            print('No.{}--->from {} to DN_{}'.format(id, tunnel.ue, tunnel.dn_cluster_id))
        print('*************end*********************\n')

    def add_tunnel(self, ue, dn_cluster_id):
        
        if isinstance(ue, str):
            ue_id = int(ue.replace('ue', ''))
        else:
            ue_id = ue

        if ue_id in self.ue_has_tunnel.keys():
            print('ue_{} is already working, please add another ue'.format(ue_id))
            return -1

        ips = self.get_node_ips(ue_id, dn_cluster_id)

        for ip in ips:
            command = BASE_IP.format(ip)+'add_tunnel/{}/{}/{}/'.format(ue, dn_cluster_id, self.next_tunnel_id)
            ans = r.get(command, timeout=5)
            if ans.status_code == 200:
                print(ans.text)
            else:
                print('=========ERROR==========\n{}'.format(ans.text))

        tunnel = Tunnel(ue_id, dn_cluster_id, self.next_tunnel_id)
        self.working_tunnel[self.next_tunnel_id] = tunnel #{'ue':ue, 'dn_cluster_id':dn_cluster_id, 'tunnel':tunnel}
        self.ue_has_tunnel[ue_id] = self.next_tunnel_id
        
        self.next_tunnel_id += 1
        return self.next_tunnel_id - 1

    def del_tunnel(self, tunnel_id):
        """
        删除隧道,并返回删除的信息

        Args:
            tunnel_id (int): 隧道id

        Returns:
            int: ue_id
        """

        tunnel_id = int(tunnel_id)

        if tunnel_id not in self.working_tunnel.keys():
            print('{} is not a working tunnel, please add another ue'.format(tunnel_id))
            return -1

        ue_id = self.working_tunnel[tunnel_id].ue
        dn_cluster_id = self.working_tunnel[tunnel_id].dn_cluster_id
        ips = self.get_node_ips(ue_id, dn_cluster_id)

        for ip in ips:
            command = BASE_IP.format(ip)+'del_tunnel/{}/'.format(tunnel_id)
            ans = r.get(command,timeout=5)
            if ans.status_code == 200:
                print(ans.text)
            else:
                print('=========ERROR==========\n{}'.format(ans.text))
                return -1

        # todo 增加到self.history_tunnel
        del self.working_tunnel[tunnel_id] 
        del self.ue_has_tunnel[ue_id]

        print(f'UE {ue_id}: Tunnel Deleted \n')
        # 返回刚刚删除的tunnel对应ue的id
        return ue_id
    
    def add_ue(self, ue, log_name = None, tl=None):
        """
        启动UE并开始请求服务

        Args:
            ue (int): ue id
            log_name (str, optional): ue用于记录从发送服务请求到接受服务请求的四个时间戳的log文件名. Defaults to 'test'+time.time().
            tl (int, optional): ue发送服务的时间上限. Defaults to None.

        Returns:
            [type]: [description]
        """
        if isinstance(ue, str):
            ue_id = int(ue.replace('ue', ''))
        else:
            ue_id = ue

        if not log_name:
            # log_name = 'test'+ str(time.time())
            log_name = '{}_{}'.format(ue, int(time.time()))

        if ue_id not in self.ue_has_tunnel.keys():
            print('There is no gtp-u tunnel for ue_{}, please select another ue'.format(ue_id))
            return -1

        ran_ip = self.get_ran_ip(ue_id)
        if tl:
            command = BASE_IP.format(ran_ip)+'add_ue/{}/{}/{}/'.format(ue,log_name,tl)
        else:
            command = BASE_IP.format(ran_ip)+'add_ue/{}/{}/'.format(ue, log_name)
        ans = r.get(command,timeout=5)
        if ans.status_code == 200:
            print(ans.text)
            self.working_ue.add(ue_id)

            return ue_id
        else:
            print('=========ERROR==========\n{}'.format(ans.text))
            # 多半是由于ue向dnc申请port失败
            raise Exception('UE not start properly')


    def del_ue(self, ue):
        if isinstance(ue, str):
            ue_id = int(ue.replace('ue', ''))
        else:
            ue_id = ue

        if ue_id not in self.ue_has_tunnel.keys():
            print('There is no gtp-u tunnel for ue_{}, please select another ue'.format(ue_id))
            return -1

        ran_ip = self.get_ran_ip(ue_id)
        command = BASE_IP.format(ran_ip)+'del_ue/{}/'.format(ue)
        ans = r.get(command,timeout=5)
        if ans.status_code == 200:
            print(f'UE-{ue_id} stopped')
            if int(ans.text) == 0:
                self.working_ue.remove(ue_id)

                return 0 # 表示一切正常
            else:
                # 表示是一个broken pipe
                return -1
        else:
            print('=========ERROR==========\n{}'.format(ans.text))
            raise Exception('UE delete failed')



    def add_container(self, srv_id, dn_cluster_id):
        aupf_ip = '172.12.{}.254'.format(dn_cluster_id)
        command = "http://{}:8000/container/add/{}".format(aupf_ip, srv_id)
        res = r.get(command,timeout=10)
        if res.status_code == 200:
            data = res.json()
            container_id = data['container_id']

            if container_id > 0:
                
                print(f'Container-{container_id} added')
                
                if (srv_id, dn_cluster_id) not in self.working_container:
                    self.working_container[(srv_id, dn_cluster_id)] = set([container_id])
                else:
                    self.working_container[(srv_id, dn_cluster_id)].add(container_id)

                return container_id
            else:  # container占满了，报 core 不够的error
                return container_id # -1，表示爆仓错误

        # bug #! 正常情况下，这里的else不会被执行
        else:
            print(f'srv-{srv_id} @ cluster-{dn_cluster_id} has no more idle cpu cores, illegal operation')
            print('=========ERROR==========\n{}'.format(res.text))
            raise Exception('container not start properly')

    # 发出del信号，如果container有用户，则在用户退出后自动删除
    def del_container(self, srv_id, dn_cluster_id):
        """
        尝试删除container

        Args:
            srv_id (int): 服务类型
            dn_cluster_id (int): 操作的节点


        Returns:
            int:  删除成功返回container_id， 如果有正在使用的，就返回0，标记到待删除的队列
        """
        aupf_ip = '172.12.{}.254'.format(dn_cluster_id)
        command = "http://{}:8000/container/del/{}".format(aupf_ip, srv_id)
        res = r.get(command,timeout=5)
        if res.status_code == 200:
            data = res.json()
            container_id = data['container_id']
            

            if container_id > 0:  # 有container id说明删除成功，否则为None，表示有负载占用，标记但未删除
                print(f'Container-{container_id} deleted')
                if container_id in self.working_container[(srv_id, dn_cluster_id)]:
                    self.working_container[(srv_id, dn_cluster_id)].remove(container_id)
                    if len(self.working_container[(srv_id, dn_cluster_id)]) == 0:
                        del self.working_container[(srv_id, dn_cluster_id)]  # 在这个节点已经没有这个服务的container了
                
                    return int(container_id) #删除
                    # else:
                    #     return 0  # 标记但未删除
                else:
                    return -1 # 删除的节点没有启动srv-id对应的容器
                    # raise Exception("try to del a container not recorded")
            elif container_id ==0: # container还有ue连接，暂时不删除
                print(f'Cluster-{dn_cluster_id} DELETE FAILED: all container are working, waiting user disconnect')
                return 0 # 标记但未删除
            else:
                print(f'srv-{srv_id} @ cluster-{dn_cluster_id} has no working container, illegal operation')
                return -1 # 删除的节点没有启动srv-id对应的容器

        else:
            print('=========ERROR==========\n{}'.format(res.text))
            raise Exception('Delete container failed')


    # 强行删除container
    def remove_container(self, srv_id, dn_cluster_id, container_id):
        aupf_ip = '172.12.{}.254'.format(dn_cluster_id)
        command = "http://{}:8000/container/force_del/{}".format(aupf_ip, container_id)
        res = r.get(command,timeout=5)
        if res.status_code == 200:
            data = res.json()
            container_id = data['container_id']

            if container_id:
                print(f'Container-{container_id} deleted')
                if container_id in self.working_container[(srv_id, dn_cluster_id)]:
                    self.working_container[(srv_id, dn_cluster_id)].remove(container_id)
                    del self.working_container[(srv_id, dn_cluster_id)]

                    return int(container_id)


                else:
                    raise Exception("container not exist")


        else:
            print('=========ERROR==========\n{}'.format(res.text))
            raise Exception('Delete container failed')



    def get_container_num(self, srv_id, dn_cluster_id):
        aupf_ip = '172.12.{}.254'.format(dn_cluster_id)
        command = "http://{}:8000/container/num/{}".format(aupf_ip, srv_id)
        res = r.get(command, timeout=5)
        if res.status_code == 200:
            print(f'container num of service {srv_id} @ cluster-{dn_cluster_id} ---> {res.text}')
            return int(res.text)
        else:
            print('=========ERROR==========\n{}'.format(res.text))


if __name__ == "__main__":
    s = Scheduller()
    while True:
        try:
            x = int(input('\nchoose operation:\n0--->list\n'+
                                            '1--->add tunnel\n'+
                                            '2--->del tunnel\n'+
                                            '3--->add ue & run\n'+
                                            '4--->add ue & run with time limit\n'+
                                            '5--->del ue\n'+
                                            '6--->add container\n'+
                                            '7--->try del container\n'+
                                            '8--->force remove container\n'+
                                            '9--->get container num\n'))
            if x ==0:
                s.list_tunnel()
            elif x ==1:
                a = str(input('ue:'))
                b = input('dn_cluster_id:')
                s.add_tunnel(a,b)
            elif x==2:
                a = input('tunnel_id to be deleted:')
                s.del_tunnel(a)
            elif x==3:
                a = str(input('select ue to run service:'))
                s.add_ue(a)  #log_name如果不显式给出，则为 "test+时间戳"
            elif x==4:
                a = str(input('select ue to run service:'))
                b = input('how many seconds will this ue run:')
                s.add_ue(a, tl=b) #log_name如果不显式给出，则为 "test+时间戳"
            elif x==5:
                a = str(input('select ue to stop:'))
                s.del_ue(a)
            elif x==6:
                a = int(input('service id: '))
                b = int(input('DN cluster id: '))
                s.add_container(a,b)
            elif x==7:
                a = int(input('service id: '))
                b = int(input('DN cluster id: '))
                s.del_container(a,b)
            elif x==8:
                a = int(input('service id: '))
                b = int(input('DN cluster id: '))
                c = int(input('container id: '))
                s.remove_container(a,b,c)
            elif x==9:
                a = int(input('service id: '))
                b = int(input('DN cluster id: '))
                s.get_container_num(a,b)
            else:
                print('Wrong input, please retry')
        except Exception as e:
            print('Wrong input, please retry')
            print(e)
