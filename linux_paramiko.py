import paramiko
import os
import shutil


def upload_directory(local_path,remote_path,ssh):
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


hostname = "10.0.81.96"
port = 22
username = "root"
password = "prs@2018"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname,port,username,password)


local_path = r"./pcap"
remote_path = "/home/aiqinghua/pcap/"

upload_directory(local_path,remote_path,ssh)


# command = f"ls -l {remote_path}"
command = f"export PATH=$PATH:/usr/local/wireshark/bin/;prsdata -d {remote_path} -K -T 100 --daemon;ps -ef|grep prsdata"
print(f"Executing command: {command}")
stdin, stdout, stderr = ssh.exec_command(command)
output = stdout.read().decode("utf-8")
errors = stderr.read().decode("utf-8")
print("Command Output:")
print(output)

print("Command Errors:")
print(errors)

ssh.close()