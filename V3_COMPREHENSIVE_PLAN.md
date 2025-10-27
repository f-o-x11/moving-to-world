# Moving.to V3 - Comprehensive Data Integration Plan

**Goal:** Transform each city page into a comprehensive relocation guide with real data from multiple sources

---

## 🎯 V3 Objectives

### 1. Real Climate Data
**Current:** Generic "Temperate" label  
**Target:** Actual temperature ranges, precipitation, humidity

**Data Sources:**
- OpenWeatherMap API (Free: 1,000 calls/day)
  - Current weather
  - 5-day forecast
  - Historical averages
- Weather.gov API (Free, US only)
- Visual Crossing Weather API

**Implementation:**
- Store monthly temperature ranges in database
- Update quarterly or when user visits
- Show: "Jan: 5-15°C, Jul: 25-35°C" instead of "Temperate"

---

### 2. Tabbed Interface (Like Old Version)
**Tabs to implement:**

#### Tab 1: Overview
- City description
- Key statistics
- Quick facts (timezone, language, currency)
- Walk score
- Map

#### Tab 2: Weather & Climate
- Monthly temperature ranges
- Precipitation data
- Best time to visit
- Seasonal information
- UV index, humidity

#### Tab 3: Housing & Rentals
- **Real rental listings** from APIs:
  - Airbnb API (short-term)
  - Country-specific platforms (Yad2 for Israel, Rightmove for UK, etc.)
- Average prices by neighborhood
- Rent trends
- Buying vs renting comparison

#### Tab 4: Employment & Jobs
- Major employers
- Top industries
- Average salaries by role
- Job market trends
- **Real job listings** from:
  - LinkedIn API
  - Indeed API
  - Glassdoor API
  - Country-specific job boards

#### Tab 5: Attractions & Things to Do
- Top tourist attractions
- Museums, parks, landmarks
- Entertainment venues
- **Data from:**
  - OpenStreetMap Overpass API (Free)
  - Google Places API
  - TripAdvisor API
  - Foursquare API

#### Tab 6: Restaurants & Food
- Popular restaurants
- Local cuisine
- Price ranges
- **Data from:**
  - OpenStreetMap (Free)
  - Yelp API
  - Google Places API
  - Zomato API

#### Tab 7: Transportation
- Public transit options
- Bike infrastructure
- Car ownership costs
- Airport access
- **Data from:**
  - OpenStreetMap (transit data)
  - City transit APIs
  - Walk Score API

#### Tab 8: Education & Schools
- Top schools
- Universities
- International schools
- Education system overview
- **Data from:**
  - OpenStreetMap
  - Government education databases
  - School rating APIs

#### Tab 9: Healthcare
- Hospitals
- Clinics
- Healthcare system
- Insurance information
- **Data from:**
  - OpenStreetMap
  - Government health databases

#### Tab 10: Cost of Living
- Detailed breakdown
- Comparison with other cities
- Salary calculator
- **Data from:**
  - Numbeo API
  - Expatistan API
  - Cost of living databases

---

## 📊 Data Sources & APIs

### Free APIs (Priority)
1. **OpenWeatherMap** - Weather data (1,000 calls/day free)
2. **OpenStreetMap Overpass API** - POIs, restaurants, attractions (unlimited, free)
3. **Nominatim** - Geocoding (free)
4. **Weather.gov** - US weather (free, unlimited)
5. **Numbeo** - Cost of living (web scraping or API)
6. **Walk Score API** - Already using

### Paid/Limited APIs (Consider for premium features)
1. **Airbnb API** - Real rental listings
2. **LinkedIn API** - Job listings
3. **Google Places API** - Restaurants, attractions ($200 credit/month)
4. **Yelp Fusion API** - Restaurant data (5,000 calls/day free)
5. **TripAdvisor API** - Attractions, reviews
6. **Indeed API** - Job listings

### Web Scraping (Fallback)
1. **Yad2.co.il** - Israel rentals
2. **Rightmove.co.uk** - UK rentals
3. **Zillow** - US rentals
4. **Local job boards** - Employment data

---

## 🗄️ Database Schema Updates

### New Tables Needed:

```sql
-- Weather data
CREATE TABLE weather_data (
    id INTEGER PRIMARY KEY,
    city_id INTEGER,
    month INTEGER,
    temp_min_c REAL,
    temp_max_c REAL,
    precipitation_mm REAL,
    humidity_percent INTEGER,
    updated_at TIMESTAMP
);

-- Attractions
CREATE TABLE attractions (
    id INTEGER PRIMARY KEY,
    city_id INTEGER,
    name TEXT,
    category TEXT, -- museum, park, landmark, etc.
    description TEXT,
    latitude REAL,
    longitude REAL,
    rating REAL,
    source TEXT,
    external_url TEXT
);

-- Restaurants
CREATE TABLE restaurants (
    id INTEGER PRIMARY KEY,
    city_id INTEGER,
    name TEXT,
    cuisine TEXT,
    price_range TEXT, -- $, $$, $$$, $$$$
    rating REAL,
    latitude REAL,
    longitude REAL,
    source TEXT,
    external_url TEXT
);

-- Employers
CREATE TABLE major_employers (
    id INTEGER PRIMARY KEY,
    city_id INTEGER,
    company_name TEXT,
    industry TEXT,
    employee_count INTEGER,
    website TEXT
);

-- Schools
CREATE TABLE schools (
    id INTEGER PRIMARY KEY,
    city_id INTEGER,
    name TEXT,
    type TEXT, -- elementary, high school, university
    rating REAL,
    latitude REAL,
    longitude REAL
);

-- Healthcare facilities
CREATE TABLE healthcare (
    id INTEGER PRIMARY KEY,
    city_id INTEGER,
    name TEXT,
    type TEXT, -- hospital, clinic
    latitude REAL,
    longitude REAL
);
```

---

## 🚀 Implementation Plan

### Phase 1: Data Collection Scripts (Week 1)
1. ✅ Setup database (DONE)
2. Create weather data fetcher (OpenWeatherMap)
3. Create OSM data fetcher (attractions, restaurants, transit)
4. Create rental data fetcher (Airbnb + country-specific)
5. Create job data fetcher (LinkedIn, Indeed)

### Phase 2: Template Updates (Week 1-2)
1. Create tabbed interface with JavaScript
2. Update CSS for tabs
3. Add weather section with real data
4. Add attractions section
5. Add restaurants section
6. Add employment section
7. Add housing section with real listings

### Phase 3: Data Population (Week 2)
1. Fetch weather data for all 32,496 cities
2. Fetch POI data for top 1,000 cities
3. Fetch rental data for top 500 cities
4. Fetch job data for top 100 cities

### Phase 4: Generation & Deployment (Week 2-3)
1. Update generation script to use database
2. Generate pages with tabs
3. Test on 20 diverse cities
4. Full batch generation
5. Deploy V3

---

## 💰 Cost Estimation

### Free Tier Usage
- OpenWeatherMap: 1,000 calls/day = ~30 days for 32K cities
- OpenStreetMap: Unlimited (but rate-limited)
- Weather.gov: Free for US cities

### Paid APIs (Optional)
- Google Places: $200/month credit (enough for ~40K requests)
- Yelp: Free tier sufficient for testing
- Airbnb: Requires partnership or scraping

### Total Estimated Cost
- **Minimum:** $0 (using only free APIs)
- **Recommended:** $50-100/month (Google Places + weather premium)
- **Premium:** $500/month (all paid APIs for real-time data)

---

## 📝 V3 Success Criteria

1. ✅ Real temperature ranges (not "Temperate")
2. ✅ Tabbed interface with 8-10 sections
3. ✅ Real rental listings (at least 10 per city)
4. ✅ Real job listings (at least 5 per major city)
5. ✅ Real attractions (at least 10 per city)
6. ✅ Real restaurants (at least 10 per city)
7. ✅ All data stored in persistent database
8. ✅ Data can be updated incrementally
9. ✅ Links open actual listings (not placeholders)
10. ✅ Mobile-responsive tabs

---

## 🔄 Data Update Strategy

### Initial Load
- Fetch all data for all cities (may take weeks)
- Store in database
- Generate static pages

### Incremental Updates
- Update weather data: Monthly
- Update rental listings: Weekly
- Update job listings: Weekly
- Update POI data: Quarterly
- Regenerate affected pages only

### On-Demand Updates
- When user visits a city page
- Check if data is >7 days old
- Fetch fresh data if needed
- Regenerate page

---

## 🎨 UI/UX Improvements

### Tabs Design
```
[Overview] [Weather] [Housing] [Jobs] [Attractions] [Food] [Transport] [Schools] [Healthcare] [Cost]
```

### Mobile Design
- Collapsible accordion instead of tabs
- Swipeable sections
- Sticky navigation

### Loading States
- Show skeleton screens while loading
- Progressive enhancement
- Cache data in localStorage

---

## 🔐 API Key Management

Store API keys securely:
```python
# .env file (not in git)
OPENWEATHER_API_KEY=xxx
GOOGLE_PLACES_API_KEY=xxx
YELP_API_KEY=xxx
LINKEDIN_API_KEY=xxx
```

Use environment variables in generation scripts

---

## 📈 Metrics to Track

1. Data freshness (days since last update)
2. API usage (calls per day)
3. Data coverage (% of cities with real data)
4. User engagement (time on page, tab clicks)
5. Link click-through rates

---

## 🚧 Challenges & Solutions

### Challenge 1: API Rate Limits
**Solution:** 
- Batch requests
- Cache data in database
- Use multiple API keys
- Implement exponential backoff

### Challenge 2: Data Quality
**Solution:**
- Validate all data before storing
- Manual review for top 100 cities
- User feedback system
- Regular audits

### Challenge 3: Cost
**Solution:**
- Start with free APIs only
- Add paid APIs for top cities first
- Monetize with ads or premium features
- Partner with data providers

### Challenge 4: Maintenance
**Solution:**
- Automated update scripts
- Monitoring and alerts
- Database backups
- Version control for data

---

## 🎯 V3 Timeline

**Week 1:**
- Day 1-2: Weather API integration
- Day 3-4: OSM data fetcher
- Day 5-7: Template with tabs

**Week 2:**
- Day 1-3: Rental & job data fetchers
- Day 4-5: Data population for top 100 cities
- Day 6-7: Testing & QA

**Week 3:**
- Day 1-3: Full data population (32K cities)
- Day 4-5: Generation & deployment
- Day 6-7: Monitoring & fixes

**Total: 3 weeks for complete V3**

---

## ✅ Next Steps (Immediate)

1. Get OpenWeatherMap API key
2. Create weather data fetcher script
3. Create OSM POI fetcher script
4. Update template with tabbed interface
5. Test on Tel Aviv, Paris, Tokyo
6. Deploy to v3-development branch

---

**Status:** 📋 **PLANNED**  
**Current Version:** V2.0-stable  
**Next Version:** V3.0-comprehensive  
**Target Date:** 3 weeks from start

