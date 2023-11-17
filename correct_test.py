#!/usr/bin/python3
from csv import field_size_limit
import os
import sys
import time
import requests
import json

# pcap generator会生成各个协议的pcap, 然后将pcap放到flow generatore能访问到的目录，开始打流
# 打流结束后, 读取接口数据，比对准确性
CONFIG_PATH = "correct.conf"
LOG_FILE_PATH = "/data/log_file"

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
SERVICE_MAIL = "mail"
SERVICE_POP3 = "pop3"
SERVICE_IMAP = "imap"
SERVICE_TCP = "tcp"
SERVICE_UDP = "udp"

config = {}
services = {"test":[]}
def get_service(schema_type):
    list = {
        0: "ipfix",
        1: "http",
        2: "dns",
        3: "ssl",
        4: "ftp",
        5: "telnet",
        6: "icmp",
        7: "mail",
        8: "mysql",
        9: "arp",
        10: "rarp",
        11: "dhcp",
        12: "socks",
        13: "snmp",
        14: "llmnr",
        15: "ldap",
        16: "syslog",
        17: "rdp",
        18: "dcerpc",
        19: "drda",
        20: "adb"
    }
    if schema_type in list:
        return list[schema_type]
    return None

def print_module(msg):
    print("\033[1;37;40m%s\033[0m" % msg)

def print_warn(msg):
    print("\033[0;35;40m%s\033[0m" % msg)


def print_error(msg):
    print("\033[0;31;40m%s\033[0m" %msg)

def generate_config_pcap(config):
    service = config["service"]
    if service not in services: 
        config[service] = []
    config[service].append(config)

def get_all_pcap_conf(pcap_path):
    config_list = os.listdir(pcap_path)
    for config in config_list:
        config_path = pcap_path + "/" + config
        for line in open(config_path, "rb"):
            j = json.loads(line)
            generate_config_pcap(j)

'''
配置格式:
{
    "protocol": 10000
}
'''
def get_config():
    # read from config file 
    f = open(CONFIG_PATH,"r")
    config = json.load(f)
    get_all_pcap_conf(config["pcap_path"])
    print("-------------------测试配置:--------------------")
    print("数据包路径: ", config["pcap_path"])
    print("协议日志数: ", config["protocol"])
    return config

'''
格式:
{
    "ts": 1653285819895048400,
    "brokers": [
        {
            "broker_name": "SSL://127.0.0.1:9091",
            "total_num": 129,
            "total_bytes": 140375,
            "succ_num": 82,
            "succ_bytes": 89161,
            "fail_num": 0,
            "fail_bytes": 0,
            "topic": [
                {
                    "topic_name": "session",
                    "total_num": 88,
                    "total_bytes": 96481,
                    "succ_num": 50,
                    "succ_bytes": 54908,
                    "fail_num": 0,
                    "fail_bytes": 0
                },
                {
                    "topic_name": "dns",
                    "total_num": 0,
                    "total_bytes": 0,
                    "succ_num": 0,
                    "succ_bytes": 0,
                    "fail_num": 0,
                    "fail_bytes": 0
                }
            ]
        }
    ]
}
'''
def get_kafka_data():
    url = "http://prsadmin:prsadmin2016@127.0.0.1:18082/kafka"
    r = requests.get(url)
    protocols = r.json()["brokers"][0]["topic"]
    return protocols

'''
单条日志:
{
    "topic_name": "dns",
    "total_num": 0,
    "total_bytes": 0,
    "succ_num": 0,
    "succ_bytes": 0,
    "fail_num": 0,
    "fail_bytes": 0
}
''' 
def correct_check_kafka(kafka_protocols, config):
    # compare
    has_fail = 0

    for protocol in kafka_protocols:
        name = protocol["topic_name"]
        if name in config:
            protocol_config = config["topic_name"]
        else:
            protocol_config = config["protocol"]

        if protocol["succ_num"] != protocol["total_num"]:
            print("检查 ", name, " 协议失败，配置条数为: ", protocol_config, ", 实际条数为: ", protocol["succ_num"])
            has_fail = 1
            continue
        if protocol["fail_num"] != 0:
            has_fail = 1
            print("检查 ", name, " 协议失败，配置条数为: ", protocol_config, ", 实际条数为: ", protocol["succ_num"])
            continue
        if protocol["succ_num"] != protocol_config:
            has_fail = 1
            print("检查 ", name, " 协议失败，配置条数为: ", protocol_config, ", 实际条数为: ", protocol["succ_num"])
            continue
        print("检查 ", name, " 协议成功，配置条数为: ", protocol_config, ", 实际条数为: ", protocol["succ_num"])

    if has_fail:
        ret = False
    else:
        ret = True

    return ret

def service_compare_common(config_json, real_data, fileds):
    for field in fileds:
        if config_json[field] != real_data[field]:
            return False
    return True

def service_compare_http(config_json, real_data):
    fields = ["method", "uri", "request_version", "request_header_names", "request_header_values", 
        "request_body", "request_version", "status_code", "status_msg", "response_headr_names",
        "response_header_values", "response_body", "response_body_truncated"]
    return service_compare_common(config_json, real_data, fields)

def service_compare_dns(config_json, real_data):
    fields = ["query", "qtype", "qtype_name", "rcode", "rcode_name", "answers", "answer_quries", "answer_types"]
    return service_compare_common(config_json, real_data, fields)

def service_compare_ftp(config_json, real_data):
    fields = ["user", "command", "arg", "code", "msg"]
    return service_compare_common(config_json, real_data, fields)

def service_compare_telnet(config_json, real_data):
    fields = ["content"]
    return service_compare_common(config_json, real_data, fields)

def service_compare_icmp(config_json, real_data):
    fields = ["itype", "icode", "identifier", "seq", "payload_len", "ttl", "payload"]
    return service_compare_common(config_json, real_data, fields)

def service_compare_arp(config_json, real_data):
    fields = ["opcode", "hardware_type", "protocol_type", "spa", "sha", "tpa", "tha"]
    return service_compare_common(config_json, real_data, fields)

def service_compare_rarp(config_json, real_data):
    fields = ["opcode", "hardware_type", "protocol_type", "spa", "sha", "tpa", "tha"]
    return service_compare_common(config_json, real_data, fields)

def service_compare_dhcp(config_json, real_data):
    fields = ["assigned_ip", "assigned_netmask", "assigned_router", "assigned_dns", "lease_time", "trans_id"]
    return service_compare_common(config_json, real_data, fields)

def service_compare_syslog(config_json, real_data):
    fields = ["facility", "level", "message"]
    return service_compare_common(config_json, real_data, fields)

def service_compare_mail(config_json, real_data):
    fields = ["raw_mail", "truncated", "mail_from","rcpt_to"]
    return service_compare_common(config_json, real_data, fields)

def service_compare(service, config_json, real_data):
    if service == SERVICE_HTTP:
        return service_compare_http(config_json, real_data)
    elif service == SERVICE_DNS:
        return service_compare_dns(config_json, real_data)
    elif service == SERVICE_FTP:
        return service_compare_ftp(config_json, real_data)
    elif service == SERVICE_TELNET:
        return service_compare_telnet(config_json, real_data)
    elif service == SERVICE_ICMP:
        return service_compare_icmp(config_json, real_data)
    elif service == SERVICE_ARP:
        return service_compare_arp(config_json, real_data)
    elif service == SERVICE_RARP:
        return service_compare_rarp(config_json, real_data)
    elif service == SERVICE_DHCP:
        return service_compare_dhcp(config_json, real_data)
    elif service == SERVICE_SYSLOG:
        return service_compare_syslog(config_json, real_data)
    elif service == SERVICE_MAIL:
        return service_compare_mail(config_json, real_data)
    pass

fail_cnt_service = []
succ_cnt_service = []

def result_compare_one(one_line_data):
    fail_cnt = 0
    succ_cnt = 0

    try:
        json_data = json.loads(one_line_data)
    except Exception:
        return 1, 0

    s_data = get_service(json_data["schema_type"])
    if s_data not in services:
        return 0,0

    for s in services[s_data]:
        # 这里没有办法 使用五元组，只能使用dport, sport. 确定一个配置
        if s["dport"] == json_data["dport"] and s["sport"] == json_data["sport"]:
            ret = service_compare(s_data, s, json_data)
            if ret == False:
                print("检测失败: 配置数据: ", s_data, ", 实际数据: ", s)
                fail_cnt += 1 
                fail_cnt_service[s_data] += 1
            else:
                succ_cnt_service[s_data] += 1
                succ_cnt += 1
            ## todo stats
    return fail_cnt, succ_cnt

def result_compare(log_file_path):
    log_file_list = os.listdir(log_file_path)
    total_fail_cnt = 0
    total_succ_cnt = 0
    print("--------------- 检测协议数据 --------------------- ")
    for log_file in log_file_list:
        if not log_file.startswith("69344"):
            continue
        config_path = log_file_path + "/" + log_file
        for line in open(config_path, "rb"):
            fail_cnt, succ_cnt = result_compare_one(line)
            total_fail_cnt += fail_cnt
            total_succ_cnt += succ_cnt
    print("---------------------------各协议字段比较---------------------------")
    print("总数: ", total_fail_cnt + total_succ_cnt, ", 成功数: ", total_succ_cnt, ", 失败数: ", total_fail_cnt)

    for k, v in succ_cnt_service:
        print("协议: ", k, ", 成功数为: ", v )
    for k, v in fail_cnt_service:
        print("协议: ", k, ", 失败数为: ", v )

def check_internal_stats_packet(total_packets):
    url = "http://prsadmin:prsadmin2016@127.0.0.1:18082/application"
    r = requests.get(url)
    # 收包数 hw ipackets, l2 ipackets, 各个协议的ipackets,

    hw = r.json()["hw"][0]
    l2 = r.json()["layer2"]
    l3 = r.json()["layer2"]
    l4 = r.json()["layer2"]
    l7 = r.json()["layer7"]

    l2_pkts = 0
    l3_pkts = 0
    l4_pkts = 0
    l7_pkts = 0

    for l in l2:
        l2_pkts += l["total_packets"]
    for l in l3:
        l3_pkts += l["total_packets"]
    for l in l4:
        l4_pkts += l["total_packets"]
    for l in l7:
        l7_pkts += l["total_packets"]

    print("--------------------------- 接收包数对比 ---------------------------")
    if hw["total_packets"] != l2_pkts or l2_pkts != l3_pkts or l3_pkts != l4_pkts or l4_pkts != l7_pkts:
        print("接收包数对比失败")
        return False

    print("接收包数对比成功")
    return True

def check_internal_stats_flow(total_flow_count): 
    # 日志总数 stats output / enq ring num , 各个协议的输出日志总数
    url = "http://prsadmin:prsadmin2016@127.0.0.1:18082/stats_output"
    r = requests.get(url)
    print("--------------------------- 流对比 ---------------------------")
    outputs = r.json()["stats_output"]["kafka"]
    ring_num = 0
    for o in outputs:
        if o["module_name"]  == "enq ring num":
            ring_num = o["count"]

    if ring_num != total_flow_count:
        print("流对比失败")
        return False
    print("流对比成功")
    return True

def check_internal_stats_memory(total_flow_count):
    # memory接口, 各个pool个数
    url = "http://prsadmin:prsadmin2016@10.0.81.89:18082/memory?cpu_id=255"
    r = requests.get(url)
    pools = r.json()["mempool"]

    pool_list = ["fpc_info_0", "helper http pool", "dns pool", 
            "helper mail pool", "helper telnet pool", "ftp pool"]

    print("--------------------------- 内存对比 ---------------------------")
    for pool in pools:
        if pool in pool_list and pool["alloc_succ_objs"] != config["protocol"]:
            print("内存对比失败")
            return False

    print("内存对比成功")
    return True

def check_internal_stats(total_packets, total_flow_count):
    ret = True
    if check_internal_stats_packet(total_packets) == False:
        ret = False
    if check_internal_stats_flow(total_flow_count) == False:
        ret = False
    if check_internal_stats_memory(total_flow_count) == False:
        ret = False
    return ret

def main():
    ## 重启matrix, 并且执行脚本 
    #os.system("ambot-service restart matrix")
    #os.system("sleep 30")
    #os.system("python3 pcap_generator.py")
    ## todo 
    # generate flow config
    ## scp to flow generatore 

    config = get_config()
    runtime_data = get_kafka_data()

    # 检查kafka计数, 检查各个协议日志看总条数是否正常
    result = correct_check_kafka(runtime_data, config)
    if result:
        print("检查kafka输出成功!")
    else:
        print("检查kafka输出失败!")

    # 检查每条数据, 每个协议字段都检查看是否一致 
    result_compare(LOG_FILE_PATH)

    # 检查内部计数器
    check_internal_stats(0, 0)

if __name__ == '__main__':
    main()

