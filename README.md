# 🧭 Personalized Travel Itinerary Planner
### Skill Wallet Capstone Project 4 | Platform ID: `6ac33976fb8fc7965cd9236d`

An enterprise-ready, AI-powered travel software-as-a-service (SaaS) application built with Python and Streamlit. The application generates mathematically optimized day-by-day vacation itineraries, clusters attractions geographically by neighborhood to eliminate transit fatigue, recommends vibe-matched destination cities, enables single-slot activity swapping, and provides 1-click offline PDF travel guide generation.

---

## 🌟 Key Features & Kanban Epics Coverage

1. **Configuration & User Preferences (Epic 3)**
   - Multi-provider AI interface supporting **Google Gemini** (`google-genai`), **Groq** (`groq`), and a **Zero-Dependency High-Fidelity Demo Mode** that works 100% offline without any API keys.
   - Comprehensive preference capture: Destination, Trip Duration (1–14 days), Dates, Budget Tiers (Budget, Moderate, Luxury), Travel Party dynamics, Travel Pace, and Multi-select Interests.
   - Multi-currency support (USD, EUR, GBP, INR, JPY, AUD, CAD, AED, SGD).

2. **Tab 1: Smart Destination Recommender (Epic 3)**
   - Vibe & mood-based destination matching (Beach, Mountains, Heritage, Urban, Wildlife, Romantic, Adventure).
   - Seasonality and budget alignment generating Top 3 curated destination cities with match scores, highlight tags, estimated daily budgets, and signature experiences.
   - 1-Click *"Plan This Destination"* quick-action button.

3. **Tab 2: Day-by-Day Clustered Itinerary Generator (Epic 4)**
   - **Geographic Clustering Engine**: Automatically groups attractions within adjacent neighborhoods on the same day to eliminate cross-city backtracking and travel fatigue.
   - **Anti-Transit Fatigue Score**: Computes transit efficiency percentages, route distances, and estimated hours saved.
   - **Sequential Structured Slots**: Morning Sightseeing, Lunch Recommendation with culinary notes, Afternoon Leisure & Culture, Evening Dining & Entertainment.
   - **Interactive Route Map**: PyDeck 3D Deck and Plotly route line maps displaying day routes and color-coded cluster stops.
   - **Dual-Currency Running Budget Tracker**: Itemized activity costs and cumulative budget comparison gauges.

4. **Tab 3: Vibe Customization & Dynamic Activity Swap (Epic 4)**
   - Modify targeted single slots (e.g. *"Swap museum for outdoor local artisan market"*, *"Find vegetarian lunch spot"*) without wiping or regenerating the rest of the multi-day plan.
   - Cluster preservation: Replacements remain within the same neighborhood cluster.

5. **Tab 4: Trip Management & Offline PDF Export (Epic 5)**
   - **Zero-Config Local SQLite Persistence (`trips.db`)**: Save trips, review trip history, reload saved trips into active session, and export/import JSON backups.
   - **ReportLab Offline Travel Guide PDF**: 1-click downloadable multi-page travel document with wanderlust styling, day tables, budget summaries, packing checklist, and emergency contact directory.

---

## 🏗️ Architecture & Project Structure

```
travel-itinerary-planner/
├── app.py                      # Main Streamlit SaaS application & CSS styling
├── config.py                   # Global constants, platform metadata, budget & currency tables
├── requirements.txt            # Streamlit Community Cloud dependencies
├── README.md                   # Documentation & deployment guide
├── trips.db                    # SQLite local database (auto-generated)
├── modules/
│   ├── __init__.py
│   ├── database.py             # SQLite persistence layer & JSON backup/restore
│   ├── llm_engine.py           # Unified LLM provider (Gemini, Groq, offline demo engine)
│   ├── recommender.py          # Tab 1: Smart Destination Recommender
│   ├── itinerary_generator.py  # Tab 2: Clustered itinerary & budget calculations
│   ├── activity_swapper.py     # Tab 3: Dynamic slot-level activity swapper
│   ├── pdf_exporter.py         # Tab 4: ReportLab wanderlust offline PDF generator
│   └── geo_utils.py            # Lat/Lon coordinates, clustering metrics & maps
└── tests/
    ├── __init__.py
    └── test_planner.py         # Comprehensive automated pytest test suite
```

---

## 🚀 Quickstart & Local Setup

### 1. Prerequisites
- Python 3.9+ (tested and verified on Python 3.13)
- No external database setup required (SQLite is built-in).

### 2. Run the Application
Open a terminal in this directory and run:

```bash
python -m streamlit run app.py
```

The app will launch in your browser at `http://localhost:8501`.

### 3. Run Automated Tests
```bash
python -m pytest tests/test_planner.py -v
```

---

## ☁️ 1-Click Cloud Deployment (Streamlit Community Cloud & Render)

### Streamlit Community Cloud
1. Push this repository to GitHub.
2. Visit [share.streamlit.io](https://share.streamlit.io) and click **"New app"**.
3. Select your repository, branch (`main`), and set **Main file path** to `app.py`.
4. (Optional) In **Advanced Settings > Secrets**, configure:
   ```toml
   GEMINI_API_KEY = "your-gemini-key"
   GROQ_API_KEY = "your-groq-key"
   ```
5. Click **Deploy!**

### Render (Web Service)
1. In `render.yaml` or Render dashboard, create a new **Web Service**.
2. **Environment:** Python
3. **Build Command:** `pip install -r requirements.txt`
4. **Start Command:** `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
