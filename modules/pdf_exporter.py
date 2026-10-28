"""
ReportLab Offline Travel Guide PDF Exporter (Tab 4 / Epic 5).
Generates a beautifully formatted, multi-page offline PDF travel itinerary
with cover header, day-by-day tables, budget breakdown, and emergency checklist.
"""

import io
from typing import Dict, Any
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether
)
import config

# Color constants
COLOR_PRIMARY = colors.HexColor("#E05A47")    # Terracotta
COLOR_SECONDARY = colors.HexColor("#2A7B88")  # Aegean Blue
COLOR_SLATE = colors.HexColor("#1E293B")      # Dark Slate
COLOR_LIGHT_BG = colors.HexColor("#F8FAFC")   # Light Slate
COLOR_BORDER = colors.HexColor("#E2E8F0")     # Light Border
COLOR_GOLD = colors.HexColor("#F5A623")       # Accent Amber
COLOR_MUTED = colors.HexColor("#64748B")      # Slate Muted


def generate_pdf_itinerary(itinerary: Dict[str, Any]) -> bytes:
    """
    Compiles an itinerary dictionary into a production-grade PDF binary document.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Paragraph Styles
    title_style = ParagraphStyle(
        "CoverTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=COLOR_PRIMARY,
        spaceAfter=4,
    )
    
    subtitle_style = ParagraphStyle(
        "CoverSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=COLOR_SECONDARY,
        spaceAfter=8,
    )
    
    meta_style = ParagraphStyle(
        "MetaText",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=COLOR_SLATE,
    )
    
    h2_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=COLOR_SLATE,
        spaceBefore=10,
        spaceAfter=6,
    )
    
    day_header_style = ParagraphStyle(
        "DayHeading",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=colors.white,
    )
    
    cell_bold_style = ParagraphStyle(
        "CellBold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=COLOR_SLATE,
    )
    
    cell_normal_style = ParagraphStyle(
        "CellNormal",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=10.5,
        textColor=COLOR_SLATE,
    )
    
    cell_muted_style = ParagraphStyle(
        "CellMuted",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=7.5,
        leading=9.5,
        textColor=COLOR_MUTED,
    )

    story = []
    
    dest = itinerary.get("destination", "Wanderlust Destination")
    trip_title = itinerary.get("trip_title") or f"Personalized Itinerary: {dest}"
    duration = itinerary.get("duration_days", len(itinerary.get("days", [])))
    start_date = itinerary.get("start_date", "TBD")
    end_date = itinerary.get("end_date", "TBD")
    budget_tier = itinerary.get("budget_tier", "Moderate / Balanced")
    party = itinerary.get("travel_party", "Solo Explorer")
    pace = itinerary.get("pace", "Moderate / Balanced")
    currency = itinerary.get("currency", "USD")
    total_cost_fmt = f"${itinerary.get('total_cost', 0):,.0f}" if currency == "USD" else f"{itinerary.get('currency_symbol', '')}{itinerary.get('total_cost_local', 0):,.0f} (~${itinerary.get('total_cost', 0):,.0f})"
    fatigue_score = itinerary.get("anti_transit_fatigue_score", 95)
    
    # 1. Header Banner
    story.append(Paragraph("TRAVEL ITINERARY & OFFLINE FIELD GUIDE", subtitle_style))
    story.append(Paragraph(trip_title, title_style))
    story.append(Paragraph(f"<b>Platform ID:</b> {config.PLATFORM_ID} &nbsp;|&nbsp; <b>Framework:</b> {config.CAPSTONE_ID}", cell_muted_style))
    story.append(Spacer(1, 6))
    
    # Summary Box Table
    summary_data = [
        [
            Paragraph(f"<b>Destination:</b> {dest}", meta_style),
            Paragraph(f"<b>Duration:</b> {duration} Days", meta_style),
            Paragraph(f"<b>Dates:</b> {start_date} – {end_date}", meta_style)
        ],
        [
            Paragraph(f"<b>Travel Party:</b> {party}", meta_style),
            Paragraph(f"<b>Pace:</b> {pace}", meta_style),
            Paragraph(f"<b>Budget Tier:</b> {budget_tier}", meta_style)
        ],
        [
            Paragraph(f"<b>Total Budget:</b> {total_cost_fmt}", meta_style),
            Paragraph(f"<b>Anti-Fatigue Score:</b> {fatigue_score}% Efficiency", meta_style),
            Paragraph(f"<b>Clustering:</b> Neighborhood Optimized", meta_style)
        ]
    ]
    summary_table = Table(summary_data, colWidths=[180, 180, 180])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), COLOR_LIGHT_BG),
        ("BOX", (0, 0), (-1, -1), 1, COLOR_BORDER),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 10))
    
    # Transit Strategy Note
    transit_advice = itinerary.get("transit_advice", f"Attractions in {dest} are grouped by geographic zones to prevent backtracking.")
    strategy_text = f"<b>Transit Efficiency Strategy:</b> {transit_advice}"
    story.append(Paragraph(strategy_text, cell_normal_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_PRIMARY, spaceBefore=4, spaceAfter=8))
    
    # 2. Day-by-Day Itinerary Tables
    story.append(Paragraph("Day-by-Day Geographic Clustered Schedule", h2_style))
    
    days = itinerary.get("days", [])
    for day in days:
        day_num = day.get("day", 1)
        cluster = day.get("cluster_name", f"Zone {day_num}")
        theme = day.get("theme", "Exploration")
        day_subtotal = day.get("estimated_daily_cost_usd", 0)
        
        # Day Header Bar
        header_text = f"DAY {day_num}: {cluster.upper()} — <i>{theme}</i>"
        day_header_table = Table(
            [[Paragraph(header_text, day_header_style)]],
            colWidths=[540]
        )
        day_header_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), COLOR_SECONDARY),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ]))
        
        # Slots rows
        slot_rows = [
            [
                Paragraph("<b>Time / Slot</b>", cell_bold_style),
                Paragraph("<b>Activity & Experience Description</b>", cell_bold_style),
                Paragraph("<b>Transit Tip / Connection</b>", cell_bold_style),
                Paragraph("<b>Cost</b>", cell_bold_style)
            ]
        ]
        
        for s in day.get("slots", []):
            slot_title = f"<b>{s.get('title', 'Attraction')}</b><br/>{s.get('description', '')}"
            slot_rows.append([
                Paragraph(f"<b>{s.get('time_slot', '')}</b><br/>{s.get('time_window', '')}", cell_normal_style),
                Paragraph(slot_title, cell_normal_style),
                Paragraph(s.get("transit_tip", "Nearby in cluster"), cell_muted_style),
                Paragraph(s.get("cost_formatted", "$0"), cell_bold_style)
            ])
            
        # Day Table
        slots_table = Table(slot_rows, colWidths=[110, 250, 120, 60])
        slots_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), COLOR_LIGHT_BG),
            ("GRID", (0, 0), (-1, -1), 0.5, COLOR_BORDER),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        
        day_flowables = [
            day_header_table,
            slots_table,
            Spacer(1, 8)
        ]
        story.append(KeepTogether(day_flowables))
        
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=0.8, color=COLOR_BORDER, spaceBefore=4, spaceAfter=8))
    
    # 3. Budget Summary & Emergency Contacts (2 columns side by side)
    story.append(Paragraph("Budget Summary & Travel Safety Kit", h2_style))
    
    # Build Packing & Emergency items
    packing_items = itinerary.get("packing_essentials", [
        "Walking footwear", "Universal travel adapter", "Weather layer / jacket"
    ])
    packing_html = "<b>Essential Packing Checklist:</b><br/>" + "<br/>".join([f"• {item}" for item in packing_items[:5]])
    
    emergencies = itinerary.get("emergency_contacts", {})
    emergency_html = (
        "<b>Emergency Contacts:</b><br/>"
        f"• Universal Emergency: <b>{emergencies.get('emergency_universal', '112 / 911')}</b><br/>"
        f"• Police / Tourist Desk: {emergencies.get('police', 'Local Police HQ')}<br/>"
        f"• Medical Emergency: {emergencies.get('ambulance_medical', 'General Hospital')}<br/>"
        f"• Tourist Helpline: {emergencies.get('tourist_helpline', 'Local Tourist Info')}"
    )
    
    budget_col_html = (
        "<b>Financial Summary:</b><br/>"
        f"• Total Estimated Spend: <b>{total_cost_fmt}</b><br/>"
        f"• Target Budget: ${itinerary.get('target_total_budget_usd', 0):,.0f}<br/>"
        f"• Budget Status: {'On Track (Within Budget)' if itinerary.get('budget_variance_usd', 0) >= 0 else 'Above Baseline'}<br/>"
        f"• Average Cost / Day: ${itinerary.get('total_cost', 0) / max(1, duration):,.0f}"
    )
    
    footer_table = Table(
        [
            [
                Paragraph(budget_col_html, cell_normal_style),
                Paragraph(packing_html, cell_normal_style),
                Paragraph(emergency_html, cell_normal_style)
            ]
        ],
        colWidths=[180, 180, 180]
    )
    footer_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), COLOR_LIGHT_BG),
        ("BOX", (0, 0), (-1, -1), 1, COLOR_PRIMARY),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(footer_table)
    
    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
