# Web Scraper — Quotes to Scrape

A simple Python web scraper built with `requests` + `BeautifulSoup` that crawls
[quotes.toscrape.com](http://quotes.toscrape.com) (a sandbox site built for
scraping practice), follows pagination automatically, and saves the results
in structured **CSV** and **JSON** format.

## Features

- Fetches and parses HTML with `requests` + `BeautifulSoup`
- Automatically follows "Next page" pagination links
- Rate-limited requests (1 second delay) to be polite to the server
- Handles request failures and malformed HTML gracefully
- Exports structured data to both `quotes.csv` and `quotes.json`

## Setup

```bash
git clone https://github.com/<your-username>/web-scraper-quotes.git
cd web-scraper-quotes
pip install -r requirements.txt
```

## Usage

```bash
python scraper_bs4.py
```

This will scrape up to 5 pages (configurable) and produce:

- `quotes.csv` — spreadsheet-friendly output
- `quotes.json` — structured JSON output

## Configuration

Edit the constants near the top of `scraper_bs4.py`:

| Variable         | Description                                      |
|------------------|---------------------------------------------------|
| `TARGET_URL`     | Starting URL to scrape                             |
| `REQUEST_DELAY`  | Seconds to wait between requests                   |
| `max_pages`      | Set in the `scrape_all()` call at the bottom; `None` = scrape all pages |

## Adapting to another site

1. Change `TARGET_URL` to your target site.
2. Inspect the target page's HTML (browser dev tools → Inspect) to find the
   right tags/classes.
3. Update the CSS selectors in `parse_page()` to match.
4. Check the target site's `robots.txt` and terms of service before scraping.

## Project structure

```
web-scraper-quotes/
├── scraper_bs4.py      # main scraper script
├── requirements.txt    # Python dependencies
├── .gitignore
└── README.md
```

## License

MIT
