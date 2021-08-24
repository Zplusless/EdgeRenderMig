# 命令分解

```bash
sudo gtp5g-tunnel add far   gtp5gtest       1           --action 2
#                            gtplink      far-id          action参数，取值貌似1 2 3，目前就2能用

sudo gtp5g-tunnel add far gtp5gtest 2 --action 2   --hdr-creation    0     89   ${IUPF_IP_OUT}      2152
#					            gtp头信息        描述   TEID + 下一跳ip          gtp的端口
sudo gtp5g-tunnel add pdr gtp5gtest   1     --pcd 1  --hdr-rm 0   --ue-ipv4 ${UE_IP}    --f-teid 88 ${AUPF_IP}  --far-id 1
#				    pdr-id   优先级    去除包头       ue-ip                     TEID + 本地gtp接收ip     采用哪个far
sudo gtp5g-tunnel add pdr gtp5gtest 2 --pcd 2 --ue-ipv4 ${UE_IP} --far-id 2 --gtpu-src-ip=${AUPF_IP}
#									    记录从自己哪个ip发出去的
```




# 用法说明
```bash
gtp5n-tunnel <add|mod> <pdr|far> <gtp device> <id> [<options,...>]

gtp5n-tunnel <del|get> <pdr|far> <gtp device> <id>

gtp5n-tunnel list <pdr|far|qer>


PDR OPTIONS

	--pcd <precedence>

	--hdr-rm <outer-header-removal>

	--far-id <existed-far-id>

	--ue-ipv4 <pdi-ue-ipv4>

	--f-teid <i-teid> <local-gtpu-ipv4>

	--sdf-desp <description-string>

		ex: --sdf-desp 'permit out ip from 192.168.0.1 22,53,73 to 127.0.0.1/24'

	--sdf-tos-traff-cls <tos-traffic-class>

	--sdf-scy-param-idx <security-param-idx>

	--sdf-flow-label <flow-label>

	--sdf-id <id>

	--qer-id <id>


OTHER OPTION BUT NOT IEs
	--gtpu-src-ip <gtpu-src-ip>

		Used for set the source IP in GTP forwarding packet

	--buffer-usock-path <AF_UNIX-sock-path>

		Used for sending packet which should be buffered to user space



FAR OPTIONS

	--action <apply-action>

	--hdr-creation <description> <o-teid> <peer-ipv4> <peer-port>

	--fwd-policy <mark set in iptable>

		Set mark into packet and exec Linux routing>

QER OPTIONS

	--qer-id <qer-id>

	--qfi-id <qfi-id> [Value range: {0..63}]

	--rqi-d <rqi> [Value range: {0=not triggered, 1=triggered}]

	--ppp <ppp> [Value range: {0=not present, 1=present}]

	--ppi <ppi> [Value range: {0..7}]
```



## 打印配置

`gtp5g-tunnel list far`

```yaml
[FAR No.2 Info]
  - Apply Action: 2
  [Forwarding Parameter Info]
    [Outer Header Creation Info]
      - Description: 0
      - Out Teid: 87
      - RAN IPv4: 10.12.1.110
      - Port: 2152
  - Related PDR ID: 2 (Not a real IE)
[FAR No.1 Info]
  - Apply Action: 2
  [Forwarding Parameter Info]
    [Outer Header Creation Info]
      - Description: 0
      - Out Teid: 88
      - RAN IPv4: 10.12.0.102
      - Port: 2152
  - Related PDR ID: 1 (Not a real IE)

```

`gtp5g-tunnel list pdr`

```yaml
[PDR No.2 Info]
  - Precedence: 2
  - Outer Header Removal: 0
  [PDI Info]
    [Local F-Teid Info]
      - In Teid: 89
      - UPF IPv4: 10.12.0.101
  - FAR ID: 2
  - GTP-U IPv4: 10.12.1.101 (For routing)
[PDR No.1 Info]
  - Precedence: 1
  - Outer Header Removal: 0
  [PDI Info]
    - UE IPv4: 192.168.0.111
    [Local F-Teid Info]
      - In Teid: 78
      - UPF IPv4: 10.12.1.101
  - FAR ID: 1
  - GTP-U IPv4: 10.12.0.101 (For routing)
```

