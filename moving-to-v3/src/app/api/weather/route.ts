import { NextResponse } from 'next/server';

// Note: Add your OpenWeatherMap API key to .env.local as OPENWEATHER_API_KEY
const API_KEY = process.env.OPENWEATHER_API_KEY;

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const lat = searchParams.get('lat');
  const lon = searchParams.get('lon');

  if (!lat || !lon) {
    return NextResponse.json({ error: 'Missing coordinates' }, { status: 400 });
  }

  if (!API_KEY) {
    // Return mock data if no API key
    return NextResponse.json({
      current: {
        temp: 20,
        feels_like: 19,
        humidity: 65,
        description: 'partly cloudy',
        icon: '02d',
      },
      daily: [
        { date: new Date().toISOString(), temp_min: 15, temp_max: 25, description: 'sunny', icon: '01d' },
        { date: new Date(Date.now() + 86400000).toISOString(), temp_min: 16, temp_max: 24, description: 'cloudy', icon: '03d' },
      ],
    });
  }

  try {
    const response = await fetch(
      `https://api.openweathermap.org/data/3.0/onecall?lat=${lat}&lon=${lon}&exclude=minutely,hourly,alerts&units=metric&appid=${API_KEY}`,
      { next: { revalidate: 3600 } } // Cache for 1 hour
    );

    if (!response.ok) {
      throw new Error('Weather API failed');
    }

    const data = await response.json();

    const weather = {
      current: {
        temp: Math.round(data.current.temp),
        feels_like: Math.round(data.current.feels_like),
        humidity: data.current.humidity,
        description: data.current.weather[0].description,
        icon: data.current.weather[0].icon,
      },
      daily: data.daily.slice(0, 7).map((day: any) => ({
        date: new Date(day.dt * 1000).toISOString(),
        temp_min: Math.round(day.temp.min),
        temp_max: Math.round(day.temp.max),
        description: day.weather[0].description,
        icon: day.weather[0].icon,
      })),
    };

    return NextResponse.json(weather);
  } catch (error) {
    console.error('Weather fetch error:', error);
    return NextResponse.json({ error: 'Weather fetch failed' }, { status: 500 });
  }
}
