import requests
import re
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

# ✅ HTTP request headers to mimic a browser request
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}


class NewsArticle:
    """Represents a news article with URL, title, content, and publish date."""

    def __init__(self, url):
        self.url = url
        self.title = None
        self.content = None
        self.publish_date = self.extract_date_from_url()

    def extract_date_from_url(self):
        """Extracts the publish date from the article URL in YYYY-MM-DD format.

        If no date is found, returns 'Unknown Date'.
        """
        match = re.search(r'/(\d{8})-', self.url)  # Matches 8-digit date (e.g., 20250306)
        if match:
            date_str = match.group(1)
            return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"  # Convert to YYYY-MM-DD format
        return "Unknown Date"

    def parse(self):
        """Parses the article's title and content from the web page.

        Returns:
            dict: Extracted data including title, URL, publish date, and content.
        """
        try:
            response = requests.get(self.url, headers=HEADERS)
            if response.status_code != 200:
                print(f"❌ Failed to access: {self.url}")
                return None

            soup = BeautifulSoup(response.text, "html.parser")

            # Extract article title
            title_tag = soup.find("h1")
            self.title = title_tag.get_text(strip=True) if title_tag else "No title found"

            # Extract article content (limit to 500 characters)
            paragraphs = soup.find_all("p")
            self.content = "\n".join([p.get_text(strip=True) for p in paragraphs])[:500]

            return {
                "title": self.title,
                "url": self.url,
                "publish_date": self.publish_date,
                "content": self.content
            }
        except Exception as e:
            print(f"❌ Failed to parse {self.url}, Error: {e}")
            return None


class NewsParser:
    """Manages news parsing with multi-threaded concurrency."""

    def __init__(self, article_dict, max_workers=5):
        """
        Initializes the parser with article data and threading settings.

        Args:
            article_dict (dict): Dictionary containing categories and their article URLs.
            max_workers (int): Number of threads to use for concurrent parsing.
        """
        self.article_dict = article_dict  # Article data
        self.max_workers = max_workers
        self.content_cache = {}  # Cache for parsed content

    def parse_article(self, url):
        """Parses a single article with caching to prevent redundant requests."""
        if url in self.content_cache:
            print(f"✅ Cache hit: {url}")
            return self.content_cache[url]

        article = NewsArticle(url)
        article_data = article.parse()

        if article_data:
            self.content_cache[url] = article_data  # Store result in cache
        return article_data

    def parse_all_articles(self):
        """Parses all articles concurrently using a thread pool.

        Returns:
            dict: Dictionary where keys are category names, values are lists of parsed articles.
        """
        parsed_results = {}

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_url = {
                executor.submit(self.parse_article, url): (category, url)
                for category, urls in self.article_dict.items()
                for url in urls
            }

            for future in as_completed(future_to_url):
                category, article_url = future_to_url[future]
                try:
                    article_data = future.result()
                    if article_data:
                        if category not in parsed_results:
                            parsed_results[category] = []
                        parsed_results[category].append(article_data)
                except Exception as e:
                    print(f"❌ Failed to parse article {article_url}: {e}")

        return parsed_results


# 🚀 **Run the parser**
if __name__ == "__main__":
    # ✅ Example article data
    article_data = {
        "Earth": [
            "https://www.bbc.com/news/articles/czrnyde158po",
            "https://www.bbc.com/news/articles/c70ekknr2rwo",
            "https://www.bbc.com/future/article/20250227-the-vermont-farmers-using-urine-to-grow-their-crops",
            "https://www.bbc.com/news/articles/cvgeqw601eyo",
            "https://www.bbc.com/news/articles/c0q18gkegjpo",
            "https://www.bbc.com/future/article/20250219-kirby-misperton-the-former-fracking-site-now-tapped-for-clean-heat",
            "https://www.bbc.com/future/article/20250221-the-women-protecting-snow-leopards-in-remotest-nepal",
            "https://www.bbc.com/news/articles/cq8y3xgkpw9o",
            "https://www.bbc.com/future/article/20250303-the-worlds-strongest-ocean-current-is-at-risk",
            "https://www.bbc.com/news/articles/czedpnen168o",
            "https://www.bbc.com/news/articles/c3e4nlxlq08o",
            "https://www.bbc.com/news/articles/cg5ddnmnypvo",
            "https://www.bbc.com/news/articles/cddymq71zq5o",
            "https://www.bbc.com/news/articles/cj3nlrjnn0vo",
            "https://www.bbc.com/news/articles/cpv4m3x1ldgo",
            "https://www.bbc.com/news/articles/c4g0pz0wqp9o",
            "https://www.bbc.com/future/article/20250305-what-is-the-most-sustainable-period-product",
            "https://www.bbc.com/news/articles/c2erkry8jn8o"
        ]
    }

    print("\n📄 Parsing all articles...")
    parser = NewsParser(article_data)
    parsed_articles = parser.parse_all_articles()
    print("\n✅ Article parsing completed!")

    # 🔹 Display the parsed results
    for category, articles in parsed_articles.items():
        print(f"\n📢 Category: {category}")
        for article in articles:
            print(f"🔹 Title: {article['title']}")
            print(f"📅 Publish Date: {article['publish_date']}")
            print(f"🔗 URL: {article['url']}")
            print(f"📖 Content: {article['content'][:200]}...\n")  # Display first 200 characters
