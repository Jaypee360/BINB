import sqlite3
import time
import re
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

def extract_datetime(soup_element):
    """Attempt to extract date/time patterns from text within or around the element."""
    text = soup_element.text.strip().replace('\n', ' ').replace('\xa0', ' ')
    if soup_element.parent:
        text += " " + soup_element.parent.text.strip().replace('\n', ' ').replace('\xa0', ' ')
        
    date_patterns = [
        r"\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2}(?:st|nd|rd|th)?(?:,?\s+\d{4})?\b",
        r"\b\d{4}-\d{2}-\d{2}\b",
        r"\b\d{1,2}:\d{2}\s*(?:am|pm|AM|PM)?\b"
    ]
    
    found_parts = []
    for pattern in date_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            val = match.group(0).strip()
            if val not in found_parts:
                found_parts.append(val)
                
    if found_parts:
        return " - ".join(found_parts[:2])
    return "Check Website for Schedule"


def get_db_connection():
    conn = sqlite3.connect('events.db')
    conn.row_factory = sqlite3.Row
    return conn

def within_next_14_days(date_str):
    today = datetime.now()
    limit_date = today + timedelta(days=14)
    
    match = re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{1,2})', date_str, re.IGNORECASE)
    if match:
        month_str = match.group(1)[:3].capitalize()
        day = int(match.group(2))
        
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        try:
            month_num = months.index(month_str) + 1
            event_date = datetime(today.year, month_num, day)
            
            # If the event month is early in the year and we are in Nov/Dec, it's presumably next year
            if event_date.month < today.month and today.month >= 11:
                event_date = event_date.replace(year=today.year + 1)
                
            # Allow dates from today up to 14 days from now
            return today.date() <= event_date.date() <= limit_date.date()
        except ValueError:
            pass
            
    # Keep unstructured dates like 'Pending Schedule' per user request
    return True 

def insert_event(title, description, category, date_time):
    """Inserts a normalized event into the SQLite event database."""
    if not within_next_14_days(date_time):
        print(f"  -> Skipping {title}: '{date_time}' is beyond the 14-day cutoff.")
        return
        
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
        
        event_headings = soup.find_all(['h2', 'h3'])
        event_links = []
        for h in event_headings:
            title = h.text.strip().replace('\n', '').replace('\t', '')
            if len(title) > 10 and 'Filter' not in title and 'Search' not in title and 'Event' not in title:
                a_tag = h.find('a') if h.name != 'a' else h
                if not a_tag and h.parent and h.parent.name == 'a':
                    a_tag = h.parent
                href = a_tag.get('href') if a_tag else None
                
                event_links.append({"title": title, "href": href})
                if len(event_links) >= 3: break
                
        for event in event_links:
            title = event['title']
            description = f"Real event pulled from Brandon University calendar: {title}"
            cat = normalize_category('university', title, description)
            
            if event['href']:
                try:
                    driver.get(event['href'])
                    time.sleep(1)
                    detail_soup = BeautifulSoup(driver.page_source, 'html.parser')
                    date_val = extract_datetime(detail_soup.body)
                except Exception:
                    date_val = "Upcoming Date"
            else:
                date_val = "Upcoming Date"
                
            if date_val == "Check Website for Schedule":
                date_val = "Upcoming Date"
                
            insert_event(title, description, cat, date_val)
            print(f"Found BU Event (Deep): {title}")
            
    except Exception as e:
        print(f"BU Scrape failed: {e}")

def scrape_ebrandon(driver):
    print("Scraping E-Brandon...")
    url = "https://www.ebrandon.ca/events.aspx"
    try:
        driver.get(url)
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        links = soup.find_all('a')
        event_links = []
        for a in links:
            href = a.get('href', '')
            if 'event_id' in href.lower() or 'events' in href.lower():
                title = a.text.strip()
                if len(title) > 8 and "Calendar" not in title and "Post" not in title:
                    if href.startswith('event.aspx'):
                        href = "https://www.ebrandon.ca/" + href
                    event_links.append({"title": title, "href": href})
                    if len(event_links) >= 3: break
                    
        for event in event_links:
            title = event['title']
            description = "An authentic event happening in Brandon extracted from E-Brandon."
            cat = normalize_category('community', title, description)
            
            if event['href']:
                try:
                    driver.get(event['href'])
                    time.sleep(1)
                    detail_soup = BeautifulSoup(driver.page_source, 'html.parser')
                    date_val = extract_datetime(detail_soup.body)
                except Exception:
                    date_val = "Upcoming Event"
            else:
                date_val = "Upcoming Event"
                
            if date_val == "Check Website for Schedule":
                date_val = "Upcoming Event"
                
            insert_event(title, description, cat, date_val)
            print(f"Found E-Brandon Event (Deep): {title}")
            
    except Exception as e:
        print(f"E-Brandon Scrape failed: {e}")

def scrape_chamber_of_commerce(driver):
    print("Scraping Chamber of Commerce...")
    url = "https://members.brandonchamber.ca/events"
    try:
        driver.get(url)
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # ChamberMaster / GrowthZone structure
        links = soup.find_all('a')
        event_links = []
        for a in links:
            href = a.get('href', '')
            if '/events/details/' in href:
                title = a.text.strip().replace('\n', ' ')
                if title and len(title) > 5:
                    if href.startswith('/'):
                        href = "https://members.brandonchamber.ca" + href
                    
                    # Prevent duplicates
                    if not any(e['href'] == href for e in event_links):
                        event_links.append({"title": title, "href": href})
                    if len(event_links) >= 4: break

        for event in event_links:
            title = event['title']
            description = f"Local business event promoted by the Chamber of Commerce: {title}"
            cat = "business"  # Hardcoded per user request
            
            if event['href']:
                try:
                    driver.get(event['href'])
                    time.sleep(2)
                    detail_soup = BeautifulSoup(driver.page_source, 'html.parser')
                    date_val = extract_datetime(detail_soup.body)
                except Exception as e:
                    print(f"Deep scrape failed for {title}: {e}")
                    date_val = "Upcoming Event"
            else:
                date_val = "Upcoming Event"
                
            if date_val == "Check Website for Schedule":
                date_val = "Upcoming Event"
                
            insert_event(title, description, cat, date_val)
            print(f"Found Chamber Event (Deep): {title}")

    except Exception as e:
        print(f"Chamber of Commerce Scrape failed: {e}")

def scrape_brandon_tourism(driver):
    print("Scraping Brandon Tourism...")
    url = "https://brandontourism.com/events/"
    try:
        driver.get(url)
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        elements = soup.find_all(['h2', 'h3', 'h4'])
        event_links = []
        for tag in elements:
            title = tag.text.strip().replace('\n', ' ')
            if len(title) > 10 and not any(w in title.lower() for w in ['calendar', 'search', 'tourism', 'events', 'filter', 'contact', 'about']):
                a_tag = tag.find('a') if tag.name != 'a' else tag
                if not a_tag and tag.parent and tag.parent.name == 'a':
                    a_tag = tag.parent
                href = a_tag.get('href') if a_tag else None
                
                event_links.append({"title": title, "href": href})
                if len(event_links) >= 3: break
                
        for event in event_links:
            title = event['title']
            description = f"Discovered via Brandon Tourism: {title}"
            cat = normalize_category('community', title, description)
            
            if event['href']:
                try:
                    driver.get(event['href'])
                    time.sleep(1)
                    detail_soup = BeautifulSoup(driver.page_source, 'html.parser')
                    date_val = extract_datetime(detail_soup.body)
                except Exception:
                    date_val = "Upcoming Event"
            else:
                date_val = "Upcoming Event"
                
            if date_val == "Check Website for Schedule":
                date_val = "Upcoming Event"
            
            insert_event(title, description, cat, date_val)
            print(f"Found Tourism Event (Deep): {title}")
            
    except Exception as e:
        print(f"Brandon Tourism Scrape failed: {e}")

def scrape_keystone_centre(driver):
    print("Scraping Keystone Centre...")
    url = "https://www.keystonecentre.com/events"
    try:
        driver.get(url)
        time.sleep(4) 
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        elements = soup.find_all(['h2', 'h3'])
        event_links = []
        for tag in elements:
            title = tag.text.strip().replace('\n', ' ')
            if len(title) > 8 and not any(w in title.lower() for w in ['calendar', 'event', 'search', 'keystone', 'contact', 'about', 'ticket', 'venue']):
                a_tag = tag.find('a') if tag.name != 'a' else tag
                if not a_tag and tag.parent and tag.parent.name == 'a':
                    a_tag = tag.parent
                
                href = a_tag.get('href') if a_tag else None
                if href and href.startswith('/'):
                    href = "https://www.keystonecentre.com" + href
                
                event_links.append({"title": title, "href": href})
                if len(event_links) >= 3: break
                
        for event in event_links:
            title = event['title']
            description = f"Discover this experience hosted at Keystone Centre: {title}"
            cat = normalize_category('party', title, description)
            
            if event['href']:
                try:
                    driver.get(event['href'])
                    time.sleep(2)
                    detail_soup = BeautifulSoup(driver.page_source, 'html.parser')
                    date_val = extract_datetime(detail_soup.body)
                except Exception as e:
                    print(f"Deep scrape failed for {title}: {e}")
                    date_val = "Pending Schedule"
            else:
                date_val = "Pending Schedule"
                
            if date_val == "Check Website for Schedule":
                date_val = "Pending Schedule"
            
            insert_event(title, description, cat, date_val)
            print(f"Found Keystone Event (Deep): {title}")
            
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
