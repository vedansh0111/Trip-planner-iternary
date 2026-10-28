"""
Vibe Customization & Dynamic Activity Swap Module (Tab 3 / Epic 4).
Modifies targeted time slots while preserving the rest of the itinerary,
recalculating neighborhood cluster transit tips and running costs.
"""

import json
import uuid
from typing import Dict, Any, Optional
from modules.llm_engine import generate_completion, sanitize_json_response, generate_demo_activity_swap
import config


QUICK_SWAP_PRESETS = [
    "Swap for an authentic local artisan / flea market",
    "Find a delicious vegetarian / vegan culinary gem",
    "More thrilling adventure / panoramic viewpoint",
    "Family-friendly / kid-engaging interactive activity",
    "Rain-friendly / indoor cultural heritage experience",
    "Cozy historic cafe or rooftop sunset lounge",
]


def swap_activity_slot(
    itinerary: Dict[str, Any],
    day_number: int,
    time_slot: str,
    swap_prompt: str,
    currency: str = "USD",
    provider: str = "demo",
    api_key: str = "",
) -> Dict[str, Any]:
    """
    Dynamically swaps a single slot inside the itinerary without wiping or altering other days.
    """
    days = itinerary.get("days", [])
    target_day = None
    target_slot_idx = -1
    
    for d in days:
        if d.get("day") == day_number:
            target_day = d
            break
            
    if not target_day:
        raise ValueError(f"Day {day_number} not found in current itinerary.")
        
    slots = target_day.get("slots", [])
    for idx, s in enumerate(slots):
        if s.get("time_slot") == time_slot:
            target_slot_idx = idx
            break
            
    if target_slot_idx == -1:
        raise ValueError(f"Slot '{time_slot}' not found on Day {day_number}.")
        
    old_slot = slots[target_slot_idx]
    cluster_name = target_day.get("cluster_name", itinerary.get("destination", "City"))
    dest = itinerary.get("destination", "City")
    
    system_prompt = (
        "You are an expert travel concierge. The traveler wants to modify a single activity slot "
        "in their existing itinerary. Propose a replacement activity located in the SAME neighborhood/cluster "
        "to avoid transit fatigue. Output strictly valid JSON."
    )
    
    prompt = f"""
    Destination: {dest}
    Day: {day_number}
    Neighborhood / District: {cluster_name}
    Current Activity: {old_slot.get('title')} ({old_slot.get('time_slot')})
    User Swap Request: {swap_prompt}

    Return JSON with a single object 'replacement_slot':
    {{
      "replacement_slot": {{
        "title": "New Activity Name",
        "description": "Engaging 2-sentence description of the new experience",
        "time_window": "{old_slot.get('time_window', '09:00 - 12:00')}",
        "cost_usd": 20,
        "transit_tip": "Walking connection from nearby cluster landmark",
        "category": "Category",
        "tags": ["Tag1", "Tag2"]
      }}
    }}
    """
    
    raw_response = generate_completion(
        prompt=prompt,
        system_prompt=system_prompt,
        provider=provider,
        api_key=api_key,
    )
    
    new_slot_data = None
    try:
        cleaned = sanitize_json_response(raw_response)
        parsed = json.loads(cleaned)
        if isinstance(parsed, dict) and "replacement_slot" in parsed:
            new_slot_data = parsed["replacement_slot"]
    except Exception as e:
        print(f"Error parsing slot swap: {e}. Falling back to demo engine.")
        
    if not new_slot_data:
        demo_raw = generate_demo_activity_swap(swap_prompt)
        new_slot_data = json.loads(demo_raw).get("replacement_slot", {})
        
    # Preserve coordinates with slight perturbation to stay in cluster
    old_lat = old_slot.get("lat")
    old_lon = old_slot.get("lon")
    new_lat = round(old_lat + 0.0008, 5) if old_lat is not None else None
    new_lon = round(old_lon - 0.0008, 5) if old_lon is not None else None
    
    # Update the slot
    new_slot = {
        "slot_id": str(uuid.uuid4())[:8],
        "time_slot": time_slot,
        "title": new_slot_data.get("title", f"Alternative {time_slot}"),
        "description": new_slot_data.get("description", "A refreshed experience matching your custom vibe."),
        "time_window": new_slot_data.get("time_window", old_slot.get("time_window", "10:00 - 12:00")),
        "cost_usd": float(new_slot_data.get("cost_usd", old_slot.get("cost_usd", 20))),
        "transit_tip": new_slot_data.get("transit_tip", "Convenient walking distance within neighborhood"),
        "category": new_slot_data.get("category", "Custom Highlight"),
        "tags": new_slot_data.get("tags", ["CustomVibe", "Refreshed"]),
        "lat": new_lat,
        "lon": new_lon,
    }
    
    target_day["slots"][target_slot_idx] = new_slot
    
    # Recalculate costs for the itinerary
    currency_info = config.CURRENCIES.get(currency, config.CURRENCIES["USD"])
    rate = currency_info["rate_to_usd"]
    symbol = currency_info["symbol"]
    
    from modules.itinerary_generator import enrich_itinerary
    enrich_itinerary(
        itinerary=itinerary,
        destination=itinerary.get("destination", "Trip"),
        duration_days=int(itinerary.get("duration_days", len(days))),
        start_date=itinerary.get("start_date", ""),
        end_date=itinerary.get("end_date", ""),
        budget_tier=itinerary.get("budget_tier", "Moderate / Balanced"),
        travel_party=itinerary.get("travel_party", "Solo Explorer"),
        pace=itinerary.get("pace", "Moderate / Balanced"),
        currency=currency,
        rate=rate,
        symbol=symbol
    )
    
    return itinerary
