import requests
from bs4 import BeautifulSoup
from crawler.config import NEWS_SOURCES, HEADERS
from db.news_categories import table

# Cache for storing fetched news categories to reduce redundant network requests
CATEGORY_CACHE = None


def save_categories_to_dynamodb(categories):
    """
    Saves the fetched news categories to AWS DynamoDB.

    Args:
        categories (list): A list of tuples containing category name and URL.
    """
    with table.batch_writer() as batch:
        for category in categories:
            batch.put_item(Item={
                'category_name': category[0],  # ✅ Used as the primary key
                'category_url': category[1]
            })
    print("✅ Category data has been saved to DynamoDB")


def fetch_category_links(force_update=False):
    """
    Fetches news category links from the BBC homepage navigation bar.

    If cached data is available, it returns the cached version unless force_update is set to True.

    Args:
        force_update (bool): If True, forces a fresh request to fetch categories.

    Returns:
        list: A list of news categories, each containing category name and URL.
    """
    global CATEGORY_CACHE  # Use a global cache to avoid repeated web scraping

    if CATEGORY_CACHE and not force_update:
        print("✅ Using cached category data")
        return CATEGORY_CACHE

    response = requests.get(NEWS_SOURCES[0], headers=HEADERS)

    if response.status_code != 200:
        return {"error": "Failed to fetch BBC homepage"}

    soup = BeautifulSoup(response.text, 'html.parser')

    # Locate the navigation bar containing category links
    nav = soup.find('nav')
    if not nav:
        print("Navigation bar not found")
        return []

    links = nav.find_all('a')

    categories = []
    for link in links:
        category_name = link.get_text().strip()  # Extract the category name
        category_url = link['href']  # Extract the category URL

        # Skip links related to live broadcasts or video content
        if (
                'live' in category_url.lower()
                or 'video' in category_name.lower()
                # or 'news' in category_name.lower()
        ):
            continue  # Ignore live and video categories

        # Convert relative URLs to absolute URLs
        if category_url.startswith('/'):
            category_url = 'https://www.bbc.com' + category_url

        categories.append([category_name, category_url])  # Add to category list

    CATEGORY_CACHE = categories  # Update cache
    save_categories_to_dynamodb(categories)  # Save to database
    return categories


if __name__ == "__main__":
    print(fetch_category_links())  # Fetch and print category links
    print(CATEGORY_CACHE)  # Print cached category data
