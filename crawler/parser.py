import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

from fetch_news import fetch_category_links, fetch_article_links


def parse_article(article_url):
    """
    Parses the detailed content of an article.

    Args:
        article_url (str): The URL of the article to be parsed.

    This function performs the following steps:
    1. Sends a GET request to the given article URL and checks for a successful response.
    2. Uses BeautifulSoup to parse the HTML content of the article.
    3. Extracts the article's title, main body content, and publication date (if available).

    - The title is extracted from the first <h1> tag.
    - The main content is extracted from all <p> (paragraph) tags and concatenated into a single string.
    - The publication date is extracted from the <time> tag, specifically from its 'datetime' attribute, if present.

    The function prints the title, publication date, and the first 200 characters of the content for preview.
    If any errors occur (e.g., failed request or parsing error), the function will print an error message with details.

    Example output:
        Title: Example Article Title
        Publish Date: 2024-10-18T12:34:56
        Content: This is an example of the article content. The content could be several paragraphs long...
        --------------------------------------------------
    """
    try:
        response = requests.get(article_url)
        if response.status_code != 200:
            print(f"Failed to fetch article: {article_url}")
            return

        soup = BeautifulSoup(response.text, 'html.parser')

        # 1. Extract the article title
        title_tag = soup.find('h1')
        title = title_tag.get_text() if title_tag else "No title found"

        # 2. Extract the article body content
        paragraphs = soup.find_all('p')
        content = "\n".join([para.get_text() for para in paragraphs])

        # 3. Extract the publication date
        date_tag = soup.find('time')
        publish_date = date_tag['datetime'] if date_tag and date_tag.has_attr('datetime') else "No date found"

        # Output the result
        print(f"Title: {title}")
        print(f"Publish Date: {publish_date}")
        print(f"Content: {content[:200]}...")  # Display only the first 200 characters
        print("-" * 50)
        # return article_url, title, publish_date, content

    except Exception as e:
        print(f"Error fetching article {article_url}: {e}")


# Use a thread pool to concurrently fetch articles
def fetch_articles_threads():
    """
    Fetch articles from multiple categories concurrently using a thread pool.

    This function uses a thread pool to execute multiple article fetching tasks
    concurrently, limiting the number of threads to 5 to prevent overwhelming
    system resources. It fetches articles for each category and prints the results.

    Steps:
    1. Creates a ThreadPoolExecutor with a maximum of 5 threads.
    2. Submits a task to fetch article links for each category concurrently.
    3. Collects the results from the future objects as they complete and handles
    any potential exceptions during the process.

    This function assumes that `categories` is a list of categories where each
    category is a pair of [category_name, category_url]. The article links are fetched
    from these category URLs.

    The function prints the results of fetching articles for each category.

    Returns:
        None
    """
    all_results = []
    # Set the maximum number of threads to 5
    with ThreadPoolExecutor(max_workers=5) as executor:
        # Submit article link fetching tasks for each category using the thread pool
        future_to_category = {
            executor.submit(fetch_article_links, category[1]): category for category in categories
        }

        # As each future completes, process the result
        for future in as_completed(future_to_category):
            category = future_to_category[future]
            try:
                # Get the result of fetching articles for the category
                articles = future.result()
                # Process the fetched articles here (for example, save or print them)
                print(f"Articles fetched from category '{category[0]}': {articles}")
                if articles:
                    all_results.extend(articles)
            except Exception as e:
                # Handle exceptions that occurred during fetching
                print(f"Error occurred for category {category[0]}: {e}")

    # Optionally return or process the collected results (all_results) further


if __name__ == "__main__":
    categories = fetch_category_links()  # 获取分类链接
    # print(f"Categories: {categories}")
    start_time = time.time()
    print("Starting article fetching process...")


    # for category_name, category_url in categories:
    #     print(f"Fetching articles from category: {category_name}")

        # fetch_articles_with_threads(articles)
        # print(category_url)
    print("-"*40)
        # article_links = fetch_article_links(category_url)
    fetch_articles_threads()

    print(f"Finished article fetching process in {time.time() - start_time:.2f} seconds.")
