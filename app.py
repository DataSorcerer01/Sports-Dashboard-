import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="Sports Equipment & Facility Digital Management System",
    page_icon="??",
    layout="wide",
    initial_sidebar_state="expanded"
)

from db import init_db, expire_stale_requests, seed_database, get_inventory_stats, get_court_stats
from components.ui_helpers import load_custom_css, render_header, render_kpi_bar, render_how_to_use_guide
from components.student_portal import render_student_portal
from components.court_tracker import render_court_tracker
from components.guard_dashboard import render_guard_dashboard
from components.inventory_admin import render_inventory_admin

# Initialize database and schema
init_db()
seed_database(force_reseed=False)

# Background auto-expiration check
expire_stale_requests()

# Load CSS
load_custom_css()

# Sidebar Brand & Navigation
st.sidebar.markdown("""
<div style="padding: 0.5rem 0 1.25rem 0;">
    <div style="font-size: 1.35rem; font-weight: 700; color: #0F172A;">?? Campus Sports Hub</div>
    <div style="font-size: 0.82rem; color: #64748B;">Equipment & Facility Management</div>
</div>
""", unsafe_allow_html=True)

role_view = st.sidebar.radio(
    "Select System View / Role:",
    options=[
        "?? Student Equipment Portal",
        "??? Court & Facility Tracker",
        "??? Security Guard Dashboard",
        "?? Inventory & Bulk Data Hub",
        "?? System Rules & Guide"
    ],
    index=0,
    help="Switch between equipment booking, live court occupancy tracking, guard desk authorization, and inventory management."
)

st.sidebar.divider()
st.sidebar.markdown("### Quick System Actions")
if st.sidebar.button("?? Refresh Data & Timers", use_container_width=True):
    expire_stale_requests()
    st.rerun()

if st.sidebar.button("? Reset to Campus Inventory & Courts", use_container_width=True, help="Re-seeds the database with default campus sports equipment and all 14 courts"):
    seed_database(force_reseed=True)
    st.sidebar.success("Database re-seeded with all 14 courts and updated sports inventory!")
    st.rerun()

st.sidebar.markdown("""
<div style="margin-top: 1.5rem; padding: 0.85rem; background: #FFFFFF; border-radius: 8px; border: 1px solid #E2E8F0; font-size: 0.8rem; color: #475569; box-shadow: 0 1px 2px rgba(0,0,0,0.04);">
    <strong style="color: #0F172A;">Campus Policy Rule:</strong><br>
    All equipment allocation requests have a 30-minute physical verification window at the sports desk.
</div>
""", unsafe_allow_html=True)

# Main Screen Header & KPIs
render_header(current_role=role_view)

stats = get_inventory_stats()
render_kpi_bar(stats)

# Built-in Guidance accessible from every screen
render_how_to_use_guide()

# View Routing
if role_view == "?? Student Equipment Portal":
    render_student_portal()
elif role_view == "??? Court & Facility Tracker":
    render_court_tracker()
elif role_view == "??? Security Guard Dashboard":
    render_guard_dashboard()
elif role_view == "?? Inventory & Bulk Data Hub":
    render_inventory_admin()
elif role_view == "?? System Rules & Guide":
    st.markdown("""
    ### System Business Rules & Workflow Specifications
    
    The **Sports Equipment & Facility Digital Management System** strictly enforces campus business rules:
    
    1. **Strict 30-Minute Allocation Validity**:
       - When a student submits an allocation request, 1 unit is temporarily reserved from `available_quantity` to `pending_quantity`.
       - A live **30-minute countdown timer** begins.
       - If the student presents physical ID at the security desk within 30 minutes, the guard marks the request **In Use**.
       - If 30 minutes lapse without physical verification, the background expiry engine flips status to **Expired**, releasing the unit back to **Available**.
       
    2. **Mandatory Physical ID Verification by Security**:
       - Security guards must verify physical student ID cards and match registration DM numbers before one-click checkout authorization.
       
    3. **??? Live Court & Facility Occupancy Tracking**:
       - Real-time status (`?? Available` vs `?? Occupied`) for all 14 campus courts:
         - **Badminton**: 2 Courts in Elango Complex & 2 Courts in MG Complex
         - **Pickleball**: 2 Courts
         - **Tennis**: 1 Lawn Tennis Court
         - **Table Tennis**: 2 Tables
         - **Pool & Billiards**: 1 Pool Table
         - **Carrom**: 2 Stations
         - **Outdoor**: Main Cricket Ground & Football Turf Ground
       - Allows students to see who is playing, since when, and expected duration.
       
    4. **Peer Transparency & Accountability**:
       - When equipment is **In Use**, the borrower's name, DM number, mobile number, and checkout timestamp are displayed on the **Peer Directory** to enable student-to-student handover coordination and prevent hoarding.
       
    5. **Return Condition & Equipment Health Inspection**:
       - When equipment is returned, guards inspect physical state (*Good Condition*, *Minor Wear*, *Damaged*, *Missing Parts*).
       - If damaged, unit automatically transfers from active stock to Damaged/Maintenance inventory for repairs.
    """)
