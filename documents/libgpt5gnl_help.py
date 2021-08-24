
if __name__ == "__main__":

    name = "gtp5g-tunnel"

    print("%s <add|mod> <pdr|far> <gtp device> <id> [<options,...>]\n"% name);
    print("%s <del|get> <pdr|far> <gtp device> <id>\n"% name);
    print("%s list <pdr|far>\n\n"% name);

    print("PDR OPTIONS\n");
    print("\t--pcd <precedence>\n");
    print("\t--hdr-rm <outer-header-removal>\n");
    print("\t--far-id <esixted-far-id>\n");
    print("\t--ue-ipv4 <pdi-ue-ipv4>\n");
    print("\t--f-teid <i-teid> <local-gtpu-ipv4>\n");
    print("\t--sdf-desp <description-string>\n");
    print("\t\tex: --sdf-desp 'permit out ip from 192.168.0.1 22,53,73 to 127.0.0.1/24'\n");
    print("\t--sdf-tos-traff-cls <tos-traffic-class>\n");
    print("\t--sdf-scy-param-idx <security-param-idx>\n");
    print("\t--sdf-flow-label <flow-label>\n");
    print("\t--sdf-id <id>\n");
    print("\n");

    print("OTHER OPTION BUT NOT IEs");
    print("\t--gtpu-src-ip <gtpu-src-ip>\n");
    print("\t\tUsed for set the source IP in GTP forwarding packet");
    print("\t--buffer-usock-path <AF_UNIX-sock-path>\n");
    print("\t\tUsed for sending packet which should be buffered to user space");
    print("\n");

    print("FAR OPTIONS\n");
    print("\t--action <apply-action>\n");
    print("\t--hdr-creation <description> <o-teid> <peer-ipv4> <peer-port>\n");