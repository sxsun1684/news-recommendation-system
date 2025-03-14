import re
import random
import time
import requests
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

# Randomly choose a User-Agent
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.64 Safari/537.36",
]

def get_random_user_agent():
    """Randomly choose a User-Agent"""
    return random.choice(USER_AGENTS)

class NewsArticle:
    """Represents a news article with URL, title, content, publish date, and category."""

    def __init__(self, url):
        self.url = url
        self.category = self.extract_category_from_url()  # Automatically assign the category based on URL
        self.title = None
        self.content = None
        self.publish_date = self.extract_date_from_url()  # Try to extract date from URL first

    def extract_category_from_url(self):
        """Extract the category from the URL based on known patterns."""
        category_map = {
            "news": "News",
            "future": "Future",
            "travel": "Travel",
            "culture": "Culture",
            "business": "Business",
            "innovation": "Innovation",
            "sport": "Sport",
            "arts": "Arts",
            "home": "Home",
            "earth": "Earth",
            "audio": "Audio"
        }

        # Iterate through the dictionary and return the category if a match is found
        for key, category in category_map.items():
            if key in self.url:
                return category

        # Return "Unknown Category" if no match is found
        return "Unknown Category"

    def extract_date_from_url(self):
        """Try to extract the date from the URL."""
        match = re.search(r'/(\d{8})-', self.url)
        if match:
            date_str = match.group(1)
            return f"{date_str[4:6]}/{date_str[6:]}/{date_str[:4]}"  # Convert to MM/DD/YYYY
        return "Unknown Date"

    def fetch_publish_date(self):
        """Fetch the publish date using Playwright if URL parsing fails and format it as MM/DD/YYYY."""
        if self.publish_date != "Unknown Date":
            return

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            try:
                page.goto(self.url, wait_until="domcontentloaded", timeout=5000)
                time_tag = page.query_selector("time")
                if time_tag:
                    datetime_str = time_tag.get_attribute("datetime")
                    if datetime_str:
                        match = re.search(r"(\d{4})-(\d{2})-(\d{2})", datetime_str)
                        if match:
                            self.publish_date = f"{match.group(2)}/{match.group(3)}/{match.group(1)}"
                        else:
                            self.publish_date = "Not Found"
                    else:
                        self.publish_date = "Not Found"
            except Exception as e:
                print(f"❌ Failed to fetch publish date for {self.url}: {e}")
            finally:
                browser.close()

    def parse(self):
        """Parse the article's title, content, and category."""
        try:
            headers = {"User-Agent": get_random_user_agent()}
            response = requests.get(self.url, headers=headers, timeout=10)
            if response.status_code != 200:
                print(f"❌ Failed to access: {self.url}")
                return None

            soup = BeautifulSoup(response.text, "html.parser")

            title_tag = soup.find("h1")
            self.title = title_tag.get_text(strip=True) if title_tag else "No title found"

            paragraphs = soup.find_all("p")
            self.content = "\n".join([p.get_text(strip=True) for p in paragraphs])

            return {
                "title": self.title,
                "url": self.url,
                "publish_date": self.publish_date,
                "content": self.content,
                "category": self.category  # Include category
            }
        except Exception as e:
            print(f"❌ Failed to parse {self.url}, Error: {e}")
            return None

def process_single_article(url):
    """Process a single article (fetch publish date and parse)."""
    article = NewsArticle(url)
    article.fetch_publish_date()  # Ensure publish date is fetched
    return article.parse()

def print_article_details(url):
    """Function to print the parsed article details for a single URL."""
    result = process_single_article(url)

    if result:
        print(f"Category: {result['category']}")
        print(f"Title: {result['title']}")
        # print(f"URL: {result['url']}")
        print(f"Publish Date: {result['publish_date']}")
        print(f"Content: {result['content'][:500]}...")  # Display first 200 characters of content

# Example of calling the function with a single URL
if __name__ == "__main__":
    test_url = "https://www.bbc.com/culture/article/20250310-why-celebrities-and-gen-z-women-love-the-jacket-and-tie-look"
    print_article_details(test_url)
