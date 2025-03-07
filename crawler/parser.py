import requests
import time
import re
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from crawler.fetch_news import fetch_category_links, fetch_article_links
from functools import wraps


# Decorator: Automatically retry failed requests
def retry_on_failure(retries=3, delay=2):
    """Decorator: Automatically retries a failed request up to 'retries' times with a delay."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"Error in {func.__name__}: {e}, retrying {attempt + 1}/{retries}")
                    time.sleep(delay)
            return None  # Return None after exceeding retry attempts

        return wrapper

    return decorator


# Fetch article links concurrently using a thread pool
def fetch_articles_threads():
    """Fetch all article links for different categories concurrently and remove duplicates."""
    all_results_category = []
    category_names = []

    # Fetch category links
    categories = fetch_category_links()

    with ThreadPoolExecutor(max_workers=5) as executor:
        # Submit tasks to fetch article links for each category
        future_to_category = {
            executor.submit(fetch_article_links, category[1]): category for category in categories
        }

        # Process the results as they complete
        for future in as_completed(future_to_category):
            category = future_to_category[future]
            try:
                articles = future.result()
                if articles:
                    all_results_category.append(list(set(articles)))  # Remove duplicates
                    category_names.append(category[0])
            except Exception as e:
                print(f"Error occurred for category {category[0]}: {e}")

        # Create a dictionary with category names as keys and article URLs as values
        article_dict = dict(zip(category_names, all_results_category))
        print(article_dict)
        return article_dict  # Return the dictionary of categorized article links


# Find category based on URL
def find_category_by_url(url, data):
    """Finds the category for a given URL from the provided category data."""
    for category, urls in data.items():
        if url in urls:
            return category  # Return the matching category
    return "Unknown Category"


# Extract publication date from URL
def extract_date_from_url(article_url):
    """Extracts the publication date from the article URL if available."""
    match = re.search(r'/(\d{8})-', article_url)
    if match:
        date_str = match.group(1)
        return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"  # Convert to YYYY-MM-DD format
    return "Unknown Date"


# Fetch and parse article content
@retry_on_failure(retries=3, delay=2)
def parse_article(article_url):
    """Fetches and parses an article to extract its title, category, publish date, and content."""
    try:
        response = requests.get(article_url)
        if response.status_code != 200:
            print(f"Failed to fetch article: {article_url}")
            return None

        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract the article title
        title_tag = soup.find('h1')
        title = title_tag.get_text() if title_tag else "No title found"

        # Extract the article body content
        paragraphs = soup.find_all('p')
        content = "\n".join([para.get_text() for para in paragraphs])

        # Identify the category
        category = find_category_by_url(article_url, fetch_articles_threads())

        # Extract the publication date
        publish_date = extract_date_from_url(article_url)

        # Construct and return the article data
        return {
            'title': title,
            'category': category,
            'publish_date': publish_date,
            'content': content[:200]  # Display only the first 200 characters
        }

    except Exception as e:
        print(f"Error fetching article {article_url}: {e}")
        return None


if __name__ == "__main__":
    start_time = time.time()
    print("Starting article fetching process...")
    print("-"*40)
        # article_links = fetch_article_links(category_url)
    # print(fetch_articles_threads())
    fetch_articles_threads()
    article_url='https://www.bbc.com/news/articles/cj4x71znwxdo'
    a=parse_article('https://www.bbc.com/culture/article/20250306-who-is-cindy-lee-pops-most-mysterious-sensation')
    print(a)



    print(f"Finished article fetching process in {time.time() - start_time:.2f} seconds.")
    # t=fetch_publish_date(article_url)
    # print(t)
    # print(f"Finished article fetching process in {time.time() - start_time:.2f} seconds.")