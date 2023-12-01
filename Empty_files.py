#!/usr/bin/python
# -*- coding: UTF-8 -*-
from read_config import read_config


def clear_file_content(filename):
    with open(filename, "w", encoding="utf-8") as file:
        pass

def Empty_file_content(is_clear, file_name):
    clear_file = is_clear
    if clear_file:
        # 第一次运行时清空
        for file in file_name:
            clear_file_content(file)
            clear_file = False

# log_conf = read_config()
# file_name = log_conf["logs"]["data_comparison_logs_path"]
# print(file_name)
# is_clear = True
# Empty_file_content(is_clear, file_name)