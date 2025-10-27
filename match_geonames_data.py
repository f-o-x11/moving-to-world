#!/usr/bin/env python3
"""
Match our cities with GeoNames database to get accurate population data
GeoNames format: geonameid, name, asciiname, alternatenames, lat, lon, feature_class, feature_code,
                 country_code, cc2, admin1, admin2, admin3, admin4, population, elevation, dem, timezone, moddate
"""

import sqlite3
import csv
from difflib import SequenceMatcher

def normalize_name(name):
    """Normalize city name for matching"""
    return name.lower().strip().replace('-', ' ').replace('_', ' ')

def similarity(a, b):
    """Calculate similarity between two strings"""
    return SequenceMatcher(None, normalize_name(a), normalize_name(b)).ratio()

def load_geonames_data(filepath):
    """Load GeoNames data into memory"""
    print("Loading GeoNames data...")
    geonames = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 15:
                geonames.append({
                    'name': parts[1],
                    'ascii_name': parts[2],
                    'alt_names': parts[3].split(','),
                    'country_code': parts[8],
                    'population': int(parts[14]) if parts[14] else 0,
                    'latitude': float(parts[4]) if parts[4] else 0,
                    'longitude': float(parts[5]) if parts[5] else 0,
                    'timezone': parts[17] if len(parts) > 17 else ''
                })
    
    print(f"Loaded {len(geonames)} cities from GeoNames")
    return geonames

def get_country_code(country_name):
    """Convert country name to ISO 2-letter code"""
    country_codes = {
        'United States': 'US', 'USA': 'US', 'United States of America': 'US',
        'United Kingdom': 'GB', 'UK': 'GB', 'England': 'GB', 'Scotland': 'GB', 'Wales': 'GB',
        'China': 'CN', 'Japan': 'JP', 'India': 'IN', 'Germany': 'DE', 'France': 'FR',
        'Italy': 'IT', 'Spain': 'ES', 'Canada': 'CA', 'Australia': 'AU', 'Brazil': 'BR',
        'Mexico': 'MX', 'Russia': 'RU', 'South Korea': 'KR', 'Indonesia': 'ID',
        'Turkey': 'TR', 'Saudi Arabia': 'SA', 'Netherlands': 'NL', 'Switzerland': 'CH',
        'Poland': 'PL', 'Belgium': 'BE', 'Sweden': 'SE', 'Austria': 'AT', 'Norway': 'NO',
        'Israel': 'IL', 'United Arab Emirates': 'AE', 'UAE': 'AE', 'Singapore': 'SG',
        'Malaysia': 'MY', 'Philippines': 'PH', 'Thailand': 'TH', 'Vietnam': 'VN',
        'Egypt': 'EG', 'South Africa': 'ZA', 'Nigeria': 'NG', 'Argentina': 'AR',
        'Colombia': 'CO', 'Chile': 'CL', 'Peru': 'PE', 'Venezuela': 'VE',
        'Portugal': 'PT', 'Greece': 'GR', 'Czech Republic': 'CZ', 'Romania': 'RO',
        'Hungary': 'HU', 'Denmark': 'DK', 'Finland': 'FI', 'Ireland': 'IE',
        'New Zealand': 'NZ', 'Pakistan': 'PK', 'Bangladesh': 'BD', 'Ukraine': 'UA',
        'Dominican Republic': 'DO', 'Morocco': 'MA', 'Kenya': 'KE', 'Ethiopia': 'ET',
    }
    return country_codes.get(country_name, '')

def match_city(city_name, country_name, geonames_data):
    """Find best matching city in GeoNames data"""
    country_code = get_country_code(country_name)
    
    # Filter by country first
    candidates = [g for g in geonames_data if g['country_code'] == country_code]
    
    if not candidates:
        # Try without country filter
        candidates = geonames_data
    
    # Find best match by name similarity
    best_match = None
    best_score = 0
    
    for candidate in candidates:
        # Check main name
        score = similarity(city_name, candidate['name'])
        
        # Check ASCII name
        ascii_score = similarity(city_name, candidate['ascii_name'])
        score = max(score, ascii_score)
        
        # Check alternate names
        for alt_name in candidate['alt_names']:
            alt_score = similarity(city_name, alt_name)
            score = max(score, alt_score)
        
        if score > best_score:
            best_score = score
            best_match = candidate
    
    # Only return if similarity is high enough
    if best_score > 0.85:
        return best_match
    
    return None

def update_database():
    """Update city database with GeoNames data"""
    
    # Load GeoNames data
    geonames_data = load_geonames_data('/home/ubuntu/moving_to_world/cities15000.txt')
    
    # Connect to database
    db_path = '/home/ubuntu/moving_to_world/moving_to.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all cities
    cursor.execute("SELECT id, name, country FROM cities")
    cities = cursor.fetchall()
    
    print(f"\nMatching {len(cities)} cities with GeoNames data...")
    
    updated = 0
    not_found = 0
    
    for city_id, city_name, country in cities:
        match = match_city(city_name, country, geonames_data)
        
        if match and match['population'] > 0:
            cursor.execute("""
                UPDATE cities 
                SET population = ?,
                    latitude = ?,
                    longitude = ?,
                    timezone = ?
                WHERE id = ?
            """, (
                match['population'],
                match['latitude'],
                match['longitude'],
                match['timezone'],
                city_id
            ))
            updated += 1
            if updated % 100 == 0:
                print(f"✓ {updated} cities updated...")
        else:
            not_found += 1
        
        # Commit every 1000 cities
        if (updated + not_found) % 1000 == 0:
            conn.commit()
    
    conn.commit()
    conn.close()
    
    print(f"\n=== Results ===")
    print(f"Updated: {updated:,}")
    print(f"Not found: {not_found:,}")
    print(f"Success rate: {updated/len(cities)*100:.1f}%")

if __name__ == "__main__":
    update_database()

