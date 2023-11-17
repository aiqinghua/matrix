import paramiko
import os

def upload_directory(local_path, remote_path, sftp):
    try:
        sftp.chdir(remote_path)
        # print(f"Remote directory {remote_path} exists.")
    except IOError:
        sftp.mkdir(remote_path)
        sftp.chdir(remote_path)
        # print(f"Remote directory created: {remote_path}")

    for root, dirs, files in os.walk(local_path):
        for file in files:
            local_file_path = os.path.join(root, file)
            remote_file_path = os.path.join(remote_path, os.path.relpath(local_file_path, local_path).replace(os.sep, '/'))
            sftp.put(local_file_path, remote_file_path)
            # print(f"Uploaded: {local_file_path} to {remote_file_path}")

def execute_command(ssh, command):
    stdin, stdout, stderr = ssh.exec_command(command)
    output = stdout.read().decode("utf-8")
    return output

def main():
    # 远程服务器信息
    hostname = "10.0.81.96"
    port = 22
    username = "root"
    password = "prs@2018"

    # 本地目录路径
    local_directory_path = r"./pcap"

    # 远程服务器上存储目录的路径
    remote_directory_path = r"/home/aiqinghua/pcap/"

    # 创建SSH客户端
    ssh = paramiko.SSHClient()

    # 自动添加主机密钥
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # 连接到服务器
    ssh.connect(hostname, port, username, password)

    # 创建SFTP客户端
    sftp = ssh.open_sftp()

    # 上传整个目录
    upload_directory(local_directory_path, remote_directory_path, sftp)

    # 执行命令验证文件是否上传成功
    command = f"ls -l {remote_directory_path}"
    output = execute_command(ssh, command)
    print(output)

    # 执行打流
    Packet_playback = f"prsdata -d {remote_directory_path} -K -T 1"
    print(Packet_playback)
    output1 = execute_command(ssh, Packet_playback)
    print(output1)

    # 关闭SFTP连接
    sftp.close()

    # 关闭SSH连接
    ssh.close()

if __name__ == "__main__":
    main()