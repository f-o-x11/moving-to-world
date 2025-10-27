import sqlite3
import json
from pathlib import Path
from generate_v3 import generate_city_page, load_neighborhoods, load_rental_platforms

# Load data
neighborhoods_data = load_neighborhoods()
rental_platforms = load_rental_platforms()

# Load template
with open('city-template-v3.html', 'r') as f:
    template = f.read()

# Connect to database
conn = sqlite3.connect('moving_to.db')
cursor = conn.cursor()

# Get all cities with enriched data
cursor.execute("""
    SELECT c.id, c.name, c.country, c.state_region, c.population, 
           c.latitude, c.longitude, c.timezone,
           w.climate_zone,
           e.raw_json
    FROM cities c
    JOIN city_enriched_data e ON c.id = e.city_id
    LEFT JOIN weather_data w ON c.id = w.city_id AND w.month = 1
    ORDER BY c.name
""")

cities = cursor.fetchall()
conn.close()

print(f"Regenerating {len(cities)} cities with enriched data...")

success = 0
errors = 0

for row in cities:
    try:
        city_data = row[:9]
        enriched_json = row[9]
        enriched_data = json.loads(enriched_json) if enriched_json else None
        
        city_id, name, country, region = city_data[0], city_data[1], city_data[2], city_data[3]
        
        # Create directory structure
        country_slug = country.lower().replace(' ', '-')
        region_slug = (region or country).lower().replace(' ', '-')
        city_slug = name.lower().replace(' ', '-')
        
        city_dir = Path(f"/home/ubuntu/moving_to_world/{country_slug}/{region_slug}/{city_slug}")
        city_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate HTML
        html = generate_city_page(city_data, template, neighborhoods_data, rental_platforms, enriched_data)
        
        # Write file
        with open(city_dir / 'index.html', 'w', encoding='utf-8') as f:
            f.write(html)
        
        success += 1
        print(f"✓ {name}, {country}")
        
    except Exception as e:
        errors += 1
        print(f"✗ Error generating {name}: {e}")

print(f"\n=== Regeneration Complete ===")
print(f"✓ Success: {success}")
print(f"✗ Errors: {errors}")
