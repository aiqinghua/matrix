#!/usr/bin/python3

from curses.ascii import ACK
import os
import json
import dpkt
import ipaddress
import binascii
from scapy.all import DNS, DNSQR, DNSRR, IP, send, sniff, sr1, UDP, Ether, ICMP, ARP, DHCP, BOOTP
from read_config import read_config



SERVICE_HTTP = "http"
SERVICE_DNS = "dns"
SERVICE_FTP = "ftp"
SERVICE_TELNET = "telnet"
SERVICE_ICMP = "icmp"
SERVICE_ARP = "arp"
SERVICE_RARP = "rarp"
SERVICE_DHCP = "dhcp"
SERVICE_SYSLOG = "syslog"
SERVICE_SMTP = "smtp"
SERVICE_POP3 = "pop3"
SERVICE_IMAP = "imap"
SERVICE_TCP = "tcp"
SERVICE_UDP = "udp"

PROTOCOL_UDP = "udp"
PROTOCOL_TCP = "tcp"
PROTOCOL_ICMP = "icmp"

pcap_conf = read_config()
CONF_DIR = pcap_conf["pcap"]["CONF_DIR"]
PCAPS_DIR = pcap_conf["pcap"]["PCAPS_DIR"]

def pcap_generate_pcap_write_single(pcap_name, pkt):
    pcap_path = PCAPS_DIR + "/" + pcap_name
    write_f = open(pcap_path, "wb")
    pcap_writer = dpkt.pcap.Writer(write_f)
    pcap_writer.writepkt(pkt)
    write_f.close()


def pcap_generate_pcap_write_udp(pcap_name, pkts):
    pcap_path = PCAPS_DIR + "/" + pcap_name
    write_f = open(pcap_path, "wb")
    pcap_writer = dpkt.pcap.Writer(write_f)
    for pkt in pkts:
        pcap_writer.writepkt(pkt)
    write_f.close()


def pcap_generate_pcap_write_tcp(pcap_name, pkts):
    pcap_path = PCAPS_DIR + "/" + pcap_name
    write_f = open(pcap_path, "wb")
    pcap_writer = dpkt.pcap.Writer(write_f)
    for pkt in pkts:
        pcap_writer.writepkt(pkt)
    write_f.close()


def pcap_generate_pcap_eth_packet(src_mac, dst_mac, type, eth_data):
    #print("eth_data:", eth_data)
    #print("src_mac: ", src_mac, ", dst_mac: ", dst_mac)
    smac = src_mac.replace(":", "")
    dmac = dst_mac.replace(":", "")

    src_mac_byte = binascii.unhexlify(smac)
    dst_mac_byte = binascii.unhexlify(dmac)

    eth = dpkt.ethernet.Ethernet(
        src=src_mac_byte, dst=dst_mac_byte, type=type, data=eth_data).pack()
    return eth


def pcap_generate_pcap_ip_packet(src_mac, dst_mac, src_ip, dst_ip, proto, ip_data):
    src_ip_byte = ipaddress.ip_address(src_ip).packed
    dst_ip_byte = ipaddress.ip_address(dst_ip).packed

    eth_data = dpkt.ip.IP(src=src_ip_byte, dst=dst_ip_byte,
                          p=proto, data=ip_data).pack()
    #print("eth_data:", eth_data)
    #print("src_mac: ", src_mac, ", dst_mac: ", dst_mac)
    smac = src_mac.replace(":", "")
    dmac = dst_mac.replace(":", "")

    src_mac_byte = binascii.unhexlify(smac)
    dst_mac_byte = binascii.unhexlify(dmac)

    eth = dpkt.ethernet.Ethernet(
        src=src_mac_byte, dst=dst_mac_byte, data=eth_data).pack()
    return eth


def pcap_generate_pcap_udp_packet(src_mac, dst_mac, src_ip, dst_ip, src_port, dst_port, l7_data):
    ip_data = dpkt.udp.UDP(sport=src_port, dport=dst_port,
                           data=l7_data, ulen=len(l7_data) + 8).pack()
    return pcap_generate_pcap_ip_packet(src_mac, dst_mac, src_ip, dst_ip, 17, ip_data)


def pcap_generate_pcap_tcp_packet(pkts, src_mac, dst_mac, src_ip, dst_ip, src_port, dst_port, seq, ack, l7_data, flags=dpkt.tcp.TH_ACK):
    if l7_data == None:
        ip_data = dpkt.tcp.TCP(
            sport=src_port, dport=dst_port, seq=seq, ack=ack, flags=flags).pack()
    else:
        ip_data = dpkt.tcp.TCP(sport=src_port, dport=dst_port,
                               data=l7_data, seq=seq, ack=ack, flags=flags).pack()
    #print("tcp: len:  ", len(ip_data), ", data: ", ip_data)
    pkt = pcap_generate_pcap_ip_packet(
        src_mac, dst_mac, src_ip, dst_ip, 6, ip_data)
    pkts.append(pkt)


def pcap_generate_pcap_udp(config_json, req, res, pcap_name):
    pkts = []
    req_pkt = pcap_generate_pcap_udp_packet(config_json["orig_mac"], config_json["resp_mac"],
                                            config_json["sip"], config_json["dip"], config_json["sport"], config_json["dport"], req)
    pkts.append(req_pkt)
    res_pkt = pcap_generate_pcap_udp_packet(config_json["resp_mac"], config_json["orig_mac"],
                                            config_json["dip"], config_json["sip"], config_json["dport"], config_json["sport"], res)
    pkts.append(res_pkt)
    pcap_generate_pcap_write_udp(pcap_name, pkts)
    pass


def pcap_generate_pcap_tcp(config_json, req, res, pcap_name):
    smac = config_json["orig_mac"]
    dmac = config_json["resp_mac"]
    sip = config_json["sip"]
    dip = config_json["dip"]
    sport = config_json["sport"]
    dport = config_json["dport"],

    req_seq_next = 1
    res_seq_next = 1
    pkts = []
    # 三次握手
    # client SYN
    pcap_generate_pcap_tcp_packet(pkts, smac, dmac, sip, dip, sport,
                                  dport, req_seq_next, res_seq_next - 1, None, flags=dpkt.tcp.TH_SYN)
    req_seq_next += 1

    # server SYN/ACK
    pcap_generate_pcap_tcp_packet(pkts, dmac, smac, dip, sip, dport, sport,
                                  res_seq_next, req_seq_next - 1, None, flags=dpkt.tcp.TH_SYN + dpkt.tcp.TH_ACK)
    res_seq_next += 1

    # client ACK
    pcap_generate_pcap_tcp_packet(pkts, smac, dmac, sip, dip, sport,
                                  dport, req_seq_next, res_seq_next - 1, None, flags=dpkt.tcp.TH_ACK)

    # client pkt -> server ack -> server data -> client ack
    # client pkt
    pcap_generate_pcap_tcp_packet(pkts, smac, dmac, sip, dip, sport,
                                  dport, req_seq_next, res_seq_next - 1, req, flags=dpkt.tcp.TH_ACK)
    req_seq_next += len(req)

    # server ack
    pcap_generate_pcap_tcp_packet(pkts, dmac, smac, dip, sip, dport,
                                  sport, res_seq_next, req_seq_next - 1, None, flags=dpkt.tcp.TH_ACK)

    # server pkt
    pcap_generate_pcap_tcp_packet(pkts, dmac, smac, dip, sip, dport,
                                  sport, res_seq_next, req_seq_next - 1, res, flags=dpkt.tcp.TH_ACK)
    res_seq_next += len(res)

    # client ack
    pcap_generate_pcap_tcp_packet(pkts, smac, dmac, sip, dip, sport,
                                  dport, req_seq_next, res_seq_next - 1, None, flags=dpkt.tcp.TH_ACK)

    # 四次挥手
    # client fin
    pcap_generate_pcap_tcp_packet(pkts, smac, dmac, sip, dip, sport, dport,
                                  req_seq_next, res_seq_next - 1, None, flags=dpkt.tcp.TH_FIN + dpkt.tcp.TH_ACK)
    req_seq_next += 1
    # server ack
    pcap_generate_pcap_tcp_packet(pkts, dmac, smac, dip, sip, dport,
                                  sport, res_seq_next, req_seq_next - 1, None, flags=dpkt.tcp.TH_ACK)
    # server fin
    pcap_generate_pcap_tcp_packet(pkts, dmac, smac, dip, sip, dport, sport,
                                  res_seq_next, req_seq_next - 1, None, flags=dpkt.tcp.TH_FIN + dpkt.tcp.TH_ACK)
    res_seq_next += 1
    # client ack
    pcap_generate_pcap_tcp_packet(pkts, smac, dmac, sip, dip, sport,
                                  dport, req_seq_next, res_seq_next - 1, None, flags=dpkt.tcp.TH_ACK)

    pcap_generate_pcap_write_tcp(pcap_name, pkts)
    pass


def pcap_generate_pcap_one_http(config_json, pcap_name):
    req = dpkt.http.Request()
    req.method = config_json["method"]
    req.uri = config_json["uri"]
    req.version = "1.1"

    for i in range(len(config_json["request_header_names"])):
        key = config_json["request_header_names"][i]
        value = config_json["request_header_values"][i]
        req.headers[key] = value
    req.body = bytes(config_json["request_body"], "ascii")

    # s = b"""HTTP/1.1 200 OK\r\nCache-control: no-cache\r\nPragma: no-cache\r\nContent-Type: text/javascript; charset=utf-8\r\nContent-Encoding: gzip\r\nTransfer-Encoding: chunked\r\nSet-Cookie: S=gmail=agg:gmail_yj=v2s:gmproxy=JkU; Domain=.google.com; Path=/\r\nServer: GFE/1.3\r\nDate: Mon, 12 Dec 2005 22:33:23 GMT\r\n\r\na\r\n\x1f\x8b\x08\x00\x00\x00\x00\x00\x00\x00\r\n152\r\nm\x91MO\xc4 \x10\x86\xef\xfe\n\x82\xc9\x9eXJK\xe9\xb6\xee\xc1\xe8\x1e6\x9e4\xf1\xe0a5\x86R\xda\x12Yh\x80\xba\xfa\xef\x85\xee\x1a/\xf21\x99\x0c\xef0<\xc3\x81\xa0\xc3\x01\xe6\x10\xc1<\xa7eYT5\xa1\xa4\xac\xe1\xdb\x15:\xa4\x9d\x0c\xfa5K\x00\xf6.\xaa\xeb\x86\xd5y\xcdHY\x954\x8e\xbc*h\x8c\x8e!L7Y\xe6\'\xeb\x82WZ\xcf>8\x1ed\x87\x851X\xd8c\xe6\xbc\x17Z\x89\x8f\xac \x84e\xde\n!]\x96\x17i\xb5\x02{{\xc2z0\x1e\x0f#7\x9cw3v\x992\x9d\xfc\xc2c8\xea[/EP\xd6\xbc\xce\x84\xd0\xce\xab\xf7`\'\x1f\xacS\xd2\xc7\xd2\xfb\x94\x02N\xdc\x04\x0f\xee\xba\x19X\x03TtW\xd7\xb4\xd9\x92\n\xbcX\xa7;\xb0\x9b\'\x10$?F\xfd\xf3CzPt\x8aU\xef\xb8\xc8\x8b-\x18\xed\xec<\xe0\x83\x85\x08!\xf8"[\xb0\xd3j\x82h\x93\xb8\xcf\xd8\x9b\xba\xda\xd0\x92\x14\xa4a\rc\reM\xfd\x87=X;h\xd9j;\xe0db\x17\xc2\x02\xbd\xb0F\xc2in#\xfb:\xb6\xc4x\x15\xd6\x9f\x8a\xaf\xcf)\x0b^\xbc\xe7i\x11\x80\x8b\x00D\x01\xd8/\x82x\xf6\xd8\xf7J(\xae/\x11p\x1f+\xc4p\t:\xfe\xfd\xdf\xa3Y\xfa\xae4\x7f\x00\xc5\xa5\x95\xa1\xe2\x01\x00\x00\r\n0\r\n\r\n"""
    res = dpkt.http.Response()
    res.status = config_json["status_code"]
    res.reason = config_json["status_msg"]
    res.version = "1.1"

    #print("header names: ", config_json["response_header_names"])
    #print("header values: ", config_json["response_header_values"])
    for i in range(len(config_json["response_header_names"])):
        key = config_json["response_header_names"][i]
        value = config_json["response_header_values"][i]
        res.headers[key] = value
    res.body = bytes(config_json["response_body"], "ascii")

    req_bytes = req.pack()
    res_bytes = res.pack()

    #print("http req bytes: ", req_bytes)

    pcap_generate_pcap_tcp(config_json, req_bytes, res_bytes, pcap_name)
    pass


def pcap_generate_pcap_one_dns(config_json, pcap_name):
    qtype = config_json["qtype_name"]
    qname = config_json["query"]
    answers = config_json["answers"]
    req = DNS(id=1000, rd=1, qd=DNSQR(qtype=qtype, qname=qname))
    res = DNS(id=1000, qd=DNSQR(qtype=qtype, qname=qname), aa=1,
              rd=0, qr=1, qdcount=1, ancount=1, nscount=0, arcount=0,
              ar=DNSRR(rrname=qname, type=qtype, rdata=answers))
    # print("res: ", res, ", len: ",  len(res))
    pcap_generate_pcap_udp(config_json, req, res, pcap_name)
    pass


def pcap_generate_pcap_one_ftp(config_json, pcap_name):
    req_command = config_json["command"]
    req_arg = config_json["arg"]
    res_code = str(config_json["code"])
    res_msg = config_json["msg"]
    req = req_command + " " + req_arg + "\r\n"
    res = res_code + " " + res_msg + "\r\n"
    pcap_generate_pcap_tcp(config_json, bytes(
        req, "ascii"), bytes(res, "ascii"), pcap_name)
    pass


def pcap_generate_pcap_one_smtp(config_json, pcap_name):
    raw_mail = config_json["raw_mail"]
    mail_from = config_json["mail_from"]
    rcpt_to = config_json["rcpt_to"][0]
    req = bytes("mail from: " + mail_from + "\r\n" +
                "rcpt to: " + rcpt_to + "\r\n" + raw_mail, "utf8")
    res = bytes("200 OK \r\n", "utf8")

    #print("smtp content: ", req)
    pcap_generate_pcap_tcp(config_json, req, res, pcap_name)
    pass


def pcap_generate_pcap_payload(config_json):
    req_payload_len = config_json["req_payload_len"]
    res_payload_len = config_json["res_payload_len"]
    req_payload_char = config_json["req_payload_char"]
    res_payload_char = config_json["res_payload_char"]

    req = ""
    for i in range(int(req_payload_len / len(req_payload_char)) + 1):
        req += req_payload_char
    req = bytes(req[0:req_payload_len], "utf8")

    res = ""
    for i in range(int(res_payload_len / len(res_payload_char)) + 1):
        res += res_payload_char
    res = bytes(res[0:res_payload_len], "utf8")
    return req, res


def pcap_generate_pcap_one_tcp(config_json, pcap_name):
    req, res = pcap_generate_pcap_payload(config_json)
    # print("tcp req: ", req)
    pcap_generate_pcap_tcp(config_json, req, res, pcap_name)
    pass


def pcap_generate_pcap_one_udp(config_json, pcap_name):
    req, res = pcap_generate_pcap_payload(config_json)
    # print("udp req: ", req)
    pcap_generate_pcap_udp(config_json, req, res, pcap_name)
    pass


def pcap_generate_pcap_one_syslog(config_json, pcap_name):
    # <333> message
    message = config_json["message"]
    level = config_json["level"]
    facility = config_json["facility"]
    facility_list = ["KERN", "USER", "MAIL", "DAEMON",
                     "AUTH", "SYSLOG", "LPR", "NEWS",
                     "UUCP", "CRON", "AUTHPRIV", "FTP",
                     "NTP", "LOGAUDIT", "LOGALERT",
                     "CRON", "LOCAL1", "LOCAL2",
                     "LOCAL3", "LOCAL4", "LOCAL5",
                     "LOCAL6", "LOCAL7"]
    level_list = ["EMERG",
                  "ALERT",
                  "CRIT",
                  "ERR",
                  "WARNING",
                  "NOTICE",
                  "INFO",
                  "DEBUG"]

    facility_index = 0
    level_index = 0
    for i in range(len(facility_list)):
        if facility_list[i] == facility:
            facility_index = i
    for i in range(len(level_list)):
        if level_list[i] == level:
            level_index = i

    priority = facility_index << 3 | level_index

    content = bytes("<" + str(priority) + ">" + message, "utf8")

    # print("syslog content: ", content)

    pkts = []
    pkts.append(pcap_generate_pcap_udp_packet(config_json["orig_mac"], config_json["resp_mac"],
                config_json["sip"], config_json["dip"], config_json["sport"], config_json["dport"], content))
    pcap_generate_pcap_write_udp(pcap_name, pkts)
    pass


def pcap_generate_pcap_one_telnet(config_json, pcap_name):
    content = config_json["content"]
    req = content
    res = content
    pcap_generate_pcap_tcp(config_json, bytes(
        req, "utf8"), bytes(res, "utf8"), pcap_name)
    pass


def pcap_generate_pcap_one_icmp(config_json, pcap_name):
    type = config_json["itype"]
    code = config_json["icode"]
    id = config_json["identifier"]
    seq = config_json["seq"]
    payload = config_json["payload"]

    smac = config_json["orig_mac"]
    dmac = config_json["resp_mac"]
    sip = config_json["sip"]
    dip = config_json["dip"]

    icmp_pkt = ICMP(type=type, code=code, id=id, seq=seq)
    pkt = pcap_generate_pcap_ip_packet(smac, dmac, sip, dip, 1, icmp_pkt)
    pcap_generate_pcap_write_single(pcap_name, pkt)
    pass


def pcap_generate_pcap_one_dhcp(config_json, pcap_name):
    assigned_ip = config_json["assigned_ip"]
    assigned_netmask = config_json["assigned_netmask"]
    assigned_router = config_json["assigned_router"]
    assigned_dns = config_json["assigned_dns"]
    lease_time = config_json["lease_time"]
    trans_id = int("0x" + config_json["trans_id"], base=16)

    pkts = []
    bootp = BOOTP(op=2, xid=trans_id, yiaddr=assigned_ip,
                  chaddr=config_json["orig_mac"])
    #dhcp = DHCP(options=[('message-type', 'offer'), ('subnet_mask', assigned_netmask), ('lease_time', lease_time), ('domain', assigned_dns), ('router', assigned_router), ('name_server', assigned_dns), 'end'])
    dhcp = DHCP(options=[('message-type', 'offer'), ('subnet_mask', assigned_netmask),
                ('lease_time', lease_time), ('router', assigned_router), ('domain', assigned_dns[0]), 'end'])
    dhcp_pkt = bootp/dhcp
    # print("dhcp_pkt: ", dhcp_pkt)
    pkt = pcap_generate_pcap_udp_packet(config_json["orig_mac"], config_json["resp_mac"],
                                        config_json["sip"], config_json["dip"], config_json["sport"], config_json["dport"], dhcp_pkt)
    pkts.append(pkt)

    pcap_generate_pcap_write_udp(pcap_name, pkts)
    pass


def pcap_generate_pcap_one_rarp(config_json, pcap_name):
    htype = config_json["hardware_type"]
    ptype = config_json["protocol_type"]
    op = config_json["opcode"]
    psrc = config_json["spa"]
    pdst = config_json["tpa"]
    hwsrc = config_json["sha"]
    hwdst = config_json["tha"]

    arp_pkt = ARP(hwtype=htype, ptype=ptype, op=op, psrc=psrc,
                  pdst=pdst, hwsrc=hwsrc, hwdst=hwdst)
    eth_pkt = pcap_generate_pcap_eth_packet(
        config_json["orig_mac"], config_json["resp_mac"], dpkt.ethernet.ETH_TYPE_REVARP, arp_pkt)
    pcap_generate_pcap_write_single(pcap_name, eth_pkt)
    pass


def pcap_generate_pcap_one_arp(config_json, pcap_name):
    htype = config_json["hardware_type"]
    ptype = config_json["protocol_type"]
    op = config_json["opcode"]
    psrc = config_json["spa"]
    pdst = config_json["tpa"]
    hwsrc = config_json["sha"]
    hwdst = config_json["tha"]

    arp_pkt = ARP(hwtype=htype, ptype=ptype, op=op, psrc=psrc,
                  pdst=pdst, hwsrc=hwsrc, hwdst=hwdst)
    eth_pkt = pcap_generate_pcap_eth_packet(
        config_json["orig_mac"], config_json["resp_mac"], dpkt.ethernet.ETH_TYPE_ARP, arp_pkt)
    pcap_generate_pcap_write_single(pcap_name, eth_pkt)
    pass


def pcap_generate_pcap_one(config_str, pcap_name):
    #print ("config str: ", config_str)
    config_json = json.loads(config_str)
    if "service" not in config_json:
        print("no service in config", config_str)
    if "protocol" not in config_json:
        print("no protocol in config", config_str)

    service = config_json["service"]
    if service == SERVICE_HTTP:
        pcap_generate_pcap_one_http(config_json, pcap_name)
    elif service == SERVICE_DNS:
        pcap_generate_pcap_one_dns(config_json, pcap_name)
    elif service == SERVICE_FTP:
        pcap_generate_pcap_one_ftp(config_json, pcap_name)
    elif service == SERVICE_TELNET:
        pcap_generate_pcap_one_telnet(config_json, pcap_name)
    elif service == SERVICE_ICMP:
        pcap_generate_pcap_one_icmp(config_json, pcap_name)
    elif service == SERVICE_ARP:
        pcap_generate_pcap_one_arp(config_json, pcap_name)
    elif service == SERVICE_RARP:
        pcap_generate_pcap_one_rarp(config_json, pcap_name)
    elif service == SERVICE_DHCP:
        pcap_generate_pcap_one_dhcp(config_json, pcap_name)
    elif service == SERVICE_SYSLOG:
        pcap_generate_pcap_one_syslog(config_json, pcap_name)
    elif service == SERVICE_SMTP:
        pcap_generate_pcap_one_smtp(config_json, pcap_name)
    elif service == SERVICE_POP3:
        pcap_generate_pcap_one_smtp(config_json, pcap_name)
    elif service == SERVICE_IMAP:
        pcap_generate_pcap_one_smtp(config_json, pcap_name)
    elif service == SERVICE_TCP:
        pcap_generate_pcap_one_tcp(config_json, pcap_name)
    elif service == SERVICE_UDP:
        pcap_generate_pcap_one_udp(config_json, pcap_name)


def pcap_generate_pcap(config, pcap_name):
    config_path = CONF_DIR + "/" + config
    for line in open(config_path, "rb"):
        #print("line : ", line)
        pcap_generate_pcap_one(line, pcap_name)


def main():
    if not os.path.exists(PCAPS_DIR):
        os.mkdir(PCAPS_DIR)

    config_list = os.listdir(CONF_DIR)
    for config in config_list:
        pcap_name = os.path.basename(config) + ".pcap"
        if os.path.exists(pcap_name):
            os.unlink(pcap_name)
        pcap_generate_pcap(config, pcap_name)


if __name__ == '__main__':
    main()
