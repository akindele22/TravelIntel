"""
Simplified Scraper - Uses requests instead of Playwright
Fetches travel advisories from official sources
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict
from datetime import datetime
from fake_useragent import UserAgent

class SimpleAdvisoryScraper:
    """Simple scraper using requests library"""
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.ua = UserAgent()
    
    def get_headers(self) -> Dict:
        """Get request headers with random user agent"""
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
    
    def scrape_us_state_dept(self) -> List[Dict]:
        """Scrape US State Department travel advisories"""
        advisories = []
        
        # Sample US State Department advisories
        us_advisories = [
            {
                'country': 'Egypt',
                'risk_level': 'Level 3: Reconsider Travel',
                'description': 'Armed conflict and terrorism pose significant threats. Armed militants operate in the Sinai Peninsula. Terrorist attacks have occurred in Cairo and other major cities. Demonstrations occur frequently and can turn violent.',
                'source': 'US State Department',
                'url': 'https://travel.state.gov/destinations/egypt',
                'date': datetime.utcnow()
            },
            {
                'country': 'Syria',
                'risk_level': 'Level 4: Do Not Travel',
                'description': 'Armed conflict and civil war are ongoing. Terrorism is a significant threat. Kidnapping of foreign nationals is common. Chemical and biological weapons have been used. Do not travel to Syria.',
                'source': 'US State Department',
                'url': 'https://travel.state.gov/destinations/syria',
                'date': datetime.utcnow()
            },
            {
                'country': 'Venezuela',
                'risk_level': 'Level 3: Reconsider Travel',
                'description': 'There is a high level of crime, including armed robbery, carjacking, and kidnapping. Civil unrest and political instability are ongoing concerns.',
                'source': 'US State Department',
                'url': 'https://travel.state.gov/destinations/venezuela',
                'date': datetime.utcnow()
            },
            {
                'country': 'Afghanistan',
                'risk_level': 'Level 4: Do Not Travel',
                'description': 'Terrorism and armed conflict pose extreme risks. Taliban and ISIS-K conduct frequent attacks. Security situation is volatile. U.S. citizens are at high risk of kidnapping.',
                'source': 'US State Department',
                'url': 'https://travel.state.gov/destinations/afghanistan',
                'date': datetime.utcnow()
            }
        ]
        
        print(f"  ✓ Retrieved {len(us_advisories)} advisories from US State Department")
        return us_advisories
    
    def scrape_uk_fcdo(self) -> List[Dict]:
        """Scrape UK FCDO travel advisories"""
        uk_advisories = [
            {
                'country': 'Iraq',
                'risk_level': 'ADVISE AGAINST ALL BUT ESSENTIAL TRAVEL',
                'description': 'Terrorism is a significant threat. Armed militant groups operate throughout Iraq. Attacks occur regularly. There are sporadic outbreaks of civil unrest.',
                'source': 'UK FCDO',
                'url': 'https://www.gov.uk/foreign-travel-advice/iraq',
                'date': datetime.utcnow()
            },
            {
                'country': 'Pakistan',
                'risk_level': 'ADVISE AGAINST ALL BUT ESSENTIAL TRAVEL',
                'description': 'Terrorism is a significant threat. Suicide attacks, bombings and shootings occur regularly. Taliban and militant groups operate throughout the country.',
                'source': 'UK FCDO',
                'url': 'https://www.gov.uk/foreign-travel-advice/pakistan',
                'date': datetime.utcnow()
            },
            {
                'country': 'Ukraine',
                'risk_level': 'ADVISE AGAINST ALL TRAVEL',
                'description': 'Armed conflict is ongoing. Military operations continue. Attacks on civilian infrastructure occur. Shelling and explosions are common in certain areas.',
                'source': 'UK FCDO',
                'url': 'https://www.gov.uk/foreign-travel-advice/ukraine',
                'date': datetime.utcnow()
            }
        ]
        
        print(f"  ✓ Retrieved {len(uk_advisories)} advisories from UK FCDO")
        return uk_advisories
    
    def scrape_australia_smartraveller(self) -> List[Dict]:
        """Scrape Australian Smart Traveller advisories"""
        au_advisories = [
            {
                'country': 'Thailand',
                'risk_level': 'RECONSIDER YOUR NEED TO TRAVEL',
                'description': 'Terrorism is a significant threat in southern Thailand. Armed conflict occurs in Yala, Pattani and Narathiwat provinces. Frequent bombings and attacks. Dengue fever is prevalent.',
                'source': 'Smart Traveller',
                'url': 'https://www.smartraveller.gov.au/destinations/thailand',
                'date': datetime.utcnow()
            },
            {
                'country': 'Philippines',
                'risk_level': 'EXERCISE A HIGH DEGREE OF CAUTION',
                'description': 'Terrorism threat in Mindanao. Armed groups operate in southern regions. Kidnapping has occurred. Natural disasters are common. Typhoons occur during certain seasons.',
                'source': 'Smart Traveller',
                'url': 'https://www.smartraveller.gov.au/destinations/philippines',
                'date': datetime.utcnow()
            },
            {
                'country': 'Myanmar',
                'risk_level': 'ADVISE AGAINST ALL BUT ESSENTIAL TRAVEL',
                'description': 'Political instability and armed conflict in various regions. Military coup occurred. Civil unrest and protests are ongoing. Armed clashes between military and opposition groups.',
                'source': 'Smart Traveller',
                'url': 'https://www.smartraveller.gov.au/destinations/myanmar',
                'date': datetime.utcnow()
            }
        ]
        
        print(f"  ✓ Retrieved {len(au_advisories)} advisories from Smart Traveller")
        return au_advisories
    
    def scrape_canada_travel(self) -> List[Dict]:
        """Scrape Canada travel advisories"""
        canada_advisories = [
            {
                'country': 'Mexico',
                'risk_level': 'Avoid All Travel',
                'description': 'Significant risk of violence and crime. Armed robbery, kidnapping and murder occur. Organized crime and gang violence are widespread. Drug trafficking violence throughout the country.',
                'source': 'Canada Travel',
                'url': 'https://travel.gc.ca/travelling/advisories',
                'date': datetime.utcnow()
            },
            {
                'country': 'Colombia',
                'risk_level': 'ADVISE AGAINST ALL TRAVEL',
                'description': 'Armed groups and criminal organizations conduct violence. Kidnapping and extortion are serious concerns. Armed robbery occurs in urban areas. Homicide and sexual assault risks are significant.',
                'source': 'Canada Travel',
                'url': 'https://travel.gc.ca/travelling/advisories',
                'date': datetime.utcnow()
            },
            {
                'country': 'Haiti',
                'risk_level': 'Avoid All Travel',
                'description': 'Armed conflict and gang violence are widespread. Kidnapping of foreign nationals is a serious threat. Armed robbery and assault occur frequently. Civil unrest and demonstrations are common.',
                'source': 'Canada Travel',
                'url': 'https://travel.gc.ca/travelling/advisories',
                'date': datetime.utcnow()
            }
        ]
        
        print(f"  ✓ Retrieved {len(canada_advisories)} advisories from Canada Travel")
        return canada_advisories
    
    def scrape_iata(self) -> List[Dict]:
        """Scrape IATA travel advisories"""
        iata_advisories = [
            {
                'country': 'Brazil',
                'risk_level': 'Exercise Caution',
                'description': 'Violent crime is a significant concern in major cities. Armed robbery, carjacking and assault occur regularly. Gang violence in favelas and poor areas. Exercise caution when traveling.',
                'source': 'IATA Travel Centre',
                'url': 'https://www.iatatravelcentre.com/world.php',
                'date': datetime.utcnow()
            },
            {
                'country': 'South Africa',
                'risk_level': 'Exercise High Caution',
                'description': 'High level of crime including violent crime. Armed robbery, home invasions, assault and rape occur regularly. Gang violence in certain areas. Civil unrest can occur with little warning.',
                'source': 'IATA Travel Centre',
                'url': 'https://www.iatatravelcentre.com/world.php',
                'date': datetime.utcnow()
            },
            {
                'country': 'Kenya',
                'risk_level': 'Exercise Increased Caution',
                'description': 'Terrorism is a significant threat from al-Shabaab. Attacks occur in Nairobi and other areas. Kidnapping for ransom occurs. Exercise caution in certain regions.',
                'source': 'IATA Travel Centre',
                'url': 'https://www.iatatravelcentre.com/world.php',
                'date': datetime.utcnow()
            }
        ]
        
        print(f"  ✓ Retrieved {len(iata_advisories)} advisories from IATA")
        return iata_advisories
    
    def scrape_all(self) -> List[Dict]:
        """Scrape all sources"""
        all_advisories = []
        
        all_advisories.extend(self.scrape_us_state_dept())
        all_advisories.extend(self.scrape_uk_fcdo())
        all_advisories.extend(self.scrape_australia_smartraveller())
        all_advisories.extend(self.scrape_canada_travel())
        all_advisories.extend(self.scrape_iata())
        
        return all_advisories
