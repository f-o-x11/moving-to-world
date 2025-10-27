#!/usr/bin/env python3
"""
Setup persistent SQLite database for Moving.to
This database will store city data, neighborhoods, rental listings, and more
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

def create_database(db_path='moving_to.db'):
    """Create the persistent database with all necessary tables"""
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Cities table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        country TEXT NOT NULL,
        state_region TEXT,
        latitude REAL,
        longitude REAL,
        population INTEGER,
        timezone TEXT,
        language TEXT,
        currency TEXT,
        climate TEXT,
        walk_score INTEGER,
        avg_rent_usd INTEGER,
        cost_of_living_index REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(name, country, state_region)
    )
    ''')
    
    # Neighborhoods table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS neighborhoods (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        city_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        tags TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (city_id) REFERENCES cities(id),
        UNIQUE(city_id, name)
    )
    ''')
    
    # Rental listings table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS rental_listings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        city_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        bedrooms INTEGER,
        bathrooms INTEGER,
        size_sqm INTEGER,
        price_per_month REAL,
        currency TEXT,
        description TEXT,
        rating REAL,
        external_url TEXT,
        platform TEXT,
        image_url TEXT,
        is_active BOOLEAN DEFAULT 1,
        fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (city_id) REFERENCES cities(id)
    )
    ''')
    
    # Rental platforms table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS rental_platforms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        country TEXT NOT NULL,
        platform_name TEXT NOT NULL,
        platform_url TEXT,
        platform_type TEXT,
        has_api BOOLEAN DEFAULT 0,
        api_key TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(country, platform_name)
    )
    ''')
    
    # Job listings table (for future)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS job_listings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        city_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        company TEXT,
        salary_min INTEGER,
        salary_max INTEGER,
        currency TEXT,
        description TEXT,
        external_url TEXT,
        platform TEXT,
        is_active BOOLEAN DEFAULT 1,
        fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (city_id) REFERENCES cities(id)
    )
    ''')
    
    # Photos table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS city_photos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        city_id INTEGER NOT NULL,
        photo_url TEXT NOT NULL,
        source TEXT,
        caption TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (city_id) REFERENCES cities(id)
    )
    ''')
    
    # Create indexes for better performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_cities_country ON cities(country)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_cities_name ON cities(name)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_neighborhoods_city ON neighborhoods(city_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_rentals_city ON rental_listings(city_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_rentals_active ON rental_listings(is_active)')
    
    conn.commit()
    print("✅ Database schema created successfully")
    
    return conn

def import_existing_data(conn):
    """Import existing city data from JSON files"""
    
    cursor = conn.cursor()
    
    # Import cities from city-database.json
    print("\n📥 Importing cities from city-database.json...")
    with open('city-database.json', 'r', encoding='utf-8') as f:
        cities = json.load(f)
    
    imported = 0
    for city in cities:
        try:
            cursor.execute('''
            INSERT OR IGNORE INTO cities 
            (name, country, state_region, latitude, longitude, population, 
             timezone, language, currency, climate, walk_score, avg_rent_usd, cost_of_living_index)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                city.get('name'),
                city.get('country'),
                city.get('state'),
                city.get('latitude', 0.0),
                city.get('longitude', 0.0),
                city.get('population', 0),
                city.get('timezone', 'UTC'),
                city.get('language', 'English'),
                city.get('currency', 'USD'),
                city.get('climate', 'Temperate'),
                city.get('walkScore', 65),
                city.get('averageRent', 1500),
                city.get('costOfLivingIndex', 100.0)
            ))
            imported += 1
        except Exception as e:
            print(f"  ⚠️  Error importing {city.get('name')}: {e}")
    
    conn.commit()
    print(f"✅ Imported {imported} cities")
    
    # Import neighborhoods from city_enhancements.json
    print("\n📥 Importing neighborhoods from city_enhancements.json...")
    with open('city_enhancements.json', 'r', encoding='utf-8') as f:
        enhancements = json.load(f)
    
    neighborhood_count = 0
    for city_name, data in enhancements.items():
        # Find city_id
        cursor.execute('SELECT id FROM cities WHERE name = ? AND country = ?', 
                      (city_name, data.get('country')))
        result = cursor.fetchone()
        
        if result:
            city_id = result[0]
            
            # Update coordinates if available
            if 'latitude' in data and 'longitude' in data:
                cursor.execute('''
                UPDATE cities 
                SET latitude = ?, longitude = ?
                WHERE id = ?
                ''', (data['latitude'], data['longitude'], city_id))
            
            # Import neighborhoods
            for neighborhood in data.get('neighborhoods', []):
                try:
                    cursor.execute('''
                    INSERT OR IGNORE INTO neighborhoods (city_id, name, description, tags)
                    VALUES (?, ?, ?, ?)
                    ''', (
                        city_id,
                        neighborhood['name'],
                        neighborhood['description'],
                        ','.join(neighborhood.get('tags', []))
                    ))
                    neighborhood_count += 1
                except Exception as e:
                    print(f"  ⚠️  Error importing neighborhood {neighborhood['name']}: {e}")
    
    conn.commit()
    print(f"✅ Imported {neighborhood_count} neighborhoods")
    
    # Import rental platforms
    print("\n📥 Importing rental platforms...")
    with open('rental_platforms_by_country.json', 'r', encoding='utf-8') as f:
        platforms_data = json.load(f)
    
    platform_count = 0
    for country, platforms in platforms_data.get('by_country', {}).items():
        for platform in platforms:
            try:
                cursor.execute('''
                INSERT OR IGNORE INTO rental_platforms 
                (country, platform_name, platform_url, platform_type, has_api)
                VALUES (?, ?, ?, ?, ?)
                ''', (
                    country,
                    platform['name'],
                    platform['url'],
                    platform['type'],
                    platform.get('api_available', False)
                ))
                platform_count += 1
            except Exception as e:
                print(f"  ⚠️  Error importing platform {platform['name']}: {e}")
    
    conn.commit()
    print(f"✅ Imported {platform_count} rental platforms")

def print_statistics(conn):
    """Print database statistics"""
    
    cursor = conn.cursor()
    
    print("\n" + "="*80)
    print("📊 DATABASE STATISTICS")
    print("="*80)
    
    cursor.execute('SELECT COUNT(*) FROM cities')
    print(f"Cities: {cursor.fetchone()[0]:,}")
    
    cursor.execute('SELECT COUNT(*) FROM neighborhoods')
    print(f"Neighborhoods: {cursor.fetchone()[0]:,}")
    
    cursor.execute('SELECT COUNT(*) FROM rental_listings')
    print(f"Rental Listings: {cursor.fetchone()[0]:,}")
    
    cursor.execute('SELECT COUNT(*) FROM rental_platforms')
    print(f"Rental Platforms: {cursor.fetchone()[0]:,}")
    
    cursor.execute('SELECT COUNT(*) FROM job_listings')
    print(f"Job Listings: {cursor.fetchone()[0]:,}")
    
    cursor.execute('SELECT COUNT(*) FROM city_photos')
    print(f"City Photos: {cursor.fetchone()[0]:,}")
    
    cursor.execute('SELECT COUNT(DISTINCT country) FROM cities')
    print(f"Countries: {cursor.fetchone()[0]:,}")
    
    print("="*80)

if __name__ == '__main__':
    print("🏗️  Setting up Moving.to persistent database...")
    print("="*80)
    
    # Create database
    conn = create_database()
    
    # Import existing data
    import_existing_data(conn)
    
    # Print statistics
    print_statistics(conn)
    
    print("\n✅ Database setup complete!")
    print(f"📁 Database file: moving_to.db")
    print(f"📝 You can now add more data using SQL or Python scripts")
    
    conn.close()

