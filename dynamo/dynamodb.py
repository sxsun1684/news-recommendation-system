import boto3
import uuid
import bcrypt
from botocore.exceptions import ClientError


class DynamoDB:
    def __init__(self, table_name="Users", region_name="us-west-1"):
        """Initialize the connection to DynamoDB"""
        self.dynamodb = boto3.resource("dynamodb", region_name=region_name)
        self.table = self.dynamodb.Table(table_name)

    @staticmethod
    def hash_password(password):
        """Hash the password using bcrypt"""
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    @staticmethod
    def verify_password(password, hashed_password):
        """Verify if the provided password matches the stored hashed password"""
        return bcrypt.checkpw(password.encode(), hashed_password.encode())

    def create_user(self, email, password, preferences):
        """Create a new user while preventing duplicate registrations"""

        # Check if the user already exists
        existing_user = self.get_user_by_email(email)
        if existing_user:
            print(f"❌ User with email {email} is already registered!")
            return None  # Return None if registration fails

        # Generate a unique user_id
        new_user_id = str(uuid.uuid4())
        hashed_password = self.hash_password(password)

        try:
            # Store user details in DynamoDB
            self.table.put_item(
                Item={
                    "user_id": new_user_id,
                    "email": email,
                    "password": hashed_password,
                    "preferences": preferences
                }
            )
            print(f"✅ User {email} registered successfully! ID: {new_user_id}")
            return new_user_id
        except ClientError as e:
            print("❌ Failed to store user data:", e)
            return None

    def get_user(self, user_id, email):
        """Retrieve user information using user_id and email"""
        try:
            response = self.table.get_item(
                Key={
                    "user_id": user_id,
                    "email": email
                }
            )
            if "Item" in response:
                return response["Item"]
            else:
                print("❌ User does not exist")
                return None
        except ClientError as e:
            print(f"❌ Failed to retrieve user: {e}")
            return None

    def get_user_by_email(self, email):
        """Retrieve user using email, assuming a Global Secondary Index (GSI) exists"""
        try:
            response = self.table.query(
                IndexName="email-index",
                KeyConditionExpression="email = :email",
                ExpressionAttributeValues={":email": email}
            )
            items = response.get("Items", [])
            return items[0] if items else None
        except ClientError as e:
            print(f"❌ Failed to retrieve user by email: {e}")
            return None

    def authenticate_user(self, email, password):
        """Authenticate user: First find user_id using email, then verify password"""
        user = self.get_user_by_email(email)
        if not user:
            print("❌ User not found")
            return False

        retrieved_user_id = user["user_id"]
        full_user = self.get_user(retrieved_user_id, email)

        if not full_user:
            print("❌ User not found using user_id")
            return False

        if "password" in full_user and self.verify_password(password, full_user["password"]):
            print("✅ Login successful!")
            return full_user
        else:
            print("❌ Incorrect password")
            return False


# Test code
db = DynamoDB("Users", "us-west-1")
#
# # Create a user with encrypted password
user_id = db.create_user("cc@neu.edu", "mypassword123", ["Tech", "Finance"])

# Test user login (password verification)
db.authenticate_user("cc@neu.edu", "mypassword123")  # ✅ Correct password
db.authenticate_user("cc@neu.edu", "wrongpassword")  # ❌ Incorrect password
u = db.create_user("cc1@neu.edu", "mypassword123", ["Tech", "Finance"])
