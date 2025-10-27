export interface City {
  id?: number;
  name: string;
  state: string | null;
  country: string;
  population: number;
  latitude: number;
  longitude: number;
  cost_index: number;
  rent_1br_center: number;
  rent_3br_center: number;
  monthly_cost_single: number;
  timezone?: string;
  language?: string;
  currency?: string;
  climate?: string;
  walk_score?: number;
  url?: string;
}

export interface SearchResult {
  name: string;
  state: string | null;
  country: string;
  url: string;
  population: number;
  cost_index: number;
  climate: string;
}

export interface WeatherData {
  current: {
    temp: number;
    feels_like: number;
    humidity: number;
    description: string;
    icon: string;
  };
  daily: {
    date: string;
    temp_min: number;
    temp_max: number;
    description: string;
    icon: string;
  }[];
}

export interface CityRecommendation {
  city: City;
  score: number;
  reasons: string[];
}

export interface UserPreferences {
  climate?: 'hot' | 'warm' | 'temperate' | 'cold';
  maxCost?: number;
  minPopulation?: number;
  maxPopulation?: number;
  regions?: string[];
}

export interface Neighborhood {
  id?: number;
  city_id: number;
  name: string;
  description: string;
  characteristics: string;
  tags: string;
}

export interface ComparisonData {
  cities: City[];
  categories: {
    costOfLiving: number[];
    housing: number[];
    population: number[];
    climate: string[];
  };
}
