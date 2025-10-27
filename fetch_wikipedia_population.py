#!/usr/bin/env python3
"""
Fetch accurate population data from Wikipedia for all cities
Uses Wikipedia API and DBpedia SPARQL endpoint
"""

import json
import requests
import time
from urllib.parse import quote
import sqlite3

def get_wikipedia_population(city_name, country_name):
    """Fetch population from Wikipedia API"""
    try:
        # Try Wikipedia API first
        search_term = f"{city_name}, {country_name}"
        wiki_url = "https://en.wikipedia.org/w/api.php"
        
        # Search for the article
        search_params = {
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": search_term,
            "srlimit": 1
        }
        
        response = requests.get(wiki_url, params=search_params, timeout=10)
        data = response.json()
        
        if not data.get('query', {}).get('search'):
            return None
            
        page_title = data['query']['search'][0]['title']
        
        # Get page content
        content_params = {
            "action": "query",
            "format": "json",
            "prop": "revisions",
            "titles": page_title,
            "rvprop": "content",
            "rvslots": "main"
        }
        
        response = requests.get(wiki_url, params=content_params, timeout=10)
        data = response.json()
        
        pages = data.get('query', {}).get('pages', {})
        if not pages:
            return None
            
        page = list(pages.values())[0]
        if 'revisions' not in page:
            return None
            
        content = page['revisions'][0]['slots']['main']['*']
        
        # Parse infobox for population
        import re
        
        # Look for population patterns
        patterns = [
            r'\|population_total\s*=\s*([0-9,]+)',
            r'\|population\s*=\s*([0-9,]+)',
            r'\|pop\s*=\s*([0-9,]+)',
            r'population.*?([0-9,]{4,})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                pop_str = match.group(1).replace(',', '').replace(' ', '')
                try:
                    population = int(pop_str)
                    if 1000 < population < 100000000:  # Sanity check
                        return population
                except:
                    continue
                    
        return None
        
    except Exception as e:
        print(f"Error fetching {city_name}, {country_name}: {e}")
        return None

def get_dbpedia_population(city_name, country_name):
    """Fetch population from DBpedia SPARQL endpoint"""
    try:
        sparql_url = "https://dbpedia.org/sparql"
        
        query = f"""
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX dbr: <http://dbpedia.org/resource/>
        PREFIX rdfs: <http://rdfs.org/label/>
        
        SELECT ?pop WHERE {{
          ?city rdfs:label "{city_name}"@en .
          ?city dbo:country ?country .
          ?country rdfs:label "{country_name}"@en .
          ?city dbo:populationTotal ?pop .
        }}
        LIMIT 1
        """
        
        response = requests.get(
            sparql_url,
            params={"query": query, "format": "json"},
            timeout=10
        )
        
        data = response.json()
        results = data.get('results', {}).get('bindings', [])
        
        if results:
            pop = int(results[0]['pop']['value'])
            if 1000 < pop < 100000000:
                return pop
                
        return None
        
    except Exception as e:
        return None

def update_city_populations():
    """Update population data for all cities in database"""
    
    db_path = '/home/ubuntu/moving_to_world/moving_to.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all cities
    cursor.execute("SELECT id, name, country FROM cities LIMIT 1000")  # Start with first 1000
    cities = cursor.fetchall()
    
    print(f"Updating population for {len(cities)} cities...")
    
    updated = 0
    failed = 0
    
    for city_id, city_name, country in cities:
        # Try Wikipedia first
        population = get_wikipedia_population(city_name, country)
        
        # If Wikipedia fails, try DBpedia
        if not population:
            population = get_dbpedia_population(city_name, country)
        
        if population:
            cursor.execute(
                "UPDATE cities SET population = ? WHERE id = ?",
                (population, city_id)
            )
            updated += 1
            print(f"✓ {city_name}, {country}: {population:,}")
        else:
            failed += 1
            print(f"✗ {city_name}, {country}: No data found")
        
        # Rate limiting
        time.sleep(0.5)
        
        # Commit every 100 cities
        if (updated + failed) % 100 == 0:
            conn.commit()
            print(f"\nProgress: {updated} updated, {failed} failed\n")
    
    conn.commit()
    conn.close()
    
    print(f"\n=== Final Results ===")
    print(f"Updated: {updated}")
    print(f"Failed: {failed}")
    print(f"Success rate: {updated/(updated+failed)*100:.1f}%")

if __name__ == "__main__":
    update_city_populations()

