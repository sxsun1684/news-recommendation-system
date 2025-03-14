import requests
import random
import time
import boto3
from bs4 import BeautifulSoup
import urllib.parse
from crawler.fetch_article_links import fetch_all_articles
from concurrent.futures import ThreadPoolExecutor, as_completed

# ScraperAPI key
API_KEY = '3606c7448c1650aaa96eda6faf894f65'

# AWS DynamoDB setup
dynamodb = boto3.resource('dynamodb', region_name='us-west-1')  # Update with your region
table = dynamodb.Table('NewsArticles')  # Replace with your table name

# Example news data
news_data = fetch_all_articles()

# Define User-Agent strings
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:48.0) Gecko/20100101 Firefox/48.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0'
]


def get_random_user_agent():
    """Randomly choose a User-Agent"""
    return random.choice(user_agents)


def fetch_content_with_scraperapi(url):
    """Use ScraperAPI to fetch page content"""
    encoded_url = urllib.parse.quote(url, safe=':/?=&')  # URL encoding
    scraper_api_url = f'https://api.scraperapi.com?api_key={API_KEY}&url={encoded_url}'

    # Randomly select a User-Agent
    headers = {'User-Agent': get_random_user_agent()}

    retries = 3
    for attempt in range(retries):
        try:
            response = requests.get(scraper_api_url, headers=headers)
            if response.status_code == 200:
                return response.text
            else:
                print(f"Attempt {attempt + 1}: Failed to fetch URL: {url} (Status code: {response.status_code})")
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1}: Error fetching URL {url}: {e}")
        time.sleep(2)  # Wait before retrying

    return None


def extract_article_details(url):
    """Extract article details (title, time, content) and store it in DynamoDB"""
    html_content = fetch_content_with_scraperapi(url)
    if html_content:
        soup = BeautifulSoup(html_content, 'html.parser')

        # Extract title
        title_tag = soup.find('h1')
        title = title_tag.get_text(strip=True) if title_tag else 'No title found'

        # Extract publication date
        time_tag = soup.find('time')
        pub_date = time_tag.get_text(strip=True) if time_tag else 'No date found'

        # Extract content
        paragraphs = soup.find_all('p')
        content = "\n".join([p.get_text(strip=True) for p in paragraphs])

        # Prepare the article data
        article_data = {
            'category': category,  # Concatenate URL and category for uniqueness
            'title': title,
            'pub_date': pub_date,
            'content': content,  # Storing the first 500 characters as an example
            'url': url
        }

        # Store in DynamoDB
        store_article_in_dynamodb(article_data)

        return article_data

    return None


def store_article_in_dynamodb(article_data):
    """Store article details in DynamoDB, avoiding duplicates based on category and url"""
    try:
        # 确保 category 和 url 是字符串类型
        if not isinstance(article_data['category'], str) or not isinstance(article_data['url'], str):
            raise ValueError("Category and URL must be strings")

        # 使用 category 和 url 作为主键进行查询
        response = table.get_item(
            Key={
                'category': article_data['category'],  # partition key
                'url': article_data['url']  # sort key
            }
        )

        if 'Item' in response:
            # 如果文章已存在，则跳过
            print(f"Article with URL {article_data['url']} already exists in DynamoDB.")
        else:
            # 如果不存在，插入新文章
            response = table.put_item(
                Item={
                    'category': article_data['category'],  # partition key
                    'url': article_data['url'],  # sort key
                    'title': article_data['title'],
                    'pub_date': article_data['pub_date'],
                    'content': article_data['content'],
                }
            )
            print(f"🤍 Successfully stored article {article_data['title']} in DynamoDB.")
            print(f"Response: {response}")  # 输出响应以进行调试
    except Exception as e:
        print(f"Error storing article in DynamoDB: {e}")



def fetch_articles_for_category(category, urls):
    """🤍Fetch articles for a specific category and store them in DynamoDB using concurrency"""
    print(f"Fetching from category: {category}")

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(extract_article_details, url): url for url in urls}

        for future in as_completed(futures):
            url = futures[future]
            try:
                article_details = future.result()
                if article_details:
                    print(f"Category: {category}")
                    print(f"Title: {article_details['title']}")
                    print(f"Date: {article_details['pub_date']}")
                    print(f"Content: {article_details['content']}")
                    print(f"URL: {article_details['url']}")
            except Exception as e:
                print(f"Error fetching URL {url}: {e}")


# Fetch and store articles for each category using concurrency
for category, urls in news_data.items():
    fetch_articles_for_category(category, urls)
