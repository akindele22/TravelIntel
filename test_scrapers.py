"""
Test script for individual scrapers
"""
import sys
from proxy_manager import ProxyManager
from scrapers import (
    USStateDeptScraper,
    UKFCDOScraper,
    #SmartTravellerScraper,
    IATAScraper,
    #CanadaTravelScraper
)
import config


def test_scraper(scraper_class, url, name):
    """Test a single scraper"""
    print(f"\n{'='*60}")
    print(f"Testing {name}")
    print(f"{'='*60}")
    print(f"URL: {url}")
    
    try:
        # Initialize proxy manager if proxies are configured
        proxy_manager = None
        if config.PROXY_CONFIG['proxies']:
            proxy_manager = ProxyManager(
                proxies=config.PROXY_CONFIG['proxies'],
                rotation_strategy='round_robin'
            )
        
        # Create scraper
        scraper = scraper_class(
            url=url,
            proxy_manager=proxy_manager,
            use_playwright=True  # Use Playwright for JS rendering
        )
        
        # Scrape
        print("Scraping...")
        advisories = scraper.scrape()
        
        # Display results
        if advisories:
            print(f"\n✓ Successfully scraped {len(advisories)} advisories")
            print("\nSample results:")
            for i, adv in enumerate(advisories[:3], 1):  # Show first 3
                print(f"\n{i}. Country: {adv.get('country', 'N/A')}")
                print(f"   Risk Level: {adv.get('risk_level', 'N/A')}")
                print(f"   Source: {adv.get('source', 'N/A')}")
                print(f"   URL: {adv.get('url', 'N/A')}")
        else:
            print("\n✗ No advisories found")
            print("This could mean:")
            print("  - The website structure has changed")
            print("  - The selectors need to be updated")
            print("  - The page requires different handling")
        
        scraper.close()
        return len(advisories) > 0
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Test all scrapers"""
    scrapers_to_test = [
        (USStateDeptScraper, config.TARGET_URLS['us_state_dept'], 'US State Department'),
        (UKFCDOScraper, config.TARGET_URLS['uk_fcdo'], 'UK FCDO'),
        (IATAScraper, config.TARGET_URLS['iata'], 'IATA Travel Centre'),
    ]
    
    results = {}
    
    for scraper_class, url, name in scrapers_to_test:
        success = test_scraper(scraper_class, url, name)
        results[name] = success
        print("\n")
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    for name, success in results.items():
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status}: {name}")
    
    total = len(results)
    passed = sum(results.values())
    print(f"\nTotal: {passed}/{total} scrapers working")


if __name__ == '__main__':
    main()
