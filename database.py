"""
PostgreSQL Database Handler
"""
import psycopg2
from psycopg2.extras import execute_values
from psycopg2 import sql
from typing import List, Dict, Optional
from datetime import datetime
import config
from contextlib import contextmanager


class DatabaseHandler:
    """Handles all database operations for travel advisories"""
    
    def __init__(self):
        """Initialize database connection"""
        self.conn = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        """Establish database connection"""
        try:
            # If DATABASE_URL is set (e.g., by Render), use it directly
            db_url = config.DATABASE_CONFIG.get('DATABASE_URL', '')
            if db_url:
                self.conn = psycopg2.connect(db_url)
            else:
                # Otherwise use individual components
                self.conn = psycopg2.connect(
                    host=config.DATABASE_CONFIG['host'],
                    port=config.DATABASE_CONFIG['port'],
                    database=config.DATABASE_CONFIG['database'],
                    user=config.DATABASE_CONFIG['user'],
                    password=config.DATABASE_CONFIG['password']
                )
            self.conn.autocommit = False
            print("Database connection established")
        except Exception as e:
            print(f"Error connecting to database: {e}")
            raise
    
    @contextmanager
    def get_cursor(self):
        """Context manager for database cursor"""
        cursor = self.conn.cursor()
        try:
            yield cursor
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            print(f"Database error: {e}")
            raise
        finally:
            cursor.close()
    
    def create_tables(self):
        """Create necessary database tables"""
        with self.get_cursor() as cursor:
            # Main advisories table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS travel_advisories (
                    id SERIAL PRIMARY KEY,
                    source VARCHAR(100) NOT NULL,
                    country VARCHAR(200) NOT NULL,
                    risk_level VARCHAR(50),
                    date TIMESTAMP,
                    description TEXT,
                    url TEXT,
                    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(source, country, date)
                )
            """)
            
            # Processed/cleaned data table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS processed_advisories (
                    id SERIAL PRIMARY KEY,
                    advisory_id INTEGER REFERENCES travel_advisories(id),
                    country_normalized VARCHAR(200),
                    risk_level_normalized VARCHAR(50),
                    risk_score INTEGER,
                    keywords TEXT[],
                    sentiment_score FLOAT,
                    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Predictions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS predictions (
                    id SERIAL PRIMARY KEY,
                    advisory_id INTEGER REFERENCES travel_advisories(id),
                    predicted_risk_level VARCHAR(50),
                    predicted_risk_score FLOAT,
                    confidence FLOAT,
                    model_version VARCHAR(50),
                    predicted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for better query performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_advisories_country 
                ON travel_advisories(country)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_advisories_source 
                ON travel_advisories(source)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_advisories_date 
                ON travel_advisories(date)
            """)
            
            print("Database tables created/verified")
    
    def insert_advisories(self, advisories: List[Dict]) -> int:
        """Insert or update travel advisories"""
        if not advisories:
            return 0
        
        inserted_count = 0
        with self.get_cursor() as cursor:
            for advisory in advisories:
                try:
                    # Parse date if available
                    date_value = None
                    if advisory.get('date'):
                        try:
                            date_value = datetime.fromisoformat(advisory['date'].replace('Z', '+00:00'))
                        except:
                            pass
                    
                    cursor.execute("""
                        INSERT INTO travel_advisories 
                        (source, country, risk_level, date, description, url, scraped_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (source, country, date) 
                        DO UPDATE SET
                            risk_level = EXCLUDED.risk_level,
                            description = EXCLUDED.description,
                            url = EXCLUDED.url,
                            updated_at = CURRENT_TIMESTAMP
                    """, (
                        advisory.get('source'),
                        advisory.get('country'),
                        advisory.get('risk_level'),
                        date_value,
                        advisory.get('description', ''),
                        advisory.get('url'),
                        datetime.now()
                    ))
                    inserted_count += 1
                except Exception as e:
                    print(f"Error inserting advisory: {e}")
                    continue
        
        return inserted_count
    
    def get_advisories(self, country: Optional[str] = None, 
                      source: Optional[str] = None,
                      limit: int = 100) -> List[Dict]:
        """Retrieve advisories from database"""
        with self.get_cursor() as cursor:
            query = "SELECT * FROM travel_advisories WHERE 1=1"
            params = []
            
            if country:
                query += " AND country ILIKE %s"
                params.append(f"%{country}%")
            
            if source:
                query += " AND source = %s"
                params.append(source)
            
            query += " ORDER BY scraped_at DESC LIMIT %s"
            params.append(limit)
            
            cursor.execute(query, params)
            columns = [desc[0] for desc in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            return results
    
    def insert_processed_data(self, processed_data: List[Dict]):
        """Insert processed/cleaned advisory data"""
        with self.get_cursor() as cursor:
            for data in processed_data:
                cursor.execute("""
                    INSERT INTO processed_advisories 
                    (advisory_id, country_normalized, risk_level_normalized, 
                     risk_score, keywords, sentiment_score)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    data.get('advisory_id'),
                    data.get('country_normalized'),
                    data.get('risk_level_normalized'),
                    data.get('risk_score'),
                    data.get('keywords', []),
                    data.get('sentiment_score')
                ))
    
    def insert_prediction(self, prediction: Dict):
        """Insert AI prediction result"""
        with self.get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO predictions 
                (advisory_id, predicted_risk_level, predicted_risk_score, 
                 confidence, model_version)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                prediction.get('advisory_id'),
                prediction.get('predicted_risk_level'),
                prediction.get('predicted_risk_score'),
                prediction.get('confidence'),
                prediction.get('model_version', 'v1.0')
            ))
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print("Database connection closed")
