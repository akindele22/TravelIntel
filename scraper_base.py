"""
Base Scraper for Travel Advisory Sites
Uses only HTTP requests + BeautifulSoup
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import config

class BaseScraper(ABC):
    """Base class for all scrapers using requests only"""

    def __init__(self, url: str):
        self.url = url
        self.ua = UserAgent()

    def get_random_user_agent(self) -> str:
        return self.ua.random

    def fetch_with_requests(self) -> Optional[BeautifulSoup]:
        """Fetch page using requests library"""
        headers = {
            'User-Agent': self.get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }

        try:
            response = requests.get(self.url, headers=headers, timeout=config.SCRAPER_CONFIG['timeout'])
            response.raise_for_status()
            return BeautifulSoup(response.content, 'lxml')
        except Exception as e:
            print(f"Error fetching {self.url}: {e}")
            return None

    @abstractmethod
    def parse(self, soup: BeautifulSoup) -> List[Dict]:
        """Parse scraped content - must be implemented by subclasses"""
        pass

    def scrape(self) -> List[Dict]:
        """Fetch + parse"""
        soup = self.fetch_with_requests()
        if soup:
            return self.parse(soup)
        return []
