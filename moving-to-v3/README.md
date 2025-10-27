# Moving.to V3 - 10X Better 🚀

A modern, feature-rich city exploration and relocation planning platform built with Next.js 14, TypeScript, and Tailwind CSS.

## 🌟 What Makes V3 10X Better

### 🎨 **Modern Tech Stack**
- **Next.js 14** with App Router and Server Components
- **TypeScript** for type safety and better developer experience
- **Tailwind CSS** for beautiful, responsive design
- **Framer Motion** for smooth animations
- **Better-SQLite3** for fast server-side database queries
- **Lucide React** for modern, beautiful icons

### ⚡ **Performance Improvements**
- **Server-side search** - No more loading 260K line JSON files
- **API routes** for dynamic data fetching
- **Optimized database queries** with indexes
- **Server Components** for faster initial page loads
- **Progressive enhancement** with client components only where needed

### 🎯 **Advanced Features**

#### 1. **AI-Powered Recommendations**
- Smart city suggestions based on your preferences
- Climate, cost, and lifestyle matching
- Personalized scoring algorithm

#### 2. **Interactive City Comparison**
- Compare up to 4 cities side-by-side
- Visual cost comparisons
- Population, climate, and housing metrics

#### 3. **Cost of Living Calculator**
- Customizable based on your lifestyle
- Real-time cost estimates
- Breakdown by category (rent, food, transport, etc.)
- Dynamic updates with beautiful animations

#### 4. **Real Weather Integration**
- OpenWeatherMap API support
- Current weather and 7-day forecast
- Falls back to mock data when API key not provided

#### 5. **Beautiful UI/UX**
- Gradient backgrounds and modern design
- Smooth animations and transitions
- Dark mode support (via Tailwind)
- Mobile-first responsive design
- Glassmorphism effects
- Hover animations and micro-interactions

#### 6. **Instant Search**
- Server-side search API
- Sub-second response times
- Autocomplete with keyboard navigation
- Search across 32,496 cities

### 📊 **Data Coverage**
- **32,496 cities** across 195+ countries
- Real data from SQLite database
- Neighborhoods for major cities
- Cost of living metrics
- Climate information
- Timezone, language, and currency data

## 🚀 Getting Started

### Prerequisites
- Node.js 18+
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

Open [http://localhost:3000](http://localhost:3000) to see the result.

### Optional: Add Weather API

To enable real weather data:

1. Get a free API key from [OpenWeatherMap](https://openweathermap.org/api)
2. Create `.env.local` file:
```bash
OPENWEATHER_API_KEY=your_api_key_here
```

## 🏗️ Project Structure

```
moving-to-v3/
├── src/
│   ├── app/                    # Next.js App Router pages
│   │   ├── api/               # API routes
│   │   │   ├── search/        # Search API
│   │   │   ├── cities/        # Cities filtering API
│   │   │   ├── weather/       # Weather data API
│   │   │   └── recommendations/ # AI recommendations API
│   │   ├── [country]/[state]/[city]/ # Dynamic city pages
│   │   └── page.tsx           # Homepage
│   ├── components/            # React components
│   │   ├── SearchBar.tsx      # Instant search component
│   │   ├── CityCard.tsx       # City display card
│   │   ├── CityComparison.tsx # City comparison tool
│   │   └── CostCalculator.tsx # Cost of living calculator
│   ├── lib/                   # Utilities
│   │   └── db.ts             # Database queries
│   └── types/                # TypeScript types
│       └── index.ts          # Shared types
├── moving_to.db              # SQLite database
└── city-database.json        # Fallback data
```

## 🎨 Key Features Breakdown

### Homepage
- **Stunning hero section** with gradient backgrounds
- **Live search** with instant results
- **Featured cities** carousel with random cities
- **Quick stats** showing total coverage
- **Responsive design** that works on all devices

### City Pages
- **Comprehensive overview** with all key metrics
- **Housing costs** breakdown
- **Neighborhood explorer** with descriptions and tags
- **Interactive cost calculator**
- **Quick info sidebar** with sticky positioning
- **Breadcrumb navigation**

### API Endpoints

#### `/api/search?q=query&limit=20`
Search cities by name, country, or state

#### `/api/cities?type=random&count=6`
Get random cities for featured sections

#### `/api/cities?minPopulation=100000&maxCost=75`
Filter cities by various criteria

#### `/api/weather?lat=40.7128&lon=-74.0060`
Get weather data for coordinates

#### `/api/recommendations` (POST)
Get AI-powered city recommendations based on preferences

## 🔧 Technologies Used

- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first CSS framework
- **Framer Motion** - Animation library
- **Better-SQLite3** - Fast SQLite database
- **Lucide React** - Icon library
- **SWR** - Data fetching (available for client components)
- **Axios** - HTTP client

## 📈 Comparison: V2 vs V3

| Feature | V2 (Static) | V3 (Modern) |
|---------|-------------|-------------|
| Tech Stack | Static HTML | Next.js 14 + TypeScript |
| Search | 260KB JSON file | Server-side API |
| Performance | Slow initial load | Fast SSR + streaming |
| UI Framework | Vanilla CSS | Tailwind CSS + Framer Motion |
| Animations | Basic CSS | Advanced Framer Motion |
| API | None | Full REST API |
| Recommendations | None | AI-powered matching |
| Comparison Tool | None | Interactive 4-city compare |
| Cost Calculator | None | Dynamic calculator |
| Weather Data | Generic labels | Real API integration |
| Mobile UX | Basic responsive | Mobile-first design |
| Dark Mode | None | Full support |

## 🎯 Future Enhancements

- [ ] User accounts and saved cities
- [ ] Community reviews and ratings
- [ ] Real rental listings integration
- [ ] Job postings integration
- [ ] Visa requirement checker
- [ ] Moving timeline planner
- [ ] Photo galleries from Unsplash
- [ ] Map view with clustering
- [ ] Multi-language support
- [ ] PWA capabilities
- [ ] Offline mode

## 📝 License

MIT License - feel free to use this project for your own purposes!

## 🙏 Acknowledgments

- City data from various open sources
- Weather data from OpenWeatherMap
- Icons from Lucide
- Built with Next.js and Vercel

---

**Made with ❤️ for people exploring the world**

Data covering 32,496 cities across 195+ countries
