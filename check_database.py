"""
Quick script to check if database has data
"""
from database import DatabaseHandler  # replacing sqlite import

db = DatabaseHandler()

try:
    # Check advisories
    advisories = db.get_advisories(limit=5)
    print(f"\n📊 Total advisories in database: {len(db.get_advisories(limit=99999))}")
    
    if advisories:
        print(f"\n✓ Found {len(advisories)} recent advisories:")
        for adv in advisories[:3]:
            print(f"  - {adv.get('country')} ({adv.get('source')}): {adv.get('date')}")
    else:
        print("\n✗ No advisories found - scraper may not have run yet")
    
    # Check countries
    countries = db.get_all_countries()
    if countries:
        print(f"\n✓ Countries in database: {len(countries)}")
        print(f"  Sample: {', '.join(countries[:5])}")
    
finally:
    db.close()
