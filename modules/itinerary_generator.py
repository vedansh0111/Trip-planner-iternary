"""
Day-by-Day Optimized Itinerary Generator Module (Tab 2 / Epic 4).
Enforces geographic clustering, sequential time slots, running budget calculations,
and anti-transit fatigue scoring.
"""

import json
import uuid
from typing import Dict, Any, List
from modules.llm_engine import generate_completion, sanitize_json_response, generate_demo_itinerary
from modules.geo_utils import get_city_coordinates, calculate_clustering_metrics
import config


def generate_itinerary(
    destination: str,
    duration_days: int,
    start_date: str,
    end_date: str,
    budget_tier: str,
    travel_party: str,
    pace: str,
    interests: List[str],
    currency: str = "USD",
    provider: str = "demo",
    api_key: str = "",
) -> Dict[str, Any]:
    """
    Generates a geographically clustered, sequential day-by-day vacation itinerary.
    """
    currency_info = config.CURRENCIES.get(currency, config.CURRENCIES["USD"])
    rate = currency_info["rate_to_usd"]
    symbol = currency_info["symbol"]
    interests_str = ", ".join(interests) if interests else "Sightseeing, Local Culture & Cuisine"
    city_center = get_city_coordinates(destination)
    base_lat = city_center["lat"]
    base_lon = city_center["lon"]
    
    system_prompt = (
        "You are a master travel logistics architect specializing in eliminating travel fatigue. "
        "Create an optimized day-by-day vacation itinerary grouping attractions geographically "
        "by neighborhood or zone on each day to minimize transit fatigue and prevent backtracking. "
        "Strictly output valid JSON only."
    )
    
    prompt = f"""
    Destination: {destination}
    Duration: {duration_days} days
    Dates: {start_date} to {end_date}
    Budget Tier: {budget_tier}
    Travel Party: {travel_party}
    Pace: {pace}
    Interests: {interests_str}
    Currency: {currency}
    Approximate City Center: lat={base_lat}, lon={base_lon}

    Generate a complete itinerary adhering to this JSON format:
    {{
      "destination": "{destination}",
      "duration_days": {duration_days},
      "trip_title": "Creative Trip Title",
      "clustering_strategy": "Explanation of geographic clusters used per day",
      "anti_transit_fatigue_score": 94,
      "transit_advice": "Advice for getting around efficiently",
      "packing_essentials": ["Item 1", "Item 2", "Item 3", "Item 4", "Item 5"],
      "emergency_contacts": {{
        "emergency_universal": "112 / 911",
        "police": "City Police & Tourist Desk",
        "ambulance_medical": "Central Medical Emergency",
        "tourist_helpline": "Tourist Assistance Number"
      }},
      "days": [
        {{
          "day": 1,
          "title": "Day 1: Cluster Name",
          "cluster_name": "Neighborhood / District Name",
          "theme": "Theme of this day",
          "cluster_transit_summary": "Transit tip explaining why these are grouped together",
          "estimated_daily_cost_usd": 120,
          "slots": [
            {{
              "time_slot": "Morning Sightseeing",
              "title": "Attraction Name",
              "description": "Engaging 2-sentence description",
              "time_window": "09:00 - 12:30",
              "cost_usd": 20,
              "transit_tip": "Walking or metro line",
              "category": "Sightseeing",
              "tags": ["Tag1", "Tag2"],
              "lat": {base_lat},
              "lon": {base_lon}
            }},
            {{
              "time_slot": "Lunch Recommendation",
              "title": "Restaurant Name",
              "description": "Culinary specialty & dietary details",
              "time_window": "12:30 - 14:00",
              "cost_usd": 25,
              "transit_tip": "Short walk from morning sight",
              "category": "Culinary",
              "tags": ["LocalFood", "Bistro"],
              "lat": {base_lat + 0.002},
              "lon": {base_lon + 0.002}
            }},
            {{
              "time_slot": "Afternoon Leisure & Culture",
              "title": "Museum or Park Name",
              "description": "Afternoon highlight",
              "time_window": "14:30 - 17:30",
              "cost_usd": 15,
              "transit_tip": "Short walk or quick 1-stop metro",
              "category": "Culture",
              "tags": ["Culture", "Art"],
              "lat": {base_lat - 0.001},
              "lon": {base_lon + 0.003}
            }},
            {{
              "time_slot": "Evening Dining & Entertainment",
              "title": "Evening Venue or Night Market",
              "description": "Dinner and evening vibes",
              "time_window": "18:30 - 22:00",
              "cost_usd": 45,
              "transit_tip": "5 min walk from afternoon spot",
              "category": "Dining & Nightlife",
              "tags": ["Nightlife", "Scenic"],
              "lat": {base_lat - 0.003},
              "lon": {base_lon - 0.001}
            }}
          ]
        }}
      ]
    }}
    """
    
    raw_response = generate_completion(
        prompt=prompt,
        system_prompt=system_prompt,
        provider=provider,
        api_key=api_key,
    )
    
    itinerary_data = None
    try:
        cleaned = sanitize_json_response(raw_response)
        parsed = json.loads(cleaned)
        if isinstance(parsed, dict) and "days" in parsed and len(parsed["days"]) > 0:
            itinerary_data = parsed
    except Exception as e:
        print(f"Error parsing LLM itinerary output: {e}. Generating procedural plan.")
        
    if not itinerary_data:
        demo_output = generate_demo_itinerary(f"Destination: {destination}\nDuration: {duration_days}\nCurrency: {currency}")
        itinerary_data = json.loads(demo_output)
        
    # Enrich and standardize the itinerary data
    enrich_itinerary(itinerary_data, destination, duration_days, start_date, end_date, budget_tier, travel_party, pace, currency, rate, symbol)
    
    return itinerary_data


def enrich_itinerary(
    itinerary: Dict[str, Any],
    destination: str,
    duration_days: int,
    start_date: str,
    end_date: str,
    budget_tier: str,
    travel_party: str,
    pace: str,
    currency: str,
    rate: float,
    symbol: str
):
    """Adds metadata, calculates cumulative costs, IDs, and geographic fatigue metrics."""
    itinerary["trip_id"] = itinerary.get("trip_id") or str(uuid.uuid4())
    itinerary["destination"] = destination
    itinerary["duration_days"] = duration_days
    itinerary["start_date"] = start_date
    itinerary["end_date"] = end_date
    itinerary["budget_tier"] = budget_tier
    itinerary["travel_party"] = travel_party
    itinerary["pace"] = pace
    itinerary["currency"] = currency
    itinerary["currency_symbol"] = symbol
    
    # Target budget estimation
    tier_info = config.BUDGET_TIERS.get(budget_tier, config.BUDGET_TIERS["Moderate / Balanced"])
    party_info = config.TRAVEL_PARTIES.get(travel_party, config.TRAVEL_PARTIES["Solo Explorer"])
    target_daily_usd = tier_info["daily_per_person_usd"] * party_info["multiplier"]
    target_total_usd = target_daily_usd * duration_days
    
    itinerary["target_total_budget_usd"] = target_total_usd
    itinerary["target_total_budget_local"] = round(target_total_usd * rate)
    
    running_cumulative_usd = 0.0
    days = itinerary.get("days", [])
    
    for day in days:
        day_total_usd = 0.0
        slots = day.get("slots", [])
        for slot in slots:
            # Ensure unique slot id for dynamic activity swap
            if "slot_id" not in slot:
                slot["slot_id"] = str(uuid.uuid4())[:8]
                
            cost_usd = float(slot.get("cost_usd", 15.0))
            day_total_usd += cost_usd
            slot_cost_local = round(cost_usd * rate)
            
            # Format dual currency
            if currency == "USD":
                slot["cost_formatted"] = f"${cost_usd:,.0f}"
            else:
                slot["cost_formatted"] = f"{symbol}{slot_cost_local:,.0f} (~${cost_usd:,.0f})"
                
        day["estimated_daily_cost_usd"] = day_total_usd
        day["estimated_daily_cost_local"] = round(day_total_usd * rate)
        
        running_cumulative_usd += day_total_usd
        day["cumulative_cost_usd"] = running_cumulative_usd
        day["cumulative_cost_local"] = round(running_cumulative_usd * rate)
        
    total_trip_usd = running_cumulative_usd
    itinerary["total_cost"] = total_trip_usd
    itinerary["total_cost_local"] = round(total_trip_usd * rate)
    itinerary["budget_variance_usd"] = round(target_total_usd - total_trip_usd, 1)
    
    # Calculate transit fatigue score
    clustering_metrics = calculate_clustering_metrics(days)
    itinerary["clustering_metrics"] = clustering_metrics
    itinerary["anti_transit_fatigue_score"] = clustering_metrics["efficiency_score"]
    
    # Ensure center coordinates
    coords = get_city_coordinates(destination)
    itinerary["center_lat"] = coords["lat"]
    itinerary["center_lon"] = coords["lon"]
