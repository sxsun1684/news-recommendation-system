import requests
import time
import re
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from crawler.fetch_news import fetch_category_links, fetch_article_links
from functools import wraps


# Decorator: Automatically retry failed requests
# Retries the decorated function upon encountering an exception, for robustness in HTTP requests.
def retry_on_failure(retries=3, delay=2):
    """Decorator to retry a function call upon failure.

    Args:
        retries (int): Maximum number of retry attempts.
        delay (int): Delay between retries in seconds.

    Returns:
        function: Wrapped function with retry logic.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"Error in {func.__name__}: {e}, retrying {attempt + 1}/{retries}")
                    time.sleep(delay)
            return None  # Return None if all retry attempts fail
        return wrapper
    return decorator


# Fetch article links concurrently using ThreadPoolExecutor
def fetch_articles_threads():
    """Fetches article links concurrently for multiple news categories, removing duplicate entries.

    Returns:
        dict: Dictionary containing category names as keys and lists of unique article URLs as values.
    """
    all_results_category = []
    category_names = []

    # Fetch all available category links
    categories = fetch_category_links()

    # Utilize ThreadPoolExecutor for concurrent fetching
    with ThreadPoolExecutor(max_workers=5) as executor:
        # Submit fetch tasks concurrently for each category URL
        future_to_category = {
            executor.submit(fetch_article_links, category[1]): category for category in categories
        }

        # Process completed futures
        for future in as_completed(future_to_category):
            category = future_to_category[future]
            try:
                articles = future.result()
                if articles:
                    # Remove duplicates and store unique article links per category
                    all_results_category.append(list(set(articles)))
                    category_names.append(category[0])
            except Exception as e:
                print(f"Error occurred for category {category[0]}: {e}")

    # Map category names to their respective article URLs
    article_dict = dict(zip(category_names, all_results_category))
    print(article_dict)
    return article_dict


# Find the category name based on a given article URL
def find_category_by_url(url, data):
    """Determines the news category for a given article URL.

    Args:
        url (str): Article URL to classify.
        data (dict): Dictionary of category-to-URL mappings.

    Returns:
        str: Category name if found, else 'Unknown Category'.
    """
    for category, urls in data.items():
        if url in urls:
            return category
    return "Unknown Category"


# Extract publication date from article URL using regular expressions
def extract_date_from_url(article_url):
    """Extracts the publication date from a structured article URL.

    Args:
        article_url (str): The URL of the article containing the date.

    Returns:
        str: Publication date in YYYY-MM-DD format or 'Unknown Date'.
    """
    match = re.search(r'/(\d{8})-', article_url)
    if match:
        date_str = match.group(1)
        return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
    return "Unknown Date"


# Fetch and parse the content of an article from its URL
@retry_on_failure(retries=3, delay=2)
def parse_article(article_url):
    """Fetches and parses the article to extract title, category, publish date, and content.

    Args:
        article_url (str): URL of the article to parse.

    Returns:
        dict: Structured data containing the article's metadata and content snippet.
    """
    try:
        response = requests.get(article_url)
        if response.status_code != 200:
            print(f"Failed to fetch article: {article_url}")
            return None

        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract the article title
        title_tag = soup.find('h1')
        title = title_tag.get_text(strip=True) if title_tag else "No title found"

        # Extract main content paragraphs
        paragraphs = soup.find_all('p')
        content = "\n".join([para.get_text(strip=True) for para in paragraphs])

        # Retrieve category using URL-based lookup
        category = find_category_by_url(article_url, fetch_articles_threads())

        # Extract publication date from URL
        publish_date = extract_date_from_url(article_url)

        # Return article information with content snippet (first 200 characters)
        return {
            'title': title,
            'category': category,
            'publish_date': publish_date,
            'content': content[:200]
        }

    except Exception as e:
        print(f"Error fetching article {article_url}: {e}")
        return None


# Main execution block
if __name__ == "__main__":
    start_time = time.time()
    print("Starting article fetching process...")

    # Fetch article links concurrently for debugging or testing
    fetch_articles_threads()

    # Parse a single test article URL
    article_data = parse_article('https://www.bbc.com/culture/article/20250306-who-is-cindy-lee-pops-most-mysterious-sensation')
    print(article_data)

    print(f"Finished article fetching process in {time.time() - start_time:.2f} seconds.")
