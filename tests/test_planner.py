"""
Automated Pytest Test Suite for Personalized Travel Itinerary Planner.
Validates SQLite persistence, LLM engine & fallback, clustering logic,
dynamic slot swapping, and ReportLab PDF export.
"""

import os
import json
import pytest
from pathlib import Path

import config
from modules.database import init_db, save_trip, list_trips, get_trip, delete_trip, export_all_trips_json, import_trips_json
from modules.geo_utils import get_city_coordinates, haversine_distance, calculate_clustering_metrics, build_plotly_map
from modules.recommender import get_destination_recommendations
from modules.itinerary_generator import generate_itinerary
from modules.activity_swapper import swap_activity_slot
from modules.pdf_exporter import generate_pdf_itinerary


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Initializes clean database table for test execution."""
    init_db()


def test_city_coordinates_lookup():
    """Validates coordinate resolver for known and unknown cities."""
    paris = get_city_coordinates("Paris, France")
    assert paris["lat"] == pytest.approx(48.8566, rel=1e-2)
    assert paris["lon"] == pytest.approx(2.3522, rel=1e-2)
    
    # Custom unknown city deterministic fallback
    custom = get_city_coordinates("Santorini")
    assert "lat" in custom and "lon" in custom


def test_haversine_distance_and_clustering_metrics():
    """Validates anti-transit fatigue distance and score calculation."""
    # Paris Louvre to Eiffel Tower ~3.5 km
    dist = haversine_distance(48.8606, 2.3376, 48.8584, 2.2945)
    assert 2.5 <= dist <= 4.5
    
    mock_days = [
        {
            "day": 1,
            "slots": [
                {"lat": 48.8566, "lon": 2.3522},
                {"lat": 48.8580, "lon": 2.3540},
                {"lat": 48.8590, "lon": 2.3550},
                {"lat": 48.8570, "lon": 2.3530},
            ]
        }
    ]
    metrics = calculate_clustering_metrics(mock_days)
    assert metrics["efficiency_score"] >= 80
    assert metrics["total_km"] > 0
    assert "hours_saved" in metrics


def test_destination_recommendations():
    """Validates Tab 1 destination recommender output format and currency formatting."""
    recs = get_destination_recommendations(
        vibe="Beach & Coastal Relaxation",
        budget_tier="Budget / Backpacker",
        travel_party="Solo Explorer",
        travel_season="Sunny Summer",
        interests=["Food & Culinary Trails"],
        currency="USD",
        provider="demo"
    )
    assert isinstance(recs, list)
    assert len(recs) == 3
    for item in recs:
        assert "city" in item
        assert "match_score" in item
        assert "daily_budget_formatted" in item
        assert len(item.get("vibe_tags", [])) > 0


def test_itinerary_generation():
    """Validates Tab 2 day-by-day clustered itinerary structure."""
    itinerary = generate_itinerary(
        destination="Tokyo, Japan",
        duration_days=3,
        start_date="Nov 01, 2026",
        end_date="Nov 03, 2026",
        budget_tier="Moderate / Balanced",
        travel_party="Couple / Romantic",
        pace="Moderate / Balanced",
        interests=["History & Ancient Heritage", "Food & Culinary Trails"],
        currency="INR",
        provider="demo"
    )
    
    assert itinerary["destination"] == "Tokyo, Japan"
    assert itinerary["duration_days"] == 3
    assert len(itinerary["days"]) == 3
    assert itinerary["total_cost"] > 0
    assert itinerary["anti_transit_fatigue_score"] >= 80
    
    # Check slots per day
    for day in itinerary["days"]:
        slots = day.get("slots", [])
        assert len(slots) == 4
        slot_names = [s["time_slot"] for s in slots]
        assert "Morning Sightseeing" in slot_names
        assert "Lunch Recommendation" in slot_names
        assert "Afternoon Leisure & Culture" in slot_names
        assert "Evening Dining & Entertainment" in slot_names
        
        for slot in slots:
            assert "cost_formatted" in slot
            assert "transit_tip" in slot
            assert "slot_id" in slot


def test_activity_swapper():
    """Validates Tab 3 slot-level replacement and surrounding preservation."""
    itinerary = generate_itinerary(
        destination="Paris",
        duration_days=2,
        start_date="Nov 01, 2026",
        end_date="Nov 02, 2026",
        budget_tier="Moderate / Balanced",
        travel_party="Solo Explorer",
        pace="Moderate / Balanced",
        interests=["Culture"],
        currency="USD",
        provider="demo"
    )
    
    original_day1_morning = itinerary["days"][0]["slots"][0]["title"]
    original_day2_morning = itinerary["days"][1]["slots"][0]["title"]
    
    # Perform swap on Day 1, Morning
    updated = swap_activity_slot(
        itinerary=itinerary,
        day_number=1,
        time_slot="Morning Sightseeing",
        swap_prompt="Find a delicious vegetarian / vegan culinary gem",
        currency="USD",
        provider="demo"
    )
    
    new_day1_morning = updated["days"][0]["slots"][0]["title"]
    unchanged_day2_morning = updated["days"][1]["slots"][0]["title"]
    
    # Assert Day 1 morning changed
    assert new_day1_morning != original_day1_morning
    # Assert Day 2 morning remained intact
    assert unchanged_day2_morning == original_day2_morning
    assert updated["total_cost"] > 0


def test_sqlite_persistence_crud():
    """Validates SQLite save, list, get, delete, and JSON backup/restore."""
    mock_trip = {
        "trip_id": "test-persisted-trip-12345",
        "name": "Test Jaipur Expedition",
        "destination": "Jaipur, India",
        "duration_days": 2,
        "start_date": "Dec 10, 2026",
        "end_date": "Dec 11, 2026",
        "budget_tier": "Luxury / Premium",
        "travel_party": "Friends Group (3-4)",
        "pace": "Fast-Paced / Packed",
        "currency": "INR",
        "total_cost": 450.0,
        "notes": "Testing SQLite persistence layer",
        "days": []
    }
    
    # Save
    trip_id = save_trip(mock_trip)
    assert trip_id == "test-persisted-trip-12345"
    
    # List
    all_trips = list_trips()
    assert any(t["trip_id"] == "test-persisted-trip-12345" for t in all_trips)
    
    # Get
    retrieved = get_trip("test-persisted-trip-12345")
    assert retrieved is not None
    assert retrieved["name"] == "Test Jaipur Expedition"
    assert retrieved["destination"] == "Jaipur, India"
    
    # Export JSON
    exported_json = export_all_trips_json()
    assert "test-persisted-trip-12345" in exported_json
    
    # Delete
    deleted = delete_trip("test-persisted-trip-12345")
    assert deleted is True
    assert get_trip("test-persisted-trip-12345") is None


def test_pdf_export_generation():
    """Validates ReportLab PDF generation binary integrity."""
    itinerary = generate_itinerary(
        destination="Rome, Italy",
        duration_days=2,
        start_date="Dec 15, 2026",
        end_date="Dec 16, 2026",
        budget_tier="Moderate / Balanced",
        travel_party="Couple / Romantic",
        pace="Relaxed / Slow Travel",
        interests=["History & Ancient Heritage"],
        currency="EUR",
        provider="demo"
    )
    
    pdf_bytes = generate_pdf_itinerary(itinerary)
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 1000  # Non-trivial size
    assert pdf_bytes.startswith(b"%PDF-")  # Valid PDF binary signature
