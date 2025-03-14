from kafka import KafkaProducer
import json
from concurrent.futures import ThreadPoolExecutor



producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda m: json.dumps(m).encode('utf-8'),  # JSON 序列化
    retries=5
)
