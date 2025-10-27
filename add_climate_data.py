#!/usr/bin/env python3
"""
Calculate climate data from latitude
Provides reasonable temperature ranges without needing weather APIs
"""

import sqlite3
import math

def get_climate_zone(latitude):
    """Determine climate zone from latitude"""
    abs_lat = abs(latitude)
    
    if abs_lat < 23.5:
        return "Tropical"
    elif abs_lat < 35:
        return "Subtropical"
    elif abs_lat < 50:
        return "Temperate"
    elif abs_lat < 66.5:
        return "Cold"
    else:
        return "Polar"

def estimate_temperatures(latitude, longitude):
    """
    Estimate temperature ranges based on latitude
    Returns (winter_low, winter_high, summer_low, summer_high) in Celsius
    """
    abs_lat = abs(latitude)
    
    # Base temperatures by climate zone
    if abs_lat < 23.5:  # Tropical
        winter_low, winter_high = 22, 32
        summer_low, summer_high = 24, 34
    elif abs_lat < 35:  # Subtropical
        winter_low, winter_high = 8, 18
        summer_low, summer_high = 22, 32
    elif abs_lat < 50:  # Temperate
        winter_low, winter_high = -2, 8
        summer_low, summer_high = 15, 25
    elif abs_lat < 66.5:  # Cold
        winter_low, winter_high = -15, -5
        summer_low, summer_high = 10, 20
    else:  # Polar
        winter_low, winter_high = -30, -15
        summer_low, summer_high = -5, 5
    
    # Adjust for coastal vs inland (rough approximation)
    # Coastal cities have smaller temperature ranges
    # This is a simplification - real data would be better
    
    # Adjust for elevation (not available in our data, so skip)
    
    return winter_low, winter_high, summer_low, summer_high

def add_climate_data():
    """Add climate data to all cities with coordinates"""
    
    conn = sqlite3.connect('/home/ubuntu/moving_to_world/moving_to.db')
    cursor = conn.cursor()
    
    # Get cities with coordinates
    cursor.execute("""
        SELECT id, name, country, latitude, longitude
        FROM cities
        WHERE latitude != 0 AND longitude != 0
    """)
    cities = cursor.fetchall()
    
    print(f"Adding climate data for {len(cities)} cities...")
    
    for city_id, name, country, lat, lon in cities:
        climate_zone = get_climate_zone(lat)
        winter_low, winter_high, summer_low, summer_high = estimate_temperatures(lat, lon)
        
        # Insert into weather_data table
        cursor.execute("""
            INSERT OR REPLACE INTO weather_data 
            (city_id, month, temp_min_c, temp_max_c, climate_zone)
            VALUES 
            (?, 1, ?, ?, ?),
            (?, 7, ?, ?, ?)
        """, (
            city_id, winter_low, winter_high, climate_zone,
            city_id, summer_low, summer_high, climate_zone
        ))
    
    conn.commit()
    conn.close()
    
    print(f"✓ Climate data added for {len(cities)} cities")

if __name__ == "__main__":
    add_climate_data()

