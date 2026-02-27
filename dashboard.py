"""
Main Orchestration Script for Travel Advisory Scraper
HTTP-only, manual scraping (no Playwright/Selenium)
"""
import streamlit as st

st.title("TravelIntel Test")
st.write("If you can see this, Streamlit is working.")

import time
from typing import List, Dict
from scrapers import (
    USStateDeptScraper,
    UKFCDOScraper,
    # SmartTravellerScraper,
    # IATAScraper,
    # CanadaTravelScraper
)
from db_factory import DatabaseHandler
from data_cleaner import DataCleaner
import config
from tqdm import tqdm


def scrape_all() -> List[Dict]:
    """Scrape all configured sources via HTTP requests only"""
    all_advisories = []

    print("\n" + "=" * 60)
    print("Starting Scraping Process")
    print("=" * 60)

    scrapers = {
        'us_state_dept': (USStateDeptScraper, config.TARGET_URLS['us_state_dept']),
        'uk_fcdo': (UKFCDOScraper, config.TARGET_URLS['uk_fcdo']),
        # 'smartraveller': (SmartTravellerScraper, config.TARGET_URLS['smartraveller']),
        # 'iata': (IATAScraper, config.TARGET_URLS['iata']),
        # 'canada': (CanadaTravelScraper, config.TARGET_URLS['canada'])
    }

    for source_name, (scraper_class, url) in tqdm(scrapers.items(), desc="Scraping sources"):
        print(f"\nScraping {source_name}...")
        try:
            scraper = scraper_class(url=url, use_playwright=False, use_selenium=False)
            advisories = scraper.scrape()
            scraper.close()

            if advisories:
                print(f"  ✓ Found {len(advisories)} advisories from {source_name}")
                all_advisories.extend(advisories)
            else:
                print(f"  ✗ No advisories found from {source_name}")

            # Rate limiting
            time.sleep(2)

        except Exception as e:
            print(f"  ✗ Error scraping {source_name}: {e}")
            continue

    print(f"\nTotal advisories scraped: {len(all_advisories)}")
    return all_advisories


def clean_data(advisories: List[Dict]) -> List[Dict]:
    """Clean and normalize scraped data"""
    print("\n" + "=" * 60)
    print("Cleaning Data")
    print("=" * 60)

    cleaner = DataCleaner()
    cleaned = cleaner.clean_batch(advisories)
    deduplicated = cleaner.deduplicate(cleaned)

    print(f"Cleaned {len(cleaned)} advisories")
    print(f"After deduplication: {len(deduplicated)} advisories")

    return deduplicated


def store_data(advisories: List[Dict]):
    """Store cleaned data in database"""
    print("\n" + "=" * 60)
    print("Storing Data in Database")
    print("=" * 60)

    db = DatabaseHandler()
    inserted = db.insert_advisories(advisories)
    print(f"Inserted/Updated {inserted} advisories in database")

    # Optional: store processed data for analytics
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
        db.insert_processed_data(processed_data)
        print(f"Stored {len(processed_data)} processed records")

    db.close()


def run_pipeline():
    """Run the full pipeline manually"""
    print("\n" + "=" * 60)
    print("TRAVEL ADVISORY SCRAPER PIPELINE")
    print("=" * 60)

    try:
        # Step 1: Scrape
        advisories = scrape_all()
        if not advisories:
            print("No advisories scraped. Exiting.")
            return

        # Step 2: Clean
        cleaned_advisories = clean_data(advisories)

        # Step 3: Store
        store_data(cleaned_advisories)

        print("\nPipeline completed successfully!")

    except Exception as e:
        print(f"\nError in pipeline: {e}")
        raise
