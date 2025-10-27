#!/usr/bin/env python3
"""
Comprehensive Autonomous Data Collection System
Fetches ALL data for ALL cities using OpenAI API and web search
"""

import sqlite3
import json
import sys
from openai import OpenAI

# Initialize OpenAI
client = OpenAI()

def fetch_comprehensive_city_data(city_name, country, population):
    """
    Fetch ALL data for a city using GPT-4
    Returns: dict with rent, jobs, attractions, restaurants, schools, hospitals, etc.
    """
    
    prompt = f"""You are a comprehensive city data expert. Provide accurate, current (2025) data for {city_name}, {country} (population: {population:,}).

Return ONLY valid JSON (no markdown, no explanation) with this structure:
{{
    "rent": {{
        "studio": <number>,
        "1br": <number>,
        "2br": <number>,
        "3br": <number>,
        "currency_symbol": "<symbol>"
    }},
    "rental_platforms": [
        {{"name": "<platform>", "url": "<url>"}}
    ],
    "major_employers": ["<company1>", "<company2>", "<company3>"],
    "top_attractions": ["<place1>", "<place2>", "<place3>"],
    "popular_restaurants": ["<restaurant1>", "<restaurant2>", "<restaurant3>"],
    "schools": ["<school1>", "<school2>"],
    "hospitals": ["<hospital1>", "<hospital2>"],
    "transport_score": <0-100>,
    "climate_description": "<brief description>"
}}

Be realistic and specific to this city."""

    try:
        print(f"  Fetching data...", flush=True)
        
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are a comprehensive city data expert. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=800
        )
        
        result = response.choices[0].message.content.strip()
        
        # Clean markdown if present
        if '```' in result:
            result = result.split('```')[1]
            if result.startswith('json'):
                result = result[4:]
            result = result.strip()
        
        data = json.loads(result)
        return data
        
    except Exception as e:
        print(f"  ✗ Error: {e}", flush=True)
        return None

def save_city_data(cursor, city_id, city_name, data):
    """Save comprehensive data to database"""
    
    if not data:
        return False
    
    try:
        # Update rent data
        rent = data.get('rent', {})
        cursor.execute("""
            INSERT OR REPLACE INTO rent_data 
            (city_id, studio_rent, br1_rent, br2_rent, br3_rent, currency)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            city_id,
            rent.get('studio', 0),
            rent.get('1br', 0),
            rent.get('2br', 0),
            rent.get('3br', 0),
            rent.get('currency_symbol', '$')
        ))
        
        # Update city with avg rent
        cursor.execute("""
            UPDATE cities
            SET avg_rent_usd = ?
            WHERE id = ?
        """, (rent.get('1br', 0), city_id))
        
        # Store JSON data for other fields
        cursor.execute("""
            INSERT OR REPLACE INTO city_enriched_data
            (city_id, rental_platforms, major_employers, attractions, 
             restaurants, schools, hospitals, transport_score, climate_desc, raw_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            city_id,
            json.dumps(data.get('rental_platforms', [])),
            json.dumps(data.get('major_employers', [])),
            json.dumps(data.get('top_attractions', [])),
            json.dumps(data.get('popular_restaurants', [])),
            json.dumps(data.get('schools', [])),
            json.dumps(data.get('hospitals', [])),
            data.get('transport_score', 50),
            data.get('climate_description', ''),
            json.dumps(data)
        ))
        
        return True
        
    except Exception as e:
        print(f"  ✗ Save error: {e}", flush=True)
        return False

def create_tables(conn):
    """Create necessary tables"""
    cursor = conn.cursor()
    
    # Rent data table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rent_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city_id INTEGER UNIQUE,
            studio_rent INTEGER,
            br1_rent INTEGER,
            br2_rent INTEGER,
            br3_rent INTEGER,
            currency TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (city_id) REFERENCES cities(id)
        )
    """)
    
    # Comprehensive enriched data table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS city_enriched_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city_id INTEGER UNIQUE,
            rental_platforms TEXT,
            major_employers TEXT,
            attractions TEXT,
            restaurants TEXT,
            schools TEXT,
            hospitals TEXT,
            transport_score INTEGER,
            climate_desc TEXT,
            raw_json TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (city_id) REFERENCES cities(id)
        )
    """)
    
    conn.commit()
    print("✓ Database tables ready\n", flush=True)

def fetch_for_top_cities(limit=100):
    """Fetch data for top N cities by population"""
    
    conn = sqlite3.connect('/home/ubuntu/moving_to_world/moving_to.db')
    create_tables(conn)
    cursor = conn.cursor()
    
    # Get top cities
    cursor.execute("""
        SELECT id, name, country, population
        FROM cities
        WHERE population > 0
        ORDER BY population DESC
        LIMIT ?
    """, (limit,))
    
    cities = cursor.fetchall()
    
    print(f"=== Fetching Comprehensive Data for Top {len(cities)} Cities ===\n", flush=True)
    
    success = 0
    errors = 0
    
    for i, (city_id, name, country, population) in enumerate(cities, 1):
        print(f"[{i}/{len(cities)}] {name}, {country} ({population:,})", flush=True)
        
        data = fetch_comprehensive_city_data(name, country, population)
        
        if data and save_city_data(cursor, city_id, name, data):
            rent = data.get('rent', {})
            print(f"  ✓ {rent.get('currency_symbol', '$')}{rent.get('1br', 0):,}/mo (1BR)", flush=True)
            success += 1
            
            if success % 10 == 0:
                conn.commit()
                print(f"\n--- Checkpoint: {success} cities completed ---\n", flush=True)
        else:
            errors += 1
            print(f"  ✗ Failed", flush=True)
        
        print(flush=True)  # Blank line
    
    conn.commit()
    conn.close()
    
    print(f"\n=== Complete ===")
    print(f"✓ Success: {success}/{len(cities)}")
    print(f"✗ Errors: {errors}")
    print(f"Success rate: {success/len(cities)*100:.1f}%")

if __name__ == "__main__":
    # Get limit from command line or default to 100
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    
    print(f"Starting comprehensive data fetch for top {limit} cities...\n", flush=True)
    fetch_for_top_cities(limit)

