import { NextResponse } from 'next/server';
import { searchCities } from '@/lib/db';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const query = searchParams.get('q');
  const limit = parseInt(searchParams.get('limit') || '20');

  if (!query || query.length < 2) {
    return NextResponse.json({ results: [] });
  }

  try {
    const results = searchCities(query, limit);
    return NextResponse.json({ results });
  } catch (error) {
    console.error('Search error:', error);
    return NextResponse.json({ error: 'Search failed' }, { status: 500 });
  }
}
