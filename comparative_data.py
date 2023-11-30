#!/usr/bin/python
# -*- coding: UTF-8 -*-

data1 = [{'orig_mac': '00:02:3f:ec:61:11', 'resp_mac': 'ff:ff:ff:ff:ff:ff', 'sip': '195.168.186.21', 'dip': '10.132.123.191', 'dport': 80, 'sport': 13888, 'service': 'http', 'protocol': 'tcp', 'method': 'GET', 'uri': 'madoc/index.php', 'request_version': '1.1', 'request_header_names': ['USER-AGENT', 'HOST', 'ACCEPT'], 'request_header_values': ['curl/7.29.0', 'claxet.co.uk', '*/*'], 'request_body': '', 'response_version': '1.1', 'status_code': 200, 'status_msg': 'OK', 'response_header_names': ['ACCEPT-RANGES', 'CACHE-CONTROL', 'CONNECTION', 'CONTENT-TYPE', 'DATE', 'ETAG', 'LAST-MODIFIED', 'PRAGMA', 'SERVER', 'SET-COOKIE'], 'response_header_values': ['bytes', 'private, no-cache, no-store, proxy-revalidate, no-transform', 'keep-alive', 'text/html', 'Thu, 30 Jul 2020 05:55:04 GMT', '\\"588604c8-94d\\"', 'Mon, 23 Jan 2017 13:27:36 GMT', 'no-cache', 'bfe/1.0.8.18', 'BDORZ=27315; max-age=86400; domain=.baidu.com; path=/'], 'response_body': 'title,keywords,description,link_tags,url_name,content,is_recommend,tags,publish_time,alert,<!DOCTYPE html>\r\n<!--STATUS OK--><html> <head><meta http-equiv=content-type content=text/html;charset=utf-8><meta http-equiv=X-UA-Compatible content=IE=Edge><meta content=always name=referrer><link rel=stylesheet type=text/css href=http://s1.bdstatic.com/r/www/cache/bdorz/baidu.mi', 'response_body_truncated': False, 'schema_type': 1, 'schema_version': 1, 'sensor_id': '4c15235536204d4cb52a81547953a2f6', 'error': 'mbuf is null'}]
data2 = [{'ts': 1701070395358, 'sid': '6303ec95f7402aaa', 'parent_sid': '', 'schema_type': 1, 'schema_version': 1, 'sensor_id': 'e5e19ce97c23456b83777ee27bcc3f17', 'id': '6303ec95f7802aab', 'vwire_name': 'abcd6a830cc7cc6b', 'vsys_name': 'vsys_second', 'sip': '195.168.186.21', 'dip': '10.132.123.191', 'sport': 13888, 'dport': 80, 'method': 'GET', 'uri': 'madoc/index.php', 'request_version': '1', 'request_header_names': ['USER-AGENT', 'HOST', 'ACCEPT'], 'request_header_values': ['curl/7.29.0', 'claxet.co.uk', '*/*'], 'request_body_len': 0, 'request_body_truncated': False, 'request_body': '', 'response_version': '', 'status_code': 0, 'status_msg': '', 'response_header_names': [], 'response_header_values': [], 'response_body_len': 0, 'response_body_truncated': False, 'response_body': '', 'request_body_b64encoded': False, 'response_body_b64encoded': False, 'error': 'req_ack: 1, rsp_seq: 0, rsp no data, first seq: 2, expect next parser seq: 754, real next parser seq: 0'}, {'ts': 1701070416358, 'sid': '6303ec95f7402aaa', 'parent_sid': '', 'schema_type': 1, 'schema_version': 1, 'sensor_id': 'e5e19ce97c23456b83777ee27bcc3f17', 'id': '6303ecaa79802abf', 'vwire_name': 'abcd6a830cc7cc6b', 'vsys_name': 'vsys_second', 'sip': '195.168.186.21', 'dip': '10.132.123.191', 'sport': 13888, 'dport': 80, 'method': '', 'uri': '', 'request_version': '', 'request_header_names': [], 'request_header_values': [], 'request_body_len': 0, 'request_body_truncated': False, 'request_body': '', 'response_version': '1', 'status_code': 200, 'status_msg': 'OK', 'response_header_names': ['ACCEPT-RANGES', 'CACHE-CONTROL', 'CONNECTION', 'CONTENT-TYPE', 'DATE', 'ETAG', 'LAST-MODIFIED', 'PRAGMA', 'SERVER', 'SET-COOKIE'], 'response_header_values': ['bytes', 'private, no-cache, no-store, proxy-revalidate, no-transform', 'keep-alive', 'text/html', 'Thu, 30 Jul 2020 05:55:04 GMT', '\\"588604c8-94d\\"', 'Mon, 23 Jan 2017 13:27:36 GMT', 'no-cache', 'bfe/1.0.8.18', 'BDORZ=27315; max-age=86400; domain=.baidu.com; path=/'], 'response_body_len': 0, 'response_body_truncated': False, 'response_body': '', 'request_body_b64encoded': False, 'response_body_b64encoded': False, 'error': 'req_ack: 0, rsp_seq: 2'}]


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


def field_data(data1, data2, field):
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
            "data1": data1
        })
    for res in result:
        print(f"\033[34m匹配成功的字段：{res['field_success']}\033[0m\t \033[31m匹配失败的字段：{res['field_fail']}\033[0m"
              f"\n匹配的数据：{res['line']}\n原始数据：{res['data1']}")
        print("")
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
