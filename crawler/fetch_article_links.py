import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

# ✅ Cached category data to avoid repeated scraping
CATEGORY_CACHE = [
    ['Home', 'https://www.bbc.com/'],
    ['Sport', 'https://www.bbc.com/sport'],
    ['Business', 'https://www.bbc.com/business'],
    ['Innovation', 'https://www.bbc.com/innovation'],
    ['Culture', 'https://www.bbc.com/culture'],
    ['Arts', 'https://www.bbc.com/arts'],
    ['Travel', 'https://www.bbc.com/travel'],
    ['Earth', 'https://www.bbc.com/future-planet'],
    ['Audio', 'https://www.bbc.com/audio']
]

# ✅ HTTP request headers to mimic a browser request
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# ✅ Global cache to prevent redundant fetching
ARTICLE_CACHE = {}


# 1️⃣ **Fetch article links for a specific category**
def fetch_article_links(category_name, category_url):
    """
    Scrapes all article links from a given category page.

    Args:
        category_name (str): The name of the category.
        category_url (str): The URL of the category.

    Returns:
        list: A list of article URLs under the specified category.
    """
    print(f"🌐 Fetching articles from category {category_name}: {category_url}")

    # Check cache before making a request
    if category_name in ARTICLE_CACHE:
        print(f"✅ Loading cached articles for {category_name}...")
        return ARTICLE_CACHE[category_name]

    try:
        response = requests.get(category_url, headers=HEADERS)
        if response.status_code != 200:
            print(f"❌ Failed to access category page: {category_url}")
            return []

        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []

        # Find all links containing 'article' in the href
        for link in soup.find_all('a', href=True):
            href = link['href']
            if 'article' in href:
                # Convert relative URLs to absolute URLs
                article_url = f"https://www.bbc.com{href}" if href.startswith('/') else href
                articles.append(article_url)

        articles = list(set(articles))  # Remove duplicates
        ARTICLE_CACHE[category_name] = articles  # Store in cache
        print(f"✅ Finished fetching {category_name}: {len(articles)} articles found")
        return articles
    except Exception as e:
        print(f"❌ Failed to scrape {category_name}: {e}")
        return []


# 2️⃣ **Fetch articles from all categories concurrently**
def fetch_all_articles():
    """
    Scrapes article links from all categories concurrently using threading.

    Returns:
        dict: A dictionary where keys are category names and values are lists of article URLs.
    """
    article_dict = {}

    # Use ThreadPoolExecutor to speed up category scraping
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_category = {
            executor.submit(fetch_article_links, category[0], category[1]): category[0] for category in CATEGORY_CACHE
        }

        # Process results as soon as they are available
        for future in as_completed(future_to_category):
            category_name = future_to_category[future]
            try:
                articles = future.result()
                if articles:
                    article_dict[category_name] = articles
            except Exception as e:
                print(f"❌ Failed to fetch articles for category {category_name}: {e}")

    return article_dict


# 🚀 **Run the scraper**
if __name__ == "__main__":
    print("📰 Fetching all news articles...")
    news_data = fetch_all_articles()
    print(news_data)  # Print the fetched article data
