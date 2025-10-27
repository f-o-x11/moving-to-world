"""
V4 Enhanced Page Generator
Uses enriched data to create comprehensive city pages with AI chat
"""

import sqlite3
import json
import os
from pathlib import Path

DB_PATH = "/home/ubuntu/moving_to_world/moving_to.db"
TEMPLATE_PATH = "/home/ubuntu/moving_to_world/city-template-v4.html"
OUTPUT_BASE = "/home/ubuntu/moving_to_world"

def get_city_data(city_id):
    """Get all data for a city"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get basic city info
    cursor.execute("""
        SELECT name, country, state_region, population, latitude, longitude,
               timezone, language, currency, climate, walk_score, avg_rent_usd,
               cost_of_living_index
        FROM cities WHERE id = ?
    """, (city_id,))
    
    city = cursor.fetchone()
    if not city:
        return None
    
    # Get enriched data if available
    cursor.execute("""
        SELECT data FROM city_enriched_data WHERE city_id = ?
    """, (city_id,))
    
    enriched_row = cursor.fetchone()
    enriched = json.loads(enriched_row[0]) if enriched_row else {}
    
    conn.close()
    
    return {
        'id': city_id,
        'name': city[0],
        'country': city[1],
        'state_region': city[2],
        'population': city[3],
        'latitude': city[4],
        'longitude': city[5],
        'timezone': city[6],
        'language': city[7],
        'currency': city[8],
        'climate': city[9],
        'walk_score': city[10],
        'avg_rent_usd': city[11],
        'cost_of_living_index': city[12],
        'enriched': enriched
    }

def format_number(num):
    """Format number with commas"""
    if num is None:
        return "N/A"
    try:
        return f"{int(num):,}"
    except:
        return str(num)

def format_currency(amount, currency="$"):
    """Format currency"""
    if amount is None:
        return "N/A"
    try:
        return f"{currency}{int(amount):,}"
    except:
        return f"{currency}{amount}"

def generate_page(city_data):
    """Generate HTML page for a city"""
    
    # Read template
    with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
        template = f.read()
    
    # Extract enriched data
    enriched = city_data.get('enriched', {})
    
    # Basic replacements
    replacements = {
        '{{CITY_NAME}}': city_data['name'],
        '{{COUNTRY}}': city_data['country'],
        '{{STATE_REGION}}': city_data['state_region'] or city_data['country'],
        '{{POPULATION}}': format_number(city_data['population']),
        '{{POPULATION_FORMATTED}}': format_number(city_data['population']),
        '{{TIMEZONE}}': city_data['timezone'] or 'UTC',
        '{{TIMEZONE_NAME}}': city_data['timezone'] or 'UTC',
        '{{LANGUAGE}}': city_data['language'] or 'Local language',
        '{{CURRENCY}}': city_data['currency'] or '$',
        '{{CURRENCY_SYMBOL}}': city_data['currency'] or '$',
        '{{CLIMATE}}': city_data['climate'] or 'Temperate',
        '{{WALK_SCORE}}': str(city_data['walk_score'] or 50),
        '{{AVG_RENT}}': format_currency(city_data['avg_rent_usd'], city_data['currency'] or '$'),
        '{{COST_OF_LIVING_INDEX}}': str(city_data['cost_of_living_index'] or 100),
    }
    
    # Enriched data replacements
    if enriched:
        # Rent prices
        rent = enriched.get('rent', {})
        replacements['{{RENT_STUDIO}}'] = format_currency(rent.get('studio'), city_data['currency'])
        replacements['{{RENT_1BR}}'] = format_currency(rent.get('1br'), city_data['currency'])
        replacements['{{RENT_2BR}}'] = format_currency(rent.get('2br'), city_data['currency'])
        replacements['{{RENT_3BR}}'] = format_currency(rent.get('3br'), city_data['currency'])
        
        # Employers
        employers = enriched.get('employers', [])
        if employers:
            employers_html = '<ul class="list-disc pl-5">'
            for emp in employers[:10]:
                employers_html += f'<li>{emp}</li>'
            employers_html += '</ul>'
            replacements['{{MAJOR_EMPLOYERS_HTML}}'] = employers_html
        else:
            replacements['{{MAJOR_EMPLOYERS_HTML}}'] = '<p>Information not available</p>'
        
        # Attractions
        attractions = enriched.get('attractions', [])
        if attractions:
            attr_html = '<ul class="list-disc pl-5">'
            for attr in attractions[:10]:
                attr_html += f'<li>{attr}</li>'
            attr_html += '</ul>'
            replacements['{{ATTRACTIONS_HTML}}'] = attr_html
        else:
            replacements['{{ATTRACTIONS_HTML}}'] = '<p>Information not available</p>'
        
        # Restaurants
        restaurants = enriched.get('restaurants', [])
        if restaurants:
            rest_html = '<ul class="list-disc pl-5">'
            for rest in restaurants[:10]:
                rest_html += f'<li>{rest}</li>'
            rest_html += '</ul>'
            replacements['{{RESTAURANTS_HTML}}'] = rest_html
        else:
            replacements['{{RESTAURANTS_HTML}}'] = '<p>Information not available</p>'
        
        # Transport score
        transport_score = enriched.get('transport_score', city_data['walk_score'])
        replacements['{{TRANSPORT_SCORE}}'] = str(transport_score or 50)
    
    # Apply replacements
    html = template
    for key, value in replacements.items():
        html = html.replace(key, str(value))
    
    # Remove any remaining template variables
    import re
    html = re.sub(r'\{\{[A-Z_]+\}\}', 'N/A', html)
    
    return html

def main():
    print("V4 Enhanced Page Generator")
    print("=" * 50)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get all cities
    cursor.execute("SELECT id FROM cities ORDER BY population DESC")
    city_ids = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    print(f"Generating pages for {len(city_ids)} cities...")
    
    success = 0
    errors = 0
    
    for idx, city_id in enumerate(city_ids, 1):
        try:
            city_data = get_city_data(city_id)
            if not city_data:
                errors += 1
                continue
            
            html = generate_page(city_data)
            
            # Create output path
            country = city_data['country'].lower().replace(' ', '-')
            state = (city_data['state_region'] or city_data['country']).lower().replace(' ', '-')
            city = city_data['name'].lower().replace(' ', '-')
            
            output_dir = Path(OUTPUT_BASE) / country / state / city
            output_dir.mkdir(parents=True, exist_ok=True)
            
            output_file = output_dir / "index.html"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html)
            
            success += 1
            
            if idx % 1000 == 0:
                print(f"Progress: {idx}/{len(city_ids)} ({success} success, {errors} errors)")
        
        except Exception as e:
            print(f"Error generating page for city {city_id}: {e}")
            errors += 1
    
    print("\n" + "=" * 50)
    print(f"Generation Complete!")
    print(f"✓ Success: {success}")
    print(f"✗ Errors: {errors}")
    print(f"Success rate: {success/len(city_ids)*100:.1f}%")

if __name__ == "__main__":
    main()

