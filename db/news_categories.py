# Connect AWS DynamoDB
import boto3

dynamodb = boto3.resource('dynamodb', region_name='us-west-1')
table = dynamodb.Table('NewsCategories')