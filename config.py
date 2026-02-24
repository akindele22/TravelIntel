"""
Configuration file for the travel advisory scraper
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Database Configuration (PostgreSQL only)
#
# In production the app connects to a PostgreSQL instance.  Set the
# following environment variables in your deployment:
#
#   DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
#
# The older SQLite fallback has been removed; if you need a lightweight
# local database for testing, set up a Postgres container or use the
# `travel_advisories.db` file manually.

DATABASE_CONFIG = {
    # A complete connection URL (Render sets ``DATABASE_URL`` automatically for
    # managed Postgres instances).  If provided it will take precedence in
    # ``database.connect()``; otherwise individual components below are used.
    'url': os.getenv('DB_URL', ''),

    'host': os.getenv('DB_HOST', 'postgresql://traveldb_beh4_user:O3kEpjP135z4iGsNs6v1IWSxxfstuCc9@dpg-d6endrp5pdvs73fv9sb0-a.oregon-postgres.render.com/traveldb_beh4
'),
    'port': int(os.getenv('DB_PORT', '5432')),
    'database': os.getenv('DB_NAME', 'travel_advisories'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', ''),
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
    'un_reliefweb': 'https://reliefweb.int/',
    'crisisgroup': 'https://www.crisisgroup.org/',
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
