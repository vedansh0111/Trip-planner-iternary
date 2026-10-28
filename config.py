"""
Configuration and constants for Personalized Travel Itinerary Planner.
Platform ID: 6ac33976fb8fc7965cd9236d
Skill Wallet Capstone Project 4
"""

import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "trips.db"

# Platform Metadata
PLATFORM_ID = "6ac33976fb8fc7965cd9236d"
PROJECT_NAME = "Personalized Travel Itinerary Planner"
PROJECT_SUBTITLE = "AI-Powered SaaS Itinerary Architect with Geographic Clustering"
CAPSTONE_ID = "Skill Wallet Capstone Project 4"

# Currencies supported and approximate conversion rates to 1 USD
CURRENCIES = {
    "USD": {"symbol": "$", "name": "US Dollar", "rate_to_usd": 1.0},
    "EUR": {"symbol": "€", "name": "Euro", "rate_to_usd": 0.92},
    "GBP": {"symbol": "£", "name": "British Pound", "rate_to_usd": 0.79},
    "INR": {"symbol": "₹", "name": "Indian Rupee", "rate_to_usd": 83.5},
    "JPY": {"symbol": "¥", "name": "Japanese Yen", "rate_to_usd": 155.0},
    "AUD": {"symbol": "A$", "name": "Australian Dollar", "rate_to_usd": 1.52},
    "CAD": {"symbol": "C$", "name": "Canadian Dollar", "rate_to_usd": 1.37},
    "AED": {"symbol": "AED", "name": "UAE Dirham", "rate_to_usd": 3.67},
    "SGD": {"symbol": "S$", "name": "Singapore Dollar", "rate_to_usd": 1.35},
}

# Travel Vibes for Recommender and Filtering
VIBE_CATEGORIES = [
    "Beach & Coastal Relaxation",
    "Mountains & Alpine Serenity",
    "Cultural & Historic Heritage",
    "Urban Exploration & Skyline",
    "Nature, Safari & Wildlife",
    "Romantic & Scenic Getaway",
    "High-Adrenaline Adventure",
    "Food, Wine & Gastronomy",
]

# Budget Tiers
BUDGET_TIERS = {
    "Budget / Backpacker": {
        "daily_per_person_usd": 45,
        "description": "Hostels/budget guesthouses, street food, public transit, free walking tours",
        "badge_color": "#10b981",
    },
    "Moderate / Balanced": {
        "daily_per_person_usd": 130,
        "description": "3-4 star boutique hotels, local bistros, mix of taxis & metro, popular attractions",
        "badge_color": "#3b82f6",
    },
    "Luxury / Premium": {
        "daily_per_person_usd": 350,
        "description": "5-star luxury resorts, fine dining tasting menus, private chauffeur & VIP guides",
        "badge_color": "#8b5cf6",
    },
}

# Travel Parties
TRAVEL_PARTIES = {
    "Solo Explorer": {"multiplier": 1.0, "icon": "🎒"},
    "Couple / Romantic": {"multiplier": 1.9, "icon": "🥂"},
    "Family with Kids": {"multiplier": 3.2, "icon": "👨‍👩‍👧‍👦"},
    "Friends Group (3-4)": {"multiplier": 3.6, "icon": "👥"},
}

# Travel Paces
TRAVEL_PACES = {
    "Relaxed / Slow Travel": {
        "description": "1-2 main highlights daily, leisurely meals, ample downtime",
        "fatigue_tolerance": "high_buffer",
    },
    "Moderate / Balanced": {
        "description": "2-3 attractions per day, well-spaced coffee and transit breaks",
        "fatigue_tolerance": "standard",
    },
    "Fast-Paced / Packed": {
        "description": "Full day itineraries maximizing sights from sunrise to night",
        "fatigue_tolerance": "dense",
    },
}

# Interests list
INTEREST_OPTIONS = [
    "Food & Culinary Trails",
    "Adventure & Thrills",
    "History & Ancient Heritage",
    "Art, Museums & Architecture",
    "Nightlife, Rooftops & Social",
    "Nature, Lakes & Hiking",
    "Local Markets & Shopping",
    "Wellness, Spas & Yoga",
    "Photography & Scenic Viewpoints",
]

# Time Slots per Day
TIME_SLOTS = [
    "Morning Sightseeing",
    "Lunch Recommendation",
    "Afternoon Leisure & Culture",
    "Evening Dining & Entertainment",
]

# Custom Wanderlust Color Palette
THEME_COLORS = {
    "primary": "#E05A47",      # Terracotta / Sunset Orange
    "secondary": "#2A7B88",    # Aegean Deep Sea Teal
    "accent": "#F5A623",       # Golden Sun Amber
    "bg_light": "#FAF7F2",     # Warm Linen Sand
    "card_bg": "#FFFFFF",      # Crisp White
    "text_dark": "#1E293B",    # Dark Slate
    "text_muted": "#64748B",   # Slate Grey
    "border": "#E2E8F0",       # Light Border
    "success": "#10B981",      # Emerald Green
}
