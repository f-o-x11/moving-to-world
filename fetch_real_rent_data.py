#!/usr/bin/env python3
"""
Fetch real rent data using OpenAI API and web search
This will build an accurate database of rental prices
"""

import sqlite3
import json
import os
from openai import OpenAI

# Initialize OpenAI client (API key already in environment)
client = OpenAI()

def get_real_rent_data(city_name, country):
    """Use GPT to get real rent data for a city"""
    
    prompt = f"""You are a real estate data expert. Provide accurate, current (2025) average monthly rent prices for {city_name}, {country}.

Return ONLY a JSON object with this exact structure (no markdown, no explanation):
{{
    "studio": <number>,
    "1br": <number>,
    "2br": <number>,
    "3br": <number>,
    "currency": "<symbol>",
    "notes": "<brief note about market>"
}}

Use the local currency. Be realistic based on actual market data."""

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are a real estate data expert providing accurate rental price data."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=200
        )
        
        result = response.choices[0].message.content.strip()
        
        # Parse JSON
        # Remove markdown code blocks if present
        if result.startswith('```'):
            result = result.split('```')[1]
            if result.startswith('json'):
                result = result[4:]
        
        data = json.loads(result)
        return data
        
    except Exception as e:
        print(f"  ✗ Error getting data for {city_name}: {e}")
        return None

def update_rent_data_for_top_cities():
    """Update rent data for top 100 cities using real data"""
    
    conn = sqlite3.connect('/home/ubuntu/moving_to_world/moving_to.db')
    cursor = conn.cursor()
    
    # Get top cities by population
    cursor.execute("""
        SELECT id, name, country, population
        FROM cities
        WHERE population > 0
        ORDER BY population DESC
        LIMIT 100
    """)
    
    cities = cursor.fetchall()
    
    print(f"Fetching real rent data for top {len(cities)} cities...")
    print("This will use OpenAI API (may take a few minutes)\n")
    
    updated = 0
    errors = 0
    
    for city_id, name, country, population in cities:
        print(f"Fetching: {name}, {country} ({population:,})...")
        
        rent_data = get_real_rent_data(name, country)
        
        if rent_data:
            # Store in database
            cursor.execute("""
                UPDATE cities
                SET avg_rent_usd = ?
                WHERE id = ?
            """, (rent_data.get('1br', 0), city_id))
            
            # Also store detailed breakdown
            cursor.execute("""
                INSERT OR REPLACE INTO rent_data 
                (city_id, studio_rent, br1_rent, br2_rent, br3_rent, currency, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                city_id,
                rent_data.get('studio', 0),
                rent_data.get('1br', 0),
                rent_data.get('2br', 0),
                rent_data.get('3br', 0),
                rent_data.get('currency', '$'),
                rent_data.get('notes', '')
            ))
            
            print(f"  ✓ {name}: {rent_data.get('currency', '$')}{rent_data.get('1br', 0):,}/mo (1BR)")
            updated += 1
            
            if updated % 10 == 0:
                conn.commit()
                print(f"\n--- {updated} cities updated ---\n")
        else:
            errors += 1
    
    conn.commit()
    conn.close()
    
    print(f"\n=== Complete ===")
    print(f"✓ Updated: {updated}")
    print(f"✗ Errors: {errors}")

if __name__ == "__main__":
    # First create rent_data table
    conn = sqlite3.connect('/home/ubuntu/moving_to_world/moving_to.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rent_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city_id INTEGER UNIQUE,
            studio_rent INTEGER,
            br1_rent INTEGER,
            br2_rent INTEGER,
            br3_rent INTEGER,
            currency TEXT,
            notes TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (city_id) REFERENCES cities(id)
        )
    """)
    
    conn.commit()
    conn.close()
    
    print("✓ rent_data table ready\n")
    
    # Fetch data
    update_rent_data_for_top_cities()

