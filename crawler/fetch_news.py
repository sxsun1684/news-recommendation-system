import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from crawler.config import NEWS_SOURCES, HEADERS
from db.news_categories import table

CACHE_EXPIRY_HOURS = 24  # 设置数据库数据过期时间


def save_categories_to_dynamodb(categories):
    """
    Saves the fetched news categories to AWS DynamoDB.

    - ✅ 添加 `last_updated` 字段，表示数据爬取时间
    """
    with table.batch_writer() as batch:
        for category in categories:
            batch.put_item(Item={
                'category_name': category[0],  # ✅ 作为主键
                'category_url': category[1],
                'last_updated': datetime.utcnow().isoformat()  # ⏳ 记录更新时间
            })
    print("✅ Category data has been saved to DynamoDB")


def get_categories_from_dynamodb():
    """
    Retrieves category data from DynamoDB.

    - ✅ 仅查询 `category_name` 和 `category_url`
    - ✅ 按 `last_updated` 时间排序，获取最新的数据
    """
    try:
        response = table.scan(ProjectionExpression="category_name, category_url, last_updated")
        items = response.get("Items", [])
        return sorted(items, key=lambda x: x["last_updated"], reverse=True)  # 按更新时间排序
    except Exception as e:
        print(f"❌ Error fetching categories from DynamoDB: {e}")
        return None


def fetch_category_links(force_update=False):
    """
    Fetches news category links from the BBC homepage navigation bar.

    - **优先从数据库读取数据**
    - **如果 `force_update=True` 或数据过期，重新爬取并更新数据库**

    Args:
        force_update (bool): 是否强制更新分类数据。

    Returns:
        list: 新闻分类数据
    """
    # ✅ **1. 先检查数据库，看看是否有可用数据**
    categories = get_categories_from_dynamodb()
    if categories and not force_update:
        last_updated = datetime.fromisoformat(categories[0]["last_updated"])
        if datetime.utcnow() - last_updated < timedelta(hours=CACHE_EXPIRY_HOURS):
            print("⏳ 数据未过期，使用数据库缓存")
            return [[c["category_name"], c["category_url"]] for c in categories]

    # ✅ **2. 数据过期 or `force_update=True`，执行爬虫**
    print("🔄 正在爬取分类数据...")
    response = requests.get(NEWS_SOURCES[0], headers=HEADERS)

    if response.status_code != 200:
        return {"error": "❌ 无法访问 BBC 主页"}

    soup = BeautifulSoup(response.text, 'html.parser')

    # 定位导航栏
    nav = soup.find('nav')
    if not nav:
        print("❌ 找不到导航栏")
        return []

    links = nav.find_all('a')

    categories = []
    for link in links:
        category_name = link.get_text(strip=True)
        category_url = link['href']

        # ❌ 过滤掉直播、视频等不需要的分类
        if ('live' in category_url.lower() or 'video' in category_name.lower()):
            continue

        # 🔗 补全 URL
        if category_url.startswith('/'):
            category_url = 'https://www.bbc.com' + category_url

        categories.append([category_name, category_url])

    # ✅ **3. 爬取完成后，存入数据库**
    save_categories_to_dynamodb(categories)
    return categories


if __name__ == "__main__":
    print(fetch_category_links())  # 🛠 运行测试
