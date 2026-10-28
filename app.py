"""
Personalized Travel Itinerary Planner (Skill Wallet Capstone Project 4)
Platform ID: 6ac33976fb8fc7965cd9236d
Full-stack AI-powered Streamlit Application with Geographic Clustering & Offline PDF Export.
"""

import streamlit as st
import datetime
import json
from typing import Dict, Any, List

import config
from modules.database import init_db, save_trip, list_trips, get_trip, delete_trip, export_all_trips_json, import_trips_json
from modules.recommender import get_destination_recommendations
from modules.itinerary_generator import generate_itinerary
from modules.activity_swapper import swap_activity_slot, QUICK_SWAP_PRESETS
from modules.geo_utils import build_pydeck_map, build_plotly_map, get_city_coordinates
from modules.pdf_exporter import generate_pdf_itinerary

# ---------------------------------------------------------
# Page Configuration & Modern Wanderlust CSS Injection
# ---------------------------------------------------------
st.set_page_config(
    page_title="Personalized Travel Itinerary Planner",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database schema
init_db()

# Custom CSS styling for luxury SaaS wanderlust aesthetic
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Playfair+Display:ital,wght@0,600;0,700;1,400&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Top Banner / Platform Tag */
    .platform-header {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        padding: 18px 24px;
        border-radius: 14px;
        color: white;
        margin-bottom: 24px;
        border-left: 5px solid #E05A47;
        box-shadow: 0 4px 15px rgba(0,0,0,0.06);
    }
    .platform-tag {
        background: rgba(224, 90, 71, 0.2);
        color: #FFA590;
        font-size: 11px;
        padding: 4px 10px;
        border-radius: 20px;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        display: inline-block;
        margin-bottom: 6px;
    }
    .platform-title {
        font-family: 'Playfair Display', serif;
        font-size: 26px;
        font-weight: 700;
        margin: 0;
        color: #FFFFFF;
    }
    
    /* Metric & Highlight Cards */
    .metric-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 14px rgba(0,0,0,0.08);
    }
    .metric-val {
        font-size: 22px;
        font-weight: 800;
        color: #E05A47;
        margin-bottom: 2px;
    }
    .metric-label {
        font-size: 12px;
        color: #64748B;
        font-weight: 600;
        text-transform: uppercase;
    }
    
    /* Day Itinerary Card */
    .day-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 20px;
        border-left: 4px solid #2A7B88;
        box-shadow: 0 3px 10px rgba(0,0,0,0.03);
    }
    .day-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 14px;
        border-bottom: 1px solid #F1F5F9;
        padding-bottom: 10px;
    }
    .cluster-badge {
        background: #E6F4F1;
        color: #2A7B88;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
    }
    
    /* Slot Card */
    .slot-card {
        background: #F8FAFC;
        border-left: 3px solid #CBD5E1;
        border-radius: 8px;
        padding: 12px 14px;
        margin-bottom: 10px;
        transition: all 0.2s ease;
    }
    .slot-card:hover {
        background: #F1F5F9;
        border-left-color: #E05A47;
    }
    .slot-time {
        font-size: 11px;
        font-weight: 700;
        color: #E05A47;
        text-transform: uppercase;
        margin-bottom: 2px;
    }
    .slot-title {
        font-size: 15px;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 4px;
    }
    .slot-desc {
        font-size: 13px;
        color: #475569;
        margin-bottom: 6px;
        line-height: 1.4;
    }
    .slot-meta {
        display: flex;
        gap: 12px;
        font-size: 12px;
        color: #64748B;
        align-items: center;
    }
    .tag-badge {
        background: #E2E8F0;
        color: #334155;
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 500;
    }
    
    /* Destination Recommendation Card */
    .reco-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 16px;
        border-top: 4px solid #E05A47;
        box-shadow: 0 4px 12px rgba(0,0,0,0.04);
    }
    .reco-score {
        background: #FEF3C7;
        color: #D97706;
        font-weight: 800;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 13px;
        display: inline-block;
        float: right;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# State Initialization
# ---------------------------------------------------------
if "current_itinerary" not in st.session_state:
    st.session_state.current_itinerary = None

if "recommended_destinations" not in st.session_state:
    st.session_state.recommended_destinations = []

if "destination_input" not in st.session_state:
    st.session_state.destination_input = "Paris, France"

if "active_tab_index" not in st.session_state:
    st.session_state.active_tab_index = 0

# ---------------------------------------------------------
# Sidebar: Engine Configuration & Preferences (Epic 3)
# ---------------------------------------------------------
with st.sidebar:
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 12px;">
        <span style="font-size: 32px;">🧭</span>
        <h3 style="margin: 0; color: #1E293B;">Trip Architect</h3>
        <p style="font-size: 11px; color: #64748B; margin-top: 2px;">{config.CAPSTONE_ID}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 1. AI Engine & Credentials
    st.markdown("#### ⚡ AI Provider & Credentials")
    provider = st.selectbox(
        "Engine Selection",
        options=["Demo Mode (Offline Fast, No Key Required)", "Google Gemini (gemini-2.5-flash)", "Groq (llama-3.3-70b-versatile)"],
        index=0,
        help="Demo Mode works 100% offline with zero dependencies and built-in curated travel intelligence."
    )
    
    api_key = ""
    provider_code = "demo"
    if "Gemini" in provider:
        provider_code = "gemini"
        api_key = st.text_input("Gemini API Key", type="password", placeholder="AIzaSy...")
        if not api_key:
            st.info("💡 Tip: Leave blank to automatically use high-fidelity Demo Mode.")
    elif "Groq" in provider:
        provider_code = "groq"
        api_key = st.text_input("Groq API Key", type="password", placeholder="gsk_...")
        if not api_key:
            st.info("💡 Tip: Leave blank to automatically use high-fidelity Demo Mode.")
            
    st.markdown("---")
    
    # 2. Trip Preferences Form
    st.markdown("#### ✈️ Trip Preferences")
    
    # Quick destination selector pills
    quick_dest = st.selectbox(
        "Popular Quick Destinations",
        options=["(Custom / Choose Below)", "Paris, France", "Tokyo, Japan", "Jaipur, India", "Bali, Indonesia", "Rome, Italy", "Dubai, UAE", "New York, USA", "Goa, India"],
        index=0
    )
    
    default_dest = quick_dest if quick_dest != "(Custom / Choose Below)" else st.session_state.destination_input
    destination = st.text_input("Destination City / Region", value=default_dest)
    st.session_state.destination_input = destination
    
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        duration_days = st.slider("Trip Duration (Days)", min_value=1, max_value=10, value=3)
    with col_d2:
        today = datetime.date.today()
        start_date = st.date_input("Start Date", value=today + datetime.timedelta(days=14))
        end_date = start_date + datetime.timedelta(days=duration_days - 1)
        
    budget_tier = st.selectbox(
        "Budget Tier",
        options=list(config.BUDGET_TIERS.keys()),
        index=1
    )
    
    travel_party = st.selectbox(
        "Travel Party",
        options=list(config.TRAVEL_PARTIES.keys()),
        index=1
    )
    
    pace = st.selectbox(
        "Travel Pace",
        options=list(config.TRAVEL_PACES.keys()),
        index=1
    )
    
    currency = st.selectbox(
        "Preferred Currency",
        options=list(config.CURRENCIES.keys()),
        index=0
    )
    
    interests = st.multiselect(
        "Core Interests & Passions",
        options=config.INTEREST_OPTIONS,
        default=["Food & Culinary Trails", "History & Ancient Heritage", "Local Markets & Shopping"]
    )
    
    generate_btn = st.button("🚀 Generate Optimized Itinerary", type="primary", use_container_width=True)
    
    st.markdown("---")
    st.markdown(f"""
    <div style="font-size: 11px; color: #94A3B8; text-align: center;">
        Platform ID: <code>{config.PLATFORM_ID}</code><br/>
        Zero External DB Dependencies
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# Action: Generate Itinerary Trigger
# ---------------------------------------------------------
if generate_btn:
    with st.spinner(f"Architecting geographically clustered itinerary for {destination}..."):
        try:
            itinerary = generate_itinerary(
                destination=destination,
                duration_days=duration_days,
                start_date=start_date.strftime("%b %d, %Y"),
                end_date=end_date.strftime("%b %d, %Y"),
                budget_tier=budget_tier,
                travel_party=travel_party,
                pace=pace,
                interests=interests,
                currency=currency,
                provider=provider_code,
                api_key=api_key,
            )
            st.session_state.current_itinerary = itinerary
            st.success(f"✨ Itinerary for {destination} successfully generated with {itinerary.get('anti_transit_fatigue_score', 95)}% transit efficiency!")
        except Exception as e:
            st.error(f"Error generating itinerary: {e}")

# ---------------------------------------------------------
# Main App Header
# ---------------------------------------------------------
st.markdown(f"""
<div class="platform-header">
    <div class="platform-tag">SaaS Capstone Project 4 &nbsp;|&nbsp; ID: {config.PLATFORM_ID}</div>
    <h1 class="platform-title">{config.PROJECT_NAME}</h1>
    <p style="margin: 4px 0 0 0; color: #E2E8F0; font-size: 13px;">
        Intelligent Day-by-Day Vacation Architect &bull; Geographic Attraction Clustering &bull; Dynamic Activity Swapping &bull; Offline PDF Guides
    </p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Tabs Layout
# ---------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "🌟 Smart Destination Recommender",
    "🗺️ Day-by-Day Clustered Itinerary",
    "🎨 Vibe Customization & Dynamic Swap",
    "💾 Trip Management & Offline PDF Export"
])

# =========================================================
# TAB 1: Smart Destination Recommender (Epic 3)
# =========================================================
with tab1:
    st.markdown("### 🌟 Smart Destination Recommender")
    st.caption("Not sure where to travel? Discover top 3 destination cities tailored to your travel mood, season, budget, and party.")
    
    col_r1, col_r2, col_r3 = st.columns([1.5, 1, 1])
    with col_r1:
        reco_vibe = st.selectbox(
            "What's your primary travel vibe / mood?",
            options=config.VIBE_CATEGORIES,
            index=0
        )
    with col_r2:
        reco_season = st.selectbox(
            "Travel Season / Timeframe",
            options=["Spring Blossoms & Mild Days", "Sunny Summer & Beach Vibes", "Autumn Foliage & Harvest", "Cozy Winter / Snow Sports"],
            index=0
        )
    with col_r3:
        reco_budget = st.selectbox(
            "Budget Preference",
            options=list(config.BUDGET_TIERS.keys()),
            index=1,
            key="reco_budget_select"
        )
        
    find_dest_btn = st.button("✨ Discover Top 3 Matching Destinations", type="primary")
    
    if find_dest_btn:
        with st.spinner("Analyzing global destinations matching your vibe and budget..."):
            recs = get_destination_recommendations(
                vibe=reco_vibe,
                budget_tier=reco_budget,
                travel_party=travel_party,
                travel_season=reco_season,
                interests=interests,
                currency=currency,
                provider=provider_code,
                api_key=api_key,
            )
            st.session_state.recommended_destinations = recs

    # Display recommendations
    recs = st.session_state.recommended_destinations
    if recs:
        st.markdown(f"#### Top 3 Curated Destinations for *'{reco_vibe}'*")
        reco_cols = st.columns(len(recs))
        
        for idx, item in enumerate(recs):
            with reco_cols[idx]:
                city = item.get("city", "Destination")
                country = item.get("country", "")
                score = item.get("match_score", 95)
                tags = " ".join([f"`{t}`" for t in item.get("vibe_tags", [])])
                budget_str = item.get("daily_budget_formatted", "$100/day")
                season_str = item.get("best_season", "Year-round")
                why = item.get("why_it_matches", "")
                must = item.get("must_experience", "")
                
                st.markdown(f"""
                <div class="reco-card">
                    <span class="reco-score">★ {score}% Match</span>
                    <h3 style="margin: 0; color: #1E293B;">{city}</h3>
                    <p style="color: #64748B; font-size: 13px; margin: 2px 0 10px 0;">📍 {country}</p>
                    <div style="margin-bottom: 8px;">{tags}</div>
                    <p style="font-size: 13px; color: #334155; margin-bottom: 8px;">{why}</p>
                    <div style="background: #F8FAFC; padding: 10px; border-radius: 8px; font-size: 12px; margin-bottom: 10px;">
                        <b>🌟 Must Experience:</b> {must}<br/>
                        <b>🗓️ Best Season:</b> {season_str}<br/>
                        <b>💰 Est. Daily Budget:</b> {budget_str}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"🚀 Plan Trip to {city}", key=f"select_reco_{idx}", use_container_width=True):
                    st.session_state.destination_input = f"{city}, {country}"
                    with st.spinner(f"Generating optimized itinerary for {city}..."):
                        new_itinerary = generate_itinerary(
                            destination=f"{city}, {country}",
                            duration_days=duration_days,
                            start_date=start_date.strftime("%b %d, %Y"),
                            end_date=end_date.strftime("%b %d, %Y"),
                            budget_tier=reco_budget,
                            travel_party=travel_party,
                            pace=pace,
                            interests=interests,
                            currency=currency,
                            provider=provider_code,
                            api_key=api_key,
                        )
                        st.session_state.current_itinerary = new_itinerary
                        st.success(f"Trip planned for {city}! Switch to Tab 2 to view your day-wise itinerary.")
                        st.rerun()
    else:
        st.info("👆 Click **'Discover Top 3 Matching Destinations'** above to receive AI vibe-matched recommendations.")

# =========================================================
# TAB 2: Day-by-Day Clustered Itinerary (Epic 4)
# =========================================================
with tab2:
    itinerary = st.session_state.current_itinerary
    
    if not itinerary:
        st.markdown("""
        <div style="text-align: center; padding: 40px 20px; background: #FFFFFF; border: 1px dashed #CBD5E1; border-radius: 16px;">
            <span style="font-size: 48px;">🗺️</span>
            <h3 style="color: #1E293B; margin-top: 10px;">No Active Itinerary Generated Yet</h3>
            <p style="color: #64748B; max-width: 500px; margin: 0 auto 20px auto;">
                Select your destination and preferences in the sidebar and click <b>'Generate Optimized Itinerary'</b>, 
                or discover tailored destinations in <b>Tab 1</b>.
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Itinerary Header Metrics
        dest_name = itinerary.get("destination", "Destination")
        days = itinerary.get("days", [])
        total_cost_fmt = f"${itinerary.get('total_cost', 0):,.0f}" if itinerary.get("currency") == "USD" else f"{itinerary.get('currency_symbol', '')}{itinerary.get('total_cost_local', 0):,.0f} (~${itinerary.get('total_cost', 0):,.0f})"
        target_budget_fmt = f"${itinerary.get('target_total_budget_usd', 0):,.0f}" if itinerary.get("currency") == "USD" else f"{itinerary.get('currency_symbol', '')}{itinerary.get('target_total_budget_local', 0):,.0f} (~${itinerary.get('target_total_budget_usd', 0):,.0f})"
        fatigue_score = itinerary.get("anti_transit_fatigue_score", 95)
        clustering_info = itinerary.get("clustering_metrics", {})
        
        # 4 Core KPI Metric Cards
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        with col_m1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-val">{len(days)} Days</div>
                <div class="metric-label">{itinerary.get('travel_party', 'Traveler')}</div>
            </div>
            """, unsafe_allow_html=True)
        with col_m2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-val">{total_cost_fmt}</div>
                <div class="metric-label">Estimated Spend</div>
            </div>
            """, unsafe_allow_html=True)
        with col_m3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-val">{fatigue_score}%</div>
                <div class="metric-label">Transit Efficiency</div>
            </div>
            """, unsafe_allow_html=True)
        with col_m4:
            hours_saved = clustering_info.get("hours_saved", 3.5)
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-val">{hours_saved} hrs</div>
                <div class="metric-label">Transit Time Saved</div>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<br/>", unsafe_allow_html=True)
        
        # Transit Efficiency & Budget Gauge Bar
        col_g1, col_g2 = st.columns([1.5, 1])
        with col_g1:
            st.markdown(f"**⚡ Anti-Transit Fatigue Strategy:** {itinerary.get('transit_advice', 'Attractions grouped into tight geographic clusters to prevent cross-city backtracking.')}")
            st.caption(f"Status: {clustering_info.get('fatigue_status', 'Optimized')} &bull; Est. Total Route Distance: {clustering_info.get('total_km', 8.5)} km")
        with col_g2:
            target_val = itinerary.get("target_total_budget_usd", 1)
            spend_val = itinerary.get("total_cost", 0)
            pct = min(1.0, spend_val / max(1.0, target_val))
            st.progress(pct, text=f"Budget: {total_cost_fmt} of {target_budget_fmt} target")
            
        st.markdown("---")
        
        # Interactive Map Section
        st.markdown("#### 📍 Interactive Route & Neighborhood Cluster Map")
        map_type = st.radio("Map Visualization Engine", options=["Interactive 3D Deck (PyDeck)", "Route Trail (Plotly Map)"], horizontal=True)
        
        center_lat = itinerary.get("center_lat", 48.8566)
        center_lon = itinerary.get("center_lon", 2.3522)
        
        try:
            if "PyDeck" in map_type:
                deck = build_pydeck_map(days, center_lat, center_lon)
                st.pydeck_chart(deck)
            else:
                fig = build_plotly_map(days, center_lat, center_lon)
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.warning(f"Map rendering fallback: {e}")
            
        st.markdown("---")
        
        # Day-by-Day Clustered Cards
        st.markdown(f"### 🗓️ Day-by-Day Optimized Schedule for {dest_name}")
        
        for day in days:
            day_num = day.get("day", 1)
            cluster = day.get("cluster_name", f"Zone {day_num}")
            theme = day.get("theme", "Exploration")
            day_cost = day.get("estimated_daily_cost_usd", 0)
            day_cost_fmt = f"${day_cost:,.0f}" if itinerary.get("currency") == "USD" else f"{itinerary.get('currency_symbol', '')}{day.get('estimated_daily_cost_local', 0):,.0f} (~${day_cost:,.0f})"
            cumul_cost_fmt = f"${day.get('cumulative_cost_usd', 0):,.0f}" if itinerary.get("currency") == "USD" else f"{itinerary.get('currency_symbol', '')}{day.get('cumulative_cost_local', 0):,.0f}"
            
            with st.container():
                st.markdown(f"""
                <div class="day-card">
                    <div class="day-header">
                        <div>
                            <span style="font-size: 18px; font-weight: 800; color: #1E293B;">Day {day_num}</span> &nbsp;
                            <span class="cluster-badge">📍 {cluster}</span>
                        </div>
                        <div style="text-align: right; font-size: 13px; color: #64748B;">
                            Daily Est: <b style="color: #E05A47;">{day_cost_fmt}</b> &bull; Cumulative: <b>{cumul_cost_fmt}</b>
                        </div>
                    </div>
                    <p style="font-size: 13px; color: #64748B; margin-top: -6px; margin-bottom: 12px;">
                        <i>Theme: {theme}</i> &bull; {day.get('cluster_transit_summary', '')}
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # Render 4 slots in 2 columns
                slots = day.get("slots", [])
                scol1, scol2 = st.columns(2)
                
                for s_idx, slot in enumerate(slots):
                    target_col = scol1 if s_idx % 2 == 0 else scol2
                    with target_col:
                        tags_html = " ".join([f"<span class='tag-badge'>#{t}</span>" for t in slot.get("tags", [])])
                        st.markdown(f"""
                        <div class="slot-card">
                            <div class="slot-time">⏰ {slot.get('time_slot', 'Activity')} &bull; {slot.get('time_window', '')}</div>
                            <div class="slot-title">{slot.get('title', 'Attraction')}</div>
                            <div class="slot-desc">{slot.get('description', '')}</div>
                            <div class="slot-meta">
                                <span>🚇 {slot.get('transit_tip', 'Nearby')}</span>
                                <span style="font-weight: 700; color: #E05A47;">💰 {slot.get('cost_formatted', '$0')}</span>
                            </div>
                            <div style="margin-top: 6px;">{tags_html}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                st.markdown("<br/>", unsafe_allow_html=True)

# =========================================================
# TAB 3: Vibe Customization & Dynamic Activity Swap (Epic 4)
# =========================================================
with tab3:
    st.markdown("### 🎨 Vibe Customization & Dynamic Activity Swap")
    st.caption("Customize specific time slots on the fly without wiping or disturbing the rest of your vacation itinerary.")
    
    itinerary = st.session_state.current_itinerary
    if not itinerary:
        st.info("⚠️ Please generate or load an itinerary first in Tab 2 to use dynamic activity swapping.")
    else:
        days = itinerary.get("days", [])
        day_options = [f"Day {d.get('day')}: {d.get('cluster_name')}" for d in days]
        
        col_s1, col_s2 = st.columns([1, 1.2])
        with col_s1:
            selected_day_str = st.selectbox("Select Day to Modify", options=day_options)
            selected_day_num = int(selected_day_str.split(":")[0].replace("Day", "").strip())
            
            selected_slot_name = st.selectbox(
                "Select Time Slot to Swap",
                options=config.TIME_SLOTS
            )
            
            # Find existing slot
            curr_day = next((d for d in days if d.get("day") == selected_day_num), None)
            curr_slot = None
            if curr_day:
                curr_slot = next((s for s in curr_day.get("slots", []) if s.get("time_slot") == selected_slot_name), None)
                
            if curr_slot:
                st.markdown(f"""
                <div style="background: #F8FAFC; border: 1px solid #CBD5E1; border-radius: 10px; padding: 14px; margin-top: 10px;">
                    <span style="font-size: 11px; font-weight: 700; color: #64748B; text-transform: uppercase;">Current Activity in Slot:</span>
                    <h4 style="margin: 4px 0; color: #1E293B;">{curr_slot.get('title')}</h4>
                    <p style="font-size: 12px; color: #475569; margin: 0 0 6px 0;">{curr_slot.get('description')}</p>
                    <span style="font-size: 12px; font-weight: 700; color: #E05A47;">Current Cost: {curr_slot.get('cost_formatted')}</span>
                </div>
                """, unsafe_allow_html=True)
                
        with col_s2:
            st.markdown("#### Choose New Vibe or Requirement")
            swap_preset = st.selectbox(
                "Quick Vibe Presets",
                options=["(Custom Prompt Below)"] + QUICK_SWAP_PRESETS
            )
            
            custom_prompt_text = st.text_area(
                "Custom Swap Instruction",
                value="" if swap_preset != "(Custom Prompt Below)" else "Find an authentic vegetarian dinner spot with candlelit ambience",
                placeholder="e.g. 'Swap museum for outdoor local artisan market' or 'Find kid-friendly indoor activity'",
                help="The AI will keep the replacement in the same neighborhood cluster to maintain zero transit fatigue."
            )
            
            chosen_prompt = custom_prompt_text if swap_preset == "(Custom Prompt Below)" else swap_preset
            
            swap_btn = st.button("🔄 Swap This Activity Slot", type="primary", use_container_width=True)
            
            if swap_btn:
                if not chosen_prompt:
                    st.warning("Please enter or select a swap instruction.")
                else:
                    with st.spinner(f"Swapping {selected_slot_name} on Day {selected_day_num}..."):
                        try:
                            updated_itinerary = swap_activity_slot(
                                itinerary=itinerary,
                                day_number=selected_day_num,
                                time_slot=selected_slot_name,
                                swap_prompt=chosen_prompt,
                                currency=itinerary.get("currency", "USD"),
                                provider=provider_code,
                                api_key=api_key,
                            )
                            st.session_state.current_itinerary = updated_itinerary
                            st.success(f"🎉 Successfully swapped '{selected_slot_name}' on Day {selected_day_num}! Itinerary and costs recalculated.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error during activity swap: {e}")

# =========================================================
# TAB 4: Trip Management & Offline PDF Export (Epic 5)
# =========================================================
with tab4:
    st.markdown("### 💾 Trip Management & Offline PDF Export")
    st.caption("Persist your itineraries locally to SQLite, manage trip history, and generate 1-click printable offline PDF travel guides.")
    
    itinerary = st.session_state.current_itinerary
    
    col_p1, col_p2 = st.columns([1.2, 1])
    
    with col_p1:
        st.markdown("#### 📄 1-Click Offline PDF Travel Guide")
        if not itinerary:
            st.info("Generate an itinerary in Tab 2 to enable PDF export.")
        else:
            dest_name = itinerary.get("destination", "Trip")
            st.markdown(f"""
            Generate a high-resolution, wanderlust-formatted offline travel guide for **{dest_name}** including:
            - **Executive Summary** & anti-transit fatigue score
            - **Structured Day-by-Day Itinerary Tables** with cluster tips and costs
            - **Budget Breakdown & Currency Conversion**
            - **Tailored Packing Checklist**
            - **Emergency Contacts Checklist** (police, medical, tourist hotline)
            """)
            
            try:
                pdf_bytes = generate_pdf_itinerary(itinerary)
                file_name = f"Travel_Guide_{dest_name.replace(' ', '_').replace(',', '')}.pdf"
                
                st.download_button(
                    label="📥 Download Travel Guide PDF (ReportLab)",
                    data=pdf_bytes,
                    file_name=file_name,
                    mime="application/pdf",
                    type="primary",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Error compiling PDF: {e}")
                
            st.markdown("---")
            
            # Save Trip Section
            st.markdown("#### 💾 Save Current Trip to Local Database")
            save_name = st.text_input("Trip Title", value=itinerary.get("trip_title", f"{dest_name} Vacation"))
            save_notes = st.text_area("Personal Notes / Reminders", placeholder="Hotel confirmation numbers, flight details, packing reminders...")
            
            if st.button("💾 Save Trip to SQLite", use_container_width=True):
                itinerary["trip_title"] = save_name
                itinerary["notes"] = save_notes
                saved_id = save_trip(itinerary)
                st.success(f"Trip saved successfully to local SQLite database! (ID: {saved_id[:8]}...)")
                st.rerun()

    with col_p2:
        st.markdown("#### 🎒 Emergency & Packing Checklist Preview")
        if itinerary:
            st.markdown("**Essential Packing Checklist:**")
            for item in itinerary.get("packing_essentials", []):
                st.markdown(f"- [ ] {item}")
                
            st.markdown("**Local Emergency Contacts:**")
            em = itinerary.get("emergency_contacts", {})
            st.markdown(f"- 🚨 **Universal Emergency:** `{em.get('emergency_universal', '112 / 911')}`")
            st.markdown(f"- 👮 **Police / Tourist Desk:** `{em.get('police', 'Local Police')}`")
            st.markdown(f"- 🚑 **Medical / Ambulance:** `{em.get('ambulance_medical', 'General Hospital')}`")
            st.markdown(f"- ℹ️ **Tourist Helpline:** `{em.get('tourist_helpline', 'Tourist Support')}`")
        else:
            st.info("Checklist preview will appear once an itinerary is active.")
            
    st.markdown("---")
    
    # Trip History Section
    st.markdown("### 🗄️ Saved Trips History (SQLite Database)")
    saved_trips = list_trips()
    
    if not saved_trips:
        st.info("No saved trips in database yet. Save your current trip above!")
    else:
        st.markdown(f"Found **{len(saved_trips)}** saved trip(s) in local storage:")
        
        for t in saved_trips:
            t_id = t["trip_id"]
            with st.expander(f"📍 {t['name']} ({t['destination']}) — {t['duration_days']} Days | {t['budget_tier']}"):
                col_th1, col_th2, col_th3 = st.columns([2, 1, 1])
                with col_th1:
                    st.markdown(f"""
                    **Dates:** {t['start_date']} to {t['end_date']}<br/>
                    **Party:** {t['travel_party']} &bull; **Pace:** {t['pace']}<br/>
                    **Saved On:** {t['created_at']}<br/>
                    **Notes:** {t['notes'] or 'None'}
                    """, unsafe_allow_html=True)
                with col_th2:
                    if st.button("📂 Load Trip", key=f"load_{t_id}", use_container_width=True):
                        loaded = get_trip(t_id)
                        if loaded:
                            st.session_state.current_itinerary = loaded
                            st.success(f"Trip '{t['name']}' loaded into active workspace!")
                            st.rerun()
                with col_th3:
                    if st.button("🗑️ Delete", key=f"del_{t_id}", use_container_width=True):
                        delete_trip(t_id)
                        st.warning(f"Trip deleted.")
                        st.rerun()
                        
    # Backup & Restore
    st.markdown("---")
    with st.expander("⚙️ Database Backup & JSON Export / Import"):
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            all_json = export_all_trips_json()
            st.download_button(
                "📤 Export All Trips (JSON Backup)",
                data=all_json,
                file_name="trips_backup.json",
                mime="application/json",
                use_container_width=True
            )
        with col_b2:
            uploaded_file = st.file_uploader("📥 Import Trips from JSON", type=["json"])
            if uploaded_file is not None:
                content = uploaded_file.read().decode("utf-8")
                count = import_trips_json(content)
                st.success(f"Successfully imported {count} trip(s) into database!")
                st.rerun()
