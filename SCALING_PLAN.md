# Scaling Plan: Data Collection for All 32,496 Cities

## Current Status

✅ **Implemented:**
- Comprehensive data fetcher using OpenAI API
- Fetches: rent, jobs, attractions, restaurants, schools, hospitals, transport, climate
- Persistent SQLite database with proper schema
- Real-time progress tracking
- Error handling
- Currently running for top 100 cities

## Scaling to All Cities

### Option 1: Batch Processing (Recommended)

**Approach:**
- Process cities in batches of 1,000
- Run overnight or over several days
- Prioritize by population (largest first)

**Command:**
```bash
# Batch 1: Top 1,000 cities
python3 comprehensive_data_fetcher.py 1000

# Batch 2: Next 1,000 cities (modify script to skip first 1000)
python3 comprehensive_data_fetcher.py 2000

# Continue until all 32,496 cities processed
```

**Estimated Time:**
- 100 cities = ~15 minutes
- 1,000 cities = ~2.5 hours
- 10,000 cities = ~25 hours
- 32,496 cities = ~80 hours (3-4 days)

**Cost Estimate:**
- OpenAI API: ~$0.002 per city
- 32,496 cities × $0.002 = ~$65 total

### Option 2: Parallel Processing

**Approach:**
- Split cities into 10 groups
- Run 10 parallel processes
- Complete in ~8 hours instead of 80

**Implementation:**
```python
# Split by ID ranges
# Process 1: cities WHERE id BETWEEN 1 AND 3250
# Process 2: cities WHERE id BETWEEN 3251 AND 6500
# etc.
```

### Option 3: Hybrid (Smart Prioritization)

**Tier 1: Top 1,000 cities** (High quality, complete data)
- Use GPT-4 for comprehensive data
- ~2.5 hours

**Tier 2: Next 5,000 cities** (Good quality)
- Use GPT-4 mini (faster, cheaper)
- ~12 hours

**Tier 3: Remaining 26,496 cities** (Basic data)
- Use estimates based on country/region averages
- Instant

## Rate Limiting

**OpenAI API Limits:**
- GPT-4 mini: 10,000 requests/minute (no issue)
- GPT-4: 500 requests/minute (may need throttling)

**Solution:**
Add sleep between requests if needed:
```python
import time
time.sleep(0.1)  # 100ms delay = max 600 requests/min
```

## Data Quality Tiers

### Tier 1: AI-Fetched (Top 1,000 cities)
- Real rent data
- Actual platforms
- Specific employers/attractions
- High accuracy

### Tier 2: Estimated (Mid-tier cities)
- Calculated rent based on country/region
- Generic platforms
- General attractions
- Medium accuracy

### Tier 3: Default (Small cities)
- Country averages
- National platforms
- Basic info
- Low accuracy but acceptable

## Database Optimization

**Current:** SQLite (good for 32K cities)
**Future:** PostgreSQL or Supabase (if scaling beyond 100K)

**Indexes to add:**
```sql
CREATE INDEX idx_cities_population ON cities(population DESC);
CREATE INDEX idx_cities_country ON cities(country);
CREATE INDEX idx_rent_data_city ON rent_data(city_id);
```

## Incremental Updates

**Strategy:**
- Fetch top 100 cities: Weekly
- Fetch top 1,000 cities: Monthly
- Fetch all cities: Quarterly

**Implementation:**
```python
# Only update cities older than 30 days
WHERE updated_at < datetime('now', '-30 days')
```

## Alternative Data Sources

### Free APIs (No cost, but limited)
1. **Numbeo API** - Cost of living data
2. **OpenStreetMap** - Attractions, restaurants
3. **Wikipedia API** - City info
4. **Weather APIs** - Climate data

### Paid APIs (Higher quality)
1. **RapidAPI** - Multiple data sources
2. **Zillow/Rightmove** - Real estate
3. **LinkedIn** - Job market
4. **Yelp/Google Places** - Restaurants/attractions

## Web Scraping (Last Resort)

**Platforms to scrape:**
- Airbnb (rentals)
- Indeed (jobs)
- TripAdvisor (attractions)
- Yelp (restaurants)

**Legal considerations:**
- Check robots.txt
- Respect rate limits
- Use official APIs when available

## Next Steps

### Immediate (Today)
1. ✅ Complete top 100 cities fetch (running now)
2. ⏳ Test data quality
3. ⏳ Generate V3 pages with real data
4. ⏳ Deploy and verify

### Short-term (This Week)
1. Fetch top 1,000 cities
2. Add more data sources (Numbeo, OSM)
3. Implement caching layer
4. Add data validation

### Long-term (Next Month)
1. Scale to all 32,496 cities
2. Set up automated updates
3. Add more data fields
4. Implement API rate limiting
5. Consider PostgreSQL migration

## Cost-Benefit Analysis

**Option A: AI for All Cities**
- Cost: ~$65
- Time: 80 hours
- Quality: High

**Option B: AI for Top 1K, Estimates for Rest**
- Cost: ~$2
- Time: 3 hours
- Quality: High for major cities, medium for rest

**Option C: Hybrid (Recommended)**
- Cost: ~$10
- Time: 15 hours
- Quality: High for top 5K, medium for rest

## Recommendation

**Phase 1 (Now):** Top 100 cities with AI ✅ Running
**Phase 2 (Today):** Generate V3 with real data, deploy
**Phase 3 (This week):** Top 1,000 cities with AI
**Phase 4 (Next week):** Remaining cities with estimates + OSM data
**Phase 5 (Ongoing):** Incremental updates, add more sources

This approach balances cost, time, and quality while getting the site live with great data quickly.

