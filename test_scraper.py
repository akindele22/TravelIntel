"""
Test the scraper with detailed output
"""
import sys
from scrapers import USStateDeptScraper
import config

print("Testing US State Department Scraper...\n")

try:
    scraper = USStateDeptScraper(
        url=config.TARGET_URLS['us_state_dept'],
        proxy_manager=None,
        use_playwright=True
    )
    
    print(f"Scraper initialized for: {config.TARGET_URLS['us_state_dept']}")
    print("\nAttempting to scrape...")
    
    advisories = scraper.scrape()
    
    print(f"\n✓ Scraping completed!")
    print(f"Found {len(advisories)} advisories")
    
    if advisories:
        print(f"\nFirst advisory:")
        adv = advisories[0]
        for key, value in adv.items():
            print(f"  {key}: {str(value)[:100]}")
    
    scraper.close()
    
except Exception as e:
    print(f"\n✗ Error during scraping:")
    print(f"  {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
