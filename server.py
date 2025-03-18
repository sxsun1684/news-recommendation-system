import re
import os
import boto3
import json
from boto3.dynamodb.conditions import Key
from dotenv import load_dotenv
from flask_session import Session
from dynamo.dynamodb import DynamoDB
from boto3.dynamodb.conditions import Attr
from kafka import KafkaProducer
from flask import Flask, jsonify, request, session
from flask_cors import CORS
from crawler.parser import fetch_articles_threads
from confluent_kafka import Producer

app = Flask(__name__)
CORS(
    app,
    supports_credentials=True,
    origins=["http://localhost:5173"],
    allow_headers=["Content-Type"],
    methods=["GET", "POST", "OPTIONS"]
)

# Load environment variables
load_dotenv()
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_FILE_DIR"] = "./flask_session"
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SECURE"] = False
app.config["SESSION_COOKIE_SAMESITE"] = "None"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_USE_SIGNER"] = True
Session(app)

# 🔥 Initialize DynamoDB
db = DynamoDB("Users", "us-west-1")

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


### 🚀 1. User Registration API
@app.route('/api/auth/register', methods=['POST'])
def register():
    """Registers a new user with email and password"""
    data = request.json
    email = data.get("email")
    password = data.get("password")

    if not EMAIL_REGEX.match(email):
        return jsonify({"message": "Invalid email format"}), 400

    if not email or not password:
        return jsonify({"message": "Email and password cannot be empty"}), 400

    # ✅ Check if the email is already registered
    existing_user = db.get_user_by_email(email)
    if existing_user:
        return jsonify({"message": "Email is already registered"}), 409

        # ✅ Create the user and return their ID
    new_user_id = db.create_user(email, password, [])
    if not new_user_id:
        return jsonify({"message": "Database error, please try again later"}), 500

    print(f"✅ User {email} registered successfully!")
    return jsonify({"message": "Registration successful", "user_id": new_user_id}), 201


### 🚀 2. User Login API
from flask import session, jsonify, request

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Authenticates a user and starts a session"""
    data = request.json
    email = data.get("email")
    password = data.get("password")

    # 验证用户身份
    user = db.authenticate_user(email, password)
    if not user:
        return jsonify({"message": "Invalid email or password"}), 401

    # 将用户信息存储到 session 中
    session["user"] = {"user_id": user["user_id"], "email": user["email"]}
    session.modified = True

    # 返回登录成功的响应，并设置 CORS 相关头
    response = jsonify({"message": "Login successful", "user": session["user"]})
    response.headers["Access-Control-Allow-Origin"] = "http://localhost:5173"
    response.headers["Access-Control-Allow-Credentials"] = "true"

    print(f"🔑 Set-Cookie: {response.headers}")


    return response

### 🚀 3. Get Current User API
@app.route('/api/auth/me', methods=['GET'])
def get_current_user():
    """Returns the currently logged-in user"""
    if 'user' in session:
        return jsonify(session['user'])
    return jsonify({'message': 'Not logged in'}), 401


### 🚀 4. Logout API
@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """Logs out the user and clears the session"""
    session.pop('user', None)
    return jsonify({'message': 'Logout successful'})


### 🛠 Debug: Retrieve All Users from Database
@app.route('/api/auth/debug_users', methods=['GET'])
def debug_users():
    """Retrieves all users from DynamoDB for debugging purposes"""
    users = db.get_all_users()
    return jsonify(users)



### 📢 News API Root Endpoint
@app.route('/')
def get_news():
    """Returns a welcome message for the news API"""
    return jsonify({"message": "This is the news API"})

dynamodb = boto3.resource(
    'dynamodb',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION")
)

news = dynamodb.Table('NewsArticles')
### 📌 Get News by Category
@app.route('/category/<category_name>')
def category(category_name):

    # news_data = fetch_articles_threads()
    # filtered_news = [news for news in news_data if news['category'] == category_name]
    # return jsonify({"category": category_name, "news": filtered_news})
    try:
        formatted_category = category_name.capitalize()  # 确保 category 大小写匹配
        items = []

        # ✅ 使用分页获取完整数据，避免 1MB 限制
        scan_kwargs = {
            'FilterExpression': Attr('category').eq(formatted_category)
        }

        response = news.scan(**scan_kwargs)
        items.extend(response.get('Items', []))

        # 如果数据量超 1MB，继续获取
        while 'LastEvaluatedKey' in response:
            scan_kwargs['ExclusiveStartKey'] = response['LastEvaluatedKey']
            response = news.scan(**scan_kwargs)
            items.extend(response.get('Items', []))

        print(f"🔥 查询 `{formatted_category}` -> 找到 {len(items)} 篇新闻")
        return jsonify({"news": items}), 200

    except Exception as e:
        print(f"❌ DynamoDB 查询错误: {str(e)}")
        return jsonify({"error": "Could not fetch news"}), 500



@app.route('/debug-categories', methods=['GET'])
def debug_categories():
    """列出所有数据库里的 category"""
    try:
        response = news.scan()
        items = response.get('Items', [])

        # 获取所有唯一的分类名称
        categories = list(set(item.get('category', 'UNKNOWN') for item in items))

        print("📜 数据库里的所有分类:", categories)
        return jsonify({"categories": categories}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/debug-all-news', methods=['GET'])
def debug_all_news():
    """扫描数据库，确保获取所有数据"""
    try:
        items = []
        scan_kwargs = {}

        # ✅ 使用 `pagination`，完整扫描数据库，避免 1MB 限制
        while True:
            response = news.scan(**scan_kwargs)
            items.extend(response.get('Items', []))

            if 'LastEvaluatedKey' not in response:
                break  # 所有数据已获取
            scan_kwargs['ExclusiveStartKey'] = response['LastEvaluatedKey']

        # 统计 `category` 文章数量
        category_count = {}
        for item in items:
            category = item.get('category', 'UNKNOWN')
            category_count[category] = category_count.get(category, 0) + 1

        return jsonify({
            "total_news": len(items),
            "category_count": category_count,
            "sample_data": items[:10]  # 仅返回前10条数据
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


### 🔍 Search News Articles
@app.route('/search')
def search():
    """
    Retrieve search results based on a query.

    Query Parameters:
        q (str): The search keyword to match article titles.

    Returns:
        JSON: A dictionary containing the search query and matching news articles.
    """
    query = request.args.get('q', '').lower()
    news_data = fetch_articles_threads()
    search_results = [news for news in news_data if query in news['title'].lower()]
    return jsonify({"query": query, "results": search_results})

@app.route('/like/<path:article_url>', methods=['POST'])
def like_article(article_url):
    try:
        data = request.json
        email = data.get("email")  # 获取用户 email
        like = data.get("like", False)  # 获取点赞状态

        if not email:
            return jsonify({"error": "Missing email"}), 400

        # ✅ 获取用户数据
        user = db.get_user_by_email(email)
        print(f"🔍 like_article: email={email}, user={user}")  # ✅ 调试信息

        if not user or not isinstance(user, dict):  # 确保 `user` 是 `dict`
            print(f"❌ 用户数据错误: {user}, 类型: {type(user)}")  # ✅ 打印 `user` 的类型
            return jsonify({"error": "User not found"}), 404

        # ✅ 修正 `preferences`，确保它是 `dict`
        if not isinstance(user.get("preferences"), list):
            print(f"⚠️ `preferences` 不是 `list`，将其转换为 `list`")
            user["preferences"] = user.get("preferences", [])

        # ✅ 更新 liked_articles
        liked_articles = set(user["preferences"])
        if like:
            liked_articles.add(article_url)
        else:
            liked_articles.discard(article_url)
        user["preferences"] = list(liked_articles)  # ✅ 确保是 `list`

        # ✅ 使用 `put_item()` 替换整个 `user` 记录
        db.table.put_item(Item=user)

        return jsonify({"message": "User like updated", "liked_articles": list(liked_articles)}), 200

    except Exception as e:
        print(f"❌ Error updating like: {str(e)}")
        return jsonify({"error": str(e)}), 500

# producer = KafkaProducer(
#     bootstrap_servers=['localhost:9092'],
#     value_serializer=lambda v: json.dumps(v).encode('utf-8')  # 将消息序列化为 JSON 格式
# )

# @app.route('/produce', methods=['POST'])
# def produce_message():
#     data = request.json
#     print(f"Producing message: {data}")  # 打印接收到的数据
#
#     try:
#         # 发送消息到 Kafka
#         future = producer.send('user-behavior', data)
#         result = future.get(timeout=60)  # 等待消息发送的确认结果
#         print(f"Message sent to Kafka: {result}")
#         producer.flush()
#         return jsonify({"message": "Message successfully produced to Kafka"}), 200
#     except Exception as e:
#         print(f"Failed to send message to Kafka: {e}")
#         return jsonify({"message": "Error sending message to Kafka"}), 500
kafka_config = {
    'bootstrap.servers': 'localhost:9092',  # Kafka 地址
    'client.id': 'python-flask-client'
}
# 创建 Kafka 生产者
producer = Producer(kafka_config)

# Kafka 消息发送函数
def send_to_kafka(topic, message):
    try:
        producer.produce(topic, key=str(message['userId']), value=json.dumps(message))
        producer.flush()
        print(f"Message sent to Kafka topic {topic}")
    except Exception as e:
        print(f"Failed to send message to Kafka: {e}")

@app.route('/api/user-behavior', methods=['POST'])
def send_to_kafka_endpoint():
    data = request.get_json()

    user_id = data.get('user_id')
    email = data.get('email')
    action = data.get('action')
    article_url = data.get('article_url')
    timestamp = data.get('timestamp')
    duration = data.get('duration')

    # 根据 action 选择 Kafka Topic
    if action == 'LIKE':
        topic = 'user-like-actions'
    elif action == 'VIEW':
        topic = 'user-view-actions'
    elif action == 'SHARE':
        topic = 'user-share-actions'
    elif action == 'READ':
        topic = 'user-reading-actions'  # 阅读行为
    else:
        topic = 'user-other-actions'  # 其他行为

    # 构建消息
    message = {
        'userId': user_id,
        'email': email,
        'action': action,
        'articleUrl': article_url,
        'timestamp': timestamp,
        'duration': duration,
    }

    # 发送消息到 Kafka
    send_to_kafka(topic, message)

    return jsonify({'message': 'Data sent to Kafka successfully'})



if __name__ == '__main__':
    app.run(debug=True, port=5050, use_reloader=False)
