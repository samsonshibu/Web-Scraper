"""
Web scraper using requests + BeautifulSoup.

Target: http://quotes.toscrape.com  (a sandbox site built for scraping practice)
Swap TARGET_URL and the parsing logic in `parse_page()` for a real target site.

Usage:
    pip install -r requirements.txt
    python scraper_bs4.py
"""

import csv
import json
import time
import logging
from dataclasses import dataclass, asdict
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
BASE_URL = "http://quotes.toscrape.com"
TARGET_URL = BASE_URL + "/page/1/"
REQUEST_DELAY = 1.0          # seconds between requests — be polite to the server
TIMEOUT = 10                 # seconds
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; MyScraper/1.0; +https://example.com/bot)"
}

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------
@dataclass
class Quote:
    text: str
    author: str
    tags: str  # comma-separated for easy CSV storage


# ---------------------------------------------------------------------------
# Core scraping logic
# ---------------------------------------------------------------------------
def fetch_page(url: str) -> BeautifulSoup | None:
    """Fetch a URL and return a parsed BeautifulSoup object, or None on failure."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as exc:
        log.error("Failed to fetch %s: %s", url, exc)
        return None
    return BeautifulSoup(response.text, "html.parser")


def parse_page(soup: BeautifulSoup) -> list[Quote]:
    """Extract structured records from a single page's soup."""
    records = []
    for block in soup.select("div.quote"):
        text_el = block.select_one("span.text")
        author_el = block.select_one("small.author")
        tag_els = block.select("div.tags a.tag")

        if not text_el or not author_el:
            continue  # skip malformed entries rather than crashing

        records.append(
            Quote(
                text=text_el.get_text(strip=True),
                author=author_el.get_text(strip=True),
                tags=", ".join(t.get_text(strip=True) for t in tag_els),
            )
        )
    return records


def get_next_page_url(soup: BeautifulSoup, current_url: str) -> str | None:
    """Find the 'Next' pagination link, if any."""
    next_link = soup.select_one("li.next a")
    if next_link and next_link.get("href"):
        return urljoin(current_url, next_link["href"])
    return None


def scrape_all(start_url: str, max_pages: int | None = None) -> list[Quote]:
    """Crawl through paginated pages, collecting records from each."""
    all_records: list[Quote] = []
    url = start_url
    page_count = 0

    while url:
        if max_pages and page_count >= max_pages:
            break

        log.info("Scraping: %s", url)
        soup = fetch_page(url)
        if soup is None:
            break

        page_records = parse_page(soup)
        log.info("  -> found %d records", len(page_records))
        all_records.extend(page_records)

        url = get_next_page_url(soup, url)
        page_count += 1
        time.sleep(REQUEST_DELAY)  # rate limiting

    return all_records


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------
def save_to_csv(records: list[Quote], filename: str) -> None:
    if not records:
        log.warning("No records to save to CSV.")
        return
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(asdict(records[0]).keys()))
        writer.writeheader()
        for r in records:
            writer.writerow(asdict(r))
    log.info("Saved %d records to %s", len(records), filename)


def save_to_json(records: list[Quote], filename: str) -> None:
    with open(filename, "w", encoding="utf-8") as f:
        json.dump([asdict(r) for r in records], f, indent=2, ensure_ascii=False)
    log.info("Saved %d records to %s", len(records), filename)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    results = scrape_all(TARGET_URL, max_pages=5)  # None = crawl all pages
    save_to_csv(results, "quotes.csv")
    save_to_json(results, "quotes.json")
    log.info("Done. Total records: %d", len(results))
