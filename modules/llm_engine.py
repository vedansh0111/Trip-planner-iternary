"""
Multi-provider LLM Engine supporting Google Gemini, Groq, and
a high-fidelity offline Demo Mode with curated travel intelligence.
"""

import os
import json
import re
from typing import Dict, Any, Optional

# Pre-packaged rich destination clusters for top global and Indian tourist hubs
DESTINATION_KNOWLEDGE_BASE = {
    "paris": {
        "currency": "EUR",
        "symbol": "€",
        "zones": [
            {
                "cluster_name": "Historic Île de la Cité & Latin Quarter",
                "center_offset": (0.002, 0.001),
                "theme": "Gothic Architecture, Historic Alleys & Bookshops",
                "morning": {
                    "title": "Sainte-Chapelle & Notre-Dame Forecourt",
                    "description": "Marvel at the 13th-century stained glass windows of Sainte-Chapelle and explore the restored Gothic majesty of Notre-Dame Cathedral.",
                    "time": "09:00 - 12:00",
                    "cost_usd": 15,
                    "transit_tip": "Metro Line 4 to Cité station (5 min walk)",
                    "category": "Sightseeing",
                    "tags": ["Gothic", "Heritage", "Iconic"]
                },
                "lunch": {
                    "title": "Le Comptoir du Relais (Saint-Germain)",
                    "description": "Classic Parisian bistro lunch with duck confit, fresh baguettes, and artisanal goat cheese salad.",
                    "time": "12:30 - 14:00",
                    "cost_usd": 32,
                    "transit_tip": "7 min scenic stroll across Pont Saint-Michel",
                    "category": "Culinary",
                    "tags": ["Bistro", "LocalFlavors", "OutdoorSeating"]
                },
                "afternoon": {
                    "title": "Shakespeare and Company & Luxembourg Gardens",
                    "description": "Browse the legendary English bookstore, then relax beside the Medici Fountain among chestnut trees.",
                    "time": "14:30 - 17:30",
                    "cost_usd": 0,
                    "transit_tip": "Short 10 min walk down Rue Soufflot",
                    "category": "Culture & Nature",
                    "tags": ["Books", "Gardens", "Relaxed"]
                },
                "evening": {
                    "title": "Seine Sunset Cruise & Latin Quarter Jazz Cave",
                    "description": "Glide under Pont Neuf at golden hour on a river cruise, followed by live jazz at Caveau de la Huchette.",
                    "time": "18:30 - 22:30",
                    "cost_usd": 40,
                    "transit_tip": "Board at Pont Neuf pier (5 min walk)",
                    "category": "Nightlife & Dining",
                    "tags": ["RiverCruise", "Jazz", "Romance"]
                }
            },
            {
                "cluster_name": "Louvre, Palais-Royal & Tuileries Garden",
                "center_offset": (0.005, -0.015),
                "theme": "World-Class Fine Arts & Grand Arcades",
                "morning": {
                    "title": "Musée du Louvre & Cour Napoléon",
                    "description": "Skip-the-line guided exploration of the Mona Lisa, Winged Victory of Samothrace, and Venus de Milo.",
                    "time": "09:00 - 12:30",
                    "cost_usd": 22,
                    "transit_tip": "Metro Palais-Royal Musée du Louvre",
                    "category": "Sightseeing",
                    "tags": ["WorldHeritage", "FineArt", "MustSee"]
                },
                "lunch": {
                    "title": "Café Marly overlooking the Glass Pyramid",
                    "description": "Chic terrace dining featuring gourmet croque-monsieur and seasonal French patisseries.",
                    "time": "12:45 - 14:15",
                    "cost_usd": 45,
                    "transit_tip": "Directly under the Louvre Richelieu wing",
                    "category": "Culinary",
                    "tags": ["View", "Gourmet", "Chic"]
                },
                "afternoon": {
                    "title": "Palais-Royal Columns & Musée de l'Orangerie",
                    "description": "Stroll Buren's black-and-white columns and admire Monet's monumental Water Lilies murals in an oval sanctuary.",
                    "time": "14:45 - 17:30",
                    "cost_usd": 14,
                    "transit_tip": "10 min walk across the Jardin des Tuileries",
                    "category": "Culture",
                    "tags": ["Impressionism", "Monet", "Architecture"]
                },
                "evening": {
                    "title": "Dinner at Le Grand Véfour & Rue de Rivoli Walk",
                    "description": "Historic neo-classical culinary dining followed by a moonlit walk along the illuminated arcades.",
                    "time": "19:00 - 22:30",
                    "cost_usd": 75,
                    "transit_tip": "5 min walk from Palais-Royal",
                    "category": "Dining",
                    "tags": ["HauteCuisine", "Historic", "Atmospheric"]
                }
            },
            {
                "cluster_name": "Montmartre & Sacré-Cœur Bohemian Heights",
                "center_offset": (0.025, 0.002),
                "theme": "Artistic Alleys, Windmills & Panoramic Cityscape",
                "morning": {
                    "title": "Sacré-Cœur Basilica & Place du Tertre",
                    "description": "Ascend the Montmartre butte for sunrise vistas over all of Paris and meet open-air portrait painters.",
                    "time": "09:00 - 12:00",
                    "cost_usd": 0,
                    "transit_tip": "Funiculaire de Montmartre or 222 steps",
                    "category": "Sightseeing",
                    "tags": ["Panoramas", "Artists", "Sacred"]
                },
                "lunch": {
                    "title": "La Maison Rose & Vineyard Bistro",
                    "description": "Picturesque pink facade offering rustic regional French fare and cider.",
                    "time": "12:30 - 14:00",
                    "cost_usd": 28,
                    "transit_tip": "4 min walk along Rue de l'Abreuvoir",
                    "category": "Culinary",
                    "tags": ["Iconic", "Rustic", "Photogenic"]
                },
                "afternoon": {
                    "title": "Musée de Montmartre & Renoir Gardens",
                    "description": "Visit the actual studios where Renoir painted the 'Moulin de la Galette' surrounded by lush vineyard slopes.",
                    "time": "14:30 - 17:30",
                    "cost_usd": 15,
                    "transit_tip": "3 min walk along Rue Cortot",
                    "category": "Culture",
                    "tags": ["Renoir", "Vineyard", "SecretParis"]
                },
                "evening": {
                    "title": "Moulin Rouge Cabaret & Pigalle Cocktail Bar",
                    "description": "Iconic world-famous feather-and-rhinestone cabaret spectacle followed by artisan craft cocktails.",
                    "time": "19:30 - 23:00",
                    "cost_usd": 95,
                    "transit_tip": "12 min downhill walk via Rue Lepic",
                    "category": "Nightlife",
                    "tags": ["Cabaret", "Show", "Glamour"]
                }
            }
        ]
    },
    "tokyo": {
        "currency": "JPY",
        "symbol": "¥",
        "zones": [
            {
                "cluster_name": "Asakusa & Ueno Cultural Heartland",
                "center_offset": (0.035, 0.045),
                "theme": "Ancient Temples, Traditional Crafts & Lotus Ponds",
                "morning": {
                    "title": "Senso-ji Temple & Nakamise-dori",
                    "description": "Pass through the Thunder Gate (Kaminarimon) and burn incense at Tokyo's oldest Buddhist temple.",
                    "time": "08:30 - 11:30",
                    "cost_usd": 0,
                    "transit_tip": "Ginza Line to Asakusa Station",
                    "category": "Sightseeing",
                    "tags": ["Buddhist", "OldTokyo", "EdoHeritage"]
                },
                "lunch": {
                    "title": "Asakusa Imahan Sukiyaki & Tempura",
                    "description": "Savory thinly sliced Wagyu beef cooked in sweet soy broth with hand-dipped raw egg.",
                    "time": "12:00 - 13:30",
                    "cost_usd": 38,
                    "transit_tip": "6 min walk west from Senso-ji",
                    "category": "Culinary",
                    "tags": ["Wagyu", "Traditional", "MichelinGuide"]
                },
                "afternoon": {
                    "title": "Tokyo National Museum & Ueno Park",
                    "description": "Explore samurai armor, ukiyo-e woodblock prints, and national treasures inside Ueno's grand museum.",
                    "time": "14:00 - 17:00",
                    "cost_usd": 12,
                    "transit_tip": "15 min walk or 4 min train on Ginza Line to Ueno",
                    "category": "Culture",
                    "tags": ["Samurai", "NationalTreasure", "Zen"]
                },
                "evening": {
                    "title": "Ameyoko Yokocho Market & Yakitori Under Tracks",
                    "description": "Bustling open-air post-war market alley filled with sizzling charcoal-grilled chicken skewers and cold draft beer.",
                    "time": "17:30 - 21:00",
                    "cost_usd": 25,
                    "transit_tip": "Adjacent to JR Ueno Station south exit",
                    "category": "Dining & Nightlife",
                    "tags": ["StreetFood", "Yakitori", "Vibrant"]
                }
            },
            {
                "cluster_name": "Shibuya & Harajuku Youth Innovation & Shrines",
                "center_offset": (-0.015, -0.045),
                "theme": "Neon Crossings, Forest Sanctuaries & Futuristic Fashion",
                "morning": {
                    "title": "Meiji Jingu Shinto Shrine & Evergreen Forest",
                    "description": "Step into 170 acres of tranquil sacred woodland and pass through the towering 12-meter cypress Torii gate.",
                    "time": "09:00 - 11:30",
                    "cost_usd": 0,
                    "transit_tip": "JR Yamanote Line to Harajuku Station",
                    "category": "Sightseeing",
                    "tags": ["Shinto", "ForestTranquility", "Sacred"]
                },
                "lunch": {
                    "title": "Afuri Harajuku Yuzu Ramen",
                    "description": "Signature light chicken dashi broth infused with fragrant Japanese yuzu citrus and tender chashu pork.",
                    "time": "12:00 - 13:30",
                    "cost_usd": 15,
                    "transit_tip": "5 min walk from Harajuku station",
                    "category": "Culinary",
                    "tags": ["Ramen", "CraftBroth", "QuickBite"]
                },
                "afternoon": {
                    "title": "Takeshita Street & Shibuya Sky Observation Deck",
                    "description": "Experience pop-culture boutiques, followed by an open-air 360-degree rooftop view over Shibuya Crossing.",
                    "time": "14:00 - 17:30",
                    "cost_usd": 22,
                    "transit_tip": "12 min walk or 1 stop JR train to Shibuya",
                    "category": "Culture & Sights",
                    "tags": ["Skyline", "PopCulture", "Futuristic"]
                },
                "evening": {
                    "title": "Shibuya Scramble Crossing & Nonbei Yokocho Izakayas",
                    "description": "Watch thousands cross the neon intersection in unison, then retreat to historic lantern-lit micro bars.",
                    "time": "18:00 - 22:00",
                    "cost_usd": 35,
                    "transit_tip": "Directly outside Shibuya Hachiko Exit",
                    "category": "Nightlife",
                    "tags": ["NeonTokyo", "Izakaya", "IconicCrossing"]
                }
            }
        ]
    },
    "jaipur": {
        "currency": "INR",
        "symbol": "₹",
        "zones": [
            {
                "cluster_name": "Pink City Royal Walled Enclave",
                "center_offset": (0.005, 0.002),
                "theme": "Maharaja Palaces, Astronomical Marvels & Bazaars",
                "morning": {
                    "title": "Hawa Mahal (Palace of Winds) & City Palace",
                    "description": "Admire the 953 honeycomb sandstone windows and royal museum collections of royal textiles and armor.",
                    "time": "09:00 - 12:30",
                    "cost_usd": 12,
                    "transit_tip": "E-rickshaw to Badi Chaupar (5 min)",
                    "category": "Sightseeing",
                    "tags": ["Palace", "RoyalHeritage", "PinkCity"]
                },
                "lunch": {
                    "title": "LMB (Laxmi Misthan Bhandar) Johari Bazar",
                    "description": "Heritage Rajasthani Royal Thali with Dal Baati Churma, Ker Sangri, and Ghewar sweet.",
                    "time": "12:45 - 14:15",
                    "cost_usd": 15,
                    "transit_tip": "3 min walk into Johari Bazaar",
                    "category": "Culinary",
                    "tags": ["RajasthaniThali", "Heritage", "Vegetarian"]
                },
                "afternoon": {
                    "title": "Jantar Mantar UNESCO Observatory & Johari Bazaar",
                    "description": "Inspect the world's largest stone sundial and shop for authentic block-print textiles and blue pottery.",
                    "time": "14:45 - 17:30",
                    "cost_usd": 8,
                    "transit_tip": "5 min walk from City Palace",
                    "category": "Culture & Shopping",
                    "tags": ["UNESCO", "Astronomy", "Handicrafts"]
                },
                "evening": {
                    "title": "Rooftop Folk Dance & Dinner at Wind View Cafe",
                    "description": "Watch the sunset illuminate the Hawa Mahal facade while sipping spiced masala chai and dining on kebabs.",
                    "time": "18:00 - 21:30",
                    "cost_usd": 20,
                    "transit_tip": "Opposite Hawa Mahal facade",
                    "category": "Dining & Culture",
                    "tags": ["Rooftop", "FolkMusic", "SunsetView"]
                }
            },
            {
                "cluster_name": "Amer Fort & Jal Mahal Lakeside Foothills",
                "center_offset": (0.085, 0.065),
                "theme": "Rajput Mountain Fortresses & Mirror Halls",
                "morning": {
                    "title": "Amer (Amber) Fort & Sheesh Mahal (Mirror Palace)",
                    "description": "Explore the majestic hilltop citadel with ramparts overlooking Maota Lake and opulent glass mosaic halls.",
                    "time": "08:30 - 12:30",
                    "cost_usd": 14,
                    "transit_tip": "Auto-rickshaw or taxi north along Amer Road (25 min)",
                    "category": "Sightseeing",
                    "tags": ["Fortress", "Mirrors", "Panoramic"]
                },
                "lunch": {
                    "title": "1135 AD Fine Royal Dining",
                    "description": "Aristocratic dining room inside the fort walls serving saffron biryani and regal curries on silver platters.",
                    "time": "12:45 - 14:15",
                    "cost_usd": 35,
                    "transit_tip": "Located inside Amer Fort courtyard",
                    "category": "Culinary",
                    "tags": ["FineDining", "Regal", "HistoricAmbience"]
                },
                "afternoon": {
                    "title": "Anokhi Museum of Hand Printing & Jaigarh Cannon",
                    "description": "Live demonstration of traditional block-printing inside a restored haveli and the world's largest wheeled cannon.",
                    "time": "14:30 - 17:00",
                    "cost_usd": 6,
                    "transit_tip": "10 min drive up the ridge",
                    "category": "Culture & Craft",
                    "tags": ["Textiles", "Artisan", "HiddenGem"]
                },
                "evening": {
                    "title": "Jal Mahal (Water Palace) Twilight Promenade",
                    "description": "Stroll the lit lakefront promenade as the submerged 18th-century palace glows across the water.",
                    "time": "17:30 - 20:30",
                    "cost_usd": 5,
                    "transit_tip": "15 min drive south towards city center",
                    "category": "Evening Sights",
                    "tags": ["LakeView", "Romantic", "Photography"]
                }
            }
        ]
    }
}


def sanitize_json_response(raw_text: str) -> str:
    """Strips markdown code fences and returns clean JSON string."""
    cleaned = re.sub(r"^```(?:json)?\s*", "", raw_text.strip(), flags=re.MULTILINE)
    cleaned = re.sub(r"\s*```$", "", cleaned.strip(), flags=re.MULTILINE)
    # Find outer bracket/brace
    start_brace = cleaned.find("{")
    start_bracket = cleaned.find("[")
    
    if start_brace != -1 and (start_bracket == -1 or start_brace < start_bracket):
        end_brace = cleaned.rfind("}")
        if end_brace != -1:
            return cleaned[start_brace:end_brace + 1]
    elif start_bracket != -1:
        end_bracket = cleaned.rfind("]")
        if end_bracket != -1:
            return cleaned[start_bracket:end_bracket + 1]
            
    return cleaned


def generate_completion(
    prompt: str,
    system_prompt: str = "",
    provider: str = "demo",
    api_key: str = "",
    model_name: str = ""
) -> str:
    """
    Unified LLM invocation function supporting Gemini, Groq, and fallback Demo Mode.
    """
    provider_clean = (provider or "demo").lower()
    
    if provider_clean == "gemini" and api_key:
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            target_model = model_name or "gemini-2.5-flash"
            contents = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            response = client.models.generate_content(
                model=target_model,
                contents=contents
            )
            if response and response.text:
                return response.text
        except Exception as e:
            print(f"Gemini API error: {e}. Falling back to high-fidelity demo engine.")

    elif provider_clean == "groq" and api_key:
        try:
            from groq import Groq
            client = Groq(api_key=api_key)
            target_model = model_name or "llama-3.3-70b-versatile"
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            completion = client.chat.completions.create(
                model=target_model,
                messages=messages,
                temperature=0.7,
                max_tokens=4000,
            )
            if completion.choices and completion.choices[0].message.content:
                return completion.choices[0].message.content
        except Exception as e:
            print(f"Groq API error: {e}. Falling back to high-fidelity demo engine.")

    # High-Fidelity Demo Mode Engine
    return generate_demo_response(prompt)


def generate_demo_response(prompt: str) -> str:
    """
    Procedural intelligent generator that constructs realistic responses
    for destination recommendations, itinerary plans, and activity swaps.
    """
    prompt_lower = prompt.lower()
    
    # 1. Recommendation Request check
    if "recommend top 3 matching cities" in prompt_lower or "destination recommender" in prompt_lower:
        return generate_demo_recommendations(prompt)
        
    # 2. Activity Swap Request check
    if "swap" in prompt_lower or "modify slot" in prompt_lower or "dynamic activity swap" in prompt_lower:
        return generate_demo_activity_swap(prompt)
        
    # 3. Default: Itinerary Generation Request
    return generate_demo_itinerary(prompt)


def generate_demo_recommendations(prompt: str) -> str:
    """Generates 3 tailored destinations based on prompt preferences."""
    # Vibe and budget heuristic matching
    prompt_lower = prompt.lower()
    
    if "beach" in prompt_lower or "coastal" in prompt_lower or "relaxation" in prompt_lower:
        destinations = [
            {
                "city": "Bali",
                "country": "Indonesia",
                "match_score": 97,
                "vibe_tags": ["#TropicalBeaches", "#SpiritualSanctuaries", "#SurfingParadise"],
                "best_season": "April to October (Dry Sun Season)",
                "estimated_daily_budget_usd": 65,
                "why_it_matches": "World-class surf breaks, cliffside temple sunsets at Uluwatu, and serene bamboo yoga retreats tailored for relaxing.",
                "must_experience": "Uluwatu Sunset Kecak Fire Dance followed by Jimbaran candlelit beach seafood dinner."
            },
            {
                "city": "Goa",
                "country": "India",
                "match_score": 94,
                "vibe_tags": ["#GoldenSands", "#PortugueseHeritage", "#BeachShacks"],
                "best_season": "November to March (Balmy Coastal Breeze)",
                "estimated_daily_budget_usd": 50,
                "why_it_matches": "Pristine South Goa palm beaches, vibrant coastal flea markets, and mouthwatering butter garlic prawns with feni.",
                "must_experience": "Sunset dolphin sail at Palolem Beach and heritage walk through Fontainhas Latin Quarter."
            },
            {
                "city": "Barcelona",
                "country": "Spain",
                "match_score": 91,
                "vibe_tags": ["#MediterraneanVibe", "#GaudíMasterpieces", "#SeasideTapas"],
                "best_season": "May to September (Warm Sun & Sea Festivals)",
                "estimated_daily_budget_usd": 120,
                "why_it_matches": "Unique fusion of city architecture, sun-drenched Barceloneta beach clubs, and seaside seafood paella.",
                "must_experience": "Early morning visit to Sagrada Família followed by paddleboarding at sunset on Bogatell Beach."
            }
        ]
    elif "mountain" in prompt_lower or "adventure" in prompt_lower or "nature" in prompt_lower:
        destinations = [
            {
                "city": "Interlaken & Swiss Alps",
                "country": "Switzerland",
                "match_score": 98,
                "vibe_tags": ["#AlpinePeaks", "#GlacialLakes", "#Skydiving"],
                "best_season": "June to September (Hiking) or Dec-March (Snow Sports)",
                "estimated_daily_budget_usd": 190,
                "why_it_matches": "Surrounded by the Jungfrau, Eiger, and Monch mountains with crystal turquoise glacier lakes and paragliding.",
                "must_experience": "Cogwheel railway journey up to Jungfraujoch 'Top of Europe' and panoramic cliff walk at First."
            },
            {
                "city": "Reykjavik & Golden Circle",
                "country": "Iceland",
                "match_score": 95,
                "vibe_tags": ["#NorthernLights", "#Geysers&Waterfalls", "#GeothermalLagoons"],
                "best_season": "Sept to April (Auroras) or June-August (Midnight Sun)",
                "estimated_daily_budget_usd": 160,
                "why_it_matches": "Otherworldly volcanic terrain, steaming mineral spas, erupting geysers, and glacier hikes.",
                "must_experience": "Soaking in Blue Lagoon silica waters under the arctic sky and hiking behind Seljalandsfoss waterfall."
            },
            {
                "city": "Queenstown",
                "country": "New Zealand",
                "match_score": 93,
                "vibe_tags": ["#AdventureCapital", "#MilfordSoundFjords", "#LordOfTheRings"],
                "best_season": "December to March (Summer Adventure)",
                "estimated_daily_budget_usd": 140,
                "why_it_matches": "Epic alpine adventure capital with bungee jumping, jet boating on Shotover river, and fjord cruises.",
                "must_experience": "Scenic helicopter landing on the Remarkables and cruise through majestic Milford Sound."
            }
        ]
    elif "cultural" in prompt_lower or "history" in prompt_lower or "heritage" in prompt_lower:
        destinations = [
            {
                "city": "Rome",
                "country": "Italy",
                "match_score": 99,
                "vibe_tags": ["#EternalCity", "#ColosseumGladiators", "#VaticanMuseums"],
                "best_season": "April to June & Sept to October (Mild & Breezy)",
                "estimated_daily_budget_usd": 135,
                "why_it_matches": "Over 2,800 years of living history, ancient amphitheaters, fountain piazzas, and mouth-watering cacio e pepe.",
                "must_experience": "Moonlight Colosseum tour followed by tossing a coin into the Trevi Fountain."
            },
            {
                "city": "Kyoto",
                "country": "Japan",
                "match_score": 96,
                "vibe_tags": ["#BambooGroves", "#GoldenPavilion", "#GeishaTradition"],
                "best_season": "March to May (Cherry Blossoms) or Oct-Nov (Autumn Foliage)",
                "estimated_daily_budget_usd": 115,
                "why_it_matches": "Over 1,000 Buddhist temples, meditative rock gardens, matcha tea ceremonies, and vermilion shrine gates.",
                "must_experience": "Walking through the thousands of Torii gates at Fushimi Inari Taisha at dawn."
            },
            {
                "city": "Jaipur",
                "country": "India",
                "match_score": 93,
                "vibe_tags": ["#PinkCityForts", "#RoyalPalaces", "#ArtisanalBazaars"],
                "best_season": "October to March (Pleasant Sunny Days)",
                "estimated_daily_budget_usd": 45,
                "why_it_matches": "Regal Rajput citadels, Sheesh Mahal mirror palaces, astronomy monuments, and colorful block-print textiles.",
                "must_experience": "Sunset tea overlooking Amer Fort ramparts and exploring the royal City Palace museum."
            }
        ]
    else:
        # Balanced Top Curated Picks
        destinations = [
            {
                "city": "Tokyo",
                "country": "Japan",
                "match_score": 97,
                "vibe_tags": ["#CyberpunkMetropolis", "#MichelinDining", "#ZenShrines"],
                "best_season": "March to May & September to November",
                "estimated_daily_budget_usd": 110,
                "why_it_matches": "Electrifying collision of futuristic robotics, neon alleys, ancient shrines, and pristine culinary perfection.",
                "must_experience": "Shibuya Sky panoramic rooftop view followed by omakase sushi in Ginza."
            },
            {
                "city": "Paris",
                "country": "France",
                "match_score": 95,
                "vibe_tags": ["#CityOfLight", "#LouvreTreasures", "#RomanticBoulevards"],
                "best_season": "April to June & September to October",
                "estimated_daily_budget_usd": 140,
                "why_it_matches": "Gourmet pastry cafes, iconic iron tower vistas, Seine river strolls, and world-class impressionist art.",
                "must_experience": "Sunset cruise down the Seine under illuminated bridges with champagne."
            },
            {
                "city": "Dubai",
                "country": "UAE",
                "match_score": 92,
                "vibe_tags": ["#SkylineMarvels", "#DesertSafari", "#LuxuryShopping"],
                "best_season": "November to March (Pleasant Warmth)",
                "estimated_daily_budget_usd": 160,
                "why_it_matches": "Tallest skyscraper on Earth, desert dune bashing at golden hour, and ultra-luxurious dining.",
                "must_experience": "Level 148 Burj Khalifa observation deck and evening 4x4 desert bedouin dinner camp."
            }
        ]
        
    return json.dumps({"recommendations": destinations}, indent=2)


def generate_demo_activity_swap(prompt: str) -> str:
    """Generates a contextual single activity slot replacement."""
    prompt_lower = prompt.lower()
    
    if "vegetarian" in prompt_lower or "vegan" in prompt_lower:
        slot = {
            "title": "Green Garden Organic Sanctuary & Farm-to-Table Bistro",
            "description": "Artisan 100% plant-based tasting menu featuring wood-fired heirloom squash, truffle risotto, and locally pressed botanical juices.",
            "time": "12:30 - 14:00",
            "cost_usd": 24,
            "transit_tip": "Short 4 min walk through shaded pedestrian arcade",
            "category": "Culinary (Vegetarian)",
            "tags": ["PlantBased", "Organic", "Artisan"]
        }
    elif "market" in prompt_lower or "shopping" in prompt_lower:
        slot = {
            "title": "Local Artisan Heritage & Flea Market",
            "description": "Lively open-air market stalls showcasing handmade leather goods, vintage postcards, local cheeses, and fragrant spice blends.",
            "time": "14:30 - 17:00",
            "cost_usd": 15,
            "transit_tip": "Located right in the center of the neighborhood square (2 min walk)",
            "category": "Shopping & Culture",
            "tags": ["LocalCrafts", "OpenAir", "Bargains"]
        }
    elif "adventure" in prompt_lower or "thrill" in prompt_lower:
        slot = {
            "title": "Panoramic Skyline Zipline & High-Ropes Challenge",
            "description": "High-altitude adrenaline rush with 360-degree views overlooking the city valley, guided by certified safety experts.",
            "time": "14:30 - 17:00",
            "cost_usd": 45,
            "transit_tip": "Express shuttle from the district hub (10 min)",
            "category": "Adventure & Thrills",
            "tags": ["Adrenaline", "Viewpoint", "Scenic"]
        }
    elif "kid" in prompt_lower or "family" in prompt_lower:
        slot = {
            "title": "Interactive Science & Natural Wonder Discovery Hall",
            "description": "Hands-on interactive exhibits, robotic displays, planetarium stargazing dome, and kid-friendly play discovery zones.",
            "time": "10:00 - 12:30",
            "cost_usd": 16,
            "transit_tip": "Directly accessible via pedestrian parkway (stroller friendly)",
            "category": "Family Leisure",
            "tags": ["KidFriendly", "Interactive", "Educational"]
        }
    else:
        slot = {
            "title": "Secret Rooftop Botanical Lounge & Craft Tasting",
            "description": "Hidden elevator entrance leading to a panoramic garden terrace with handcrafted floral infusions and skyline acoustic music.",
            "time": "18:30 - 21:00",
            "cost_usd": 28,
            "transit_tip": "5 min stroll from the afternoon activity hub",
            "category": "Atmospheric Leisure",
            "tags": ["Rooftop", "SunsetView", "Relaxed"]
        }
        
    return json.dumps({"replacement_slot": slot}, indent=2)


def generate_demo_itinerary(prompt: str) -> str:
    """
    Synthesizes a day-by-day geographically clustered itinerary
    either from knowledge base or via procedural generation.
    """
    from modules.geo_utils import get_city_coordinates
    
    # Extract destination from prompt
    dest = "Paris"
    match = re.search(r"Destination:\s*([^\n,]+)", prompt, re.IGNORECASE)
    if match:
        dest = match.group(1).strip()
    else:
        # Fallback search
        for candidate in ["tokyo", "rome", "jaipur", "bali", "dubai", "new york", "barcelona", "goa", "london", "zurich"]:
            if candidate in prompt.lower():
                dest = candidate.title()
                break
                
    # Extract duration
    days_count = 3
    match_days = re.search(r"Duration:\s*(\d+)", prompt, re.IGNORECASE)
    if match_days:
        try:
            days_count = max(1, min(14, int(match_days.group(1))))
        except Exception:
            pass
            
    # Extract budget tier & currency
    currency = "USD"
    match_curr = re.search(r"Currency:\s*([A-Z]{3})", prompt, re.IGNORECASE)
    if match_curr:
        currency = match_curr.group(1).strip()
        
    dest_lower = dest.lower()
    coords = get_city_coordinates(dest)
    base_lat = coords.get("lat", 48.8566)
    base_lon = coords.get("lon", 2.3522)
    
    days_data = []
    
    # If in knowledge base, use curated zones
    kb_data = None
    for k, v in DESTINATION_KNOWLEDGE_BASE.items():
        if k in dest_lower:
            kb_data = v
            break
            
    for d in range(1, days_count + 1):
        if kb_data and "zones" in kb_data:
            zone_idx = (d - 1) % len(kb_data["zones"])
            zone_template = kb_data["zones"][zone_idx]
            offset_lat, offset_lon = zone_template.get("center_offset", (0.01 * d, 0.01 * d))
            cluster_name = f"{zone_template['cluster_name']}"
            theme = zone_template.get("theme", "Exploration & Culture")
            
            # Extract slots with coordinates
            c_lat = base_lat + offset_lat
            c_lon = base_lon + offset_lon
            
            slots = [
                {
                    "time_slot": "Morning Sightseeing",
                    "title": zone_template["morning"]["title"],
                    "description": zone_template["morning"]["description"],
                    "time_window": zone_template["morning"]["time"],
                    "cost_usd": zone_template["morning"]["cost_usd"],
                    "cost_formatted": f"${zone_template['morning']['cost_usd']}",
                    "transit_tip": zone_template["morning"]["transit_tip"],
                    "category": zone_template["morning"]["category"],
                    "tags": zone_template["morning"]["tags"],
                    "lat": round(c_lat + 0.002, 5),
                    "lon": round(c_lon - 0.002, 5)
                },
                {
                    "time_slot": "Lunch Recommendation",
                    "title": zone_template["lunch"]["title"],
                    "description": zone_template["lunch"]["description"],
                    "time_window": zone_template["lunch"]["time"],
                    "cost_usd": zone_template["lunch"]["cost_usd"],
                    "cost_formatted": f"${zone_template['lunch']['cost_usd']}",
                    "transit_tip": zone_template["lunch"]["transit_tip"],
                    "category": zone_template["lunch"]["category"],
                    "tags": zone_template["lunch"]["tags"],
                    "lat": round(c_lat + 0.003, 5),
                    "lon": round(c_lon + 0.001, 5)
                },
                {
                    "time_slot": "Afternoon Leisure & Culture",
                    "title": zone_template["afternoon"]["title"],
                    "description": zone_template["afternoon"]["description"],
                    "time_window": zone_template["afternoon"]["time"],
                    "cost_usd": zone_template["afternoon"]["cost_usd"],
                    "cost_formatted": f"${zone_template['afternoon']['cost_usd']}",
                    "transit_tip": zone_template["afternoon"]["transit_tip"],
                    "category": zone_template["afternoon"]["category"],
                    "tags": zone_template["afternoon"]["tags"],
                    "lat": round(c_lat - 0.001, 5),
                    "lon": round(c_lon + 0.003, 5)
                },
                {
                    "time_slot": "Evening Dining & Entertainment",
                    "title": zone_template["evening"]["title"],
                    "description": zone_template["evening"]["description"],
                    "time_window": zone_template["evening"]["time"],
                    "cost_usd": zone_template["evening"]["cost_usd"],
                    "cost_formatted": f"${zone_template['evening']['cost_usd']}",
                    "transit_tip": zone_template["evening"]["transit_tip"],
                    "category": zone_template["evening"]["category"],
                    "tags": zone_template["evening"]["tags"],
                    "lat": round(c_lat - 0.003, 5),
                    "lon": round(c_lon - 0.001, 5)
                }
            ]
        else:
            # Procedural Cluster Synthesizer for arbitrary custom cities
            cluster_zones = [
                ("Old Town Heritage & Historic Waterfront", "Ancient stone alleys, waterfront landmarks & maritime history"),
                ("Royal Arts & Botanical Garden Mile", "Grand museums, palace squares & serene manicured gardens"),
                ("Bohemian Hills & Scenic Viewpoints", "Artisan cafes, hilltop panoramas & open-air viewpoints"),
                ("Culinary Heartland & Night Bazaars", "Flavors, food markets & lively twilight promenades"),
                ("Architectural Wonders & Modern Skyline", "Futuristic structures, observation towers & fine dining"),
            ]
            cz_idx = (d - 1) % len(cluster_zones)
            cluster_name = f"{dest} {cluster_zones[cz_idx][0]}"
            theme = cluster_zones[cz_idx][1]
            
            c_lat = base_lat + (0.015 * (d % 3)) - 0.01
            c_lon = base_lon + (0.015 * ((d + 1) % 3)) - 0.01
            
            slots = [
                {
                    "time_slot": "Morning Sightseeing",
                    "title": f"{dest} Heritage Citadel & Monumental Plaza",
                    "description": f"Morning walking tour through {dest}'s historic center exploring iconic arches, monuments, and architecture.",
                    "time_window": "09:00 - 12:00",
                    "cost_usd": 15,
                    "cost_formatted": "$15",
                    "transit_tip": "Central metro or 5 min walk from central square",
                    "category": "Sightseeing",
                    "tags": ["Heritage", "Iconic", "Guided"],
                    "lat": round(c_lat + 0.002, 5),
                    "lon": round(c_lon - 0.002, 5)
                },
                {
                    "time_slot": "Lunch Recommendation",
                    "title": f"Bistro {dest} Traditional Kitchen",
                    "description": "Authentic regional culinary tasting featuring fresh seasonal local ingredients and house specialties.",
                    "time_window": "12:30 - 14:00",
                    "cost_usd": 25,
                    "cost_formatted": "$25",
                    "transit_tip": "6 min leisurely stroll through shaded promenade",
                    "category": "Culinary",
                    "tags": ["LocalFlavors", "Artisan", "Cozy"],
                    "lat": round(c_lat + 0.003, 5),
                    "lon": round(c_lon + 0.001, 5)
                },
                {
                    "time_slot": "Afternoon Leisure & Culture",
                    "title": f"{dest} Grand Cultural Museum & Artisan Gallery",
                    "description": f"Explore regional artifacts, contemporary paintings, and local handicraft workshops in {dest}.",
                    "time_window": "14:30 - 17:30",
                    "cost_usd": 12,
                    "cost_formatted": "$12",
                    "transit_tip": "8 min walk across town park",
                    "category": "Culture",
                    "tags": ["Museum", "Art", "AirConditioned"],
                    "lat": round(c_lat - 0.001, 5),
                    "lon": round(c_lon + 0.003, 5)
                },
                {
                    "time_slot": "Evening Dining & Entertainment",
                    "title": f"{dest} Twilight Skyline Terrace & Dinner",
                    "description": "Panoramic sunset views followed by multi-course dining and local acoustic musical performance.",
                    "time_window": "18:30 - 22:00",
                    "cost_usd": 40,
                    "cost_formatted": "$40",
                    "transit_tip": "10 min scenic walk or quick taxi",
                    "category": "Nightlife & Dining",
                    "tags": ["Sunset", "Rooftop", "Cocktails"],
                    "lat": round(c_lat - 0.003, 5),
                    "lon": round(c_lon - 0.001, 5)
                }
            ]
            
        day_total_usd = sum(s["cost_usd"] for s in slots)
        days_data.append({
            "day": d,
            "title": f"Day {d}: {cluster_name}",
            "cluster_name": cluster_name,
            "theme": theme,
            "cluster_transit_summary": "All 4 activities clustered within ~2.5 km radius. Walking & short metro connections prevent transit fatigue.",
            "estimated_daily_cost_usd": day_total_usd,
            "slots": slots
        })
        
    result = {
        "destination": dest,
        "duration_days": days_count,
        "trip_title": f"{dest} Curated Explorer: Optimized {days_count}-Day Journey",
        "clustering_strategy": "Neighborhood geographic grouping to minimize cross-city backtracking and maximize leisure time.",
        "anti_transit_fatigue_score": 95,
        "transit_advice": f"Use local metro pass or contactless transit in {dest}. Attractions grouped strictly by district.",
        "packing_essentials": [
            "Comfortable broken-in walking shoes or sneakers",
            "Universal power adapter and high-capacity power bank",
            "Lightweight rain jacket or compact travel umbrella",
            "Reusable insulated water bottle",
            "Small daypack with anti-theft zipper locks"
        ],
        "emergency_contacts": {
            "emergency_universal": "112 / 911",
            "police": "Local City Police HQ & Tourist Police Desk",
            "ambulance_medical": "Central City Emergency Hospital Network",
            "tourist_helpline": "+1-800-TRAVEL-SAFE / Dedicated Tourist Support"
        },
        "days": days_data
    }
    
    return json.dumps(result, indent=2)
