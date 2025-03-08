
import boto3
import uuid
import bcrypt

class DynamoDB:
    def __init__(self, table_name="Users", region_name="us-west-1"):
        """初始化 DynamoDB 连接"""
        self.dynamodb = boto3.resource("dynamodb", region_name=region_name)
        self.table = self.dynamodb.Table(table_name)

    def hash_password(self, password):
        """使用 bcrypt 加密密码"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode(), salt).decode()

    def verify_password(self, password, hashed_password):
        """验证密码是否正确"""
        return bcrypt.checkpw(password.encode(), hashed_password.encode())

    def create_user(self, name, email, password, preferences):
        """创建新用户（带密码加密）"""
        user_id = str(uuid.uuid4())  # 生成唯一 ID
        hashed_password = self.hash_password(password)  # 加密密码

        self.table.put_item(
            Item={
                "user_id": user_id,
                "name": name,
                "email": email,
                "password": hashed_password,  # 存储加密后的密码
                "preferences": preferences
            }
        )
        print(f"User {user_id} has been created！")
        return user_id  # 返回生成的 ID

    def get_user(self, email):
        """查询用户（通过 email 获取）"""
        response = self.table.scan(
            FilterExpression="email = :email",
            ExpressionAttributeValues={":email": email}
        )
        items = response.get("Items", [])
        return items[0] if items else None

    def authenticate_user(self, email, password):
        """用户登录验证"""
        user = self.get_user(email)
        if not user:
            print("User not found")
            return False

        if self.verify_password(password, user["password"]):
            print("✅ Login successful!")
            return user  # 返回用户信息
        else:
            print("❌ Incorrect password!")
            return False


# ✅ 测试代码
db = DynamoDB("Users", "us-west-1")

# 创建用户（密码加密）
user_id = db.create_user("Alice", "alice@example.com", "mypassword123", ["Tech", "Finance"])

# 测试用户登录（验证密码）
db.authenticate_user("alice@example.com", "mypassword123")  # ✅ 正确密码
db.authenticate_user("alice@example.com", "wrongpassword")  # ❌ 错误密码
