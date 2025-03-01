import requests
import time
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from fetch_news import fetch_category_links, fetch_article_links

from fetch_publish_date import fetch_publish_date


# Use a thread pool to concurrently fetch articles
def fetch_articles_threads():
    all_results_category = []
    category_names=[]
    # Set the maximum number of threads to 5
    categories = fetch_category_links()
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
                if articles:
                    # print(articles)
                    # print(len(articles))
                    all_results_category.append(articles)
                    category_names.append(category[0])
            except Exception as e:
                # Handle exceptions that occurred during fetching
                print(f"Error occurred for category {category[0]}: {e}")
        article_dict = dict(zip(category_names, all_results_category))
        print(article_dict)

    # Optionally return or process the collected results (all_results) further

def parse_article(article_url,category):
    try:
        # fetch_articles_threads()
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

        # Output the result
        article_data = {
            'title': title,
            'category': category,
            'content': content[:200]  # 只显示前200个字符
        }

        return article_data
        # return article_url, title, publish_date, content

    except Exception as e:
        print(f"Error fetching article {article_url}: {e}")


if __name__ == "__main__":
    start_time = time.time()
    print("Starting article fetching process...")
    print("-"*40)
        # article_links = fetch_article_links(category_url)
    # print(fetch_articles_threads())
    fetch_articles_threads()
    article_url='https://www.bbc.com/news/articles/cj4x71znwxdo'
    a=parse_article('https://www.bbc.com/news/articles/cj4x71znwxdo','US Election')
    print(a)



    print(f"Finished article fetching process in {time.time() - start_time:.2f} seconds.")
    # t=fetch_publish_date(article_url)
    # print(t)
    # print(f"Finished article fetching process in {time.time() - start_time:.2f} seconds.")