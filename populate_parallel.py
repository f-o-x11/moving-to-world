#!/usr/bin/env python3.11
"""
Parallel Comprehensive Data Population
Runs 4 workers simultaneously for 4x speed
"""

import sqlite3
import json
import requests
import os
import sys
from datetime import datetime
import time

FORGE_URL = os.getenv('BUILT_IN_FORGE_API_URL', 'https://api.manus.im')
FORGE_KEY = os.getenv('BUILT_IN_FORGE_API_KEY', '')
DB_PATH = 'moving_to.db'

def call_llm(prompt):
    """Call Manus LLM API"""
    try:
        response = requests.post(
            f'{FORGE_URL}/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {FORGE_KEY}',
                'Content-Type': 'application/json'
            },
            json={
                'messages': [
                    {'role': 'system', 'content': 'You are a helpful assistant that provides accurate city information in JSON format.'},
                    {'role': 'user', 'content': prompt}
                ],
                'model': 'gemini-2.5-flash',
                'max_tokens': 32768,
                'response_format': {'type': 'json_object'}
            },
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        content = result['choices'][0]['message']['content']
        
        if '```json' in content:
            content = content.split('```json')[1].split('```')[0].strip()
        elif '```' in content:
            content = content.split('```')[1].split('```')[0].strip()
            
        return json.loads(content)
    except Exception as e:
        return None

def generate_city_data(city):
    """Generate comprehensive data for a city"""
    prompt = f"""Generate comprehensive information for {city['name']}, {city['country']} (population: {city['population']:,}).

Return a JSON object with these fields:
{{
  "major_employers": ["Company 1", "Company 2", "Company 3", "Company 4", "Company 5"],
  "attractions": ["Attraction 1", "Attraction 2", "Attraction 3", "Attraction 4", "Attraction 5"],
  "restaurants": ["Restaurant 1", "Restaurant 2", "Restaurant 3", "Restaurant 4", "Restaurant 5"],
  "schools": ["School 1", "School 2", "School 3"],
  "hospitals": ["Hospital 1", "Hospital 2", "Hospital 3"],
  "transport_score": 75,
  "climate_desc": "Brief climate description"
}}

Provide real, accurate information. If the city is small, provide proportionally less data but keep the structure."""
    
    return call_llm(prompt)

def store_enriched_data(conn, city_id, data):
    """Store enriched data in database"""
    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO city_enriched_data 
            (city_id, major_employers, attractions, restaurants, schools, hospitals, 
             transport_score, climate_desc, raw_json, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            city_id,
            json.dumps(data.get('major_employers', [])),
            json.dumps(data.get('attractions', [])),
            json.dumps(data.get('restaurants', [])),
            json.dumps(data.get('schools', [])),
            json.dumps(data.get('hospitals', [])),
            data.get('transport_score', 50),
            data.get('climate_desc', ''),
            json.dumps(data),
            datetime.now().isoformat()
        ))
        conn.commit()
        return True
    except Exception as e:
        return False

def worker(worker_id, start_id, end_id):
    """Worker process for a range of city IDs"""
    print(f"[Worker {worker_id}] Starting: IDs {start_id} to {end_id}")
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get cities in this range without enriched data
    cursor.execute('''
        SELECT c.id, c.name, c.country, c.population
        FROM cities c
        LEFT JOIN city_enriched_data e ON c.id = e.city_id
        WHERE c.id >= ? AND c.id < ? AND e.id IS NULL
        ORDER BY c.population DESC
    ''', (start_id, end_id))
    
    cities = [dict(row) for row in cursor.fetchall()]
    total = len(cities)
    
    print(f"[Worker {worker_id}] Processing {total} cities")
    
    success = 0
    errors = 0
    
    for i, city in enumerate(cities, 1):
        try:
            data = generate_city_data(city)
            
            if data and store_enriched_data(conn, city['id'], data):
                success += 1
                if success % 10 == 0:
                    print(f"[Worker {worker_id}] Progress: {success}/{total} ({(success/total*100):.1f}%)")
            else:
                errors += 1
                
            time.sleep(0.1)  # Small delay to avoid overwhelming API
            
        except Exception as e:
            errors += 1
    
    conn.close()
    print(f"[Worker {worker_id}] Complete: {success} success, {errors} errors")
    return success, errors

def main():
    """Main parallel processing"""
    print("=" * 60)
    print("PARALLEL COMPREHENSIVE DATA POPULATION")
    print("=" * 60)
    
    # Get total cities needing enrichment
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT MIN(id), MAX(id) FROM cities')
    min_id, max_id = cursor.fetchone()
    
    cursor.execute('''
        SELECT COUNT(*) FROM cities c
        LEFT JOIN city_enriched_data e ON c.id = e.city_id
        WHERE e.id IS NULL
    ''')
    remaining = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"\nCities remaining: {remaining:,}")
    print(f"ID range: {min_id} to {max_id}")
    print(f"Workers: 4")
    print(f"Expected speedup: 4x")
    print(f"Estimated time: {(remaining * 3 / 4) / 3600:.1f} hours")
    print("\nStarting workers...\n")
    
    # Divide ID range into 4 parts
    range_size = (max_id - min_id + 1) // 4
    ranges = [
        (min_id, min_id + range_size),
        (min_id + range_size, min_id + 2 * range_size),
        (min_id + 2 * range_size, min_id + 3 * range_size),
        (min_id + 3 * range_size, max_id + 1)
    ]
    
    # Run workers sequentially (multiprocessing would be better but this works)
    import concurrent.futures
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = []
        for i, (start, end) in enumerate(ranges, 1):
            future = executor.submit(worker, i, start, end)
            futures.append(future)
        
        # Wait for all to complete
        results = [f.result() for f in concurrent.futures.as_completed(futures)]
    
    total_success = sum(r[0] for r in results)
    total_errors = sum(r[1] for r in results)
    
    print("\n" + "=" * 60)
    print("PARALLEL PROCESSING COMPLETE!")
    print("=" * 60)
    print(f"Total success: {total_success:,}")
    print(f"Total errors: {total_errors:,}")
    print(f"Success rate: {(total_success / max(1, total_success + total_errors) * 100):.1f}%")

if __name__ == '__main__':
    main()

