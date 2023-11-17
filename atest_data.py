#!/usr/bin/python
# -*- coding: UTF-8 -*-

data1 = {'sip': '195.168.186.21', 'dip': '10.132.123.191', 'sport': 13888, 'dport': 80, 'protocol': 'tcp', 'method': 'GET'}
data2 = [{'sip': '195.168.186.21', 'dip': '10.132.123.191', 'sport': 13888, 'dport': 80, 'protocol': None, 'method': 'GET'}, {'sip': '195.168.186.21', 'dip': '10.132.123.191', 'sport': 13888, 'dport': 80, 'protocol': None, 'method': ''}]

'''
1.获取原始数据
2.获取kafka数据
3.原始数据与kafka中的数据进行对比
    原始数据为1条数据
    需要对比kafka的数据为1个list，里面为多条数据
        1.首先对比整条数据，看整条数据是否一致
        2.对比数据中的字段，看字段内容是否一致
4.输出对比成功/失败的字段，对比时的数据
'''

def Entire_data():
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


def field_data(field):
    # 字段对比
    # fields = field
    # field_success = []
    # field_fail = []
    # temp_success,temp_fail = Entire_data()
    # for line in temp_fail:
    #     for field in fields:
    #         if data1.get(field) == line.get(field):
    #             field_success.append(field)
    #         else:
    #             field_fail.append(field)
    #     break
    # return field_success, field_fail
    results = []

    for line in data2:
        matching_fields = []
        for key, value in line.items():
            if key in data1 and data1[key] == value:
                matching_fields.append(key)

        results.append(matching_fields)

    return results


def Processing_comparative_data():
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
        print(tmp)

field = ["sip", "dip", "protocol", "method"]
success, fail = field_data(field)
# print(f"匹配成功的字段为：{success[0]} \n匹配失败的字段为：{fail[0]}")
res = Processing_comparative_data()
print(res)
# get_result()
