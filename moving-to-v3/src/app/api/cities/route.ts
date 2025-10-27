import { NextResponse } from 'next/server';
import { getCitiesByFilter, getTopCities, getRandomCities } from '@/lib/db';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);

  const type = searchParams.get('type');

  if (type === 'random') {
    const count = parseInt(searchParams.get('count') || '6');
    const cities = getRandomCities(count);
    return NextResponse.json({ cities });
  }

  if (type === 'top') {
    const limit = parseInt(searchParams.get('limit') || '100');
    const cities = getTopCities(limit);
    return NextResponse.json({ cities });
  }

  // Filtered search
  const filters: any = {};

  if (searchParams.get('minPopulation')) {
    filters.minPopulation = parseInt(searchParams.get('minPopulation')!);
  }

  if (searchParams.get('maxPopulation')) {
    filters.maxPopulation = parseInt(searchParams.get('maxPopulation')!);
  }

  if (searchParams.get('minCost')) {
    filters.minCost = parseInt(searchParams.get('minCost')!);
  }

  if (searchParams.get('maxCost')) {
    filters.maxCost = parseInt(searchParams.get('maxCost')!);
  }

  if (searchParams.get('climate')) {
    filters.climate = searchParams.get('climate');
  }

  if (searchParams.get('countries')) {
    filters.countries = searchParams.get('countries')!.split(',');
  }

  if (searchParams.get('limit')) {
    filters.limit = parseInt(searchParams.get('limit')!);
  }

  try {
    const cities = getCitiesByFilter(filters);
    return NextResponse.json({ cities });
  } catch (error) {
    console.error('Filter error:', error);
    return NextResponse.json({ error: 'Filter failed' }, { status: 500 });
  }
}
