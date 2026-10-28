"""
SQLite persistence module for Personalized Travel Itinerary Planner.
Provides local zero-dependency database storage for trips, favorites, and history.
"""

import sqlite3
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import config

DB_PATH = config.DB_PATH


def get_connection() -> sqlite3.Connection:
    """Creates a connection to the SQLite database."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes the database schema if it doesn't already exist."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trips (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trip_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                destination TEXT NOT NULL,
                duration_days INTEGER NOT NULL,
                start_date TEXT,
                end_date TEXT,
                budget_tier TEXT,
                travel_party TEXT,
                pace TEXT,
                currency TEXT,
                total_cost REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_json TEXT NOT NULL,
                notes TEXT DEFAULT ''
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_destination ON trips (destination)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON trips (created_at)")
        conn.commit()


def save_trip(trip_data: Dict[str, Any]) -> str:
    """
    Saves or updates a trip in SQLite.
    Returns the trip_id.
    """
    init_db()
    trip_id = trip_data.get("trip_id") or str(uuid.uuid4())
    name = trip_data.get("name") or f"Trip to {trip_data.get('destination', 'Wanderlust')}"
    destination = trip_data.get("destination", "Unknown")
    duration_days = int(trip_data.get("duration_days", len(trip_data.get("days", [])) or 1))
    start_date = str(trip_data.get("start_date", ""))
    end_date = str(trip_data.get("end_date", ""))
    budget_tier = trip_data.get("budget_tier", "Moderate / Balanced")
    travel_party = trip_data.get("travel_party", "Solo Explorer")
    pace = trip_data.get("pace", "Moderate / Balanced")
    currency = trip_data.get("currency", "USD")
    total_cost = float(trip_data.get("total_cost", 0.0))
    notes = trip_data.get("notes", "")

    # Ensure trip_id is in the data dict
    trip_data["trip_id"] = trip_id
    trip_data["saved_at"] = datetime.now().isoformat()
    data_json = json.dumps(trip_data, ensure_ascii=False)

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO trips (
                trip_id, name, destination, duration_days, start_date, end_date,
                budget_tier, travel_party, pace, currency, total_cost, data_json, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(trip_id) DO UPDATE SET
                name=excluded.name,
                destination=excluded.destination,
                duration_days=excluded.duration_days,
                start_date=excluded.start_date,
                end_date=excluded.end_date,
                budget_tier=excluded.budget_tier,
                travel_party=excluded.travel_party,
                pace=excluded.pace,
                currency=excluded.currency,
                total_cost=excluded.total_cost,
                data_json=excluded.data_json,
                notes=excluded.notes
        """, (
            trip_id, name, destination, duration_days, start_date, end_date,
            budget_tier, travel_party, pace, currency, total_cost, data_json, notes
        ))
        conn.commit()

    return trip_id


def list_trips() -> List[Dict[str, Any]]:
    """Returns a summary list of all saved trips ordered by newest first."""
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT trip_id, name, destination, duration_days, start_date, end_date,
                   budget_tier, travel_party, pace, currency, total_cost, created_at, notes
            FROM trips
            ORDER BY created_at DESC
        """)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def get_trip(trip_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves full trip data for a given trip_id."""
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT data_json FROM trips WHERE trip_id = ?", (trip_id,))
        row = cursor.fetchone()
        if row:
            try:
                return json.loads(row["data_json"])
            except Exception:
                return None
    return None


def delete_trip(trip_id: str) -> bool:
    """Deletes a trip by its trip_id."""
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM trips WHERE trip_id = ?", (trip_id,))
        conn.commit()
        return cursor.rowcount > 0


def export_all_trips_json() -> str:
    """Exports all trips into a JSON string backup."""
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT data_json FROM trips ORDER BY created_at DESC")
        rows = cursor.fetchall()
        trips = []
        for r in rows:
            try:
                trips.append(json.loads(r["data_json"]))
            except Exception:
                pass
        return json.dumps({"version": "1.0", "platform_id": config.PLATFORM_ID, "trips": trips}, indent=2)


def import_trips_json(json_content: str) -> int:
    """Imports trips from a JSON string. Returns count of successfully imported trips."""
    init_db()
    count = 0
    try:
        data = json.loads(json_content)
        trips = data.get("trips", []) if isinstance(data, dict) else (data if isinstance(data, list) else [])
        for trip in trips:
            if isinstance(trip, dict) and "destination" in trip:
                save_trip(trip)
                count += 1
    except Exception as e:
        print(f"Error importing trips: {e}")
    return count
