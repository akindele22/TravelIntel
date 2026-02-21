"""
Configuration file for the travel advisory scraper
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Database Configuration
DATABASE_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'travel_advisories'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'ApexB')
}

# Proxy Configuration
PROXY_CONFIG = {
    # Format: 'http://username:password@proxy_host:port'
    # For rotating residential proxies, add multiple proxies here
    'proxies': [
        # Example format - replace with your actual proxy credentials
        # 'http://user:pass@proxy1.example.com:8080',
        # 'http://user:pass@proxy2.example.com:8080',
    ],
    'rotation_strategy': 'round_robin',  # 'round_robin', 'random', 'least_used'
    'timeout': 30,
    'max_retries': 3
}

# Scraper Configuration
SCRAPER_CONFIG = {
    'headless': True,
    'timeout': 30000,  # milliseconds
    'wait_time': 3,  # seconds
    'user_agent_rotation': True,
    'respect_robots_txt': False  # Set to True in production
}

# Target URLs
TARGET_URLS = {
    'us_state_dept': 'https://travel.state.gov/content/travel/en/traveladvisories/traveladvisories.html',
    'uk_fcdo': 'https://www.gov.uk/foreign-travel-advice',
    'smartraveller': 'https://www.smartraveller.gov.au/destinations',
    'iata': 'https://www.iatatravelcentre.com/world.php',
    'canada': 'https://travel.gc.ca/travelling/advisories'  # Additional source
}

# AI Model Configuration
AI_CONFIG = {
    'model_type': 'classification',  # 'classification' or 'regression'
    'model_path': 'models/travel_advisory_model.pkl',
    'features': ['country', 'risk_level', 'date', 'source'],
    'prediction_threshold': 0.7
}
