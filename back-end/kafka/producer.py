from kafka import KafkaProducer
import json

# 配置 Kafka 生产者
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')  # 将消息序列化为 JSON 格式
)

# 发送消息到 'user-behavior' 主题
def send_message(user_email, article_url, duration):
    user_behavior_data = {
        'user_email': user_email,
        'article_url': article_url,
        'duration': duration
    }

    # 发送消息到 Kafka
    future = producer.send('user-behavior', user_behavior_data)
    result = future.get(timeout=60)  # 等待消息发送结果
    print(f"Message sent to Kafka: {result}")
    producer.flush()

# 测试发送的消息
# send_message('user4@example.com', 'http://example.com/article/1234', 120)
