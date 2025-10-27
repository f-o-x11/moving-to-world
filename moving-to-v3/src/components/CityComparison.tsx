'use client';

import { useState } from 'react';
import { City } from '@/types';
import { X, Plus, TrendingUp, DollarSign, Users, Cloud, MapPin } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface CityComparisonProps {
  initialCities?: City[];
}

export default function CityComparison({ initialCities = [] }: CityComparisonProps) {
  const [cities, setCities] = useState<City[]>(initialCities);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<any[]>([]);

  const addCity = (city: City) => {
    if (cities.length < 4 && !cities.find(c => c.id === city.id)) {
      setCities([...cities, city]);
      setSearchQuery('');
      setSearchResults([]);
    }
  };

  const removeCity = (cityId: number | undefined) => {
    setCities(cities.filter(c => c.id !== cityId));
  };

  const handleSearch = async (query: string) => {
    setSearchQuery(query);
    if (query.length < 2) {
      setSearchResults([]);
      return;
    }

    try {
      const response = await fetch(`/api/search?q=${encodeURIComponent(query)}&limit=5`);
      const data = await response.json();
      setSearchResults(data.results || []);
    } catch (error) {
      console.error('Search error:', error);
    }
  };

  return (
    <div className="w-full">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
          Compare Cities
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          Add up to 4 cities to compare cost of living, population, and more
        </p>
      </div>

      {/* Add City Search */}
      {cities.length < 4 && (
        <div className="mb-8">
          <div className="relative">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => handleSearch(e.target.value)}
              placeholder="Search to add a city..."
              className="w-full px-4 py-3 rounded-xl border-2 border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 focus:border-blue-500 focus:outline-none"
            />
            {searchResults.length > 0 && (
              <div className="absolute z-10 w-full mt-2 bg-white dark:bg-gray-800 rounded-xl shadow-xl border border-gray-200 dark:border-gray-700 max-h-60 overflow-y-auto">
                {searchResults.map((result: any, index) => (
                  <button
                    key={index}
                    onClick={() => addCity(result as City)}
                    className="w-full px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-700 flex items-center gap-3 transition-colors border-b border-gray-100 dark:border-gray-700 last:border-0"
                  >
                    <MapPin className="h-4 w-4 text-blue-500" />
                    <div className="flex-1 text-left">
                      <div className="font-semibold">{result.name}</div>
                      <div className="text-sm text-gray-500">
                        {result.state ? `${result.state}, ` : ''}{result.country}
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Comparison Grid */}
      {cities.length === 0 ? (
        <div className="text-center py-16 bg-gray-50 dark:bg-gray-800 rounded-2xl border-2 border-dashed border-gray-300 dark:border-gray-600">
          <Plus className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-500 dark:text-gray-400">
            Search and add cities to start comparing
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <AnimatePresence>
            {cities.map((city, index) => (
              <motion.div
                key={city.id || index}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-lg border border-gray-200 dark:border-gray-700"
              >
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="font-bold text-lg text-gray-900 dark:text-white">
                      {city.name}
                    </h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      {city.country}
                    </p>
                  </div>
                  <button
                    onClick={() => removeCity(city.id)}
                    className="text-gray-400 hover:text-red-500 transition-colors"
                  >
                    <X className="h-5 w-5" />
                  </button>
                </div>

                <div className="space-y-4">
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <Users className="h-4 w-4 text-blue-500" />
                      <span className="text-xs text-gray-500 dark:text-gray-400">
                        Population
                      </span>
                    </div>
                    <div className="font-bold text-gray-900 dark:text-white">
                      {city.population.toLocaleString()}
                    </div>
                  </div>

                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <DollarSign className="h-4 w-4 text-green-500" />
                      <span className="text-xs text-gray-500 dark:text-gray-400">
                        Cost Index
                      </span>
                    </div>
                    <div className="font-bold text-gray-900 dark:text-white">
                      {city.cost_index}
                    </div>
                    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 mt-2">
                      <div
                        className="bg-gradient-to-r from-green-500 to-red-500 h-2 rounded-full"
                        style={{ width: `${city.cost_index}%` }}
                      />
                    </div>
                  </div>

                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <TrendingUp className="h-4 w-4 text-purple-500" />
                      <span className="text-xs text-gray-500 dark:text-gray-400">
                        1BR Rent
                      </span>
                    </div>
                    <div className="font-bold text-gray-900 dark:text-white">
                      ${city.rent_1br_center.toLocaleString()}
                    </div>
                  </div>

                  {city.climate && (
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <Cloud className="h-4 w-4 text-sky-500" />
                        <span className="text-xs text-gray-500 dark:text-gray-400">
                          Climate
                        </span>
                      </div>
                      <div className="font-bold text-gray-900 dark:text-white">
                        {city.climate}
                      </div>
                    </div>
                  )}
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      )}
    </div>
  );
}
