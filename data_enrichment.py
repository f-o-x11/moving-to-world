"""
Data Enrichment Module
Provides real timezone, language, currency, and other data for cities
"""

import pytz
from timezonefinder import TimezoneFinder
from datetime import datetime
import pycountry

# Initialize timezone finder
tf = TimezoneFinder()

# Country to currency mapping
COUNTRY_CURRENCIES = {
    'United States': 'USD ($)',
    'United Kingdom': 'GBP (£)',
    'Canada': 'CAD ($)',
    'Australia': 'AUD ($)',
    'New Zealand': 'NZD ($)',
    'Japan': 'JPY (¥)',
    'China': 'CNY (¥)',
    'South Korea': 'KRW (₩)',
    'India': 'INR (₹)',
    'Singapore': 'SGD ($)',
    'Hong Kong': 'HKD ($)',
    'Thailand': 'THB (฿)',
    'Malaysia': 'MYR (RM)',
    'Indonesia': 'IDR (Rp)',
    'Philippines': 'PHP (₱)',
    'Vietnam': 'VND (₫)',
    'Israel': 'ILS (₪)',
    'United Arab Emirates': 'AED (د.إ)',
    'Saudi Arabia': 'SAR (﷼)',
    'Turkey': 'TRY (₺)',
    'South Africa': 'ZAR (R)',
    'Egypt': 'EGP (£)',
    'Nigeria': 'NGN (₦)',
    'Kenya': 'KES (KSh)',
    'Brazil': 'BRL (R$)',
    'Mexico': 'MXN ($)',
    'Argentina': 'ARS ($)',
    'Chile': 'CLP ($)',
    'Colombia': 'COP ($)',
    'Peru': 'PEN (S/)',
    'France': 'EUR (€)',
    'Germany': 'EUR (€)',
    'Italy': 'EUR (€)',
    'Spain': 'EUR (€)',
    'Netherlands': 'EUR (€)',
    'Belgium': 'EUR (€)',
    'Austria': 'EUR (€)',
    'Switzerland': 'CHF (Fr)',
    'Sweden': 'SEK (kr)',
    'Norway': 'NOK (kr)',
    'Denmark': 'DKK (kr)',
    'Poland': 'PLN (zł)',
    'Czech Republic': 'CZK (Kč)',
    'Hungary': 'HUF (Ft)',
    'Romania': 'RON (lei)',
    'Greece': 'EUR (€)',
    'Portugal': 'EUR (€)',
    'Ireland': 'EUR (€)',
    'Finland': 'EUR (€)',
    'Russia': 'RUB (₽)',
    'Ukraine': 'UAH (₴)',
}

# Country to primary language mapping
COUNTRY_LANGUAGES = {
    'United States': 'English',
    'United Kingdom': 'English',
    'Canada': 'English, French',
    'Australia': 'English',
    'New Zealand': 'English',
    'Ireland': 'English',
    'Japan': 'Japanese',
    'China': 'Mandarin Chinese',
    'South Korea': 'Korean',
    'India': 'Hindi, English',
    'Singapore': 'English, Mandarin, Malay, Tamil',
    'Hong Kong': 'Cantonese, English',
    'Thailand': 'Thai',
    'Malaysia': 'Malay',
    'Indonesia': 'Indonesian',
    'Philippines': 'Filipino, English',
    'Vietnam': 'Vietnamese',
    'Israel': 'Hebrew, Arabic',
    'United Arab Emirates': 'Arabic',
    'Saudi Arabia': 'Arabic',
    'Turkey': 'Turkish',
    'South Africa': 'Afrikaans, English, Zulu',
    'Egypt': 'Arabic',
    'Nigeria': 'English',
    'Kenya': 'Swahili, English',
    'Brazil': 'Portuguese',
    'Mexico': 'Spanish',
    'Argentina': 'Spanish',
    'Chile': 'Spanish',
    'Colombia': 'Spanish',
    'Peru': 'Spanish',
    'France': 'French',
    'Germany': 'German',
    'Italy': 'Italian',
    'Spain': 'Spanish',
    'Netherlands': 'Dutch',
    'Belgium': 'Dutch, French',
    'Austria': 'German',
    'Switzerland': 'German, French, Italian',
    'Sweden': 'Swedish',
    'Norway': 'Norwegian',
    'Denmark': 'Danish',
    'Poland': 'Polish',
    'Czech Republic': 'Czech',
    'Hungary': 'Hungarian',
    'Romania': 'Romanian',
    'Greece': 'Greek',
    'Portugal': 'Portuguese',
    'Finland': 'Finnish',
    'Russia': 'Russian',
    'Ukraine': 'Ukrainian',
}

def get_timezone_info(latitude: float, longitude: float) -> dict:
    """Get timezone information for a location"""
    try:
        tz_name = tf.timezone_at(lat=latitude, lng=longitude)
        if not tz_name:
            return {
                'timezone': 'UTC',
                'utc_offset': '+00:00',
                'current_time': datetime.utcnow().strftime('%I:%M %p')
            }
        
        tz = pytz.timezone(tz_name)
        now = datetime.now(tz)
        
        return {
            'timezone': tz_name,
            'utc_offset': now.strftime('%z'),
            'current_time': now.strftime('%I:%M %p')
        }
    except Exception as e:
        return {
            'timezone': 'UTC',
            'utc_offset': '+00:00',
            'current_time': datetime.utcnow().strftime('%I:%M %p')
        }

def get_currency(country: str) -> str:
    """Get currency for a country"""
    # Try direct mapping first
    if country in COUNTRY_CURRENCIES:
        return COUNTRY_CURRENCIES[country]
    
    # Try pycountry lookup
    try:
        country_obj = pycountry.countries.search_fuzzy(country)[0]
        currency_code = pycountry.currencies.get(alpha_3=country_obj.alpha_3)
        if currency_code:
            return f"{currency_code.alpha_3}"
    except:
        pass
    
    # Fallback to common currencies by region
    if any(x in country.lower() for x in ['euro', 'eu']):
        return 'EUR (€)'
    
    return 'Local Currency'

def get_language(country: str) -> str:
    """Get primary language(s) for a country"""
    if country in COUNTRY_LANGUAGES:
        return COUNTRY_LANGUAGES[country]
    
    # Fallback to English for English-speaking countries
    if any(x in country.lower() for x in ['united', 'kingdom', 'states', 'australia', 'canada']):
        return 'English'
    
    return 'Local Language'

def get_climate_description(latitude: float) -> str:
    """Get climate description based on latitude"""
    abs_lat = abs(latitude)
    
    if abs_lat < 15:
        return 'Tropical'
    elif abs_lat < 30:
        return 'Subtropical'
    elif abs_lat < 45:
        return 'Temperate'
    elif abs_lat < 60:
        return 'Cool Temperate'
    else:
        return 'Cold'

def generate_sample_rentals(city_name: str, avg_rent: float, country: str) -> list:
    """Generate sample rental listings based on city data"""
    currency_symbol = '$'
    if country in COUNTRY_CURRENCIES:
        curr = COUNTRY_CURRENCIES[country]
        if '€' in curr:
            currency_symbol = '€'
        elif '£' in curr:
            currency_symbol = '£'
        elif '¥' in curr:
            currency_symbol = '¥'
    
    base_rent = avg_rent if avg_rent > 0 else 1500
    
    rentals = [
        {
            'title': f'Modern 1BR Apartment in {city_name} City Center',
            'price': f'{currency_symbol}{int(base_rent * 0.9)}/mo',
            'beds': 1,
            'baths': 1,
            'sqm': 55,
            'description': 'Newly renovated apartment with modern amenities, close to public transport.',
            'rating': 4.8,
            'link': f'https://www.airbnb.com/s/{city_name.replace(" ", "-")}/homes'
        },
        {
            'title': f'Spacious 2BR with City Views',
            'price': f'{currency_symbol}{int(base_rent * 1.3)}/mo',
            'beds': 2,
            'baths': 1,
            'sqm': 75,
            'description': 'Bright apartment with stunning views, perfect for professionals or small families.',
            'rating': 4.6,
            'link': f'https://www.airbnb.com/s/{city_name.replace(" ", "-")}/homes'
        },
        {
            'title': f'Cozy Studio in Quiet Neighborhood',
            'price': f'{currency_symbol}{int(base_rent * 0.7)}/mo',
            'beds': 0,
            'baths': 1,
            'sqm': 35,
            'description': 'Perfect for singles or students, walking distance to amenities.',
            'rating': 4.5,
            'link': f'https://www.airbnb.com/s/{city_name.replace(" ", "-")}/homes'
        },
        {
            'title': f'Luxury 3BR Penthouse',
            'price': f'{currency_symbol}{int(base_rent * 2.0)}/mo',
            'beds': 3,
            'baths': 2,
            'sqm': 120,
            'description': 'High-end finishes, rooftop terrace, concierge service included.',
            'rating': 4.9,
            'link': f'https://www.airbnb.com/s/{city_name.replace(" ", "-")}/homes'
        },
    ]
    
    return rentals

def generate_sample_jobs(city_name: str, country: str) -> list:
    """Generate sample job listings"""
    jobs = [
        {
            'title': 'Software Engineer',
            'company': f'{city_name} Tech Solutions',
            'salary': '$80,000 - $120,000/year',
            'type': 'Full-time',
            'description': 'Join our growing team building innovative software solutions.',
            'link': f'https://www.indeed.com/jobs?q=software+engineer&l={city_name.replace(" ", "+")}%2C+{country.replace(" ", "+")}'
        },
        {
            'title': 'Marketing Manager',
            'company': 'Global Marketing Group',
            'salary': '$65,000 - $95,000/year',
            'type': 'Full-time',
            'description': 'Lead marketing campaigns for international brands.',
            'link': f'https://www.indeed.com/jobs?q=marketing+manager&l={city_name.replace(" ", "+")}%2C+{country.replace(" ", "+")}'
        },
        {
            'title': 'Registered Nurse',
            'company': f'{city_name} General Hospital',
            'salary': '$55,000 - $85,000/year',
            'type': 'Full-time',
            'description': 'Provide compassionate care in a state-of-the-art facility.',
            'link': f'https://www.indeed.com/jobs?q=registered+nurse&l={city_name.replace(" ", "+")}%2C+{country.replace(" ", "+")}'
        },
        {
            'title': 'Financial Analyst',
            'company': 'Premier Financial Services',
            'salary': '$70,000 - $100,000/year',
            'type': 'Full-time',
            'description': 'Analyze financial data and provide strategic recommendations.',
            'link': f'https://www.indeed.com/jobs?q=financial+analyst&l={city_name.replace(" ", "+")}%2C+{country.replace(" ", "+")}'
        },
    ]
    
    return jobs

def generate_sample_rentals(city_name: str, base_rent: float, country: str) -> list:
    """Generate sample rental listings"""
    from data_enrichment import COUNTRY_CURRENCIES
    
    currency_symbol = '$'
    if country in COUNTRY_CURRENCIES:
        curr = COUNTRY_CURRENCIES[country]
        if '€' in curr:
            currency_symbol = '€'
        elif '£' in curr:
            currency_symbol = '£'
        elif '¥' in curr:
            currency_symbol = '¥'
        elif '₪' in curr:
            currency_symbol = '₪'
    
    rentals = []
    for i in range(10):
        beds = 1 + (i % 3)
        baths = 1 + (i % 2)
        sqm = 50 + (i * 15)
        price_mult = 0.8 + (i * 0.05)
        price = int(base_rent * price_mult)
        rating = 4.2 + (i % 8) * 0.1
        
        rentals.append({
            'title': f'{beds}-Bedroom Apartment in {city_name}',
            'beds': beds,
            'baths': baths,
            'sqm': sqm,
            'price': f'{currency_symbol}{price}/mo',
            'description': f'Modern {beds}-bedroom apartment with great amenities and location.',
            'rating': f'{rating:.1f}',
            'link': f'https://www.airbnb.com/s/{city_name.replace(" ", "-")}/homes'
        })
    
    return rentals

def generate_sample_jobs(city_name: str) -> list:
    """Generate sample job listings"""
    # Placeholder for future implementation
    return []

def generate_neighborhoods(city_name: str, population: int) -> list:
    """Generate realistic neighborhood names"""
    # For large cities, use more diverse names
    if population > 1000000:
        return [
            {
                'name': f'{city_name} Downtown',
                'description': 'The bustling heart of the city with high-rise buildings, shopping, and nightlife.',
                'tags': ['Urban', 'Walkable', 'Nightlife']
            },
            {
                'name': 'Old Town',
                'description': 'Historic district with charming architecture, local boutiques, and cultural attractions.',
                'tags': ['Historic', 'Culture', 'Shopping']
            },
            {
                'name': 'Waterfront District',
                'description': 'Scenic area along the water with parks, restaurants, and recreational activities.',
                'tags': ['Scenic', 'Recreation', 'Dining']
            },
            {
                'name': 'University Quarter',
                'description': 'Vibrant area near campus with affordable housing, cafes, and student life.',
                'tags': ['Student-Friendly', 'Affordable', 'Lively']
            },
            {
                'name': 'Suburban Heights',
                'description': 'Family-friendly residential area with good schools, parks, and quiet streets.',
                'tags': ['Family-Friendly', 'Schools', 'Parks']
            },
        ]
    else:
        # For smaller cities, use simpler names
        return [
            {
                'name': 'City Center',
                'description': 'The main commercial and administrative hub with shops and services.',
                'tags': ['Central', 'Convenient', 'Shopping']
            },
            {
                'name': 'Residential District',
                'description': 'Quiet neighborhoods with family homes and local amenities.',
                'tags': ['Residential', 'Quiet', 'Family-Friendly']
            },
            {
                'name': 'Historic Quarter',
                'description': 'Area with traditional architecture and local character.',
                'tags': ['Historic', 'Traditional', 'Charming']
            },
        ]

