from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper

class QuotesScraper(BaseScraper):
    START_URL = "https://quotes.toscrape.com/"

    def scrape(self):
        url = self.START_URL
        page = 1
        while url:
            self.logger.info("Quotes page %d: %s", page, url)
            response = self.fetch(url)
            if response is None:
                break
            soup = BeautifulSoup(response.text, "lxml")
            for quote in soup.select("div.quote"):
                try:
                    text = quote.select_one("span.text")
                    author = quote.select_one("small.author")
                    tags = quote.select("a.tag")
                    if not text or not author:
                        self.logger.warning("Quote record missing text/author on %s", url)
                        continue
                    yield {
                        "source": "Quotes to Scrape",
                        "source_url": url,
                        "name_or_title": text.get_text(" ", strip=True),
                        "category": None,
                        "price": None,
                        "rating": None,
                        "author": author.get_text(" ", strip=True),
                        "tags": [t.get_text(" ", strip=True) for t in tags],
                        "description": None,
                        "availability": None,
                        "scraped_at": datetime.now(timezone.utc).isoformat(),
                    }
                except Exception as exc:
                    self.logger.warning("Quote parsing error on %s: %s", url, exc)
            next_link = soup.select_one("li.next > a")
            url = urljoin(url, next_link.get("href")) if next_link and next_link.get("href") else None
            page += 1
