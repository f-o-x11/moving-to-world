'use client';

import { useState } from 'react';
import { City } from '@/types';
import { DollarSign, Home, Utensils, Car, Heart } from 'lucide-react';
import { motion } from 'framer-motion';

interface CostCalculatorProps {
  city: City;
}

export default function CostCalculator({ city }: CostCalculatorProps) {
  const [people, setPeople] = useState(1);
  const [bedroom, setBedroom] = useState(1);
  const [meals, setMeals] = useState(2);
  const [transport, setTransport] = useState('public');

  const calculateCosts = () => {
    const baseRent = bedroom === 1 ? city.rent_1br_center : city.rent_3br_center;
    const groceries = (city.monthly_cost_single * 0.3) * people;
    const dining = meals * 15 * 30 * (city.cost_index / 100);
    const transportCost = transport === 'public' ? 50 * (city.cost_index / 100) : 200 * (city.cost_index / 100);
    const utilities = 150 * (city.cost_index / 100);
    const entertainment = 200 * (city.cost_index / 100) * people;

    return {
      rent: Math.round(baseRent),
      groceries: Math.round(groceries),
      dining: Math.round(dining),
      transport: Math.round(transportCost),
      utilities: Math.round(utilities),
      entertainment: Math.round(entertainment),
    };
  };

  const costs = calculateCosts();
  const total = Object.values(costs).reduce((a, b) => a + b, 0);

  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl p-8 shadow-xl border border-gray-200 dark:border-gray-700">
      <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
        Cost of Living Calculator
      </h3>

      {/* Inputs */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Number of People
          </label>
          <input
            type="number"
            min="1"
            max="10"
            value={people}
            onChange={(e) => setPeople(parseInt(e.target.value) || 1)}
            className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 focus:ring-2 focus:ring-blue-500 focus:outline-none"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Bedrooms
          </label>
          <select
            value={bedroom}
            onChange={(e) => setBedroom(parseInt(e.target.value))}
            className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 focus:ring-2 focus:ring-blue-500 focus:outline-none"
          >
            <option value={1}>1 Bedroom</option>
            <option value={3}>3 Bedrooms</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Dining Out (per day)
          </label>
          <input
            type="number"
            min="0"
            max="10"
            value={meals}
            onChange={(e) => setMeals(parseInt(e.target.value) || 0)}
            className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 focus:ring-2 focus:ring-blue-500 focus:outline-none"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Transportation
          </label>
          <select
            value={transport}
            onChange={(e) => setTransport(e.target.value)}
            className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 focus:ring-2 focus:ring-blue-500 focus:outline-none"
          >
            <option value="public">Public Transit</option>
            <option value="car">Car/Taxi</option>
          </select>
        </div>
      </div>

      {/* Cost Breakdown */}
      <div className="space-y-4 mb-6">
        <CostItem icon={Home} label="Rent" amount={costs.rent} color="blue" />
        <CostItem icon={Utensils} label="Food & Groceries" amount={costs.groceries + costs.dining} color="green" />
        <CostItem icon={Car} label="Transportation" amount={costs.transport} color="purple" />
        <CostItem icon={DollarSign} label="Utilities" amount={costs.utilities} color="orange" />
        <CostItem icon={Heart} label="Entertainment" amount={costs.entertainment} color="pink" />
      </div>

      {/* Total */}
      <div className="pt-6 border-t border-gray-200 dark:border-gray-700">
        <div className="flex justify-between items-center">
          <span className="text-lg font-semibold text-gray-900 dark:text-white">
            Estimated Monthly Total
          </span>
          <motion.div
            key={total}
            initial={{ scale: 1.2 }}
            animate={{ scale: 1 }}
            className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent"
          >
            ${total.toLocaleString()}
          </motion.div>
        </div>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
          This is an estimate based on average costs in {city.name}
        </p>
      </div>
    </div>
  );
}

function CostItem({ icon: Icon, label, amount, color }: any) {
  const colors: any = {
    blue: 'text-blue-500',
    green: 'text-green-500',
    purple: 'text-purple-500',
    orange: 'text-orange-500',
    pink: 'text-pink-500',
  };

  return (
    <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
      <div className="flex items-center gap-3">
        <Icon className={`h-5 w-5 ${colors[color]}`} />
        <span className="font-medium text-gray-900 dark:text-white">{label}</span>
      </div>
      <span className="font-bold text-gray-900 dark:text-white">
        ${amount.toLocaleString()}
      </span>
    </div>
  );
}
