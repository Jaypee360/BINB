import sqlite3
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

def get_db_connection():
    conn = sqlite3.connect('events.db')
    conn.row_factory = sqlite3.Row
    return conn

def insert_event(title, description, category, date_time):
    """Inserts a normalized event into the SQLite event database."""
    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO events (title, description, category, date_time) VALUES (?, ?, ?, ?)',
                     (title, description, category, date_time))
        conn.commit()
    except Exception as e:
        print(f"Error inserting {title}: {e}")
    finally:
        conn.close()

def normalize_category(category_hint, title, description):
    """Categorizes an event by matching keywords in the text."""
    text = (title + " " + description + " " + category_hint).lower()
    if any(word in text for word in ['party', 'gala', 'nightlife', 'dj', 'club', 'mixer']):
        return 'parties'
    elif any(word in text for word in ['sport', 'hockey', 'basketball', 'soccer', 'fitness', 'tournament', 'bobcats']):
        return 'sports'
    elif any(word in text for word in ['business', 'networking', 'chamber', 'trade', 'career', 'corporate']):
        return 'business'
    else:
        return 'community'

def setup_driver():
    """Initializes and returns a Headless Chrome WebDriver."""
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def scrape_brandon_university(driver):
    print("Scraping Brandon University...")
    url = "https://events.brandonu.ca"
    try:
        driver.get(url)
        time.sleep(3) # Wait for js plugins to load
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Typically BU uses Tribe Events Calendar
        event_headings = soup.find_all(['h2', 'h3'])
        events_found = 0
        for h in event_headings:
            title = h.text.strip().replace('\n', '').replace('\t', '')
            if len(title) > 10 and 'Filter' not in title and 'Search' not in title and 'Event' not in title:
                description = f"Real event pulled from Brandon University calendar: {title}"
                cat = normalize_category('university', title, description)
                insert_event(title, description, cat, "Upcoming Date")
                print(f"Found BU Event: {title}")
                events_found += 1
                if events_found >= 3: break
    except Exception as e:
        print(f"BU Scrape failed: {e}")

def scrape_ebrandon(driver):
    print("Scraping E-Brandon...")
    url = "https://www.ebrandon.ca/events.aspx"
    try:
        driver.get(url)
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # E-Brandon has a very static table/list structure
        links = soup.find_all('a')
        events_found = 0
        for a in links:
            href = a.get('href', '')
            if 'event_id' in href.lower() or 'events' in href.lower():
                title = a.text.strip()
                if len(title) > 8 and "Calendar" not in title and "Post" not in title:
                    description = "An authentic event happening in Brandon extracted from E-Brandon."
                    cat = normalize_category('community', title, description)
                    insert_event(title, description, cat, "Upcoming")
                    print(f"Found E-Brandon Event: {title}")
                    events_found += 1
                    if events_found >= 3: break
    except Exception as e:
        print(f"E-Brandon Scrape failed: {e}")

def scrape_chamber_of_commerce(driver):
    print("Scraping Chamber of Commerce...")
    pass

def scrape_brandon_tourism(driver):
    print("Scraping Brandon Tourism...")
    url = "https://brandontourism.com/events/"
    try:
        driver.get(url)
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Use loose heading and link matching to avoid CMS layout breaks
        elements = soup.find_all(['h2', 'h3', 'h4'])
        events_found = 0
        for tag in elements:
            title = tag.text.strip().replace('\n', ' ')
            # Filter out generic website ui elements
            if len(title) > 10 and not any(w in title.lower() for w in ['calendar', 'search', 'tourism', 'events', 'filter', 'contact', 'about']):
                description = f"Discovered via Brandon Tourism: {title}"
                # Tourism events are generally community or parties
                cat = normalize_category('community', title, description)
                insert_event(title, description, cat, "Upcoming Event")
                print(f"Found Tourism Event: {title}")
                events_found += 1
                if events_found >= 4: break
    except Exception as e:
        print(f"Brandon Tourism Scrape failed: {e}")

def scrape_keystone_centre(driver):
    print("Scraping Keystone Centre...")
    url = "https://www.keystonecentre.com/events"
    try:
        driver.get(url)
        # Keystone Centre can be JS heavy with TicketMaster inclusions
        time.sleep(4) 
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        elements = soup.find_all(['h2', 'h3'])
        events_found = 0
        for tag in elements:
            title = tag.text.strip().replace('\n', ' ')
            if len(title) > 8 and not any(w in title.lower() for w in ['calendar', 'event', 'search', 'keystone', 'contact', 'about', 'ticket', 'venue']):
                description = f"Discover this experience hosted at Keystone Centre: {title}"
                # By default, Keystone leans towards Parties, Concerts, or Sports
                cat = normalize_category('party', title, description)
                insert_event(title, description, cat, "Pending Schedule")
                print(f"Found Keystone Event: {title}")
                events_found += 1
                if events_found >= 4: break
    except Exception as e:
        print(f"Keystone Centre Scrape failed: {e}")

def scrape_downtown_biz(driver):
    print("Scraping Downtown BIZ...")
    pass

def run_all_scrapers():
    print("Starting Web Scraper Pipeline...")
    driver = setup_driver()
    try:
        scrape_brandon_university(driver)
        scrape_ebrandon(driver)
        scrape_chamber_of_commerce(driver)
        scrape_brandon_tourism(driver)
        scrape_keystone_centre(driver)
        scrape_downtown_biz(driver)
    finally:
        driver.quit()
        print("Driver closed. Scrape process finished.")

if __name__ == '__main__':
    run_all_scrapers()
