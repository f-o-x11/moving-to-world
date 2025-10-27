'use client';

import { useState, useEffect, useCallback } from 'react';
import { Search, MapPin, TrendingUp } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { SearchResult } from '@/types';
import { useRouter } from 'next/navigation';

export default function SearchBar() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();

  const searchCities = useCallback(async (searchQuery: string) => {
    if (searchQuery.length < 2) {
      setResults([]);
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch(`/api/search?q=${encodeURIComponent(searchQuery)}&limit=10`);
      const data = await response.json();
      setResults(data.results || []);
    } catch (error) {
      console.error('Search error:', error);
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => {
      searchCities(query);
    }, 300);

    return () => clearTimeout(timer);
  }, [query, searchCities]);

  const handleSelectCity = (result: SearchResult) => {
    router.push(result.url);
    setIsOpen(false);
    setQuery('');
  };

  return (
    <div className="relative w-full max-w-2xl">
      <div className="relative">
        <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
        <input
          type="text"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setIsOpen(true);
          }}
          onFocus={() => setIsOpen(true)}
          placeholder="Search 32,496 cities worldwide..."
          className="w-full pl-12 pr-4 py-4 text-lg rounded-2xl border-2 border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 focus:border-blue-500 dark:focus:border-blue-400 focus:outline-none transition-all shadow-lg hover:shadow-xl"
        />
        {isLoading && (
          <div className="absolute right-4 top-1/2 -translate-y-1/2">
            <div className="animate-spin h-5 w-5 border-2 border-blue-500 border-t-transparent rounded-full" />
          </div>
        )}
      </div>

      <AnimatePresence>
        {isOpen && results.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="absolute z-50 w-full mt-2 bg-white dark:bg-gray-800 rounded-2xl shadow-2xl border border-gray-200 dark:border-gray-700 overflow-hidden"
          >
            <div className="max-h-96 overflow-y-auto">
              {results.map((result, index) => (
                <motion.button
                  key={`${result.name}-${result.country}-${index}`}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                  onClick={() => handleSelectCity(result)}
                  className="w-full px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-700 flex items-center gap-3 transition-colors border-b border-gray-100 dark:border-gray-700 last:border-0"
                >
                  <MapPin className="h-5 w-5 text-blue-500 flex-shrink-0" />
                  <div className="flex-1 text-left">
                    <div className="font-semibold text-gray-900 dark:text-white">
                      {result.name}
                    </div>
                    <div className="text-sm text-gray-500 dark:text-gray-400">
                      {result.state ? `${result.state}, ` : ''}{result.country}
                    </div>
                  </div>
                  <div className="flex items-center gap-2 text-xs text-gray-500">
                    <TrendingUp className="h-3 w-3" />
                    <span>{result.population.toLocaleString()}</span>
                  </div>
                </motion.button>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {isOpen && results.length > 0 && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setIsOpen(false)}
        />
      )}
    </div>
  );
}
