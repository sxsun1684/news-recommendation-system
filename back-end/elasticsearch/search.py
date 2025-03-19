from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import json

# 初始化 Elasticsearch 客户端
es = Elasticsearch()

# 创建索引映射（定义字段类型）
index_mapping = {
    "mappings": {
        "properties": {
            "title": {"type": "text"},
            "content": {"type": "text"}
        }
    }
}


es.indices.create(index="articles", body=index_mapping, ignore=400)


articles = [
    {"title": "Machine Learning Basics", "content": "This article discusses the basics of machine learning."},
    {"title": "Deep Learning Overview", "content": "This article explores deep learning concepts."},
    {"title": "Introduction to AI", "content": "This article introduces artificial intelligence."}
]

bulk(es, [{"_index": "articles", "_source": data} for data in articles])

# 查询关键词聚合（例如，根据词频获取关键词）
response = es.search(index="articles", body={
    "query": {
        "match": {"content": "machine"}
    },
    "aggs": {
        "keywords": {
            "terms": {
                "field": "content.keyword",
                "size": 10
            }
        }
    }
})


print(response['aggregations']['keywords'])
