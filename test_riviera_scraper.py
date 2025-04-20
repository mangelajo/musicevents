import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_scrape_riviera_events():
    """
    Test function to scrape events from Sala Riviera website
    """
    url = "https://salariviera.com/conciertossalariviera/"
    logger.info(f"Fetching events from {url}")
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Print the page title to verify we're getting the right page
        title = soup.title.text if soup.title else "No title found"
        logger.info(f"Page title: {title}")
        
        # Let's look for event links and extract information from them
        event_links = soup.find_all('a', href=lambda h: h and 'concierto' in h.lower())
        logger.info(f"Found {len(event_links)} links with 'concierto' in href")
        
        # Create a set to store unique event URLs
        unique_event_urls = set()
        
        # Extract unique event URLs
        for link in event_links:
            url = link.get('href')
            if url:
                unique_event_urls.add(url)
        
        logger.info(f"Found {len(unique_event_urls)} unique event URLs")
        
        # Process each unique event URL
        events = []
        for i, url in enumerate(list(unique_event_urls)[:5]):  # Process first 5 for testing
            logger.info(f"Processing event URL {i+1}: {url}")
            
            # Extract event information from URL
            event_info = extract_event_info_from_url(url)
            if event_info:
                events.append(event_info)
                logger.info(f"Extracted event: {event_info['title']} on {event_info.get('date', 'Unknown date')}")
        
        # Look for event information in the page content
        # Try to find event blocks
        event_blocks = soup.find_all('div', class_=lambda c: c and 'et_pb_module' in c)
        logger.info(f"Found {len(event_blocks)} potential event blocks")
        
        # Try to extract event information from these blocks
        for i, block in enumerate(event_blocks[:10]):  # Check first 10 blocks
            # Look for title
            title_elem = block.find(['h1', 'h2', 'h3', 'h4'])
            if title_elem:
                title = title_elem.text.strip()
                
                # Look for date
                date_text = None
                date_elem = block.find(string=lambda s: s and re.search(r'\d{1,2}/\d{1,2}/\d{4}|\d{1,2}-\d{1,2}-\d{4}', s))
                if date_elem:
                    date_text = date_elem.strip()
                
                # Look for link
                link = None
                link_elem = block.find('a')
                if link_elem:
                    link = link_elem.get('href')
                
                logger.info(f"Potential event in block {i+1}: Title: {title}, Date: {date_text}, Link: {link}")
        
        # Try to find event information in the page's structured data
        structured_data = extract_structured_data(soup)
        if structured_data:
            logger.info(f"Found {len(structured_data)} structured data items")
            for i, data in enumerate(structured_data):
                logger.info(f"Structured data {i+1}: {json.dumps(data, indent=2)}")
        
        # Try to find event information in iframes
        iframes = soup.find_all('iframe')
        logger.info(f"Found {len(iframes)} iframes")
        for i, iframe in enumerate(iframes[:3]):
            src = iframe.get('src', '')
            logger.info(f"Iframe {i+1} source: {src}")
            
            # If the iframe is from a known event provider, we might need to scrape it separately
            if 'wegow.com' in src or 'ticketmaster' in src:
                logger.info(f"Found event provider iframe: {src}")
        
        return True
    except Exception as e:
        logger.error(f"Error scraping Sala Riviera website: {e}")
        return False

def extract_event_info_from_url(url):
    """
    Extract event information from the URL
    """
    try:
        # Extract event name from URL
        match = re.search(r'conciertos/([^/]+)', url)
        if match:
            event_slug = match.group(1)
            # Convert slug to title (replace hyphens with spaces and capitalize words)
            title = ' '.join(word.capitalize() for word in event_slug.split('-'))
            
            # Try to extract date from URL or title
            date_match = re.search(r'(\d{1,2}[-/]\d{1,2}[-/]\d{4})', url)
            date = date_match.group(1) if date_match else None
            
            # Extract venue
            venue = "Sala Riviera" if "riviera" in url.lower() else None
            
            return {
                'title': title,
                'date': date,
                'venue': venue,
                'url': url
            }
    except Exception as e:
        logger.error(f"Error extracting event info from URL {url}: {e}")
    
    return None

def extract_structured_data(soup):
    """
    Extract structured data (JSON-LD) from the page
    """
    structured_data = []
    
    # Look for JSON-LD scripts
    scripts = soup.find_all('script', type='application/ld+json')
    for script in scripts:
        try:
            data = json.loads(script.string)
            structured_data.append(data)
        except Exception as e:
            logger.error(f"Error parsing JSON-LD: {e}")
    
    return structured_data

if __name__ == "__main__":
    test_scrape_riviera_events()