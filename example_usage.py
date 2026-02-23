"""
Example Usage Script
Demonstrates how to use individual components
"""
from proxy_manager import ProxyManager
from scrapers import USStateDeptScraper
from database import DatabaseHandler
from data_cleaner import DataCleaner
from ai_predictor import AIPredictor
import config


def example_proxy_manager():
    """Example: Using proxy manager"""
    print("="*60)
    print("Example: Proxy Manager")
    print("="*60)
    
    # Initialize proxy manager
    proxies = [
        'http://user:pass@proxy1.example.com:8080',
        'http://user:pass@proxy2.example.com:8080',
    ]
    
    proxy_manager = ProxyManager(proxies, rotation_strategy='round_robin')
    
    # Get a proxy
    proxy = proxy_manager.get_proxy()
    print(f"Got proxy: {proxy}")
    
    # Test proxy
    if proxy_manager.test_proxy(proxy):
        print("Proxy is working!")
        proxy_manager.mark_success(proxy['http'])
    else:
        print("Proxy failed")
        proxy_manager.mark_failure(proxy['http'])
    
    # Get statistics
    stats = proxy_manager.get_stats()
    print(f"Stats: {stats}")


def example_scraper():
    """Example: Using a scraper"""
    print("\n" + "="*60)
    print("Example: Scraper")
    print("="*60)
    
    # Initialize proxy manager (optional)
    proxy_manager = None
    if config.PROXY_CONFIG['proxies']:
        proxy_manager = ProxyManager(
            proxies=config.PROXY_CONFIG['proxies'],
            rotation_strategy='round_robin'
        )
    
    # Create scraper
    scraper = USStateDeptScraper(
        url=config.TARGET_URLS['us_state_dept'],
        proxy_manager=proxy_manager,
        use_playwright=True
    )
    
    # Scrape
    advisories = scraper.scrape()
    
    print(f"Scraped {len(advisories)} advisories")
    if advisories:
        print("\nFirst advisory:")
        print(f"  Country: {advisories[0].get('country')}")
        print(f"  Risk Level: {advisories[0].get('risk_level')}")
        print(f"  Source: {advisories[0].get('source')}")
    
    scraper.close()


def example_data_cleaner():
    """Example: Using data cleaner"""
    print("\n" + "="*60)
    print("Example: Data Cleaner")
    print("="*60)
    
    cleaner = DataCleaner()
    
    # Sample advisory
    sample_advisory = {
        'source': 'US State Department',
        'country': 'france',
        'risk_level': 'Level 2: Exercise Increased Caution',
        'date': '2024-01-15',
        'description': 'Terrorism threat exists. Exercise caution.',
        'url': 'https://example.com'
    }
    
    # Clean it
    cleaned = cleaner.clean_advisory(sample_advisory)
    
    print("Original:")
    print(f"  Country: {sample_advisory['country']}")
    print(f"  Risk Level: {sample_advisory['risk_level']}")
    
    print("\nCleaned:")
    print(f"  Country Normalized: {cleaned['country_normalized']}")
    print(f"  Risk Level Normalized: {cleaned['risk_level_normalized']}")
    print(f"  Risk Score: {cleaned['risk_score']}")
    print(f"  Keywords: {cleaned['keywords']}")


def example_database():
    """Example: Using database handler"""
    print("\n" + "="*60)
    print("Example: Database Handler")
    print("="*60)
    
    db = DatabaseHandler()
    
    # Sample advisory
    sample_advisory = {
        'source': 'US State Department',
        'country': 'France',
        'risk_level': 'Level 2',
        'date': '2024-01-15',
        'description': 'Exercise increased caution',
        'url': 'https://example.com'
    }
    
    # Insert
    count = db.insert_advisories([sample_advisory])
    print(f"Inserted {count} advisory")
    
    # Query
    advisories = db.get_advisories(country='France', limit=5)
    print(f"Found {len(advisories)} advisories for France")
    
    db.close()


def example_ai_predictor():
    """Example: Using AI predictor"""
    print("\n" + "="*60)
    print("Example: AI Predictor")
    print("="*60)
    
    predictor = AIPredictor()
    
    # Sample advisory
    sample_advisory = {
        'country_normalized': 'France',
        'description_cleaned': 'Terrorism threat exists. Exercise increased caution.',
        'keywords': ['terrorism', 'caution', 'threat'],
        'source': 'US State Department'
    }
    
    # If model is trained, make prediction
    if predictor.is_trained:
        prediction = predictor.predict_single(sample_advisory)
        print("Prediction:")
        print(f"  Predicted Risk Level: {prediction.get('predicted_risk_level')}")
        print(f"  Confidence: {prediction.get('confidence', 0):.2%}")
    else:
        print("Model not trained yet.")
        print("Train the model first by running the full pipeline with historical data.")


def example_full_pipeline():
    """Example: Full pipeline workflow"""
    print("\n" + "="*60)
    print("Example: Full Pipeline")
    print("="*60)
    
    # 1. Initialize components
    proxy_manager = None
    if config.PROXY_CONFIG['proxies']:
        proxy_manager = ProxyManager(
            proxies=config.PROXY_CONFIG['proxies'],
            rotation_strategy='round_robin'
        )
    
    db = DatabaseHandler()
    cleaner = DataCleaner()
    predictor = AIPredictor()
    
    # 2. Scrape
    scraper = USStateDeptScraper(
        url=config.TARGET_URLS['us_state_dept'],
        proxy_manager=proxy_manager,
        use_playwright=True
    )
    advisories = scraper.scrape()
    scraper.close()
    
    print(f"Step 1: Scraped {len(advisories)} advisories")
    
    # 3. Clean
    cleaned = cleaner.clean_batch(advisories)
    deduplicated = cleaner.deduplicate(cleaned)
    print(f"Step 2: Cleaned and deduplicated to {len(deduplicated)} advisories")
    
    # 4. Store
    count = db.insert_advisories(deduplicated)
    print(f"Step 3: Stored {count} advisories in database")
    
    # 5. Predict (if model is trained)
    if predictor.is_trained:
        predictions = predictor.predict(deduplicated)
        print(f"Step 4: Generated {len(predictions)} predictions")
    else:
        print("Step 4: Model not trained - skipping predictions")
    
    db.close()
    print("\nPipeline completed!")


if __name__ == '__main__':
    print("Travel Advisory Scraper - Example Usage")
    print("="*60)
    
    # Uncomment the examples you want to run:
    
    # example_proxy_manager()
    # example_scraper()
    # example_data_cleaner()
    # example_database()
    # example_ai_predictor()
    example_full_pipeline()
