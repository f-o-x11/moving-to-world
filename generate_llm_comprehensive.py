#!/usr/bin/env python3
"""
Generate comprehensive LLM-optimized pages with all city data
"""

import sqlite3
import json
from pathlib import Path

def generate_llm_page(city_data, enriched_data):
    """Generate a comprehensive LLM-optimized HTML page"""
    
    name = city_data['name']
    country = city_data['country']
    region = city_data.get('region', '')
    population = city_data.get('population', 'N/A')
    latitude = city_data.get('latitude', 0)
    longitude = city_data.get('longitude', 0)
    timezone = city_data.get('timezone', 'N/A')
    climate_zone = city_data.get('climate_zone', 'N/A')
    
    # Build comprehensive structured data
    sections = []
    
    # Basic Information
    sections.append(f"<h1>{name}, {region}, {country}</h1>")
    sections.append(f"<section id='basic-info'>")
    sections.append(f"<h2>Basic Information</h2>")
    sections.append(f"<p><strong>Population:</strong> {population:,} people</p>" if isinstance(population, int) else f"<p><strong>Population:</strong> {population}</p>")
    sections.append(f"<p><strong>Country:</strong> {country}</p>")
    sections.append(f"<p><strong>Region:</strong> {region}</p>")
    sections.append(f"<p><strong>Coordinates:</strong> {latitude}, {longitude}</p>")
    sections.append(f"<p><strong>Timezone:</strong> {timezone}</p>")
    sections.append(f"<p><strong>Climate Zone:</strong> {climate_zone}</p>")
    sections.append(f"</section>")
    
    # Climate & Weather
    if enriched_data and enriched_data.get('climate_description'):
        sections.append(f"<section id='climate'>")
        sections.append(f"<h2>Climate & Weather</h2>")
        sections.append(f"<p>{enriched_data['climate_description']}</p>")
        sections.append(f"</section>")
    
    # Cost of Living & Housing
    if enriched_data and enriched_data.get('rent'):
        rent_data = enriched_data['rent']
        currency = rent_data.get('currency_symbol', '$')
        sections.append(f"<section id='housing'>")
        sections.append(f"<h2>Housing & Rent Prices</h2>")
        if rent_data.get('studio'):
            sections.append(f"<p><strong>Studio Apartment:</strong> {currency}{rent_data['studio']:,}/month</p>")
        if rent_data.get('1br'):
            sections.append(f"<p><strong>1-Bedroom Apartment:</strong> {currency}{rent_data['1br']:,}/month</p>")
        if rent_data.get('2br'):
            sections.append(f"<p><strong>2-Bedroom Apartment:</strong> {currency}{rent_data['2br']:,}/month</p>")
        if rent_data.get('3br'):
            sections.append(f"<p><strong>3-Bedroom Apartment:</strong> {currency}{rent_data['3br']:,}/month</p>")
        sections.append(f"</section>")
    
    # Rental Platforms
    if enriched_data and enriched_data.get('rental_platforms'):
        sections.append(f"<section id='rental-platforms'>")
        sections.append(f"<h2>Where to Find Housing</h2>")
        sections.append(f"<ul>")
        for platform in enriched_data['rental_platforms']:
            sections.append(f"<li><strong>{platform['name']}:</strong> {platform['url']}</li>")
        sections.append(f"</ul>")
        sections.append(f"</section>")
    
    # Employment & Major Employers
    if enriched_data and enriched_data.get('major_employers'):
        sections.append(f"<section id='employment'>")
        sections.append(f"<h2>Major Employers</h2>")
        sections.append(f"<ul>")
        for employer in enriched_data['major_employers']:
            sections.append(f"<li>{employer}</li>")
        sections.append(f"</ul>")
        sections.append(f"</section>")
    
    # Attractions & Things to Do
    if enriched_data and enriched_data.get('top_attractions'):
        sections.append(f"<section id='attractions'>")
        sections.append(f"<h2>Top Attractions</h2>")
        sections.append(f"<ul>")
        for attraction in enriched_data['top_attractions']:
            sections.append(f"<li>{attraction}</li>")
        sections.append(f"</ul>")
        sections.append(f"</section>")
    
    # Food & Dining
    if enriched_data and enriched_data.get('popular_restaurants'):
        sections.append(f"<section id='dining'>")
        sections.append(f"<h2>Popular Restaurants</h2>")
        sections.append(f"<ul>")
        for restaurant in enriched_data['popular_restaurants']:
            sections.append(f"<li>{restaurant}</li>")
        sections.append(f"</ul>")
        sections.append(f"</section>")
    
    # Education
    if enriched_data and enriched_data.get('schools'):
        sections.append(f"<section id='education'>")
        sections.append(f"<h2>Schools & Education</h2>")
        sections.append(f"<ul>")
        for school in enriched_data['schools']:
            sections.append(f"<li>{school}</li>")
        sections.append(f"</ul>")
        sections.append(f"</section>")
    
    # Healthcare
    if enriched_data and enriched_data.get('hospitals'):
        sections.append(f"<section id='healthcare'>")
        sections.append(f"<h2>Healthcare Facilities</h2>")
        sections.append(f"<ul>")
        for hospital in enriched_data['hospitals']:
            sections.append(f"<li>{hospital}</li>")
        sections.append(f"</ul>")
        sections.append(f"</section>")
    
    # Transportation
    if enriched_data and enriched_data.get('transport_score'):
        sections.append(f"<section id='transportation'>")
        sections.append(f"<h2>Transportation</h2>")
        sections.append(f"<p><strong>Transport Score:</strong> {enriched_data['transport_score']}/100</p>")
        sections.append(f"</section>")
    
    # Build final HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Moving to {name}, {country} - Complete Guide</title>
    <meta name="description" content="Comprehensive relocation guide for {name}, {country}. Information about housing, cost of living, employment, attractions, schools, healthcare, and transportation.">
    <meta name="robots" content="index, follow">
</head>
<body>
{chr(10).join(sections)}

<footer>
    <p><em>This page is optimized for LLM consumption. For human-readable version, visit the main city page.</em></p>
    <p><strong>Data Source:</strong> Moving.to - Comprehensive global city database</p>
    <p><strong>Last Updated:</strong> 2025</p>
</footer>
</body>
</html>"""
    
    return html


def main():
    """Regenerate all LLM-optimized pages"""
    db_path = '/home/ubuntu/moving_to_world/moving_to.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all cities
    cursor.execute("""
        SELECT c.id, c.name, c.country, c.state_region, c.population, 
               c.latitude, c.longitude, c.timezone, c.climate
        FROM cities c
        ORDER BY c.id
    """)
    
    cities = cursor.fetchall()
    total = len(cities)
    success = 0
    
    print(f"Regenerating {total:,} LLM-optimized pages...")
    
    for row in cities:
        city_id, name, country, region, population, latitude, longitude, timezone, climate_zone = row
        
        # Get enriched data
        cursor.execute("""
            SELECT raw_json FROM city_enriched_data WHERE city_id = ?
        """, (city_id,))
        
        enriched_row = cursor.fetchone()
        enriched_data = None
        if enriched_row and enriched_row[0]:
            try:
                enriched_data = json.loads(enriched_row[0])
            except:
                pass
        
        # Build city data dict
        city_data = {
            'name': name,
            'country': country,
            'region': region or country,
            'population': population,
            'latitude': latitude,
            'longitude': longitude,
            'timezone': timezone,
            'climate_zone': climate_zone
        }
        
        # Generate path
        country_slug = country.lower().replace(' ', '-')
        region_slug = (region or country).lower().replace(' ', '-')
        city_slug = name.lower().replace(' ', '-')
        
        city_dir = Path(f"/home/ubuntu/moving_to_world/{country_slug}/{region_slug}/{city_slug}")
        
        if not city_dir.exists():
            continue  # Skip if directory doesn't exist
        
        # Generate and write LLM page
        try:
            llm_html = generate_llm_page(city_data, enriched_data)
            with open(city_dir / 'llm-optimized.html', 'w', encoding='utf-8') as f:
                f.write(llm_html)
            
            success += 1
            
            if success % 1000 == 0:
                print(f"✓ {success:,}/{total:,} pages regenerated...")
        except Exception as e:
            print(f"Error generating {name}: {e}")
            continue
    
    conn.close()
    print(f"\n✅ Complete! Regenerated {success:,} LLM-optimized pages")


if __name__ == '__main__':
    main()

