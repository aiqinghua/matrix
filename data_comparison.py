#!/usr/bin/python
# -*- coding: UTF-8 -*-

import json
from read_config import read_config
import comparative_data


confs = read_config()
kafka_msg_file = confs["kafka"]["kafka_msg"]
raw_data_file = confs["pcap"]["config_path"]


def comparison_json_field():
    new_data = []
    for raw_data in raw_data_file:
        with open(raw_data, "r", encoding="utf-8") as f1:
            line1 = f1.readlines()
            new_data.append({raw_data:line1})

    kafka_data = []
    for file_name in kafka_msg_file:
        with open(file_name, "r", encoding="utf-8") as f2:
            line2 = f2.readlines()
            kafka_data.append({file_name: line2})

    return new_data, kafka_data

def process_protocol_data(data1_keys, data1_value, data2_value, fields_to_compare):
    if data1_keys == "http.conf":
        http_field = ["protocol", "method"]
        http_field.extend(fields_to_compare)
        comparative_data.field_data(data1_value[0], data2_value, http_field)
    elif data1_keys == "dns.conf":
        dns_field = ["query", "qtype_name"]
        dns_field.extend(fields_to_compare)
        comparative_data.field_data(data1_value[0], data2_value, dns_field)
    elif data1_keys == "tcp.conf":
        tcp_field = ["orig_mac", "resp_mac", "protocol"]
        tcp_field.extend(fields_to_compare)
        comparative_data.field_data(data1_value[0], data2_value, tcp_field)
    elif data1_keys == "udp.conf":
        udp_field = ["orig_mac", "resp_mac", "protocol"]
        udp_field.extend(fields_to_compare)
        comparative_data.field_data(data1_value[0], data2_value, udp_field)
    elif data1_keys == "icmp.conf":
        icmp_field = ["sip", "dip", "is_echo", "itype", "icode", "payload_len", "ttl", "payload"]
        comparative_data.field_data(data1_value[0], data2_value, icmp_field)
    elif data1_keys == "smtp.conf":
        smtp_field = []
        comparative_data.field_data(data1_value[0], data2_value, smtp_field)
    elif data1_keys == "pop3.conf":
        pop3_field = []
        comparative_data.field_data(data1_value[0], data2_value, pop3_field)
    elif data1_keys == "imap.conf":
        imap_field = []
        comparative_data.field_data(data1_value[0], data2_value, imap_field)
    elif data1_keys == "arp.conf":
        arp_field = ["schema_type", "spa", "sha", "tpa", "tpa", "tha", "opcode", "hardware_type", "protocol_type"]
        comparative_data.field_data(data1_value[0], data2_value, arp_field)
    elif data1_keys == "dhcp.conf":
        dhcp_field = ["schema_type", "lease_time", "trans_id", "assigned_dns", "assigned_ip", "assigned_netmask",
                      "assigned_router", "mac"]
        comparative_data.field_data(data1_value[0], data2_value, dhcp_field)
    elif data1_keys == "ftp.conf":
        ftp_field = ["schema_type", "user", "command", "arg", "code", "msg"]
        comparative_data.field_data(data1_value[0], data2_value, ftp_field)
    elif data1_keys == "rarp.conf":
        rarp_field = ["schema_type", "src_mac", "dst_mac", "opcode", "hardware_type", "protocol_type", "spa", "sha",
                      "tpa", "tha"]
        comparative_data.field_data(data1_value[0], data2_value, rarp_field)
    elif data1_keys == "syslog.conf":
        syslog_field = ["schema_type", "facility", "level", "message"]
        comparative_data.field_data(data1_value[0], data2_value, syslog_field)
    elif data1_keys == "telnet.conf":
        telnet_field = ["schema_type", "content"]
        telnet_field.extend(fields_to_compare)
        comparative_data.field_data(data1_value[0], data2_value, telnet_field)



def Processing_data1():
    data1, data2 = comparison_json_field()
    max_length = max(len(data1), len(data2))

    key_data1 = []
    for i in range(max_length):
        tmp_data1 = data1[i]
        # 获取data1中的key并进行切片
        tmp_key = list(tmp_data1.keys())[0][10:]
        key_data1.append(tmp_key)
    one_keys = key_data1[:5]
    mail_keys = key_data1[5:8]
    protocol_keys = key_data1[8:]

    for i in range(max_length):
        if i < len(data1):
            temp_data1 = data1[i]
            data1_keys = list(temp_data1.keys())[0][10:]
            data1_value = [json.loads(event) for event in list(temp_data1.values())[0]]

            print(f"{data1_keys}")
            print(f"\033[32m正在匹配{data1_keys}数据：\033[0m")
            field_to_compare = ["sip", "dip", "sport", "dport"]

            if i < len(data2):
                temp_data2 = data2[i]
                data2_value = [json.loads(event) for event in list(temp_data2.values())[0]]

                # if data1_keys in ["http.conf", "dns.conf", "tcp.conf", "udp.conf", "icmp.conf"]:
                if data1_keys in one_keys:
                    process_protocol_data(data1_keys, data1_value, data2_value, field_to_compare)
                else:
                    pass

            elif data1_keys in mail_keys:
                temp_data2 = data2[len(data2) - 2]
                data2_value = [json.loads(event) for event in list(temp_data2.values())[0]]
                process_protocol_data(data1_keys, data1_value, data2_value, field_to_compare)

            elif data1_keys in protocol_keys:
                temp_data2 = data2[len(data2) - 1]
                data2_value = [json.loads(event) for event in list(temp_data2.values())[0]]
                process_protocol_data(data1_keys, data1_value, data2_value, field_to_compare)


def Processing_data():
    data1, data2 = comparison_json_field()
    max_lenght = max(len(data1), len(data2))
    # indices = [index for index, element in enumerate(data2) if kafka_msg_file[0] in element.keys()]

    for i in range(max_lenght):
        if i < len(data1):
            temp_data1 = data1[i]
            data1_keys = (list(temp_data1.keys())[0])[10:]
            data1_value = list(temp_data1.values())[0]
            data1_value = [json.loads(event) for event in data1_value]


            print(f"{data1_keys}")
            print(f"\033[32m正在匹配{data1_keys}数据：\033[0m")
            field_to_compare = ["sip", "dip", "sport", "dport"]
            if i < len(data2):
                temp_data2 = data2[i]
                data2_keys = (list(temp_data2.keys())[0])[10:]
                data2_value = list(temp_data2.values())[0]
                data2_value = [json.loads(event) for event in data2_value]


                if data1_keys == "http.conf":
                    http_field = ["protocol", "method"]
                    http_field.extend(field_to_compare)
                    comparative_data.field_data(data1_value[0], data2_value, http_field)
                elif data1_keys == "dns.conf":
                    dns_field = ["query", "qtype_name"]
                    dns_field.extend(field_to_compare)
                    comparative_data.field_data(data1_value[0], data2_value, dns_field)
                elif data1_keys == "tcp.conf":
                    tcp_field = ["orig_mac", "resp_mac", "protocol"]
                    tcp_field.extend(field_to_compare)
                    comparative_data.field_data(data1_value[0], data2_value, tcp_field)
                elif data1_keys == "udp.conf":
                    udp_field = ["orig_mac", "resp_mac", "protocol"]
                    udp_field.extend(field_to_compare)
                    comparative_data.field_data(data1_value[0], data2_value, udp_field)
                elif data1_keys == "icmp.conf":
                    icmp_field = ["sip", "dip", "is_echo", "itype", "icode", "payload_len", "ttl", "payload"]
                    comparative_data.field_data(data1_value[0], data2_value, icmp_field)

            elif (data1_keys == "smtp.conf" or data1_keys == "pop3.conf" or data1_keys == "imap.conf"):
                # 邮件协议
                temp_data2 = data2[len(data2) - 2]
                data2_keys = (list(temp_data2.keys())[0])[10:]
                data2_value = list(temp_data2.values())[0]
                data2_value = [json.loads(event) for event in data2_value]
                if data1_keys == "smtp.conf":
                    smtp_field = []
                    comparative_data.field_data(data1_value[0], data2_value, smtp_field)
                elif data1_keys == "pop3.conf":
                    pop3_field = []
                    comparative_data.field_data(data1_value[0], data2_value, pop3_field)
                elif data1_keys == "imap.conf":
                    imap_field = []
                    comparative_data.field_data(data1_value[0], data2_value,imap_field)

            elif data1_keys == "arp.conf" or data1_keys == "dhcp.conf" or data1_keys == "ftp.conf" or data1_keys == "rarp.conf" or data1_keys == "syslog.conf" or data1_keys == "telnet.conf":
                # 混合协议
                temp_data2 = data2[len(data2) - 1]
                data2_keys = (list(temp_data2.keys())[0])[10:]
                data2_value = list(temp_data2.values())[0]
                data2_value = [json.loads(event) for event in data2_value]
                print(f"混合协议的key为:{data2_keys}")

                if data1_keys == "arp.conf":
                    arp_field = ["schema_type", "spa", "sha", "tpa", "tpa", "tha", "opcode", "hardware_type", "protocol_type"]
                    comparative_data.field_data(data1_value[0], data2_value, arp_field)
                elif data1_keys == "dhcp.conf":
                    dhcp_field = ["schema_type", "lease_time", "trans_id", "assigned_dns", "assigned_ip", "assigned_netmask", "assigned_router", "mac"]
                    comparative_data.field_data(data1_value[0], data2_value, dhcp_field)
                elif data1_keys == "ftp.conf":
                    ftp_field = ["schema_type", "user", "command", "arg", "code", "msg"]
                    comparative_data.field_data(data1_value[0], data2_value, ftp_field)
                elif data1_keys == "rarp.conf":
                    rarp_field = ["schema_type", "src_mac", "dst_mac", "opcode", "hardware_type", "protocol_type", "spa", "sha", "tpa", "tha"]
                    comparative_data.field_data(data1_value[0], data2_value, rarp_field)
                elif data1_keys == "syslog.conf":
                    syslog_field = ["schema_type", "facility", "level", "message"]
                    comparative_data.field_data(data1_value[0], data2_value, syslog_field)
                elif data1_keys == "telnet.conf":
                    telnet_field = ["schema_type", "content"]
                    telnet_field.extend(field_to_compare)
                    comparative_data.field_data(data1_value[0], data2_value, telnet_field)
                # print(f"{data1_keys}\t{data2_keys}")
                #     '''
                #     arp检验字段：schema_type、spa、sha、tpa、tha、opcode、hardware_type、protocol_type
                #     dhcp检验字段：lease_time、trans_id、assigned_dns、assigned_ip、assigned_netmask、assigned_router、mac、schema_type(11)
                #     ftp校验字段：schema_type、user、command、arg、code、msg
                #     rarp校验字段：schema_type、schema_version、src_mac、dst_mac、opcode、hardware_type、protocol_type、spa、sha、tpa、tha
                #     syslog校验字段：schema_type、facility、level、message
                #     telnet校验字段：schema_type、content



    # for temp_data1, temp_data2, temp_kafka_file in zip(data1, data2, kafka_msg_file):
    #     # print(f"{temp_data1}\t{temp_data2}\t{temp_kafka_file}")
    #     data1_keys = (list(temp_data1.keys())[0])[10:]
    #     data1_value = list(temp_data1.values())[0]
    #     data1_value = [json.loads(event) for event in data1_value]
    #
    #     print(f"temp_data2的值为：{type(temp_data2)}")
    #     data2_keys = list(temp_data2.keys())[0][4:]
    #     temp = list(temp_data2.values())[0]
    #     data2_value = [json.loads(event) for event in temp]
    #
    #     print(f"\033[32m正在匹配{data2_keys}数据：\033[0m")
    #     field_to_compare = ["sip", "dip", "sport", "dport"]
    #     if data2_keys == "kafka_http.txt":
    #         http_field = ["protocol", "method"]
    #         http_field.extend(field_to_compare)
    #         comparative_data.field_data(data1_value[0], data2_value, http_field)
    #     elif data2_keys == "kafka_dns.txt":
    #         dns_field = ["query", "qtype_name"]
    #         dns_field.extend(field_to_compare)
    #         comparative_data.field_data(data1_value[0], data2_value, dns_field)
    #     elif data2_keys == "kafka_tcp.txt":
    #         tcp_field = ["orig_mac", "resp_mac", "protocol"]
    #         tcp_field.extend(field_to_compare)
    #         comparative_data.field_data(data1_value[0], data2_value, tcp_field)
    #     elif data2_keys == "kafka_udp.txt":
    #         udp_field = ["orig_mac", "resp_mac", "protocol"]
    #         udp_field.extend(field_to_compare)
    #         comparative_data.field_data(data1_value[0], data2_value, udp_field)
    #     elif data2_keys == "kafka_icmp.txt":
    #         icmp_field = ["sip", "dip", "is_echo", "itype", "icode", "payload_len", "ttl", "payload"]
    #         comparative_data.field_data(data1_value[0], data2_value, icmp_field)
    #
    #     # elif (data1_keys == "smtp.conf" or data1_keys == "pop3.conf" or data1_keys == "imap.conf") and data2_keys == "kafka_mail.txt":
    #     #     # 邮件协议
    #     #     pass
    #     # elif data1_keys == "ftp.conf" and data2_keys == "kafka_protocol.txt":
    #     #     pass
    #     elif data1_keys == "arp.conf" and data2_keys == "kafka_protocol.txt":
    #         arp_field = ["schema_type", "spa", "sha", "tpa", "tpa", "tha", "opcode", "hardware_type", "protocol_type"]
    #         comparative_data.field_data(data1_value[0], data2_value, arp_field)
    #     # print(f"{data1_keys}\t{data2_keys}")
    #     '''
    #     arp检验字段：schema_type、spa、sha、tpa、tha、opcode、hardware_type、protocol_type
    #     dhcp检验字段：lease_time、trans_id、assigned_dns、assigned_ip、assigned_netmask、assigned_router、mac、schema_type(11)
    #     ftp校验字段：schema_type、user、command、arg、code、msg
    #     rarp校验字段：schema_type、schema_version、src_mac、dst_mac、opcode、hardware_type、protocol_type、spa、sha、tpa、tha
    #     syslog校验字段：schema_type、facility、level、message
    #     telnet校验字段：schema_type、content
    #     '''


# Processing_data()
Processing_data1()