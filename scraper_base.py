"""
Base Scraper Class with Proxy Support
"""
import time
import random
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from fake_useragent import UserAgent
from playwright.sync_api import sync_playwright, Browser, Page, TimeoutError as PlaywrightTimeout
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import requests
from bs4 import BeautifulSoup
from proxy_manager import ProxyManager
import config


class BaseScraper(ABC):
    """Base class for all scrapers with proxy rotation support"""
    
    def __init__(self, url: str, proxy_manager: Optional[ProxyManager] = None, 
                 use_playwright: bool = True, use_selenium: bool = False):
        """
        Initialize base scraper
        
        Args:
            url: Target URL to scrape
            proxy_manager: ProxyManager instance for proxy rotation
            use_playwright: Use Playwright for scraping (default)
            use_selenium: Use Selenium for scraping (alternative)
        """
        self.url = url
        self.proxy_manager = proxy_manager
        self.use_playwright = use_playwright
        self.use_selenium = use_selenium
        self.ua = UserAgent()
        self.browser: Optional[Browser] = None
        self.driver = None
        self.playwright = None
        
    def get_random_user_agent(self) -> str:
        """Get random user agent"""
        return self.ua.random
    
    def setup_playwright(self) -> Browser:
        """Setup Playwright browser with proxy"""
        if not self.playwright:
            self.playwright = sync_playwright().start()
        
        proxy = None
        if self.proxy_manager:
            proxy_dict = self.proxy_manager.get_proxy()
            if proxy_dict:
                proxy_url = proxy_dict.get('http', '').replace('http://', '').replace('https://', '')
                if '@' in proxy_url:
                    auth, server = proxy_url.split('@')
                    username, password = auth.split(':')
                    host, port = server.split(':')
                    proxy = {
                        'server': f'http://{host}:{port}',
                        'username': username,
                        'password': password
                    }
        
        browser = self.playwright.chromium.launch(
            headless=config.SCRAPER_CONFIG['headless'],
            proxy=proxy
        )
        
        return browser
    
    def setup_selenium(self) -> webdriver.Chrome:
        """Setup Selenium WebDriver with proxy"""
        chrome_options = ChromeOptions()
        
        if config.SCRAPER_CONFIG['headless']:
            chrome_options.add_argument('--headless')
        
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument(f'--user-agent={self.get_random_user_agent()}')
        
        if self.proxy_manager:
            proxy_dict = self.proxy_manager.get_proxy()
            if proxy_dict:
                proxy_url = proxy_dict.get('http', '')
                chrome_options.add_argument(f'--proxy-server={proxy_url}')
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(config.SCRAPER_CONFIG['timeout'] / 1000)
        
        return driver
    
    def fetch_with_requests(self) -> Optional[BeautifulSoup]:
        """Fetch page using requests library (faster but no JS rendering)"""
        headers = {
            'User-Agent': self.get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        proxy = None
        if self.proxy_manager:
            proxy = self.proxy_manager.get_proxy()
        
        try:
            response = requests.get(
                self.url,
                headers=headers,
                proxies=proxy,
                timeout=config.PROXY_CONFIG['timeout']
            )
            response.raise_for_status()
            
            if proxy and self.proxy_manager:
                proxy_url = proxy.get('http', '')
                self.proxy_manager.mark_success(proxy_url)
            
            return BeautifulSoup(response.content, 'lxml')
        except Exception as e:
            if proxy and self.proxy_manager:
                proxy_url = proxy.get('http', '')
                self.proxy_manager.mark_failure(proxy_url)
            print(f"Error fetching {self.url}: {e}")
            return None
    
    def fetch_with_playwright(self) -> Optional[str]:
        """Fetch page using Playwright (supports JS rendering)"""
        try:
            if not self.browser:
                self.browser = self.setup_playwright()
            
            context = self.browser.new_context(
                user_agent=self.get_random_user_agent(),
                viewport={'width': 1920, 'height': 1080}
            )
            page = context.new_page()
            
            page.goto(self.url, wait_until='networkidle', timeout=config.SCRAPER_CONFIG['timeout'])
            time.sleep(config.SCRAPER_CONFIG['wait_time'])
            
            content = page.content()
            
            context.close()
            
            if self.proxy_manager:
                # Mark proxy success (proxy is handled at browser level)
                pass
            
            return content
        except PlaywrightTimeout:
            print(f"Timeout loading {self.url}")
            return None
        except Exception as e:
            print(f"Error fetching {self.url} with Playwright: {e}")
            return None
    
    def fetch_with_selenium(self) -> Optional[str]:
        """Fetch page using Selenium (supports JS rendering)"""
        try:
            if not self.driver:
                self.driver = self.setup_selenium()
            
            self.driver.get(self.url)
            WebDriverWait(self.driver, config.SCRAPER_CONFIG['timeout'] / 1000).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(config.SCRAPER_CONFIG['wait_time'])
            
            return self.driver.page_source
        except TimeoutException:
            print(f"Timeout loading {self.url}")
            return None
        except Exception as e:
            print(f"Error fetching {self.url} with Selenium: {e}")
            return None
    
    def fetch(self) -> Optional[BeautifulSoup]:
        """Fetch page content using configured method"""
        if self.use_playwright:
            html_content = self.fetch_with_playwright()
            if html_content:
                return BeautifulSoup(html_content, 'lxml')
        elif self.use_selenium:
            html_content = self.fetch_with_selenium()
            if html_content:
                return BeautifulSoup(html_content, 'lxml')
        else:
            return self.fetch_with_requests()
        
        return None
    
    @abstractmethod
    def parse(self, soup: BeautifulSoup) -> List[Dict]:
        """Parse scraped content - must be implemented by subclasses"""
        pass
    
    def scrape(self) -> List[Dict]:
        """Main scraping method"""
        soup = self.fetch()
        if soup:
            return self.parse(soup)
        return []
    
    def close(self):
        """Clean up resources"""
        if self.browser:
            self.browser.close()
        if self.driver:
            self.driver.quit()
        if self.playwright:
            self.playwright.stop()
