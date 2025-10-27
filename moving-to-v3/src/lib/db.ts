import Database from 'better-sqlite3';
import path from 'path';
import { City, SearchResult, Neighborhood } from '@/types';

const dbPath = path.join(process.cwd(), 'moving_to.db');
let db: Database.Database | null = null;

export function getDb() {
  if (!db) {
    db = new Database(dbPath, { readonly: true });
    db.pragma('journal_mode = WAL');
  }
  return db;
}

export function searchCities(query: string, limit = 20): SearchResult[] {
  const db = getDb();
  const searchTerm = `%${query.toLowerCase()}%`;

  const stmt = db.prepare(`
    SELECT
      name,
      state,
      country,
      population,
      cost_index,
      climate,
      CASE
        WHEN state IS NOT NULL THEN '/' || LOWER(REPLACE(country, ' ', '-')) || '/' || LOWER(REPLACE(state, ' ', '-')) || '/' || LOWER(REPLACE(name, ' ', '-'))
        ELSE '/' || LOWER(REPLACE(country, ' ', '-')) || '/' || LOWER(REPLACE(name, ' ', '-'))
      END as url
    FROM cities
    WHERE LOWER(name) LIKE ? OR LOWER(country) LIKE ? OR LOWER(state) LIKE ?
    ORDER BY population DESC
    LIMIT ?
  `);

  return stmt.all(searchTerm, searchTerm, searchTerm, limit) as SearchResult[];
}

export function getCityBySlug(country: string, state: string | null, city: string): City | null {
  const db = getDb();

  let stmt;
  let result;

  if (state) {
    stmt = db.prepare(`
      SELECT * FROM cities
      WHERE LOWER(REPLACE(name, ' ', '-')) = ?
        AND LOWER(REPLACE(state, ' ', '-')) = ?
        AND LOWER(REPLACE(country, ' ', '-')) = ?
      LIMIT 1
    `);
    result = stmt.get(city.toLowerCase(), state.toLowerCase(), country.toLowerCase());
  } else {
    stmt = db.prepare(`
      SELECT * FROM cities
      WHERE LOWER(REPLACE(name, ' ', '-')) = ?
        AND LOWER(REPLACE(country, ' ', '-')) = ?
      LIMIT 1
    `);
    result = stmt.get(city.toLowerCase(), country.toLowerCase());
  }

  return result as City | null;
}

export function getCitiesByCountry(country: string, limit = 50): City[] {
  const db = getDb();
  const stmt = db.prepare(`
    SELECT * FROM cities
    WHERE LOWER(country) = ?
    ORDER BY population DESC
    LIMIT ?
  `);

  return stmt.all(country.toLowerCase(), limit) as City[];
}

export function getTopCities(limit = 100): City[] {
  const db = getDb();
  const stmt = db.prepare(`
    SELECT * FROM cities
    ORDER BY population DESC
    LIMIT ?
  `);

  return stmt.all(limit) as City[];
}

export function getCitiesByFilter(filters: {
  minPopulation?: number;
  maxPopulation?: number;
  minCost?: number;
  maxCost?: number;
  climate?: string;
  countries?: string[];
  limit?: number;
}): City[] {
  const db = getDb();
  const conditions: string[] = [];
  const params: any[] = [];

  if (filters.minPopulation) {
    conditions.push('population >= ?');
    params.push(filters.minPopulation);
  }

  if (filters.maxPopulation) {
    conditions.push('population <= ?');
    params.push(filters.maxPopulation);
  }

  if (filters.minCost) {
    conditions.push('cost_index >= ?');
    params.push(filters.minCost);
  }

  if (filters.maxCost) {
    conditions.push('cost_index <= ?');
    params.push(filters.maxCost);
  }

  if (filters.climate) {
    conditions.push('LOWER(climate) = ?');
    params.push(filters.climate.toLowerCase());
  }

  if (filters.countries && filters.countries.length > 0) {
    const placeholders = filters.countries.map(() => '?').join(',');
    conditions.push(`LOWER(country) IN (${placeholders})`);
    params.push(...filters.countries.map(c => c.toLowerCase()));
  }

  const whereClause = conditions.length > 0 ? `WHERE ${conditions.join(' AND ')}` : '';
  const limit = filters.limit || 50;

  const stmt = db.prepare(`
    SELECT * FROM cities
    ${whereClause}
    ORDER BY population DESC
    LIMIT ?
  `);

  return stmt.all(...params, limit) as City[];
}

export function getNeighborhoods(cityId: number): Neighborhood[] {
  const db = getDb();
  const stmt = db.prepare(`
    SELECT * FROM neighborhoods
    WHERE city_id = ?
  `);

  return stmt.all(cityId) as Neighborhood[];
}

export function getRandomCities(count = 6): City[] {
  const db = getDb();
  const stmt = db.prepare(`
    SELECT * FROM cities
    WHERE population > 100000
    ORDER BY RANDOM()
    LIMIT ?
  `);

  return stmt.all(count) as City[];
}

export function getAllCountries(): string[] {
  const db = getDb();
  const stmt = db.prepare(`
    SELECT DISTINCT country FROM cities
    ORDER BY country
  `);

  return stmt.all().map((row: any) => row.country);
}

export function getCityStats() {
  const db = getDb();

  const totalCities = db.prepare('SELECT COUNT(*) as count FROM cities').get() as { count: number };
  const totalCountries = db.prepare('SELECT COUNT(DISTINCT country) as count FROM cities').get() as { count: number };

  return {
    totalCities: totalCities.count,
    totalCountries: totalCountries.count,
  };
}
