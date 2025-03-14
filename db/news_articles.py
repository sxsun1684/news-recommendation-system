import boto3
import traceback
from fetch_bbc import fetch_all_articles

# ✅ Connect to DynamoDB (Replace your AWS Region accordingly)
AWS_REGION = "us-west-1"
TABLE_NAME = "NewsCategoryLinks"
news_data = fetch_all_articles()

class DynamoDBHandler:
    """Manage the DynamoDB table for NewsCategoryLinks"""

    def __init__(self, region, table_name):
        """Initialize connection to DynamoDB"""
        self.dynamodb = boto3.resource('dynamodb', region_name=region)
        self.table = self.dynamodb.Table(table_name)

    def batch_write(self, news_data):
        """Batch write categories and URLs to DynamoDB"""
        try:
            with self.table.batch_writer() as batch:
                for category, urls in news_data.items():
                    if not isinstance(urls, list):
                        urls = [urls]
                    batch.put_item(Item={"category_name": category, "URLs": urls})
            print(f"✅ Successfully inserted articles for {len(news_data)} categories.")
        except Exception as e:
            print(f"❌ Error writing data: {e}")

    def get_category_urls(self, category):
        """Fetch all URLs for a specific category"""
        try:
            response = self.table.get_item(Key={"category_name": category})
            item = response.get("Item")
            return item["URLs"] if item else None
        except Exception as e:
            print(f"❌ Error fetching data: {e}")

    def update_category_urls(self, category, new_urls):
        """Append new URLs to an existing category"""
        try:
            response = self.table.update_item(
                Key={"category_name": category},
                UpdateExpression="SET URLs = list_append(URLs, :new_urls)",
                ExpressionAttributeValues={":new_urls": new_urls},
                ReturnValues="UPDATED_NEW"
            )
            print(f"✅ Updated {category} with {len(new_urls)} new articles.")
        except Exception as e:
            print(f"❌ Error updating data: {e}")

    def delete_category(self, category):
        """Delete a category from the table"""
        try:
            self.table.delete_item(Key={"category_name": category})
            print(f"✅ Deleted category: {category}")
        except Exception as e:
            print(f"❌ Error deleting data: {e}")

    def scan_all_categories(self):
        """Scan all categories and return their URLs"""
        try:
            response = self.table.scan()
            return response.get("Items", [])
        except Exception as e:
            print(f"❌ Error scanning data: {e}")
            return []

if __name__ == "__main__":
    dynamodb_handler = DynamoDBHandler(AWS_REGION, TABLE_NAME)
    dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
    dynamodb_handler.table = dynamodb.Table(TABLE_NAME)

    dynamodb_handler.batch_writer = dynamodb_handler.batch_write

    # Batch insert news data
    dynamodb_handler.batch_write(news_data)

    # Fetch URLs for the "Arts" category
    arts_articles = dynamodb_handler.get_category_urls("Arts")
    print(f"📄 Art Articles: {arts_articles}")
