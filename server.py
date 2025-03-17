import re
from flask import Flask, jsonify, request, session
from flask_cors import CORS
import boto3
import os
from dotenv import load_dotenv
from flask_session import Session
from werkzeug.security import generate_password_hash
from db.news_users import NewsUserDB

app = Flask(__name__)
CORS(
    app,
    supports_credentials=True,
    origins=["http://localhost:5173"],  # 只允许 5173
    allow_headers=["Content-Type", "Authorization"],
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
db = NewsUserDB("Users", "us-west-1")

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


### 🚀 1. User Registration API
@app.route('/api/auth/register', methods=['POST'])
# def register():
#     """Registers a new user with email and password"""
#     data = request.json
#     email = data.get("email")
#     password = data.get("password")
#
#     if not EMAIL_REGEX.match(email):
#         return jsonify({"message": "Invalid email format"}), 400
#
#     if not email or not password:
#         return jsonify({"message": "Email and password cannot be empty"}), 400
#
#     # ✅ Check if the email is already registered
#     existing_user = db.get_user_by_email(email)
#     if existing_user:
#         return jsonify({"message": "Email is already registered"}), 409
#
#         # ✅ Create the user and return their ID
#     new_user_id = db.create_user(email, password, [])
#     if not new_user_id:
#         return jsonify({"message": "Database error, please try again later"}), 500
#
#     print(f"✅ User {email} registered successfully!")
#     return jsonify({"message": "Registration successful", "user_id": new_user_id}), 201
def register():
    """注册新用户（密码会哈希存储）"""
    data = request.json
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"message": "邮箱和密码不能为空"}), 400

    if not EMAIL_REGEX.match(email):  # 假设你有EMAIL_REGEX校验邮箱格式
        return jsonify({"message": "邮箱格式无效"}), 400

    existing_user = db.get_user_by_email(email)
    if existing_user:
        return jsonify({"message": "邮箱已注册"}), 409

    hashed_password = generate_password_hash(password)  # 🔑 加密密码存储
    new_user_id = db.create_user(email, hashed_password, [])

    if not new_user_id:
        return jsonify({"message": "数据库错误，请稍后重试"}), 500

    return jsonify({"message": "注册成功"}), 201

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


### 📌 Get News by Category
# @app.route('/category/<category_name>')
# def category(category_name):
#     """
#     Retrieve news articles filtered by category.
#
#     Args:
#         category_name (str): The category name for filtering news articles.
#
#     Returns:
#         JSON: A dictionary containing the category name and filtered list of news articles.
#     """
#     # news_data = fetch_articles_threads()
#     # filtered_news = [news for news in news_data if news['category'] == category_name]
#     # return jsonify({"category": category_name, "news": filtered_news})

dynamodb = boto3.resource("dynamodb", region_name="us-west-1")
table = dynamodb.Table("NewsCategories")
@app.route('/category/<category_name>', methods=["GET"])
def category(category_name):
    """
    Retrieve news articles filtered by category from DynamoDB.
    """
    # 查询 DynamoDB，获取指定类别的新闻
    limit = int(request.args.get("limit", 10))  # 每次返回 10 条新闻
    last_evaluated_key = request.args.get("last_key")  # 分页起始点

    scan_kwargs = {
        "FilterExpression": "category = :c",
        "ExpressionAttributeValues": {":c": category_name},
        "Limit": limit,
    }

    if last_evaluated_key:
        scan_kwargs["ExclusiveStartKey"] = {"news_id": last_evaluated_key}

    response = table.scan(**scan_kwargs)
    filtered_news = response["Items"]  # 这里包含 title, content, url

    return jsonify({
        "category": category_name,
        "news": filtered_news,  # 返回所有新闻
        "last_key": response.get("LastEvaluatedKey")  # 分页
    })


### 🔍 Search News Articles
# @app.route('/search')
# def search():
#     """
#     Retrieve search results based on a query.
#
#     Query Parameters:
#         q (str): The search keyword to match article titles.
#
#     Returns:
#         JSON: A dictionary containing the search query and matching news articles.
#     """
#     query = request.args.get('q', '').lower()
#     news_data = fetch_articles_threads()
#     search_results = [news for news in news_data if query in news['title'].lower()]
#     return jsonify({"query": query, "results": search_results})


if __name__ == '__main__':
    app.run(debug=True, port=5050, use_reloader=False)
