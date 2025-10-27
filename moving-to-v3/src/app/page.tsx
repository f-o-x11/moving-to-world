import { getRandomCities, getCityStats } from '@/lib/db';
import SearchBar from '@/components/SearchBar';
import CityCard from '@/components/CityCard';
import { Sparkles, Globe, TrendingUp, Heart } from 'lucide-react';

export const dynamic = 'force-dynamic';

export default async function HomePage() {
  const featuredCities = getRandomCities(6);
  const stats = getCityStats();

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      {/* Header */}
      <header className="border-b border-gray-200 dark:border-gray-700 bg-white/80 dark:bg-gray-800/80 backdrop-blur-lg sticky top-0 z-30">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Globe className="h-8 w-8 text-blue-600 dark:text-blue-400" />
              <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Moving.to
              </h1>
            </div>
            <nav className="flex items-center gap-6">
              <a href="#explore" className="text-gray-600 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 transition-colors font-medium">
                Explore
              </a>
              <a href="#compare" className="text-gray-600 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 transition-colors font-medium">
                Compare
              </a>
              <a href="#about" className="text-gray-600 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 transition-colors font-medium">
                About
              </a>
            </nav>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto px-4 pt-20 pb-16">
        <div className="text-center max-w-4xl mx-auto">
          <div className="inline-flex items-center gap-2 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 px-4 py-2 rounded-full text-sm font-semibold mb-6">
            <Sparkles className="h-4 w-4" />
            Now with AI-powered recommendations
          </div>

          <h1 className="text-5xl md:text-7xl font-bold mb-6 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent leading-tight">
            Find Your Perfect City
          </h1>

          <p className="text-xl md:text-2xl text-gray-600 dark:text-gray-300 mb-12 leading-relaxed">
            Discover comprehensive guides for <span className="font-bold text-blue-600 dark:text-blue-400">{stats.totalCities.toLocaleString()}</span> cities
            across <span className="font-bold text-purple-600 dark:text-purple-400">{stats.totalCountries}</span> countries worldwide
          </p>

          <SearchBar />

          {/* Quick Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-16">
            <div className="bg-white/60 dark:bg-gray-800/60 backdrop-blur-lg rounded-2xl p-6 border border-gray-200 dark:border-gray-700">
              <Globe className="h-8 w-8 text-blue-600 dark:text-blue-400 mb-3 mx-auto" />
              <div className="text-3xl font-bold text-gray-900 dark:text-white mb-1">
                {stats.totalCountries}+
              </div>
              <div className="text-gray-600 dark:text-gray-400">Countries Covered</div>
            </div>

            <div className="bg-white/60 dark:bg-gray-800/60 backdrop-blur-lg rounded-2xl p-6 border border-gray-200 dark:border-gray-700">
              <TrendingUp className="h-8 w-8 text-purple-600 dark:text-purple-400 mb-3 mx-auto" />
              <div className="text-3xl font-bold text-gray-900 dark:text-white mb-1">
                {stats.totalCities.toLocaleString()}
              </div>
              <div className="text-gray-600 dark:text-gray-400">Cities to Explore</div>
            </div>

            <div className="bg-white/60 dark:bg-gray-800/60 backdrop-blur-lg rounded-2xl p-6 border border-gray-200 dark:border-gray-700">
              <Heart className="h-8 w-8 text-pink-600 dark:text-pink-400 mb-3 mx-auto" />
              <div className="text-3xl font-bold text-gray-900 dark:text-white mb-1">
                100%
              </div>
              <div className="text-gray-600 dark:text-gray-400">Free & Open</div>
            </div>
          </div>
        </div>
      </section>

      {/* Featured Cities */}
      <section className="container mx-auto px-4 py-16" id="explore">
        <div className="mb-12">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">
            Featured Destinations
          </h2>
          <p className="text-lg text-gray-600 dark:text-gray-400">
            Explore these popular cities or search for your dream destination above
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {featuredCities.map((city, index) => (
            <CityCard key={city.id || index} city={city} index={index} />
          ))}
        </div>
      </section>

      {/* Features Section */}
      <section className="container mx-auto px-4 py-16 mb-16">
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-3xl p-12 text-white">
          <div className="max-w-3xl mx-auto text-center">
            <h2 className="text-3xl md:text-4xl font-bold mb-6">
              Everything You Need to Plan Your Move
            </h2>
            <p className="text-xl mb-8 text-blue-100">
              Cost of living, weather data, neighborhoods, job markets, and more
            </p>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
              <div>
                <div className="text-4xl mb-2">💰</div>
                <div className="font-semibold">Cost Analysis</div>
              </div>
              <div>
                <div className="text-4xl mb-2">🌤️</div>
                <div className="font-semibold">Weather Data</div>
              </div>
              <div>
                <div className="text-4xl mb-2">🏘️</div>
                <div className="font-semibold">Neighborhoods</div>
              </div>
              <div>
                <div className="text-4xl mb-2">💼</div>
                <div className="font-semibold">Job Markets</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 py-12">
        <div className="container mx-auto px-4">
          <div className="text-center text-gray-600 dark:text-gray-400">
            <p className="mb-2">
              Made with <Heart className="inline h-4 w-4 text-red-500" /> for people exploring the world
            </p>
            <p className="text-sm">
              Data covering {stats.totalCities.toLocaleString()} cities across {stats.totalCountries}+ countries
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
