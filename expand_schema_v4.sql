-- V4 Database Schema Expansion
-- Add comprehensive cost-of-living, income, and quality scores

-- Table: costs (detailed cost breakdown)
CREATE TABLE IF NOT EXISTS costs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  city_id INTEGER NOT NULL,
  housing_monthly REAL,
  food_monthly REAL,
  transport_monthly REAL,
  utilities_monthly REAL,
  healthcare_monthly REAL,
  education_monthly REAL,
  leisure_monthly REAL,
  currency VARCHAR(3),
  exchange_rate_to_usd REAL,
  cost_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (city_id) REFERENCES cities(id)
);

CREATE INDEX IF NOT EXISTS idx_costs_city ON costs(city_id);
CREATE INDEX IF NOT EXISTS idx_costs_date ON costs(cost_date);

-- Table: incomes (median income data)
CREATE TABLE IF NOT EXISTS incomes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  city_id INTEGER NOT NULL,
  median_individual_income REAL,
  median_household_income REAL,
  sample_size INTEGER,
  income_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (city_id) REFERENCES cities(id)
);

CREATE INDEX IF NOT EXISTS idx_incomes_city ON incomes(city_id);

-- Table: scores (quality of life metrics)
CREATE TABLE IF NOT EXISTS scores (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  city_id INTEGER NOT NULL,
  walkability INTEGER CHECK (walkability BETWEEN 0 AND 100),
  bikeability INTEGER CHECK (bikeability BETWEEN 0 AND 100),
  safety_index INTEGER CHECK (safety_index BETWEEN 0 AND 100),
  healthcare_index INTEGER CHECK (healthcare_index BETWEEN 0 AND 100),
  internet_speed INTEGER,
  education_quality INTEGER CHECK (education_quality BETWEEN 0 AND 100),
  FOREIGN KEY (city_id) REFERENCES cities(id)
);

CREATE INDEX IF NOT EXISTS idx_scores_city ON scores(city_id);

-- Enhance neighborhoods table with tags
ALTER TABLE neighborhoods ADD COLUMN tags TEXT; -- JSON array of tags
ALTER TABLE neighborhoods ADD COLUMN description TEXT;

-- Add last_updated to cities table
ALTER TABLE cities ADD COLUMN last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
