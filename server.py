import re
from flask import Flask, jsonify, request, session
from flask_cors import CORS
from crawler.parser import fetch_articles_threads
import os
import boto3
from dotenv import load_dotenv
from flask_session import Session
from dynamo.dynamodb import DynamoDB
from boto3.dynamodb.conditions import Attr

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
@app.route('/api/auth/login', methods=['POST'])
def login():
    """Authenticates a user and starts a session"""
    data = request.json
    email = data.get("email")
    password = data.get("password")

    user = db.authenticate_user(email, password)
    if not user:
        return jsonify({"message": "Invalid email or password"}), 401

    session["user"] = {"user_id": user["user_id"], "email": user["email"]}
    session.modified = True

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

table = dynamodb.Table('NewsArticles')
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

        response = table.scan(**scan_kwargs)
        items.extend(response.get('Items', []))

        # 如果数据量超 1MB，继续获取
        while 'LastEvaluatedKey' in response:
            scan_kwargs['ExclusiveStartKey'] = response['LastEvaluatedKey']
            response = table.scan(**scan_kwargs)
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
        response = table.scan()
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
            response = table.scan(**scan_kwargs)
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

likes = {}
@app.route('/like/<path:article_url>', methods=['POST', 'OPTIONS'])
def like_article(article_url):
    global likes  # 确保访问全局变量

    if request.method == 'OPTIONS':
        return '', 204  # 处理 CORS 预检请求

    data = request.json
    like = data.get("like", False)

    # 初始化点赞数
    if article_url not in likes:
        likes[article_url] = 0

    # 处理点赞或取消点赞
    if like:
        likes[article_url] += 1
    else:
        likes[article_url] = max(0, likes[article_url] - 1)

    return jsonify({"count": likes[article_url]})

@app.route('/likes', methods=['GET'])
def get_likes():
    global likes  # 确保访问全局变量
    return jsonify(likes)




if __name__ == '__main__':
    app.run(debug=True, port=5050, use_reloader=False)
