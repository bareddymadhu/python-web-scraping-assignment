from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper

class BooksScraper(BaseScraper):
    START_URL = "https://books.toscrape.com/"

    def scrape(self):
        url = self.START_URL
        page = 1
        while url:
            self.logger.info("Books page %d: %s", page, url)
            response = self.fetch(url)
            if response is None:
                break
            soup = BeautifulSoup(response.text, "lxml")
            for article in soup.select("article.product_pod"):
                try:
                    link = article.select_one("h3 > a")
                    price = article.select_one("p.price_color")
                    rating = article.select_one("p.star-rating")
                    availability = article.select_one("p.instock")
                    if not link:
                        self.logger.warning("Book record missing title/link on %s", url)
                        continue
                    classes = rating.get("class", []) if rating else []
                    rating_word = next((x for x in classes if x.lower() in {"one", "two", "three", "four", "five"}), None)
                    yield {
                        "source": "Books to Scrape",
                        "source_url": urljoin(url, link.get("href", "")) if link.get("href") else None,
                        "name_or_title": link.get("title") or link.get_text(" ", strip=True),
                        "category": None,
                        "price": price.get_text(" ", strip=True) if price else None,
                        "rating": rating_word,
                        "author": None,
                        "tags": None,
                        "description": None,
                        "availability": availability.get_text(" ", strip=True) if availability else None,
                        "scraped_at": datetime.now(timezone.utc).isoformat(),
                    }
                except Exception as exc:
                    self.logger.warning("Book parsing error on %s: %s", url, exc)
            next_link = soup.select_one("li.next > a")
            url = urljoin(url, next_link.get("href")) if next_link and next_link.get("href") else None
            page += 1
