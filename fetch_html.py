import time
import io
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument('--headless')
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    print("Fetching E-Brandon...")
    driver.get("https://ebrandon.ca/events.aspx")
    time.sleep(3)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    with io.open('temp_ebrandon.html', 'w', encoding='utf-8') as f:
        f.write(soup.prettify())
finally:
    driver.quit()
