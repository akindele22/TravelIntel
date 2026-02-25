"""
Manual Travel Advisory Scraper Pipeline
HTTP-only scraping, no scheduler
"""
from typing import List, Dict
from scrapers import USStateDeptScraper, UKFCDOScraper  # add more if needed
from db_factory import DatabaseHandler
from data_cleaner import DataCleaner
import config
import time

class TravelAdvisoryPipeline:
    """Pipeline for scraping, cleaning, storing travel advisories"""

    def __init__(self):
        # Initialize database
        self.db = DatabaseHandler()
        # Data cleaner
        self.cleaner = DataCleaner()
        # Scraper mapping
        self.scrapers = {
            'us_state_dept': (USStateDeptScraper, config.TARGET_URLS['us_state_dept']),
            'uk_fcdo': (UKFCDOScraper, config.TARGET_URLS['uk_fcdo']),
            # Add other scrapers if needed
        }

    def scrape_all(self) -> List[Dict]:
        """Scrape all configured sources"""
        all_advisories = []

        for source_name, (scraper_class, url) in self.scrapers.items():
            print(f"Scraping {source_name}...")
            try:
                scraper = scraper_class(url=url)
                advisories = scraper.scrape()
                if advisories:
                    print(f"  ✓ Found {len(advisories)} advisories")
                    all_advisories.extend(advisories)
                else:
                    print(f"  ✗ No advisories found")
            except Exception as e:
                print(f"  ✗ Error scraping {source_name}: {e}")

        print(f"Total advisories scraped: {len(all_advisories)}")
        return all_advisories

    def clean_data(self, advisories: List[Dict]) -> List[Dict]:
        """Clean + deduplicate"""
        cleaned = self.cleaner.clean_batch(advisories)
        deduped = self.cleaner.deduplicate(cleaned)
        print(f"Cleaned: {len(cleaned)}, Deduplicated: {len(deduped)}")
        return deduped

    def store_data(self, advisories: List[Dict]):
        """Store data in DB"""
        inserted = self.db.insert_advisories(advisories)
        print(f"Inserted/Updated {inserted} advisories")
        # Optional: store processed data as needed

    def run_full_pipeline(self):
        """Run scraping, cleaning, storing once"""
        advisories = self.scrape_all()
        if not advisories:
            print("No advisories scraped. Exiting.")
            return
        cleaned = self.clean_data(advisories)
        self.store_data(cleaned)
        self.db.close()
        print("Pipeline completed successfully!")

# Single function Streamlit can call
def run_pipeline():
    pipeline = TravelAdvisoryPipeline()
    pipeline.run_full_pipeline()
