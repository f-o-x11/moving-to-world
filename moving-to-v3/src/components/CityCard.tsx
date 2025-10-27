'use client';

import { City } from '@/types';
import { motion } from 'framer-motion';
import { MapPin, Users, DollarSign, Cloud } from 'lucide-react';
import Link from 'next/link';

interface CityCardProps {
  city: City;
  index?: number;
}

export default function CityCard({ city, index = 0 }: CityCardProps) {
  const url = city.state
    ? `/${city.country.toLowerCase().replace(/ /g, '-')}/${city.state.toLowerCase().replace(/ /g, '-')}/${city.name.toLowerCase().replace(/ /g, '-')}`
    : `/${city.country.toLowerCase().replace(/ /g, '-')}/${city.name.toLowerCase().replace(/ /g, '-')}`;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
      whileHover={{ y: -8, scale: 1.02 }}
      className="group"
    >
      <Link href={url}>
        <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-lg hover:shadow-2xl transition-all border border-gray-100 dark:border-gray-700 h-full">
          <div className="flex justify-between items-start mb-4">
            <div>
              <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-1">
                {city.name}
              </h3>
              <p className="text-sm text-gray-500 dark:text-gray-400 flex items-center gap-1">
                <MapPin className="h-3 w-3" />
                {city.state ? `${city.state}, ` : ''}{city.country}
              </p>
            </div>
            <div className="bg-gradient-to-br from-blue-500 to-purple-600 text-white px-3 py-1 rounded-full text-xs font-semibold">
              {city.cost_index < 50 ? 'Affordable' : city.cost_index < 75 ? 'Moderate' : 'Expensive'}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="flex items-center gap-2 text-sm">
              <Users className="h-4 w-4 text-blue-500" />
              <div>
                <div className="text-xs text-gray-500 dark:text-gray-400">Population</div>
                <div className="font-semibold text-gray-900 dark:text-white">
                  {city.population > 1000000
                    ? `${(city.population / 1000000).toFixed(1)}M`
                    : `${(city.population / 1000).toFixed(0)}K`}
                </div>
              </div>
            </div>

            <div className="flex items-center gap-2 text-sm">
              <DollarSign className="h-4 w-4 text-green-500" />
              <div>
                <div className="text-xs text-gray-500 dark:text-gray-400">Cost Index</div>
                <div className="font-semibold text-gray-900 dark:text-white">
                  {city.cost_index}
                </div>
              </div>
            </div>

            {city.climate && (
              <div className="flex items-center gap-2 text-sm col-span-2">
                <Cloud className="h-4 w-4 text-sky-500" />
                <div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">Climate</div>
                  <div className="font-semibold text-gray-900 dark:text-white">
                    {city.climate}
                  </div>
                </div>
              </div>
            )}
          </div>

          <div className="mt-4 pt-4 border-t border-gray-100 dark:border-gray-700">
            <div className="flex justify-between items-center text-sm">
              <span className="text-gray-500 dark:text-gray-400">Monthly rent (1br)</span>
              <span className="font-bold text-gray-900 dark:text-white">
                ${city.rent_1br_center.toLocaleString()}
              </span>
            </div>
          </div>

          <div className="mt-4">
            <span className="text-blue-600 dark:text-blue-400 font-semibold text-sm group-hover:translate-x-2 inline-block transition-transform">
              Explore →
            </span>
          </div>
        </div>
      </Link>
    </motion.div>
  );
}
