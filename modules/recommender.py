"""
Smart Destination Recommender Module (Tab 1 / Epic 3).
Matches travel vibes, budget tiers, and party dynamics to optimal global destinations.
"""

import json
from typing import List, Dict, Any
from modules.llm_engine import generate_completion, sanitize_json_response
import config


def get_destination_recommendations(
    vibe: str,
    budget_tier: str,
    travel_party: str,
    travel_season: str,
    interests: List[str],
    currency: str = "USD",
    provider: str = "demo",
    api_key: str = "",
) -> List[Dict[str, Any]]:
    """
    Generates 3 top matching destination cities based on user vibe, budget, and party type.
    """
    currency_info = config.CURRENCIES.get(currency, config.CURRENCIES["USD"])
    rate = currency_info["rate_to_usd"]
    symbol = currency_info["symbol"]
    
    interests_str = ", ".join(interests) if interests else "General Sights & Culture"
    
    system_prompt = (
        "You are an expert global luxury and budget travel curator. "
        "Recommend exactly 3 exceptional matching travel destination cities tailored to the user's vibe, "
        "budget, travel party, and interests. Return valid JSON only with no markdown or preamble."
    )
    
    prompt = f"""
    Please recommend top 3 matching cities based on:
    - Vibe/Mood: {vibe}
    - Budget Tier: {budget_tier}
    - Travel Party: {travel_party}
    - Travel Season / Dates: {travel_season}
    - Interests: {interests_str}
    - Currency: {currency}

    Return a strict JSON object with a single key 'recommendations' containing an array of 3 objects:
    {{
      "recommendations": [
        {{
          "city": "City Name",
          "country": "Country Name",
          "match_score": 95,
          "vibe_tags": ["#Tag1", "#Tag2", "#Tag3"],
          "best_season": "Season or months to visit",
          "estimated_daily_budget_usd": 120,
          "why_it_matches": "2 sentences explaining why this city matches their vibe and party",
          "must_experience": "The single most unforgettable highlight experience"
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
    
    destinations = []
    try:
        cleaned = sanitize_json_response(raw_response)
        parsed = json.loads(cleaned)
        if isinstance(parsed, dict) and "recommendations" in parsed:
            destinations = parsed["recommendations"]
        elif isinstance(parsed, list):
            destinations = parsed
    except Exception as e:
        print(f"Error parsing recommendations: {e}. Falling back to default curated set.")
        # Fallback to demo response
        from modules.llm_engine import generate_demo_recommendations
        try:
            demo_raw = generate_demo_recommendations(f"{vibe} {budget_tier}")
            destinations = json.loads(demo_raw).get("recommendations", [])
        except Exception:
            destinations = []

    # Format localized costs and badges
    for item in destinations:
        cost_usd = item.get("estimated_daily_budget_usd", 100)
        local_cost = round(cost_usd * rate)
        item["daily_budget_formatted"] = f"{symbol}{local_cost:,.0f} / day"
        item["currency_symbol"] = symbol
        
    return destinations
