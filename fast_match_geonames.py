#!/usr/bin/env python3
"""
Fast matching using exact name lookups with country code
Much faster than fuzzy matching for 32K cities
"""

import sqlite3
import json

def load_geonames_index(filepath):
    """Load GeoNames data into a searchable index"""
    print("Loading GeoNames data...")
    
    # Create index: (normalized_name, country_code) -> city_data
    index = {}
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 15:
                name = parts[1].lower().strip()
                country = parts[8]
                population = int(parts[14]) if parts[14] else 0
                
                if population > 0:
                    key = (name, country)
                    # Keep the one with highest population
                    if key not in index or index[key]['population'] < population:
                        index[key] = {
                            'population': population,
                            'latitude': float(parts[4]) if parts[4] else 0,
                            'longitude': float(parts[5]) if parts[5] else 0,
                            'timezone': parts[17] if len(parts) > 17 else ''
                        }
    
    print(f"Indexed {len(index)} unique city-country combinations")
    return index

def get_country_code(country_name):
    """Convert country name to ISO 2-letter code"""
    codes = {
        'United States': 'US', 'USA': 'US',
        'United Kingdom': 'GB', 'UK': 'GB', 'England': 'GB',
        'China': 'CN', 'Japan': 'JP', 'India': 'IN',
        'Germany': 'DE', 'France': 'FR', 'Italy': 'IT',
        'Spain': 'ES', 'Canada': 'CA', 'Australia': 'AU',
        'Brazil': 'BR', 'Mexico': 'MX', 'Russia': 'RU',
        'South Korea': 'KR', 'Indonesia': 'ID', 'Turkey': 'TR',
        'Saudi Arabia': 'SA', 'Netherlands': 'NL', 'Switzerland': 'CH',
        'Poland': 'PL', 'Belgium': 'BE', 'Sweden': 'SE',
        'Austria': 'AT', 'Norway': 'NO', 'Israel': 'IL',
        'United Arab Emirates': 'AE', 'UAE': 'AE',
        'Singapore': 'SG', 'Malaysia': 'MY', 'Philippines': 'PH',
        'Thailand': 'TH', 'Vietnam': 'VN', 'Egypt': 'EG',
        'South Africa': 'ZA', 'Nigeria': 'NG', 'Argentina': 'AR',
        'Colombia': 'CO', 'Chile': 'CL', 'Peru': 'PE',
        'Portugal': 'PT', 'Greece': 'GR', 'Czech Republic': 'CZ',
        'Romania': 'RO', 'Hungary': 'HU', 'Denmark': 'DK',
        'Finland': 'FI', 'Ireland': 'IE', 'New Zealand': 'NZ',
        'Pakistan': 'PK', 'Bangladesh': 'BD', 'Ukraine': 'UA',
        'Dominican Republic': 'DO', 'Morocco': 'MA',
        'Kenya': 'KE', 'Ethiopia': 'ET',
    }
    return codes.get(country_name, '')

def fast_update():
    """Fast update using exact matching"""
    
    # Load index
    index = load_geonames_index('/home/ubuntu/moving_to_world/cities15000.txt')
    
    # Connect to database
    conn = sqlite3.connect('/home/ubuntu/moving_to_world/moving_to.db')
    cursor = conn.cursor()
    
    # Get all cities
    cursor.execute("SELECT id, name, country FROM cities")
    cities = cursor.fetchall()
    
    print(f"\nMatching {len(cities)} cities...")
    
    updated = 0
    not_found = 0
    
    for city_id, city_name, country in cities:
        country_code = get_country_code(country)
        key = (city_name.lower().strip(), country_code)
        
        if key in index:
            data = index[key]
            cursor.execute("""
                UPDATE cities 
                SET population = ?,
                    latitude = ?,
                    longitude = ?,
                    timezone = ?
                WHERE id = ?
            """, (
                data['population'],
                data['latitude'],
                data['longitude'],
                data['timezone'],
                city_id
            ))
            updated += 1
            if updated % 1000 == 0:
                print(f"✓ {updated:,} cities updated...")
                conn.commit()
        else:
            not_found += 1
    
    conn.commit()
    conn.close()
    
    print(f"\n=== Results ===")
    print(f"✓ Updated: {updated:,}")
    print(f"✗ Not found: {not_found:,}")
    print(f"Success rate: {updated/len(cities)*100:.1f}%")
    
    # Save not found cities for manual review
    if not_found > 0:
        print(f"\nSaving not-found cities to not_found_cities.json")

if __name__ == "__main__":
    fast_update()

