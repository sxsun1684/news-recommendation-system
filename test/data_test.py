# from fetch_article_links import fetch_all_articles
#
# # ✅ Retain only the "Earth" category from the fetched article links
# filtered_data = {"Earth": fetch_all_articles().get("Earth", [])}
#
# # ✅ Print the final filtered result
# print(filtered_data)

import re
from playwright.sync_api import sync_playwright
import requests
from bs4 import BeautifulSoup

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
        self.publish_date = self.extract_date_from_url()  # 先尝试从 URL 解析

    def extract_date_from_url(self):
        """尝试从 URL 提取日期，如果失败则返回 'Unknown Date'"""
        match = re.search(r'/(\d{8})-', self.url)  # 识别 8 位日期 (e.g., 20250306)
        if match:
            date_str = match.group(1)
            return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"  # 转换为 YYYY-MM-DD
        return "Unknown Date"

    def fetch_publish_date(self):
        """Playwright 爬取发布时间，仅在 URL 解析失败时调用"""
        if self.publish_date != "Unknown Date":
            return  # 如果 URL 解析成功，跳过 Playwright 爬取

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            try:
                page.goto(self.url, wait_until="domcontentloaded", timeout=5000)
                time_tag = page.query_selector("time")
                if time_tag:
                    self.publish_date = time_tag.get_attribute("datetime") or "Not Found"
            except Exception as e:
                print(f"❌ Failed to fetch publish date for {self.url}: {e}")
            finally:
                browser.close()

    def parse(self):
        """解析文章的标题和内容"""
        try:
            response = requests.get(self.url, headers=HEADERS, timeout=10)
            if response.status_code != 200:
                print(f"❌ Failed to access: {self.url}")
                return None

            soup = BeautifulSoup(response.text, "html.parser")

            # 提取标题
            title_tag = soup.find("h1")
            self.title = title_tag.get_text(strip=True) if title_tag else "No title found"

            # 提取文章内容（限制 500 字）
            paragraphs = soup.find_all("p")
            self.content = "\n".join([p.get_text(strip=True) for p in paragraphs])[:500]

            return {
                "title": self.title,
                "url": self.url,
                "publish_date": self.publish_date,  # 先 URL 解析，再 Playwright 兜底
                "content": self.content
            }
        except Exception as e:
            print(f"❌ Failed to parse {self.url}, Error: {e}")
            return None


# ✅ **测试代码**
if __name__ == "__main__":
    test_urls = [
        "https://www.bbc.com/news/articles/cly3mn5kykzo",
        "https://www.bbc.com/future/article/20250306-the-future-of-conservation-might-be-in-vr-headsets",
        "https://www.bbc.com/news/articles/cy87y0pwv95o",
        "https://www.bbc.com/travel/article/20250307-the-art-curator-saving-the-worlds-rarest-fruit",
        "https://www.bbc.com/future/article/20250311-the-women-fighting-indias-worm-poachers",
        "https://www.bbc.com/news/articles/c9de972w8wvo",
        "https://www.bbc.com/future/article/20240905-have-we-improved-oil-spill-clean-ups-since-bp-deepwater-horizon",
        "https://www.bbc.com/news/articles/cd65wqnyzyxo",
        "https://www.bbc.com/future/article/20250305-what-is-the-most-sustainable-period-product",
        "https://www.bbc.com/future/article/20250303-the-worlds-strongest-ocean-current-is-at-risk",
        "https://www.bbc.com/future/article/20250310-the-divers-venturing-under-the-ice-in-the-name-of-science",
        "https://www.bbc.com/future/article/20250227-the-vermont-farmers-using-urine-to-grow-their-crops",
        "https://www.bbc.com/news/articles/cwyd1j0q5wwo",
        "https://www.bbc.com/future/article/20250228-how-italy-and-chile-foiled-an-1m-international-smugglers-cactus-heist",
        "https://www.bbc.com/news/articles/cg5ddnmnypvo",
        "https://www.bbc.com/news/articles/c3e4nlxlq08o",
        "https://www.bbc.com/news/articles/cd65x1wg22jo"
    ]


    for url in test_urls:
        article = NewsArticle(url)
        article.fetch_publish_date()  # 确保发布时间被 Playwright 获取
        article_data = article.parse()

        print("\n📄 **文章解析结果**:")
        print(f"🔹 标题: {article_data['title']}")
        print(f"📅 发布时间: {article_data['publish_date']}")
        print(f"🔗 网址: {article_data['url']}")
        print(f"📖 内容: {article_data['content'][:200]}...")  # 显示前 200 个字符
