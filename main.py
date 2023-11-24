import os
from threading import Thread


# 生成pcap包
def pcap_generator():
    os.system("python pcap_generator.py")


# 上传pcap至sensor并执行打流
def upload_pcap():
    os.system("python linux_paramiko.py")

# 消费kafka数据
def consumer_kafka():
    os.system("python consumer_confluent_kafka.py")

# 本地config文件与kafka数据对比

if __name__ == '__main__':
    pcap_generator()
    upload = Thread(target=upload_pcap())
    upload.start()
    cons = Thread(target=consumer_kafka())
    cons.start()