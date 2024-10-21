# BBC (News source URL)
NEWS_SOURCES = [
    'https://www.bbc.com/news'
]

# Request headers to avoid being blocked by anti-scraping mechanisms
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Set crawl interval time
CRAWL_INTERVAL = 3600  # Fetch every 1 hour

