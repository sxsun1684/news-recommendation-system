from kafka import KafkaConsumer
import json

# 配置 Kafka 消费者
consumer = KafkaConsumer(
    'user-behavior',  # 监听的 Kafka 主题
    bootstrap_servers=['localhost:9092'],  # Kafka 服务器地址
    group_id='user-behavior-group',  # 消费者组 ID
    auto_offset_reset='earliest',  # 从最早的消息开始消费
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))  # 反序列化消息
)

# 消费数据
for message in consumer:
    print(f"Received message: {message.value}")
    # 在这里可以处理消息（例如存储到数据库）
