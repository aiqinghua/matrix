import sys
from confluent_kafka.cimpl import KafkaError, KafkaException
from read_config import read_config
from confluent_kafka import Consumer
import datetime
import time


kafka_conf = read_config()
kafka_server_ip = kafka_conf["kafka"]["kafka_server_ip"]
kafka_server_port = kafka_conf["kafka"]["kafka_port"]
kafka_consumer_timeout = kafka_conf["kafka"]["kafka_consumer_timeout"]
kafka_topic = kafka_conf["kafka"]["topic"]
kafka_group_id = kafka_conf["kafka"]["group_id"] + str(time.time()*1000)
kafka_output_msg = kafka_conf["kafka"]["kafka_msg"]
ssl_dir = kafka_conf["kafka"]["kafka_cert_path"]


conf = {
    'bootstrap.servers': f'{kafka_server_ip}:{kafka_server_port}',
    'group.id': f'{kafka_group_id}',
    'security.protocol': 'SSL',
    'sasl.password':'Tophant.PRS@2018',
    'ssl.ca.location': ssl_dir + r'/ca-cert',
    'ssl.certificate.location': ssl_dir + r'/kafka.client.pem',
    'ssl.key.location': ssl_dir + r'/kafka.client.key',
    'auto.offset.reset': 'latest'
}

consumer = Consumer(conf)

def clear_file_content(filename):
    with open(filename,"w") as file:
        pass


def consumer_loop(consumer,topics):
    topic_to_file = {topic:file for topic,file in zip(topics, kafka_output_msg)}

    # 设置output文件是否需要被清空标识
    clear_file = True
    if clear_file:
        # 第一次运行时清空
        for file in kafka_output_msg:
            clear_file_content(file)
            clear_file = False

    try:
        consumer.subscribe(topics)
        while True:
            # print(f"当前时间为：{datetime.datetime.now()}")
            msg = consumer.poll(timeout=kafka_consumer_timeout)
            if msg is None:
                break
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    # End of partition event
                    sys.stderr.write('%% %s [%d] reached end at offset %d\n' %
                                     (msg.topic(), msg.partition(), msg.offset()))
                elif msg.error():
                    raise KafkaException(msg.error())
            else:
                decode_msg = msg.value().decode('latin-1')
                print(decode_msg)
                with open(topic_to_file[msg.topic()], "a", encoding="utf-8") as file:
                    file.write(f"{decode_msg}\n")
    finally:
        consumer.close()


consumer_loop(consumer,kafka_topic)