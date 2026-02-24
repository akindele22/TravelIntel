"""
Demo Data Generator - Creates sample travel advisories for testing
"""
from database import DatabaseHandler  # Postgres only
from data_cleaner import DataCleaner
from datetime import datetime, timedelta
import random

SAMPLE_ADVISORIES = [
    {
        'source': 'US State Department',
        'country': 'Egypt',
        'risk_level': 'Level 3: Reconsider Travel',
        'date': datetime.utcnow() - timedelta(days=5),
        'description': 'Armed conflict and terrorism pose significant threats. Armed militants operate in the Sinai Peninsula. Terrorist attacks have occurred in Cairo and other major cities. Demonstrations occur frequently in Cairo and other major cities. Some political demonstrations have turned violent.',
        'url': 'https://travel.state.gov/destinations/egypt'
    },
    {
        'source': 'UK FCDO',
        'country': 'Egypt',
        'risk_level': 'ADVISE AGAINST ALL BUT ESSENTIAL TRAVEL',
        'date': datetime.utcnow() - timedelta(days=3),
        'description': 'Terrorism is a significant and ongoing threat. There is a high threat of terrorism. Armed conflict in Sinai has caused significant casualties. Demonstrations can occur without warning and may turn violent.',
        'url': 'https://www.gov.uk/foreign-travel-advice/egypt'
    },
    {
        'source': 'Smart Traveller',
        'country': 'Thailand',
        'risk_level': 'RECONSIDER YOUR NEED TO TRAVEL',
        'date': datetime.utcnow() - timedelta(days=7),
        'description': 'There is a significant threat from terrorism and armed conflict in southern Thailand, particularly in Yala, Pattani and Narathiwat provinces. There is a high risk of further terrorist attacks. Health risks in Thailand include dengue fever and Japanese encephalitis.',
        'url': 'https://www.smartraveller.gov.au/destinations/thailand'
    },
    {
        'source': 'IATA Travel Centre',
        'country': 'Brazil',
        'risk_level': 'Exercise Caution',
        'date': datetime.utcnow() - timedelta(days=10),
        'description': 'Crime, including violent crime, is a significant concern in Brazil. Armed robbery, carjacking and assault occur regularly, particularly in major cities. Gang violence is prevalent in favelas and poor areas. Exercise caution when travelling.',
        'url': 'https://www.iatatravelcentre.com/world.php'
    },
    {
        'source': 'Canada Travel',
        'country': 'Mexico',
        'risk_level': 'Avoid All Travel',
        'date': datetime.utcnow() - timedelta(days=2),
        'description': 'There is significant risk of violence and crime, including armed robbery, kidnapping and murder. Organized crime activity and gang violence are widespread. Drug trafficking violence occurs throughout the country, particularly in certain states. Several regions experience high levels of civil unrest.',
        'url': 'https://travel.gc.ca/travelling/advisories'
    },
    {
        'source': 'US State Department',
        'country': 'Philippines',
        'risk_level': 'Level 3: Reconsider Travel',
        'date': datetime.utcnow() - timedelta(days=8),
        'description': 'Terrorism and armed conflict are ongoing concerns. Terrorist groups operate in Mindanao. There is a threat of dengue fever, typhoid fever and other infectious diseases. Typhoons are common during certain seasons. Natural disasters including flooding and earthquakes occur.',
        'url': 'https://travel.state.gov/destinations/philippines'
    },
    {
        'source': 'UK FCDO',
        'country': 'Colombia',
        'risk_level': 'ADVISE AGAINST ALL TRAVEL',
        'date': datetime.utcnow() - timedelta(days=6),
        'description': 'Armed groups and criminal organizations engage in violence and armed conflict. Kidnapping and extortion are serious concerns. Armed robbery and carjacking occur in urban areas. There are significant crime risks including homicide and sexual assault.',
        'url': 'https://www.gov.uk/foreign-travel-advice/colombia'
    },
    {
        'source': 'Smart Traveller',
        'country': 'South Africa',
        'risk_level': 'EXERCISE A HIGH DEGREE OF CAUTION',
        'date': datetime.utcnow() - timedelta(days=4),
        'description': 'There is a high level of crime including violent crime in South Africa. Armed robbery, home invasions, assault and rape occur regularly. Gang violence occurs in certain areas. Civil unrest and protests can occur with little warning.',
        'url': 'https://www.smartraveller.gov.au/destinations/south-africa'
    }
]

def generate_demo_data():
    """Generate and store demo advisories"""
    print("Generating demo travel advisory data...\n")
    
    db = DatabaseHandler()
    cleaner = DataCleaner()
    
    try:
        # Insert raw advisories
        print(f"Inserting {len(SAMPLE_ADVISORIES)} sample advisories...")
        inserted = db.insert_advisories(SAMPLE_ADVISORIES)
        print(f"✓ Inserted {inserted} advisories\n")
        
        # Clean and process advisories
        print("Cleaning and processing advisories...")
        cleaned = cleaner.clean_batch(SAMPLE_ADVISORIES)
        
        # Store processed data
        processed_data = []
        for cleaned_adv in cleaned:
            processed_data.append({
                'advisory_id': None,
                'country_normalized': cleaned_adv.get('country_normalized'),
                'risk_level_normalized': cleaned_adv.get('risk_level_normalized'),
                'risk_score': cleaned_adv.get('risk_score'),
                'keywords': cleaned_adv.get('keywords', []),
                'sentiment_score': cleaned_adv.get('sentiment_score', 0.0),
                'has_security_concerns': cleaned_adv.get('has_security_concerns', False),
                'has_safety_concerns': cleaned_adv.get('has_safety_concerns', False),
                'has_serenity_concerns': cleaned_adv.get('has_serenity_concerns', False)
            })
        
        stored = db.insert_processed_data(processed_data)
        print(f"✓ Processed and stored {stored} records\n")
        
        # Show summary
        all_advisories = db.get_advisories(limit=999)
        countries = db.get_all_countries()
        
        print("="*60)
        print("DEMO DATA SUMMARY")
        print("="*60)
        print(f"Total advisories: {len(all_advisories)}")
        print(f"Countries: {', '.join(countries)}")
        print("\n✓ Ready to use! Launch dashboard with:")
        print("  streamlit run dashboard.py")
        
    finally:
        db.close()

if __name__ == '__main__':
    generate_demo_data()
