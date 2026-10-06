import logging
import time
from typing import Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class BaseScraper:
    def __init__(self, delay: float = 0.5, timeout: int = 15):
        self.delay = delay
        self.timeout = timeout
        self.logger = logging.getLogger(self.__class__.__name__)
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "ScrapingAssignment/1.0 (learning project)"})
        retries = Retry(
            total=3,
            connect=3,
            read=3,
            backoff_factor=1.0,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def fetch(self, url: str) -> Optional[requests.Response]:
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            response.encoding = "utf-8"
            time.sleep(self.delay)
            return response
        except requests.RequestException as exc:
            self.logger.error("Failed request: %s | %s", url, exc)
            return None
