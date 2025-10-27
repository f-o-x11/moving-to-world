#!/usr/bin/env python3.11
"""
Fetch comprehensive cost-of-living, income, and quality scores for cities using OpenAI API
"""

import sqlite3
import json
import os
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI()

def fetch_city_comprehensive_data(city_name, country):
    """Fetch comprehensive data for a city using OpenAI"""
    
    prompt = f"""Provide comprehensive relocation data for {city_name}, {country} in JSON format.

Return ONLY valid JSON (no markdown, no explanations) with this exact structure:
{{
  "costs": {{
    "housing_monthly": <number in local currency>,
    "food_monthly": <number>,
    "transport_monthly": <number>,
    "utilities_monthly": <number>,
    "healthcare_monthly": <number>,
    "education_monthly": <number>,
    "leisure_monthly": <number>,
    "currency": "<3-letter code>",
    "exchange_rate_to_usd": <number>
  }},
  "incomes": {{
    "median_individual_income": <annual in local currency>,
    "median_household_income": <annual in local currency>,
    "sample_size": <estimated sample size or null>
  }},
  "scores": {{
    "walkability": <0-100>,
    "bikeability": <0-100>,
    "safety_index": <0-100>,
    "healthcare_index": <0-100>,
    "internet_speed": <Mbps average>,
    "education_quality": <0-100>
  }},
  "neighborhoods": [
    {{
      "name": "<real neighborhood name>",
      "description": "<brief description>",
      "tags": ["<tag1>", "<tag2>", "<tag3>"]
    }}
  ]
}}

Use real, accurate data based on 2024 statistics. For costs, use monthly averages for a single person.
For neighborhoods, provide 5-10 real districts with accurate descriptions and relevant tags (e.g., "hipster", "family-friendly", "business", "nightlife", "suburban", "historic").
"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are a relocation data expert. Provide accurate, real data for cities worldwide. Always return valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1500
        )
        
        content = response.choices[0].message.content.strip()
        
        # Remove markdown code blocks if present
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
            content = content.strip()
        
        data = json.loads(content)
        return data
        
    except Exception as e:
        print(f"Error fetching data for {city_name}: {e}")
        return None

def save_comprehensive_data(city_id, city_name, country, data):
    """Save comprehensive data to database"""
    
    conn = sqlite3.connect('moving_to.db')
    cursor = conn.cursor()
    
    try:
        # Save costs
        if 'costs' in data:
            costs = data['costs']
            cursor.execute("""
                INSERT INTO costs (city_id, housing_monthly, food_monthly, transport_monthly, 
                                 utilities_monthly, healthcare_monthly, education_monthly, 
                                 leisure_monthly, currency, exchange_rate_to_usd)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                city_id,
                costs.get('housing_monthly'),
                costs.get('food_monthly'),
                costs.get('transport_monthly'),
                costs.get('utilities_monthly'),
                costs.get('healthcare_monthly'),
                costs.get('education_monthly'),
                costs.get('leisure_monthly'),
                costs.get('currency'),
                costs.get('exchange_rate_to_usd')
            ))
        
        # Save incomes
        if 'incomes' in data:
            incomes = data['incomes']
            cursor.execute("""
                INSERT INTO incomes (city_id, median_individual_income, median_household_income, sample_size)
                VALUES (?, ?, ?, ?)
            """, (
                city_id,
                incomes.get('median_individual_income'),
                incomes.get('median_household_income'),
                incomes.get('sample_size')
            ))
        
        # Save scores
        if 'scores' in data:
            scores = data['scores']
            cursor.execute("""
                INSERT INTO scores (city_id, walkability, bikeability, safety_index, 
                                  healthcare_index, internet_speed, education_quality)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                city_id,
                scores.get('walkability'),
                scores.get('bikeability'),
                scores.get('safety_index'),
                scores.get('healthcare_index'),
                scores.get('internet_speed'),
                scores.get('education_quality')
            ))
        
        # Save neighborhoods
        if 'neighborhoods' in data:
            for nb in data['neighborhoods']:
                cursor.execute("""
                    INSERT OR IGNORE INTO neighborhoods (city_id, name, description, tags)
                    VALUES (?, ?, ?, ?)
                """, (
                    city_id,
                    nb.get('name'),
                    nb.get('description'),
                    json.dumps(nb.get('tags', []))
                ))
        
        conn.commit()
        print(f"✓ Saved comprehensive data for {city_name}, {country}")
        return True
        
    except Exception as e:
        print(f"✗ Error saving data for {city_name}: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

def main():
    """Fetch comprehensive data for top 100 cities"""
    
    conn = sqlite3.connect('moving_to.db')
    cursor = conn.cursor()
    
    # Get top 100 cities by population that don't have comprehensive data yet
    cursor.execute("""
        SELECT c.id, c.name, c.country, c.population
        FROM cities c
        LEFT JOIN costs co ON c.id = co.city_id
        WHERE co.id IS NULL
        ORDER BY c.population DESC
        LIMIT 100
    """)
    
    cities = cursor.fetchall()
    conn.close()
    
    print(f"Fetching comprehensive data for {len(cities)} cities...")
    
    success = 0
    errors = 0
    
    for city_id, name, country, population in cities:
        print(f"\nFetching data for {name}, {country} (pop: {population:,})...")
        
        data = fetch_city_comprehensive_data(name, country)
        
        if data:
            if save_comprehensive_data(city_id, name, country, data):
                success += 1
            else:
                errors += 1
        else:
            errors += 1
    
    print(f"\n=== Complete ===")
    print(f"✓ Success: {success}")
    print(f"✗ Errors: {errors}")

if __name__ == "__main__":
    main()

