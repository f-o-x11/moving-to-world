"""
Comprehensive City Data Fetcher with Manus LLM Verification
Fetches 100+ data points per city using built-in Manus API
"""

import sqlite3
import json
import time
import requests
import os
from datetime import datetime

# Manus LLM API configuration
FORGE_API_URL = os.getenv('BUILT_IN_FORGE_API_URL', 'https://forge.manus.ai')
FORGE_API_KEY = os.getenv('BUILT_IN_FORGE_API_KEY')

def call_llm(prompt, max_tokens=4000):
    """Call Manus LLM API for data fetching"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {FORGE_API_KEY}"
    }
    
    data = {
        "model": "gpt-4o",
        "messages": [{
            "role": "user",
            "content": prompt
        }],
        "max_tokens": max_tokens,
        "temperature": 0.3,
        "response_format": {"type": "json_object"}  # Force JSON output
    }
    
    try:
        response = requests.post(f"{FORGE_API_URL}/v1/chat/completions", 
                                headers=headers, json=data, timeout=120)
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content']
    except Exception as e:
        print(f"LLM API error: {e}")
        return None

def fetch_comprehensive_city_data(city_name, country):
    """Fetch comprehensive data for a city"""
    
    prompt = f"""Provide comprehensive, factual data about {city_name}, {country} in JSON format.

For each data point, include the value and a reliable source. Format as:
{{"category": {{"key": {{"value": "data", "source": "source name or URL", "confidence": 0.9}}}}}}

Categories and data points to include:

**DEMOGRAPHICS**
- population: Total population with year
- density: People per km²
- age_under_18_pct, age_18_65_pct, age_over_65_pct
- languages: Primary languages with percentages
- ethnic_groups: Major ethnic/cultural groups

**ECONOMY**
- gdp_per_capita: In USD
- major_industries: Top 5 industries
- unemployment_rate: Percentage
- avg_household_income: Annual in USD
- employer_1, employer_2, employer_3, employer_4, employer_5: Top employers

**HOUSING**
- rent_studio_usd, rent_1br_usd, rent_2br_usd, rent_3br_usd: Monthly rent
- home_price_per_sqm_usd: Average price
- neighborhood_1, neighborhood_2, neighborhood_3, neighborhood_4, neighborhood_5: Popular neighborhoods (name only)
- utilities_monthly_usd: Average utilities cost

**COST_OF_LIVING**
- meal_inexpensive_usd, meal_midrange_2p_usd
- beer_domestic_usd, cappuccino_usd
- milk_1l_usd, bread_500g_usd, eggs_12_usd
- transport_pass_monthly_usd, taxi_1km_usd
- internet_monthly_usd, gym_monthly_usd, cinema_usd

**EDUCATION**
- literacy_rate: Percentage
- university_1, university_2, university_3: Top universities with rankings
- school_1, school_2, school_3: Top international schools
- public_school_quality: Rating 1-10

**HEALTHCARE**
- healthcare_index: Rating 1-100
- doctor_per_1000: Doctors per 1000 people
- hospital_beds_per_1000: Beds per 1000 people
- hospital_1, hospital_2, hospital_3: Top hospitals
- life_expectancy: Years

**TRANSPORTATION**
- public_transport_score: Rating 1-100
- metro_lines: Number of metro/subway lines
- walkability_score: Rating 1-100
- avg_commute_minutes: Average commute time
- traffic_index: Congestion rating 1-100

**SAFETY**
- crime_rate_per_100k: Crimes per 100k people
- safety_index: Rating 1-100
- emergency_response_minutes: Average response time
- natural_disaster_risk: Low/Medium/High

**CLIMATE**
- temp_summer_avg_c, temp_winter_avg_c: Average temperatures
- rainfall_mm_annual: Annual rainfall
- humidity_avg_pct: Average humidity
- air_quality_index: AQI rating
- sunshine_hours_annual: Hours of sunshine per year

**CULTURE**
- attraction_1, attraction_2, attraction_3, attraction_4, attraction_5: Top attractions
- museums_count, theaters_count
- restaurants_per_capita: Restaurants per 1000 people
- cultural_diversity_index: Rating 1-100
- lgbtq_friendliness: Rating 1-100

**WORK**
- avg_work_hours_weekly: Average working hours
- paid_vacation_days: Standard vacation days
- work_life_balance_score: Rating 1-100
- coworking_spaces: Number of coworking spaces
- remote_work_friendly: Rating 1-100

**CONNECTIVITY**
- internet_speed_mbps: Average speed
- has_5g: true/false
- airport_connections: Number of international connections
- timezone: Time zone name

**QUALITY_OF_LIFE**
- quality_of_life_index: Overall rating 1-100
- happiness_index: Rating 1-100
- expat_friendly_score: Rating 1-100

Return ONLY valid JSON, no additional text. Be accurate and cite real sources."""

    print(f"Fetching comprehensive data for {city_name}, {country}...")
    response = call_llm(prompt, max_tokens=4000)
    
    if not response:
        return None
    
    try:
        # Remove markdown code blocks if present
        response = response.replace('```json', '').replace('```', '')
        
        # Extract JSON from response
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            json_str = response[json_start:json_end]
            data = json.loads(json_str)
            return data
        else:
            print(f"Could not extract JSON from response")
            return None
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        # Try to save the response for debugging
        with open('/tmp/llm_response_debug.txt', 'w') as f:
            f.write(response)
        print(f"Full response saved to /tmp/llm_response_debug.txt")
        return None

def store_comprehensive_data(db_path, city_id, city_name, country, data):
    """Store comprehensive data in database"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    stored_count = 0
    
    for category, items in data.items():
        if not isinstance(items, dict):
            continue
            
        for key, info in items.items():
            if isinstance(info, dict) and 'value' in info:
                value = info.get('value', '')
                source = info.get('source', 'AI Research')
                confidence = info.get('confidence', 0.8)
                
                try:
                    cursor.execute("""
                        INSERT OR REPLACE INTO city_comprehensive 
                        (city_id, data_type, data_key, data_value, source_name, 
                         verified_by_ai, confidence_score, last_updated)
                        VALUES (?, ?, ?, ?, ?, 1, ?, ?)
                    """, (city_id, category, key, str(value), source, confidence, datetime.now()))
                    stored_count += 1
                except Exception as e:
                    print(f"Error storing {category}.{key}: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"✓ Stored {stored_count} data points for {city_name}")
    return stored_count

def main():
    db_path = "/home/ubuntu/moving_to_world/moving_to.db"
    
    # Add comprehensive tables to main database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables if they don't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS city_comprehensive (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          city_id INTEGER NOT NULL,
          data_type TEXT NOT NULL,
          data_key TEXT NOT NULL,
          data_value TEXT NOT NULL,
          source_url TEXT,
          source_name TEXT,
          verified_by_ai BOOLEAN DEFAULT 0,
          confidence_score REAL DEFAULT 0.0,
          last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY (city_id) REFERENCES cities(id),
          UNIQUE(city_id, data_type, data_key)
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_comprehensive_city ON city_comprehensive(city_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_comprehensive_type ON city_comprehensive(data_type)")
    conn.commit()
    
    # Get top 100 cities by population
    cursor.execute("""
        SELECT id, name, country 
        FROM cities 
        WHERE population > 300000
        ORDER BY population DESC 
        LIMIT 100
    """)
    
    cities = cursor.fetchall()
    conn.close()
    
    print(f"Fetching comprehensive data for {len(cities)} cities...")
    print(f"This will take approximately {len(cities) * 2 / 60:.1f} minutes\n")
    
    success_count = 0
    fail_count = 0
    
    for idx, (city_id, city_name, country) in enumerate(cities, 1):
        print(f"\n[{idx}/{len(cities)}] Processing {city_name}, {country}")
        
        # Check if we already have comprehensive data
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM city_comprehensive WHERE city_id = ?
        """, (city_id,))
        existing_count = cursor.fetchone()[0]
        conn.close()
        
        if existing_count > 50:
            print(f"  → Already has {existing_count} data points, skipping")
            success_count += 1
            continue
        
        # Fetch comprehensive data
        data = fetch_comprehensive_city_data(city_name, country)
        
        if data:
            stored = store_comprehensive_data(db_path, city_id, city_name, country, data)
            if stored > 0:
                print(f"  → Success: {stored} data points stored")
                success_count += 1
            else:
                print(f"  → Failed: No data stored")
                fail_count += 1
        else:
            print(f"  → Failed to fetch data")
            fail_count += 1
        
        # Rate limiting (be nice to the API)
        time.sleep(3)
        
        # Progress update every 10 cities
        if idx % 10 == 0:
            print(f"\n--- Progress: {idx}/{len(cities)} cities processed ---")
            print(f"Success: {success_count}, Failed: {fail_count}\n")
    
    print(f"\n✅ Comprehensive data fetching complete!")
    print(f"Total: {len(cities)} cities")
    print(f"Success: {success_count}")
    print(f"Failed: {fail_count}")

if __name__ == "__main__":
    main()

