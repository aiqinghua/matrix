#!/usr/bin/python
# -*- coding: UTF-8 -*-

import json
from read_config import read_config
import comparative_data
from Empty_files import Empty_file_content


confs = read_config()
kafka_msg_file = confs["kafka"]["kafka_msg"]
raw_data_file = confs["pcap"]["config_path"]
comparative_data_log = confs["logs"]["data_comparison_logs_path"]
Comparison_results_log = confs["logs"]["Comparison_results"]


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
    field_data_dict = {
        "http.conf": {
            "fields": ["protocol", "method", "uri", "status_code", "status_msg", "request_header_names",
                       "request_header_values", "request_body", "response_body"],
            "default_fields": fields_to_compare
        },
        "dns.conf": {
            "fields": ["query", "qtype_name"],
            "default_fields": fields_to_compare
        },
        "tcp.conf": {
            "fields": ["orig_mac", "resp_mac", "protocol"],
            "default_fields": fields_to_compare
        },
        "udp.conf": {
            "fields": ["orig_mac", "resp_mac", "protocol"],
            "default_fields": fields_to_compare
        },
        "icmp.conf": {
            "fields": ["sip", "dip", "is_echo", "itype", "icode", "payload_len", "ttl", "payload"],
            "default_fields": fields_to_compare
        },
        "smtp.conf": {
            "fields": ["schema_type", "protocol", "mail_from", "rcpt_to", "raw_mail"],
            "default_fields": fields_to_compare
        },
        "pop3.conf": {
            "fields": ["schema_type", "protocol", "mail_from", "rcpt_to", "raw_mail"],
            "default_fields": fields_to_compare
        },
        "imap.conf": {
            "fields": ["schema_type", "protocol", "mail_from", "rcpt_to", "raw_mail"],
            "default_fields": fields_to_compare
        },
        "arp.conf": {
            "fields": ["schema_type", "spa", "sha", "tpa", "tha", "opcode", "hardware_type", "protocol_type", "dst_mac"],
            "default_fields": fields_to_compare
        },
        "dhcp.conf": {
            "fields": ["schema_type", "lease_time", "trans_id", "assigned_dns", "assigned_ip", "assigned_netmask",
                      "assigned_router", "mac"],
            "default_fields": fields_to_compare
        },
        "ftp.conf": {
            "fields": ["schema_type", "user", "command", "arg", "code", "msg"],
            "default_fields": fields_to_compare
        },
        "rarp.conf": {
            "fields": ["schema_type", "src_mac", "dst_mac", "opcode", "hardware_type", "protocol_type", "spa", "sha",
                      "tpa", "tha"],
            "default_fields": fields_to_compare
        },
        "syslog.conf": {
            "fields": ["schema_type", "facility", "level", "message"],
            "default_fields": fields_to_compare
        },
        "telnet.conf": {
            "fields": ["schema_type", "content"],
            "default_fields": fields_to_compare
        },
        "ssl.conf": {
            "fields": ["serial", "fingerprint", "server_ja3_hash", "client_ja3_hash", "schema_type", "version", "cipher","server_name",
                     "established", "server_public_key", "subject", "issuer", "not_valid_before", "not_valid_after"],
            "default_fields": fields_to_compare
        },
        "mysql.conf": {
            "fields": ["schema_type","db_type", "username", "command", "arg", "success"],
            "default_fields": fields_to_compare
        },
        "socks.conf": {
            "fields": ["schema_type", "command", "status", "addr","port"],
            "default_fields": fields_to_compare
        },
        "snmp.conf": {
            "fields": ["schema_type", "duration", "get_request_count","get_next_request_count","response_count",
                      "set_request_count","trap_count", "get_bulk_request_count", "inform_request_count", "sys_desc", "sys_uptime",
                      "sys_contact", "sys_name", "sys_memory_size", "sys_if_number"],
            "default_fields": fields_to_compare
        },
        "llmnr.conf": {
            "fields": ["schema_type", "query", "qtype", "qtype_name", "rcode_name", "answers", "answer_queries", "rejected", "rcode",
                       "answer_types"],
            "default_fields": fields_to_compare
        },
        "ldap.conf": {
            "fields": ["schema_type", "op", "req_dn", "res_code", "matched_dn", "res_error"],
            "default_fields": fields_to_compare
        },
        "rdp.conf": {
            "fields": ["schema_type", "cookie", "cotp_connect_request", "cotp_connect_confirm", "rdp_negotiation_request",
                     "rdp_negotiation_failure", "rdp_negotiation_response"],
            "default_fields": fields_to_compare
        }
    }

    field_data = field_data_dict.get(data1_keys)
    if field_data:
        field_list = field_data["fields"] + field_data["default_fields"]
        comparative_data.field_data(data1_value[0], data2_value, field_list, data1_keys)


def Processing_data():
    data1, data2 = comparison_json_field()
    max_length = max(len(data1), len(data2))
    # print(f"{data1}\n{data2}")

    key_data1 = []
    for i in range(max_length):
        tmp_data1 = data1[i]
        # 获取data1中的key并进行切片
        tmp_key = list(tmp_data1.keys())[0][10:]
        key_data1.append(tmp_key)
    one_keys = key_data1[:5]
    mail_keys = key_data1[5:8]
    protocol_keys = key_data1[8:]
    # 清空结果文件
    is_clear = True
    Empty_file_content(is_clear, comparative_data_log)
    Empty_file_content(is_clear, Comparison_results_log)

    for i in range(max_length):
        if i < len(data1):
            temp_data1 = data1[i]
            data1_keys = list(temp_data1.keys())[0][10:]
            data1_value = [json.loads(event) for event in list(temp_data1.values())[0]]

            print(f"\033[32m正在匹配{data1_keys}数据：\033[0m")

            with open(comparative_data_log[0], "a", encoding="utf-8") as log_file:
                log_file.write(f"正在匹配{data1_keys}数据：\n")

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


Processing_data()