"""
Utility script to query the database
"""
import argparse
from database import DatabaseHandler
import pandas as pd
import config


def query_advisories(country=None, source=None, limit=100):
    """Query advisories from database"""
    db = DatabaseHandler()
    
    try:
        advisories = db.get_advisories(country=country, source=source, limit=limit)
        
        if advisories:
            df = pd.DataFrame(advisories)
            print(f"\nFound {len(advisories)} advisories")
            print("\n" + "="*80)
            print(df.to_string(index=False))
            print("="*80)
            
            # Summary statistics
            if 'risk_level' in df.columns:
                print("\nRisk Level Distribution:")
                print(df['risk_level'].value_counts())
            
            if 'source' in df.columns:
                print("\nSource Distribution:")
                print(df['source'].value_counts())
        else:
            print("No advisories found matching criteria")
    
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description='Query travel advisories database')
    parser.add_argument('--country', type=str, help='Filter by country name')
    parser.add_argument('--source', type=str, 
                       choices=['US State Department', 'UK FCDO', 'Smart Traveller (Australia)', 
                               'IATA Travel Centre', 'Canada Travel'],
                       help='Filter by source')
    parser.add_argument('--limit', type=int, default=100, help='Limit number of results')
    
    args = parser.parse_args()
    
    query_advisories(country=args.country, source=args.source, limit=args.limit)


if __name__ == '__main__':
    main()
