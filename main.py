import os



# 生成pcap包
def pcap_generator():
    os.system("python pcap_generator.py")


# 上传pcap至sensor并执行打流
def upload_pcap():
    os.system("python upload_file.py")

# 消费kafka数据

# 本地config文件与kafka数据对比

if __name__ == '__main__':
    pcap_generator()
    upload_pcap()