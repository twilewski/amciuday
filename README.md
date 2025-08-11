# 🍳 Amciu Day - Full-Stack Recipe Discovery App

A modern full-stack application that helps you discover your perfect meal through an interactive spinning wheel experience.

## 🚀 Live Demo

- **Frontend**: https://amciuday-frontend.onrender.com
- **Backend API**: https://amciuday-backend.onrender.com
- **API Docs**: https://amciuday-backend.onrender.com/docs

## 🌟 Features

- **🎡 Spin Wheel**: Colorful spinning wheel with 4-second deterministic animation
- **🍽️ Recipe Discovery**: Smart recipe matching based on meal type and ingredient preferences
- **❤️ Ingredient Management**: Add ingredients to liked/banned lists with Polish normalization
- **📱 Mobile-First**: Designed for Android tablets via Capacitor
- **📚 History**: Track all previous spins with filtering by meal type and date
- **🌐 WebView Integration**: Open recipe sources in-app
- **🇵🇱 Polish Language**: Complete Polish localization throughout

## 🏗️ Project Structure

```
amciu-day/
├── apps/
│   ├── backend/           # FastAPI + SQLModel + SQLite backend
│   │   ├── app/
│   │   │   ├── core/      # Settings and configuration
│   │   │   ├── models/    # SQLModel database models
│   │   │   ├── services/  # Business logic and filtering
│   │   │   ├── routers/   # API endpoints
│   │   │   └── main.py    # FastAPI application
│   │   └── tests/         # Comprehensive test suite
│   └── frontend/          # Vue 3 + Vite + Pinia + Tailwind frontend
│       ├── src/
│       │   ├── components/ # Vue components (SpinWheel, RecipeCard, etc.)
│       │   ├── views/     # Page components (Home, History, Ingredients)
│       │   ├── stores/    # Pinia state management
│       │   └── api/       # Typed API client
│       └── capacitor.config.ts
├── packages/
│   └── shared/            # Shared types and utilities
│       ├── types.ts       # TypeScript interfaces
│       ├── normalization.py # Python ingredient normalization
│       └── ingredients.json  # Polish synonym mapping
├── tools/
│   └── seed/              # Recipe generation and seeding
│       ├── scrape.py      # Sample recipe generator
│       └── out/recipes.json # Generated recipe data
└── Makefile               # Development workflow automation
```

## 🚀 Quick Start

### Prerequisites

- **Node.js 18+** and npm
- **Python 3.11+**
- **Android Studio** (for APK builds)

### Installation

```bash
# Install all dependencies
make install

# Or manually:
cd apps/backend && python -m venv venv && . venv/bin/activate && pip install -r requirements.txt
cd apps/frontend && npm install
```

### Development

```bash
# Start backend (Terminal 1)
make dev-backend

# Start frontend (Terminal 2) 
make dev-frontend

# Seed database with sample recipes
make seed
```

**Access Points:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Building for Android

```bash
# Build and open Android Studio
make build-apk

# Or manually:
cd apps/frontend
npm run build
npx cap sync android
npx cap open android
```

## 🔧 API Endpoints

### Recipes
- `GET /api/recipes/random` - Get random recipe matching criteria
- `GET /api/recipes/{id}` - Get recipe with ingredients

### Ingredients  
- `GET/POST/DELETE /api/ingredients/liked` - Manage liked ingredients
- `GET/POST/DELETE /api/ingredients/banned` - Manage banned ingredients

### History
- `GET /api/history/` - Get spin history with optional filters
- `DELETE /api/history/` - Clear all history

### Seed (Development)
- `POST /api/import/seed` - Import recipe data from JSON

## 🎮 Recipe Filtering Algorithm

The core algorithm filters recipes based on:

1. **Meal Type**: breakfast, lunch, snack, dinner
2. **Banned Ingredients**: Recipes containing banned ingredients are excluded
3. **Extra Ingredients**: 
   - If checkbox OFF: Only recipes with 0 ingredients outside liked list
   - If checkbox ON: Recipes with 0-1 ingredients outside liked list
4. **Recent Filter**: Optionally hide recently spun recipes (last 5 for each meal type)

## 📊 Database Schema

- **Recipe**: title, source, url, meal_type, time_minutes, image_url, tags, steps_excerpt
- **Ingredient**: name, normalized (for Polish deduplication)
- **RecipeIngredient**: Links recipes to ingredients with amounts
- **Preferences**: User's liked_ids and banned_ids (JSON arrays)
- **SpinHistory**: Tracks all spins with timestamp and settings

## 🧪 Development & Testing

```bash
# Backend
cd apps/backend
pytest                    # Run tests (80%+ coverage required)
ruff check .              # Lint code
black .                   # Format code
mypy .                    # Type check

# Frontend  
cd apps/frontend
npm run test              # Run tests
npm run lint              # Lint code
npm run format            # Format code
npm run type-check        # Type check

# All tests
make test
```

## ⚙️ Configuration

### Backend (.env)
```bash
DB_PATH=./data/amciuday.db
SEED_JSON=./tools/seed/out/recipes.json  
LOG_LEVEL=INFO
```

### Frontend
- Vite proxy forwards `/api/*` to backend
- Capacitor config in `capacitor.config.ts`

## 🌍 Ingredient Normalization

The app normalizes ingredient names using:
- **Lowercase and trim** whitespace
- **Synonym mapping** (pomidory → pomidor)  
- **Basic Polish singularization** rules
- **Shared logic** between TypeScript and Python

**Example synonyms:**
```json
{
  "pomidor": ["pomidory", "pomidora", "pomidorów"],
  "cebula": ["cebule", "cebuli", "cebulę"],
  "czosnek": ["ząbek czosnku", "ząbki czosnku"]
}
```

## 📋 Sample Data

The app includes 20 carefully curated Polish recipes:
- **5 breakfast recipes**: Naleśniki, owsianka, jajecznica, tosty, pancakes
- **5 lunch recipes**: Kotlet schabowy, pierogi, gulasz, ryba, kotlety mielone  
- **5 snack recipes**: Kanapki, smoothie, muffiny, hummus, ciasteczka
- **5 dinner recipes**: Sałatka grecka, zupa krem, wrap, risotto, łosoś

Each recipe includes:
- Polish titles and descriptions
- Realistic cooking times
- Appropriate meal type classification
- Traditional Polish ingredients
- Source attribution

## 🎨 Design System

**Child-Friendly Colors:**
- Primary: Bright orange (`#f97316`)
- Secondary: Sky blue (`#0ea5e9`)
- Success: Bright green (`#22c55e`)
- Warning: Bright yellow (`#f59e0b`)

**Key UI Components:**
- **SpinWheel**: 12-sector colorful wheel with easing animation
- **MealSelector**: Grid of meal types with emojis
- **RecipeCard**: Image, title, time, ingredients, source
- **HistoryView**: Filterable list with "choose again" functionality

## 📱 Mobile Features

**Capacitor Integration:**
- Native browser for recipe viewing
- Hardware back button support
- Splash screen with app branding
- Optimized for tablet screens

## 🏭 Deployment

### Backend Options
- **Development**: `uvicorn app.main:app --reload`
- **Production**: Gunicorn with multiple workers
- **Docker**: Standard Python container setup
- **Database**: SQLite for simplicity, PostgreSQL for scale

### Frontend Options
- **Development**: Vite dev server with HMR
- **Production**: Static files served by any web server
- **Mobile**: APK via Android Studio or Gradle

## 🤝 Contributing

1. **Code Style**: Follow existing patterns (ESLint/Prettier for TS, Ruff/Black for Python)
2. **Testing**: Add tests for new features (80%+ coverage required)
3. **Documentation**: Update README for significant changes
4. **Commits**: Use conventional commit format

## 📄 License

MIT License - see LICENSE file for details.

---

**Built with ❤️ for families who love cooking together!**