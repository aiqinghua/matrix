import paramiko
import os
from read_config import read_config
import shutil


def upload_directory(local_path,remote_path,ssh):
    # 上传pcap包
    sftp = ssh.open_sftp()
    try:
        sftp.chdir(remote_path)
    except IOError:
        sftp.mkdir(remote_path)
        sftp.chdir(remote_path)
    for root,dirs,files in os.walk(local_path):
        for file in files:
            local_file_path = os.path.join(root, file)
            remote_file_path = os.path.join(remote_path,os.path.relpath(local_file_path, local_path).replace(os.sep, '/'))
            sftp.put(local_file_path, remote_file_path)

    sftp.close()


def Execute_Command(command):
    stdin, stdout, stderr = ssh.exec_command(command)
    output = stdout.read().decode("utf-8")
    errors = stderr.read().decode("utf-8")
    print(f"Command Output:{output}")
    print(f"Command Errors:{errors}")
    ssh.close()


sysconf = read_config()
hostname = sysconf["Sensor"]["hostname"]
port = sysconf["Sensor"]["port"]
username = sysconf["Sensor"]["username"]
password = sysconf["Sensor"]["password"]

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname, port, username, password)

if __name__ == '__main__':
    local_path = r"./pcap"
    remote_path = "/home/aiqinghua/pcap/"
    upload_directory(local_path, remote_path, ssh)
    command = f"export PATH=$PATH:/usr/local/wireshark/bin/;prsdata -d {remote_path} -K -T 1 --daemon;ps -ef|grep prsdata"
    Execute_Command(command)