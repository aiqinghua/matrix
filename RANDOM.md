Matrix:
    certs:
        kafka：kafka认证文件
    config:
        system.yaml：环境配置相关
        requirements.txt：项目依赖库，"pip install -r requirements.txt"进行一键安装
    logs:
        Comparison_results.log：匹配结果日志
        data_comparison.log：匹配结果详细日志
    msg：消费kfaka数据的数据文件
    pcap:
        生成的pcap数据包的路径
    pcap_conf:
        不同协议生成pcap的配置文件
    comparative_data.py：字段对比文件
    consumer_confluent_kafka.py：kafka消费程序
    data_comparison.py：数据对比文件，调用字段对比方法
    Empty_files.py：文件情况方法
    linux_paramiko.py：上传pcap包及打流
    main.py：执行主程序
    pcap_generator.py：生成pcap包
    read_config.py：读取配置文件方法
    