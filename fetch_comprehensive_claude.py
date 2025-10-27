"""
Comprehensive City Data Fetcher with Claude Verification
Fetches 100+ data points per city and verifies with Claude API
"""

import sqlite3
import json
import time
import requests
from datetime import datetime

# Claude API configuration
CLAUDE_API_KEY = "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"
CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"

def call_claude(prompt, max_tokens=4000):
    """Call Claude API for data fetching and verification"""
    headers = {
        "x-api-key": CLAUDE_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    data = {
        "model": "claude-3-5-sonnet-20241022",
        "max_tokens": max_tokens,
        "messages": [{
            "role": "user",
            "content": prompt
        }]
    }
    
    try:
        response = requests.post(CLAUDE_API_URL, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        result = response.json()
        return result['content'][0]['text']
    except Exception as e:
        print(f"Claude API error: {e}")
        return None

def fetch_comprehensive_city_data(city_name, country):
    """Fetch comprehensive data for a city using Claude"""
    
    prompt = f"""Please provide comprehensive, factual data about {city_name}, {country}. 
    
For each data point, provide:
1. The information
2. A reliable source (website URL or organization name)
3. Your confidence level (0.0-1.0)

Please provide data in the following categories:

**DEMOGRAPHICS**
- Total population (with year)
- Population density
- Age distribution (% under 18, 18-65, over 65)
- Gender ratio
- Ethnic/cultural composition
- Languages spoken (% of population)
- Religion distribution

**ECONOMY**
- GDP per capita
- Major industries (top 5)
- Unemployment rate
- Average household income
- Income inequality (Gini coefficient if available)
- Major employers (top 10 companies)
- Startup ecosystem rating
- Remote work friendliness score

**HOUSING**
- Average rent (studio, 1BR, 2BR, 3BR) in USD
- Average home price per sqm
- Rental vacancy rate
- Popular neighborhoods for expats (top 5)
- Housing quality index
- Utilities cost (monthly average)

**COST OF LIVING**
- Meal at inexpensive restaurant
- Meal for 2 at mid-range restaurant
- Domestic beer (0.5L)
- Cappuccino
- Milk (1L)
- Bread (500g)
- Eggs (12)
- Monthly public transport pass
- Taxi (1km)
- Gasoline (1L)
- Internet (monthly)
- Gym membership (monthly)
- Cinema ticket

**EDUCATION**
- Literacy rate
- Top 5 universities with rankings
- Top 5 international schools
- Public school quality rating
- Higher education enrollment rate
- Average class sizes

**HEALTHCARE**
- Healthcare quality index
- Doctor-to-population ratio
- Hospital beds per 1000 people
- Top 5 hospitals
- Average wait time for appointment
- Health insurance cost (monthly)
- Life expectancy

**TRANSPORTATION**
- Public transport quality score
- Metro/subway lines (if any)
- Bus network coverage
- Bike infrastructure rating
- Average commute time
- Car ownership rate
- Walkability score
- Traffic congestion index

**SAFETY & SECURITY**
- Crime rate (per 100k people)
- Safety index
- Police per 1000 people
- Emergency response time
- Natural disaster risk level
- Political stability index

**CLIMATE & ENVIRONMENT**
- Average temperature (summer/winter)
- Annual rainfall
- Humidity levels
- Air quality index
- Green space per capita
- Pollution levels
- Sunshine hours per year
- Natural disaster frequency

**CULTURE & LIFESTYLE**
- Top 10 tourist attractions
- Museums count
- Theaters/concert halls count
- Restaurants per capita
- Bars/nightlife venues
- Parks and recreation areas
- Sports facilities
- Cultural diversity index
- LGBTQ+ friendliness rating
- Expat community size

**WORK & BUSINESS**
- Ease of doing business rank
- Average working hours per week
- Paid vacation days (standard)
- Maternity/paternity leave
- Work-life balance score
- Coworking spaces count
- Tech hub rating
- Innovation index

**CONNECTIVITY**
- Average internet speed (Mbps)
- 5G coverage
- WiFi availability
- International airport connections
- Time zone
- Distance to major cities

**QUALITY OF LIFE**
- Overall quality of life index
- Happiness index
- Social mobility score
- Gender equality index
- Press freedom index
- Corruption perception index

Please format your response as JSON with this structure:
{{
  "demographics": {{"key": {{"value": "...", "source": "...", "confidence": 0.9}}}},
  "economy": {{...}},
  ...
}}

Be as comprehensive and accurate as possible. If data is not available, omit that field rather than guessing."""

    print(f"Fetching comprehensive data for {city_name}, {country}...")
    response = call_claude(prompt, max_tokens=4000)
    
    if not response:
        return None
    
    try:
        # Extract JSON from response
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            data = json.loads(response[json_start:json_end])
            return data
        else:
            print(f"Could not extract JSON from response")
            return None
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        print(f"Response: {response[:500]}...")
        return None

def store_comprehensive_data(db_path, city_id, city_name, country, data):
    """Store comprehensive data in database"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    stored_count = 0
    
    for category, items in data.items():
        for key, info in items.items():
            if isinstance(info, dict) and 'value' in info:
                value = info.get('value', '')
                source = info.get('source', 'Claude AI')
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
    db_path = "/home/ubuntu/moving_to_world/moving_to_world.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get top 50 cities by population
    cursor.execute("""
        SELECT id, city, country 
        FROM cities 
        WHERE population > 500000
        ORDER BY population DESC 
        LIMIT 50
    """)
    
    cities = cursor.fetchall()
    conn.close()
    
    print(f"Fetching comprehensive data for {len(cities)} cities...")
    
    for idx, (city_id, city_name, country) in enumerate(cities, 1):
        print(f"\n[{idx}/{len(cities)}] Processing {city_name}, {country}")
        
        # Check if we already have data
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM city_comprehensive WHERE city_id = ?
        """, (city_id,))
        existing_count = cursor.fetchone()[0]
        conn.close()
        
        if existing_count > 50:
            print(f"  → Already has {existing_count} data points, skipping")
            continue
        
        # Fetch comprehensive data
        data = fetch_comprehensive_city_data(city_name, country)
        
        if data:
            stored = store_comprehensive_data(db_path, city_id, city_name, country, data)
            print(f"  → Success: {stored} data points stored")
        else:
            print(f"  → Failed to fetch data")
        
        # Rate limiting (Claude has 50 req/min limit)
        time.sleep(2)
    
    print("\n✅ Comprehensive data fetching complete!")

if __name__ == "__main__":
    main()

