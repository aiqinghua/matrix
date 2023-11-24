#!/usr/bin/python
# -*- coding: UTF-8 -*-

import yaml

def read_config():
    system_file = open("config/system.yaml",encoding="utf-8")
    system_conf = yaml.load(system_file,Loader=yaml.FullLoader)
    return system_conf