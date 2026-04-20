import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
import os

BASE_URL = "https://www.dwavequantum.com/"
START_URL = "https://www.dwavequantum.com/learn/resource-library/quantum-optimization-fit-ebook/?banner="
KEYWORDS = ["parallel processing", "pattern recognition", "quantum computing", "company"]
VISITED_URLS = set()
SCRAPED_DATA = []

def is_valid_url(url):
    parsed = urlparse(url)
    return parsed.netloc == "www.dwavequantum.com" or parsed.netloc == ""

def scrape_page(url, depth=0, max_depth=2):
    if url in VISITED_URLS or depth > max_depth:
        return
    VISITED_URLS.add(url)
    print(f"Scraping: {url} at depth {depth}")

    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return

        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract full text
        paragraphs = soup.find_all('p')
        full_text = "\n".join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])

        # Find matching sentences/paragraphs
        matched_content = []
        for p in paragraphs:
            text = p.get_text(strip=True).lower()
            if any(keyword in text for keyword in KEYWORDS):
                matched_content.append(p.get_text(strip=True))

        if full_text:
            SCRAPED_DATA.append({
                "url": url,
                "full_text": full_text,
                "matched_content": "\n---\n".join(matched_content) if matched_content else ""
            })

        # Find links
        if depth < max_depth:
            for link in soup.find_all('a', href=True):
                next_url = urljoin(url, link['href'])
                if is_valid_url(next_url):
                    # Clean URL (remove fragments)
                    clean_url = next_url.split('#')[0]
                    if clean_url not in VISITED_URLS:
                         scrape_page(clean_url, depth + 1, max_depth)

    except Exception as e:
        print(f"Error scraping {url}: {e}")

if __name__ == "__main__":
    scrape_page(START_URL, max_depth=2)
    with open("scraped_data.json", "w") as f:
        json.dump(SCRAPED_DATA, f, indent=4)
    print(f"Scraping complete. Found {len(SCRAPED_DATA)} pages with content.")
