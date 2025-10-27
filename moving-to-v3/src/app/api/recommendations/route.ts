import { NextResponse } from 'next/server';
import { getCitiesByFilter } from '@/lib/db';
import { City, CityRecommendation, UserPreferences } from '@/types';

function calculateRecommendationScore(city: City, preferences: UserPreferences): CityRecommendation {
  let score = 100;
  const reasons: string[] = [];

  // Climate preference
  if (preferences.climate && city.climate) {
    if (city.climate.toLowerCase().includes(preferences.climate.toLowerCase())) {
      score += 20;
      reasons.push(`Perfect ${preferences.climate} climate`);
    } else {
      score -= 10;
    }
  }

  // Cost preference
  if (preferences.maxCost) {
    if (city.cost_index <= preferences.maxCost) {
      score += 15;
      reasons.push('Affordable cost of living');
    } else {
      score -= (city.cost_index - preferences.maxCost) * 0.5;
      reasons.push('Higher cost than preferred');
    }
  }

  // Population preference
  if (preferences.minPopulation && city.population < preferences.minPopulation) {
    score -= 20;
  }

  if (preferences.maxPopulation && city.population > preferences.maxPopulation) {
    score -= 15;
  }

  // Bonus for moderate population (livable size)
  if (city.population >= 100000 && city.population <= 5000000) {
    score += 10;
    reasons.push('Great city size');
  }

  // Bonus for low cost index
  if (city.cost_index < 60) {
    score += 10;
    reasons.push('Very affordable');
  }

  return {
    city,
    score: Math.max(0, Math.min(100, score)),
    reasons: reasons.slice(0, 3),
  };
}

export async function POST(request: Request) {
  try {
    const preferences: UserPreferences = await request.json();

    // Get cities matching basic filters
    const filters: any = {
      limit: 100,
    };

    if (preferences.minPopulation) filters.minPopulation = preferences.minPopulation;
    if (preferences.maxPopulation) filters.maxPopulation = preferences.maxPopulation;
    if (preferences.maxCost) filters.maxCost = preferences.maxCost;
    if (preferences.climate) filters.climate = preferences.climate;
    if (preferences.regions && preferences.regions.length > 0) {
      filters.countries = preferences.regions;
    }

    const cities = getCitiesByFilter(filters);

    // Calculate recommendation scores
    const recommendations = cities
      .map(city => calculateRecommendationScore(city, preferences))
      .sort((a, b) => b.score - a.score)
      .slice(0, 10);

    return NextResponse.json({ recommendations });
  } catch (error) {
    console.error('Recommendation error:', error);
    return NextResponse.json({ error: 'Recommendation failed' }, { status: 500 });
  }
}
