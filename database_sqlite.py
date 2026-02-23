"""
SQLite Database Handler (Fallback for PostgreSQL)
Provides same API as PostgreSQL handler for development/testing
"""
import sqlite3
import json
from typing import List, Dict, Optional
from datetime import datetime
from contextlib import contextmanager
import config


class DatabaseHandler:
    """SQLite database handler - compatible with PostgreSQL version"""
    
    def __init__(self, db_path: str = 'travel_advisories.db'):
        """Initialize SQLite database"""
        self.db_path = db_path
        self.conn = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        """Establish database connection"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            print(f"Database connection established: {self.db_path}")
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
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
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
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    advisory_id INTEGER REFERENCES travel_advisories(id),
                    country_normalized VARCHAR(200),
                    risk_level_normalized VARCHAR(50),
                    risk_score INTEGER,
                    keywords TEXT,
                    sentiment_score FLOAT,
                    has_security_concerns INTEGER DEFAULT 0,
                    has_safety_concerns INTEGER DEFAULT 0,
                    has_serenity_concerns INTEGER DEFAULT 0,
                    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Predictions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    advisory_id INTEGER REFERENCES travel_advisories(id),
                    predicted_risk_level VARCHAR(50),
                    predicted_risk_score FLOAT,
                    confidence FLOAT,
                    model_version VARCHAR(50),
                    predicted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for better query performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_country ON travel_advisories(country)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_source ON travel_advisories(source)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_date ON travel_advisories(date)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_country_norm ON processed_advisories(country_normalized)")
    
    def insert_advisories(self, advisories: List[Dict]) -> int:
        """Insert/update advisories into database"""
        count = 0
        
        with self.get_cursor() as cursor:
            for advisory in advisories:
                try:
                    cursor.execute("""
                        INSERT OR REPLACE INTO travel_advisories 
                        (source, country, risk_level, date, description, url, scraped_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        advisory.get('source', ''),
                        advisory.get('country', ''),
                        advisory.get('risk_level', ''),
                        advisory.get('date'),
                        advisory.get('description', ''),
                        advisory.get('url', ''),
                        datetime.utcnow()
                    ))
                    count += 1
                except Exception as e:
                    print(f"Error inserting advisory: {e}")
                    continue
        
        return count
    
    def insert_processed_data(self, processed_data: List[Dict]) -> int:
        """Insert processed/cleaned advisory data"""
        count = 0
        
        with self.get_cursor() as cursor:
            for data in processed_data:
                try:
                    # Convert keywords list to JSON string
                    keywords_json = json.dumps(data.get('keywords', []))
                    
                    cursor.execute("""
                        INSERT INTO processed_advisories 
                        (advisory_id, country_normalized, risk_level_normalized, risk_score, 
                         keywords, sentiment_score, has_security_concerns, has_safety_concerns, 
                         has_serenity_concerns)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        data.get('advisory_id'),
                        data.get('country_normalized', ''),
                        data.get('risk_level_normalized', ''),
                        data.get('risk_score', 0),
                        keywords_json,
                        data.get('sentiment_score', 0.0),
                        1 if data.get('has_security_concerns') else 0,
                        1 if data.get('has_safety_concerns') else 0,
                        1 if data.get('has_serenity_concerns') else 0
                    ))
                    count += 1
                except Exception as e:
                    print(f"Error inserting processed data: {e}")
                    continue
        
        return count
    
    def get_advisories(self, country: Optional[str] = None, 
                      source: Optional[str] = None, 
                      limit: int = 5000) -> List[Dict]:
        """Retrieve advisories with optional filters"""
        query = "SELECT * FROM travel_advisories WHERE 1=1"
        params = []
        
        if country:
            query += " AND country LIKE ?"
            params.append(f"%{country}%")
        
        if source:
            query += " AND source = ?"
            params.append(source)
        
        query += " ORDER BY date DESC LIMIT ?"
        params.append(limit)
        
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
        return [dict(row) for row in rows]
    
    def get_processed_advisories(self, country_normalized: Optional[str] = None,
                                limit: int = 5000) -> List[Dict]:
        """Retrieve processed advisories"""
        query = "SELECT * FROM processed_advisories WHERE 1=1"
        params = []
        
        if country_normalized:
            query += " AND country_normalized = ?"
            params.append(country_normalized)
        
        query += " ORDER BY processed_at DESC LIMIT ?"
        params.append(limit)
        
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            rows = cursor.fetchall()
        
        # Parse JSON keywords back to lists
        result = []
        for row in rows:
            d = dict(row)
            try:
                d['keywords'] = json.loads(d['keywords']) if d.get('keywords') else []
            except:
                d['keywords'] = []
            result.append(d)
        
        return result
    
    def get_all_countries(self) -> List[str]:
        """Get list of all countries in database"""
        with self.get_cursor() as cursor:
            cursor.execute("SELECT DISTINCT country FROM travel_advisories ORDER BY country")
            rows = cursor.fetchall()
        
        return [row['country'] for row in rows]
    
    def delete_old_data(self, days: int = 365) -> int:
        """Delete data older than specified days"""
        from datetime import datetime, timedelta
        
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        with self.get_cursor() as cursor:
            cursor.execute(
                "DELETE FROM travel_advisories WHERE date < ?",
                (cutoff,)
            )
            count = cursor.rowcount
        
        return count
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print("Database connection closed")
    
    def __del__(self):
        """Ensure connection is closed on cleanup"""
        self.close()
