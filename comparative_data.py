#!/usr/bin/python
# -*- coding: UTF-8 -*-
from read_config import read_config

# '''
# 1.获取原始数据
# 2.获取kafka数据
# 3.原始数据与kafka中的数据进行对比
#     原始数据为1条数据
#     需要对比kafka的数据为1个list，里面为多条数据
#         1.首先对比整条数据，看整条数据是否一致
#         2.对比数据中的字段，看字段内容是否一致
# 4.输出对比成功/失败的字段，对比时的数据
# '''


data_comparison_logs_path = read_config()
comparative_data_log = data_comparison_logs_path["logs"]["data_comparison_logs_path"]

def Entire_data(data1, data2):
    # 整条数据对比
    Entire_success = []
    Entire_fail = []
    for line2 in data2:
        if data1 == line2:
            # print(f"相等的数据为：{line2}")
            Entire_success.append(line2)
        else:
            Entire_fail.append(line2)
            # print(f"不相等的数据为：{line2}")
    return Entire_success, Entire_fail


def field_data(data1, data2, field,data1_key):
    # 字段对比
    fields = field
    result = []
    temp_success, temp_fail = Entire_data(data1, data2)
    for line in temp_fail:
        field_success = []
        field_fail = []
        for field in fields:
            # 判断字段内容是否一致，此处会将内容全部转换为小写进行对比
            if str(data1.get(field)).lower() == str(line.get(field)).lower() and line.get(field) is not None:
                field_success.append(field)
            else:
                field_fail.append(field)
        result.append({
            "field_success": field_success,
            "field_fail": field_fail,
            "line": line,
            "data1": data1,
            "keys": data1_key
        })
        for res in result:
            print(f"匹配协议为：{res['keys']}\t\033[34m成功的字段：{res['field_success']}\033[0m\t "
                  f"\033[31m失败的字段：{res['field_fail']}\033[0m")
            with open(comparative_data_log[0], "a", encoding="utf-8") as log_file:
                log_file.write(f"匹配成功的字段：{res['field_success']}\t 匹配失败的字段：{res['field_fail']}"
              f"\n匹配的数据：{res['line']}\n原始数据：{res['data1']}\n\n")
    return result


def Processing_comparative_data(data1,data2,field):
    # 将对比的结果处理
    result = []
    for data in data2:
        Entire_success, Entire_fail= Entire_data()
        field_success, field_fail = field_data(field)
        f=[]
        f.append(field_success)
        f.append(field_fail)
        f.append(data)
        f.append(data1)
        result.append(f)
    return result


def get_result():
    get_res = Processing_comparative_data()
    dirty_data = []
    for tmp in get_res:
        # print(tmp)
        # print(type(len(tmp)))
        i = 1
        print(f"匹配成功的字段为：{tmp[len(tmp)- (i+3)]} \n匹配失败的字段为：{tmp[len(tmp)- (i+2)]}\n匹配的数据为：{tmp[len(tmp)- (i+1)]}"
              f"\n匹配的原始数据为：{tmp[len(tmp)-i]}\n")

# field = ["sip", "dip", "protocol", "method"]
# success, fail = field_data(field)

# field_data(data1[0], data2, field)
# get_result()
