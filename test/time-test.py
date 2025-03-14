import asyncio
import time
from playwright.async_api import async_playwright

# 最大并发数，控制任务数量，防止资源占用过高
MAX_CONCURRENT_TASKS = 10
semaphore = asyncio.Semaphore(MAX_CONCURRENT_TASKS)

async def fetch_bbc_article_datetime(url, browser):
    """爬取单个 BBC 文章的发布时间"""
    async with semaphore:  # 控制并发数，防止系统崩溃
        page = await browser.new_page()

        # 禁用图片、CSS、JS，提高加载速度
        await page.route("**/*.{png,jpg,jpeg,gif,svg,css,js}", lambda route: route.abort())

        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=8000)  # 8 秒超时
            await page.wait_for_selector("time", timeout=3000)  # 最多等待 3 秒
            date_element = await page.query_selector("time")
            publication_date = await date_element.get_attribute("datetime") if date_element else "Not Found"
        except Exception as e:
            publication_date = f"Error: {str(e)}"
        finally:
            await page.close()

        return {"url": url, "publication_date": publication_date}

async def main():
    urls = [
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

    start_time = time.time()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])

        # 并发执行任务
        tasks = [fetch_bbc_article_datetime(url, browser) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)  # 防止异常导致程序中断

        await browser.close()

    end_time = time.time()
    execution_time = end_time - start_time

    # 输出爬取结果
    for result in results:
        print(result)

    print(f"总运行时间: {execution_time:.2f} 秒")

if __name__ == "__main__":
    asyncio.run(main())
