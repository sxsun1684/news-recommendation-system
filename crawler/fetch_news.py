import requests
from bs4 import BeautifulSoup
from config import NEWS_SOURCES, HEADERS


# bbc_home_url = 'https://www.bbc.com/news'


# Fetch news category links from the navigation bar
def fetch_category_links():
    """
    Fetches the news category links from the BBC homepage navigation bar.

    This function sends a request to the BBC homepage, parses the HTML to locate
    the navigation bar, and extracts the links to different news categories. It filters
    out links related to live broadcasts or video content.

    Returns:
        categories (list): A list of [category_name, category_url] pairs. Each entry
        contains the name of the news category and the corresponding full URL. If
        the navigation bar is not found or the request fails, it returns an empty list
        or an error message.
    """
    response = requests.get(NEWS_SOURCES[0], headers=HEADERS)

    if response.status_code != 200:
        return {"error": "Failed to fetch BBC homepage"}

    soup = BeautifulSoup(response.text, 'html.parser')

    nav = soup.find('nav')  # Search for the navigation bar
    if not nav:
        print("Navigation bar not found")
        return []

    links = nav.find_all('a')

    categories = []
    for link in links:
        category_name = link.get_text().strip()  # Get the category name
        category_url = link['href']  # Get the category URL

        # Skip links related to live broadcasts or video content
        if (
                'live' in category_url.lower()
                or 'video' in category_name.lower()
                or 'home' in category_name.lower()
                or 'news' in category_name.lower()
        ):
            continue  # Skip live and video categories

        # Complete relative URLs by adding the base URL
        if category_url.startswith('/'):
            category_url = 'https://www.bbc.com' + category_url

        categories.append([category_name, category_url])  # Add category details to the list

    return categories



def fetch_article_links(category_url):
    """
    Fetches the article links from a given news category page.

    This function sends a request to the provided category URL, parses the HTML
    content, and extracts all links that are considered articles (based on URL structure).

    Args:
        category_url (str): The URL of the news category from which to scrape articles.

    Returns:
        articles (list): A list of full URLs pointing to individual news articles from
        the given category page. Only links that contain 'article' in the URL are included.
    """
    response = requests.get(category_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    articles = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        # Filter links that contain 'article' in their href attribute
        if 'article' in href:
            article_url = f"https://www.bbc.com{href}"
            articles.append(article_url)

    return articles