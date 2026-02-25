"""
Main Orchestration Script for Travel Advisory Scraper
"""
import time
import schedule
from typing import List, Dict
from proxy_manager import ProxyManager
from scrapers import (
    USStateDeptScraper,
    UKFCDOScraper,
    SmartTravellerScraper,
    IATAScraper,
    CanadaTravelScraper
) 
from db_factory import DatabaseHandler
from data_cleaner import DataCleaner
import config
from tqdm import tqdm


class TravelAdvisoryPipeline:
    """Main pipeline for scraping, cleaning, and storing travel advisories"""
    
    def __init__(self):
        """Initialize pipeline components"""
        # Initialize proxy manager
        self.proxy_manager = None
        if config.PROXY_CONFIG['proxies']:
            self.proxy_manager = ProxyManager(
                proxies=config.PROXY_CONFIG['proxies'],
                rotation_strategy=config.PROXY_CONFIG['rotation_strategy']
            )
            print(f"Proxy manager initialized with {len(config.PROXY_CONFIG['proxies'])} proxies")
        else:
            print("Warning: No proxies configured. Running without proxy rotation.")
        
        # Initialize database
        self.db = DatabaseHandler()
        
        # Initialize data cleaner
        self.cleaner = DataCleaner()
        
        # Scraper mapping
        self.scrapers = {
            'us_state_dept': (USStateDeptScraper, config.TARGET_URLS['us_state_dept']),
            'uk_fcdo': (UKFCDOScraper, config.TARGET_URLS['uk_fcdo']),
            #'smartraveller': (SmartTravellerScraper, config.TARGET_URLS['smartraveller']),
            'iata': (IATAScraper, config.TARGET_URLS['iata']),
            #'canada': (CanadaTravelScraper, config.TARGET_URLS['canada'])
        }
    
    def scrape_all(self) -> List[Dict]:
        """Scrape all configured sources"""
        all_advisories = []
        
        print("\n" + "="*60)
        print("Starting Scraping Process")
        print("="*60)
        
        for source_name, (scraper_class, url) in tqdm(self.scrapers.items(), 
                                                      desc="Scraping sources"):
            print(f"\nScraping {source_name}...")
            
            try:
                scraper = scraper_class(
                    url=url,
                    proxy_manager=self.proxy_manager,
                    use_playwright=True  # Use Playwright for JS-heavy sites
                )
                
                advisories = scraper.scrape()
                
                if advisories:
                    print(f"  ✓ Found {len(advisories)} advisories from {source_name}")
                    all_advisories.extend(advisories)
                else:
                    print(f"  ✗ No advisories found from {source_name}")
                
                scraper.close()
                
                # Rate limiting between requests
                time.sleep(2)
                
            except Exception as e:
                print(f"  ✗ Error scraping {source_name}: {e}")
                continue
        
        print(f"\nTotal advisories scraped: {len(all_advisories)}")
        return all_advisories
    
    def clean_data(self, advisories: List[Dict]) -> List[Dict]:
        """Clean and normalize scraped data"""
        print("\n" + "="*60)
        print("Cleaning Data")
        print("="*60)
        
        cleaned = self.cleaner.clean_batch(advisories)
        deduplicated = self.cleaner.deduplicate(cleaned)
        
        print(f"Cleaned {len(cleaned)} advisories")
        print(f"After deduplication: {len(deduplicated)} advisories")
        
        return deduplicated
    
    def store_data(self, advisories: List[Dict]):
        """Store cleaned data in database"""
        print("\n" + "="*60)
        print("Storing Data in Database")
        print("="*60)
        
        inserted = self.db.insert_advisories(advisories)
        print(f"Inserted/Updated {inserted} advisories in database")
        
        # Store processed data
        processed_data = []
        for advisory in advisories:
            # Get advisory ID from database (simplified - in production, fetch after insert)
            processed_data.append({
                'advisory_id': None,  # Would be fetched from DB in production
                'country_normalized': advisory.get('country_normalized'),
                'risk_level_normalized': advisory.get('risk_level_normalized'),
                'risk_score': advisory.get('risk_score'),
                'keywords': advisory.get('keywords', []),
                'sentiment_score': advisory.get('sentiment_score', 0.0),
                'has_security_concerns': advisory.get('has_security_concerns', False),
                'has_safety_concerns': advisory.get('has_safety_concerns', False),
                'has_serenity_concerns': advisory.get('has_serenity_concerns', False)
            })
        
        if processed_data:
            self.db.insert_processed_data(processed_data)
            print(f"Stored {len(processed_data)} processed records")
    
    def run_full_pipeline(self):
        """Run the complete pipeline"""
        print("\n" + "="*60)
        print("TRAVEL ADVISORY SCRAPER PIPELINE")
        print("="*60)
        
        try:
            # Step 1: Scrape
            advisories = self.scrape_all()
            
            if not advisories:
                print("No advisories scraped. Exiting.")
                return
            
            # Step 2: Clean
            cleaned_advisories = self.clean_data(advisories)
            
            # Step 3: Store
            self.store_data(cleaned_advisories)
            
            print("\n" + "="*60)
            print("Pipeline completed successfully!")
            print("="*60)
            
        except Exception as e:
            print(f"\nError in pipeline: {e}")
            raise
        finally:
            # Cleanup
            self.db.close()
    
    def run_scheduled(self, interval_hours: int = 6):
        """Run pipeline on a schedule"""
        print(f"Scheduling pipeline to run every {interval_hours} hours")
        
        schedule.every(interval_hours).hours.do(self.run_full_pipeline)
        
        # Run immediately
        self.run_full_pipeline()
        
        # Keep running
        while True:
            schedule.run_pending()
            time.sleep(60)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Travel Advisory Scraper')
    parser.add_argument('--schedule', type=int, default=0,
                       help='Run on schedule (interval in hours, 0 = run once)')
    parser.add_argument('--source', type=str, default='all',
                       choices=['all', 'us_state_dept', 'uk_fcdo', 'smartraveller', 'iata', 'canada'],
                       help='Specific source to scrape (default: all)')
    
    args = parser.parse_args()
    
    pipeline = TravelAdvisoryPipeline()
    
    if args.schedule > 0:
        pipeline.run_full_pipeline()
    else:
        continue


if __name__ == '__main__':
    main()
