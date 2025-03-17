from kafka import KafkaProducer
import json

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def send_user_click(user_id, article_id):
    event = {"user_id": user_id, "article_id": article_id}
    producer.send('user_clicks', event)
    print(f"✅ 用户点击事件已发送: {event}")

# 测试发送点击日志
send_user_click("user123", "article456")
