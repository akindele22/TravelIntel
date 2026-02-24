"""
Main Orchestration Script - Simplified with reliable scraper
"""
import time
from typing import List, Dict
from scrapers_simple import SimpleAdvisoryScraper
from database import DatabaseHandler  # always use Postgres handler
from data_cleaner import DataCleaner
from tqdm import tqdm


class TravelAdvisoryPipeline:
    """Main pipeline for scraping, cleaning, and storing travel advisories"""
    
    def __init__(self):
        """Initialize pipeline components"""
        # Initialize scraper
        self.scraper = SimpleAdvisoryScraper()
        
        # Initialize database
        self.db = DatabaseHandler()
        
        # Initialize data cleaner
        self.cleaner = DataCleaner()
    
    def scrape_all(self) -> List[Dict]:
        """Scrape all configured sources"""
        print("\n" + "="*60)
        print("Starting Scraping Process")
        print("="*60)
        
        advisories = self.scraper.scrape_all()
        
        print(f"\nTotal advisories scraped: {len(advisories)}")
        return advisories
    
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
            processed_data.append({
                'advisory_id': None,
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
            print("\n✓ Data ready for dashboard. Run:")
            print("  streamlit run dashboard.py")
            
        except Exception as e:
            print(f"\nError in pipeline: {e}")
            raise
        finally:
            # Cleanup
            self.db.close()


def main():
    """Main entry point"""
    pipeline = TravelAdvisoryPipeline()
    pipeline.run_full_pipeline()


if __name__ == '__main__':
    main()
