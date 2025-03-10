from kafka import KafkaProducer
import json
from concurrent.futures import ThreadPoolExecutor
from crawler.parser import fetch_articles_threads, parse_article

# 创建 Kafka 生产者
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda m: json.dumps(m).encode('utf-8'),  # JSON 序列化
    retries=5
)
