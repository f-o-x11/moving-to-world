import { getCityBySlug, getNeighborhoods } from '@/lib/db';
import { notFound, redirect } from 'next/navigation';

interface PageProps {
  params: Promise<{
    country: string;
    city: string;
  }>;
}

export default async function CityPageNoState({ params }: PageProps) {
  const { country, city: citySlug } = await params;
  const city = getCityBySlug(country, null, citySlug);

  if (!city) {
    notFound();
  }

  // Re-export the same component as the state version
  const CityPage = (await import('../[state]/[city]/page')).default;
  return <CityPage params={Promise.resolve({ country, state: '', city: citySlug })} />;
}
