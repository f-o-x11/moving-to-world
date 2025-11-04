#!/usr/bin/env python3.11
"""
Comprehensive Data Population for All 32,496 Cities
Processes cities in batches with resume capability
"""

import sqlite3
import json
import time
import requests
import os
from datetime import datetime

# Manus LLM API configuration
FORGE_URL = os.getenv('BUILT_IN_FORGE_API_URL', 'https://api.manus.im')
FORGE_KEY = os.getenv('BUILT_IN_FORGE_API_KEY', '')

DB_PATH = 'moving_to.db'
BATCH_SIZE = 100
PROGRESS_FILE = 'population_progress.json'

def load_progress():
    """Load processing progress"""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    return {'last_city_id': 0, 'total_processed': 0, 'total_errors': 0}

def save_progress(progress):
    """Save processing progress"""
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f)

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
        
        # Extract JSON from markdown if needed
        if '```json' in content:
            content = content.split('```json')[1].split('```')[0].strip()
        elif '```' in content:
            content = content.split('```')[1].split('```')[0].strip()
            
        return json.loads(content)
    except Exception as e:
        print(f"LLM API Error: {e}")
        return None

def generate_city_data(city):
    """Generate comprehensive data for a city"""
    prompt = f"""
Generate comprehensive information for {city['name']}, {city['country']} (population: {city['population']:,}).

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

Provide real, accurate information. If the city is small, provide proportionally less data but keep the structure.
"""
    
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
        print(f"Database error: {e}")
        return False

def process_batch(conn, cities, progress):
    """Process a batch of cities"""
    success_count = 0
    error_count = 0
    
    for city in cities:
        try:
            print(f"Processing: {city['name']}, {city['country']} (ID: {city['id']}, Pop: {city['population']:,})")
            
            # Generate data
            data = generate_city_data(city)
            
            if data:
                # Store in database
                if store_enriched_data(conn, city['id'], data):
                    success_count += 1
                    print(f"  ✓ Success! ({success_count}/{len(cities)})")
                else:
                    error_count += 1
                    print(f"  ✗ Database error ({error_count} errors)")
            else:
                error_count += 1
                print(f"  ✗ LLM API error ({error_count} errors)")
            
            # Update progress
            progress['last_city_id'] = city['id']
            progress['total_processed'] += 1
            
            # Save progress every 10 cities
            if progress['total_processed'] % 10 == 0:
                save_progress(progress)
            
            # Rate limiting (avoid overwhelming API)
            time.sleep(0.5)
            
        except Exception as e:
            error_count += 1
            print(f"  ✗ Error processing {city['name']}: {e}")
            progress['total_errors'] += 1
    
    return success_count, error_count

def main():
    """Main processing function"""
    print("=" * 60)
    print("COMPREHENSIVE DATA POPULATION FOR ALL CITIES")
    print("=" * 60)
    
    # Load progress
    progress = load_progress()
    print(f"\nResuming from city ID: {progress['last_city_id']}")
    print(f"Already processed: {progress['total_processed']} cities")
    print(f"Total errors: {progress['total_errors']}")
    
    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get cities to process
    cursor.execute('''
        SELECT c.id, c.name, c.country, c.population
        FROM cities c
        LEFT JOIN city_enriched_data e ON c.id = e.city_id
        WHERE c.id > ? AND e.id IS NULL
        ORDER BY c.population DESC, c.id ASC
    ''', (progress['last_city_id'],))
    
    all_cities = [dict(row) for row in cursor.fetchall()]
    total_remaining = len(all_cities)
    
    print(f"\nCities remaining: {total_remaining:,}")
    print(f"Batch size: {BATCH_SIZE}")
    print(f"Estimated time: {(total_remaining * 3) / 3600:.1f} hours")
    print("\nStarting processing...\n")
    
    # Process in batches
    total_success = 0
    total_errors = 0
    batch_num = 0
    
    for i in range(0, len(all_cities), BATCH_SIZE):
        batch = all_cities[i:i+BATCH_SIZE]
        batch_num += 1
        
        print(f"\n{'=' * 60}")
        print(f"BATCH {batch_num}/{(len(all_cities) + BATCH_SIZE - 1) // BATCH_SIZE}")
        print(f"Cities {i+1} to {min(i+BATCH_SIZE, len(all_cities))} of {len(all_cities)}")
        print(f"{'=' * 60}\n")
        
        success, errors = process_batch(conn, batch, progress)
        total_success += success
        total_errors += errors
        
        # Save progress after each batch
        save_progress(progress)
        
        print(f"\nBatch {batch_num} complete:")
        print(f"  Success: {success}/{len(batch)}")
        print(f"  Errors: {errors}/{len(batch)}")
        print(f"  Total progress: {progress['total_processed']:,}/{32496} cities")
        print(f"  Success rate: {(total_success / max(1, total_success + total_errors) * 100):.1f}%")
        
        # Brief pause between batches
        if i + BATCH_SIZE < len(all_cities):
            print("\nPausing 5 seconds before next batch...")
            time.sleep(5)
    
    # Final summary
    print("\n" + "=" * 60)
    print("PROCESSING COMPLETE!")
    print("=" * 60)
    print(f"Total processed: {progress['total_processed']:,} cities")
    print(f"Successful: {total_success:,}")
    print(f"Errors: {total_errors:,}")
    print(f"Success rate: {(total_success / max(1, total_success + total_errors) * 100):.1f}%")
    
    # Check final database state
    cursor.execute('SELECT COUNT(*) FROM city_enriched_data')
    total_enriched = cursor.fetchone()[0]
    print(f"\nTotal cities with enriched data: {total_enriched:,}/32,496")
    print(f"Coverage: {(total_enriched / 32496 * 100):.1f}%")
    
    conn.close()
    print("\nDone!")

if __name__ == '__main__':
    main()

