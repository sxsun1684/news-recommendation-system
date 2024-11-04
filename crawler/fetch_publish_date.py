from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from multiprocessing import Process

# set Selenium WebDriver
def create_webdriver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 无头模式
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=chrome_options)

# fetch_publish_date
def fetch_publish_date(article_url):
    driver = create_webdriver()
    try:
        driver.get(article_url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "time"))
        )
        time_element = driver.find_element(By.TAG_NAME, "time")
        publish_date = time_element.text
        # print(f"Publish Date for {article_url}: {publish_date}")
        return publish_date
    except TimeoutException:
        # print(f"Timeout occurred for {article_url}")
        return "Timeout"
    except Exception as e:
        return f"Error fetching publish date for {article_url}: {e}"
    finally:
        driver.quit()


def start_fetch_process(article_url):
    process = Process(target=fetch_publish_date, args=(article_url,))
    process.start()
    process.join()