#!/usr/bin/python
# -*- coding: UTF-8 -*-

import json
from read_config import read_config
from deepdiff import DeepDiff


confs = read_config()
kafka_msg_file = confs["kafka"]["kafka_http_msg"]
raw_data_file = confs["pcap"]["config_path"]

# print(f"kafka输出文件为：{kafka_msg_file}\n原始数据文件为：{raw_data_file}")

def find_matching_data(data1, data2):
    print(f"data1的值为：{data1},\ndata2的值为：{data2}")
    matches = False
    failed_fields = []
    for line2 in data2:
        matches = True
        failed_fields = []
        # print(f"data1的值为：{data1}")
        print(f"line2的值为：{line2}")
        for key in data1:
            print(f"key的值为：{key}")
            if key not in line2 or line2[key] != data1[key]:
                matches = False
                failed_fields.append(key)
                # break
            if matches:
                return line2,failed_fields

    return None,failed_fields

def comparison_json_field():
    field_to_compare = ["sip", "dip", "sport", "dport", "protocol", "method"]
    data1 = {field: None for field in field_to_compare}
    data2 = []
    with open(raw_data_file, "r", encoding="utf-8") as f1:
        line = f1.readline()
        obj = json.loads(line)
        for field in field_to_compare:
            if field in obj:
                data1[field] = obj[field]

    with open(kafka_msg_file, "r", encoding="utf-8") as f2:
        for line in f2:
            obj = json.loads(line)
            temp_data = {field: obj.get(field) for field in field_to_compare}
            data2.append(temp_data)

    matching_data, failed_fields = find_matching_data(data1, data2)
    if matching_data != "":
        print(f"文件2中与文件1匹配成功的字段为：{matching_data}")
    else:
        # print()
        print(f"没有匹配的数据！")
    if failed_fields:
        print(f"匹配失败的字段为：{failed_fields}")

comparison_json_field()

# def comparison_json_field():
#     field_to_compare = ["sip","dip","sport","dport","protocol","method"]
#     data1 = {field: [] for field in field_to_compare}
#     data2 = {field: [] for field in field_to_compare}
#     with open(raw_data_file,"r") as f1,open(kafka_msg_file,"r") as f2:
#         for line in f1:
#             obj = json.loads(line)
#             for field in field_to_compare:
#                 if field in obj:
#                     data1[field].append(obj[field])
#
#         for line in f2:
#             obj = json.loads(line)
#             for field in field_to_compare:
#                 if field in obj:
#                     data2[field].append(obj[field])
#
#         print(f"data1的值为：{data1},\t\ndata2的值为：{data2}")
#         diff = {}
#         # diff = DeepDiff(data1,data2)
#         for field in field_to_compare:
#             diff[field] = DeepDiff(data1[field],data2[field])
#         print(diff)
#
# comparison_json_field()