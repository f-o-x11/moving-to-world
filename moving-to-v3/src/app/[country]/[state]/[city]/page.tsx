import { getCityBySlug, getNeighborhoods } from '@/lib/db';
import { notFound } from 'next/navigation';
import { MapPin, Users, DollarSign, Cloud, Globe as GlobeIcon, Calendar, Languages, Coins } from 'lucide-react';
import Link from 'next/link';
import CostCalculator from '@/components/CostCalculator';
import { motion } from 'framer-motion';

interface PageProps {
  params: Promise<{
    country: string;
    state: string;
    city: string;
  }>;
}

export default async function CityPage({ params }: PageProps) {
  const { country, state, city: citySlug } = await params;
  const city = getCityBySlug(country, state, citySlug);

  if (!city) {
    notFound();
  }

  const neighborhoods = city.id ? getNeighborhoods(city.id) : [];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      {/* Header */}
      <header className="border-b border-gray-200 dark:border-gray-700 bg-white/80 dark:bg-gray-800/80 backdrop-blur-lg sticky top-0 z-30">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <Link href="/" className="flex items-center gap-2">
              <GlobeIcon className="h-8 w-8 text-blue-600 dark:text-blue-400" />
              <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Moving.to
              </h1>
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="bg-gradient-to-r from-blue-600 to-purple-600 text-white py-16">
        <div className="container mx-auto px-4">
          {/* Breadcrumbs */}
          <nav className="mb-8">
            <ol className="flex items-center gap-2 text-sm text-blue-100">
              <li><Link href="/" className="hover:text-white">Home</Link></li>
              <li>/</li>
              <li><Link href={`/${country}`} className="hover:text-white capitalize">{country.replace(/-/g, ' ')}</Link></li>
              <li>/</li>
              <li><Link href={`/${country}/${state}`} className="hover:text-white capitalize">{state.replace(/-/g, ' ')}</Link></li>
              <li>/</li>
              <li className="text-white font-semibold">{city.name}</li>
            </ol>
          </nav>

          <div className="max-w-4xl">
            <h1 className="text-5xl md:text-6xl font-bold mb-4">
              {city.name}
            </h1>
            <p className="text-xl text-blue-100 mb-8 flex items-center gap-2">
              <MapPin className="h-5 w-5" />
              {city.state && `${city.state}, `}{city.country}
            </p>

            {/* Quick Stats Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <StatCard icon={Users} label="Population" value={city.population.toLocaleString()} />
              <StatCard icon={DollarSign} label="Cost Index" value={city.cost_index.toString()} />
              {city.climate && <StatCard icon={Cloud} label="Climate" value={city.climate} />}
              {city.timezone && <StatCard icon={Calendar} label="Timezone" value={city.timezone} />}
            </div>
          </div>
        </div>
      </section>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-12">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Column */}
          <div className="lg:col-span-2 space-y-8">
            {/* Overview */}
            <section className="bg-white dark:bg-gray-800 rounded-2xl p-8 shadow-lg border border-gray-200 dark:border-gray-700">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
                Overview
              </h2>
              <div className="grid grid-cols-2 gap-6">
                <InfoItem
                  icon={Users}
                  label="Population"
                  value={city.population.toLocaleString()}
                />
                <InfoItem
                  icon={DollarSign}
                  label="Cost Index"
                  value={city.cost_index.toString()}
                />
                {city.language && (
                  <InfoItem
                    icon={Languages}
                    label="Language"
                    value={city.language}
                  />
                )}
                {city.currency && (
                  <InfoItem
                    icon={Coins}
                    label="Currency"
                    value={city.currency}
                  />
                )}
              </div>
            </section>

            {/* Housing Costs */}
            <section className="bg-white dark:bg-gray-800 rounded-2xl p-8 shadow-lg border border-gray-200 dark:border-gray-700">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
                Housing Costs
              </h2>
              <div className="space-y-4">
                <div className="flex justify-between items-center p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                  <span className="text-gray-700 dark:text-gray-300 font-medium">
                    1 Bedroom (City Center)
                  </span>
                  <span className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                    ${city.rent_1br_center.toLocaleString()}
                  </span>
                </div>
                <div className="flex justify-between items-center p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                  <span className="text-gray-700 dark:text-gray-300 font-medium">
                    3 Bedroom (City Center)
                  </span>
                  <span className="text-2xl font-bold text-purple-600 dark:text-purple-400">
                    ${city.rent_3br_center.toLocaleString()}
                  </span>
                </div>
                <div className="flex justify-between items-center p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                  <span className="text-gray-700 dark:text-gray-300 font-medium">
                    Monthly Cost (Single Person)
                  </span>
                  <span className="text-2xl font-bold text-green-600 dark:text-green-400">
                    ${city.monthly_cost_single.toLocaleString()}
                  </span>
                </div>
              </div>
            </section>

            {/* Neighborhoods */}
            {neighborhoods.length > 0 && (
              <section className="bg-white dark:bg-gray-800 rounded-2xl p-8 shadow-lg border border-gray-200 dark:border-gray-700">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
                  Popular Neighborhoods
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {neighborhoods.map((neighborhood, index) => (
                    <div
                      key={neighborhood.id || index}
                      className="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg hover:shadow-md transition-shadow"
                    >
                      <h3 className="font-bold text-gray-900 dark:text-white mb-2">
                        {neighborhood.name}
                      </h3>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                        {neighborhood.description}
                      </p>
                      {neighborhood.tags && (
                        <div className="flex flex-wrap gap-2">
                          {neighborhood.tags.split(',').map((tag, i) => (
                            <span
                              key={i}
                              className="text-xs px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded-full"
                            >
                              {tag.trim()}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </section>
            )}

            {/* Cost Calculator */}
            <CostCalculator city={city} />
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Quick Info */}
            <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-lg border border-gray-200 dark:border-gray-700 sticky top-24">
              <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4">
                Quick Info
              </h3>
              <div className="space-y-3 text-sm">
                {city.timezone && (
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Timezone</span>
                    <span className="font-semibold text-gray-900 dark:text-white">{city.timezone}</span>
                  </div>
                )}
                {city.language && (
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Language</span>
                    <span className="font-semibold text-gray-900 dark:text-white">{city.language}</span>
                  </div>
                )}
                {city.currency && (
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Currency</span>
                    <span className="font-semibold text-gray-900 dark:text-white">{city.currency}</span>
                  </div>
                )}
                {city.climate && (
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Climate</span>
                    <span className="font-semibold text-gray-900 dark:text-white">{city.climate}</span>
                  </div>
                )}
                {city.walk_score !== undefined && (
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Walk Score</span>
                    <span className="font-semibold text-gray-900 dark:text-white">{city.walk_score}</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({ icon: Icon, label, value }: any) {
  return (
    <div className="bg-white/10 backdrop-blur-lg rounded-xl p-4">
      <Icon className="h-6 w-6 mb-2 text-blue-100" />
      <div className="text-sm text-blue-100 mb-1">{label}</div>
      <div className="text-lg font-bold">{value}</div>
    </div>
  );
}

function InfoItem({ icon: Icon, label, value }: any) {
  return (
    <div className="flex items-start gap-3">
      <Icon className="h-5 w-5 text-blue-500 mt-1" />
      <div>
        <div className="text-sm text-gray-500 dark:text-gray-400">{label}</div>
        <div className="font-semibold text-gray-900 dark:text-white">{value}</div>
      </div>
    </div>
  );
}
