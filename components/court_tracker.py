import streamlit as st
import re
from datetime import datetime
from db import get_all_courts, occupy_court, release_court, get_court_stats
from models import USAGE_DURATIONS
from components.ui_helpers import format_iso_time


def render_court_tracker():
    st.markdown("### Campus Courts & Facility Availability Tracker")
    st.caption("Real-time occupancy status for all 14 campus playing facilities. Check availability before heading over.")
    
    court_stats = get_court_stats()
    
    # KPI Metric Bar
    st.markdown(f"""
    <div class="stat-grid">
        <div class="stat-card">
            <div class="label">Total Facilities</div>
            <div class="value" style="color: #0F2942;">{court_stats.get('total', 14)}</div>
        </div>
        <div class="stat-card" style="border-left: 4px solid #10B981 !important;">
            <div class="label">Available Now</div>
            <div class="value" style="color: #059669;">{court_stats.get('available', 0)}</div>
        </div>
        <div class="stat-card" style="border-left: 4px solid #EF4444 !important;">
            <div class="label">Currently Occupied</div>
            <div class="value" style="color: #DC2626;">{court_stats.get('occupied', 0)}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    all_courts = get_all_courts()
    
    # Filter by Sport Category
    sport_types = ["All Sports / Venues"] + sorted(list(set(c['sport_type'] for c in all_courts)))
    
    selected_sport = st.selectbox(
        "Filter Facilities by Sport / Venue:",
        options=sport_types,
        index=0,
        help="Filter campus courts and grounds by sport."
    )
        
    filtered_courts = all_courts
    if selected_sport != "All Sports / Venues":
        filtered_courts = [c for c in all_courts if c['sport_type'] == selected_sport]
        
    st.markdown(f"#### Active Facilities ({len(filtered_courts)} Courts & Grounds)")
    
    # 2-column responsive layout for courts
    cols = st.columns(2, gap="large")
    
    for idx, court in enumerate(filtered_courts):
        col_target = cols[idx % 2]
        is_occupied = court['status'] == 'Occupied'
        status_color = "#991B1B" if is_occupied else "#065F46"
        status_bg = "#FEF2F2" if is_occupied else "#ECFDF5"
        status_border = "#FECACA" if is_occupied else "#A7F3D0"
        status_text = "Occupied / In Play" if is_occupied else "Available to Play"
        
        with col_target:
            with st.container(border=True):
                # Header with Status
                h1, h2 = st.columns([2, 1.2])
                with h1:
                    st.markdown(f"### {court['court_name']}")
                    st.markdown(f"**Venue:** `{court['location_venue']}` &bull; **Sport:** `{court['sport_type']}`")
                with h2:
                    st.markdown(f"""
                    <div style="text-align: right; margin-top: 0.25rem;">
                        <span style="display: inline-block; padding: 0.35rem 0.75rem; border-radius: 9999px; font-weight: 700; font-size: 0.82rem; background: {status_bg}; color: {status_color}; border: 1px solid {status_border}; font-family: Arial, sans-serif;">
                            {status_text}
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
                
                if court.get('notes'):
                    st.caption(f"Info: {court['notes']}")
                    
                st.divider()
                
                if is_occupied:
                    # Occupant Info Card
                    st.markdown(f"""
                    <div style="background: #EFF6FF; border: 1px solid #BFDBFE; border-left: 4px solid #1D4ED8; border-radius: 8px; padding: 0.85rem; margin-bottom: 0.75rem;">
                        <div style="font-size: 0.78rem; color: #1E3A8A; font-weight: 700; text-transform: uppercase; font-family: Arial, sans-serif;">Current Player Info</div>
                        <div style="font-size: 1.05rem; font-weight: 700; color: #0F2942; margin-top: 0.2rem; font-family: Arial, sans-serif;">
                            {court['current_occupant']} <span style="font-size: 0.85rem; color: #475569; font-weight: normal;">({court['dm_number']})</span>
                        </div>
                        <div style="font-size: 0.85rem; color: #334155; margin-top: 0.35rem; font-family: Arial, sans-serif;">
                            Phone: <strong>{court['contact_number']}</strong> &bull; Room: <strong>{court['hostel_room']}</strong>
                        </div>
                        <div style="font-size: 0.82rem; color: #64748B; margin-top: 0.25rem; font-family: Arial, sans-serif;">
                            Playing Since: <strong>{format_iso_time(court['occupied_since'])}</strong> &bull; Duration: <strong>{court['intended_duration']}</strong>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"Release Court ({court['court_name']})", key=f"rel_{court['court_id']}", use_container_width=True):
                        with st.spinner("Releasing court..."):
                            ok_rel, msg_rel = release_court(court['court_id'], released_by="Campus User / Guard")
                            if ok_rel:
                                st.success(msg_rel)
                                st.rerun()
                            else:
                                st.error(msg_rel)
                else:
                    # Direct Check-in Form in Clean Card
                    st.markdown("**Check-In / Start Session**")
                    with st.form(key=f"occupy_form_{court['court_id']}"):
                        c1, c2 = st.columns(2)
                        with c1:
                            player_name = st.text_input("Lead Player Name", placeholder="e.g., Ananya Roy", key=f"name_{court['court_id']}")
                            dm_num = st.text_input("DM Number", placeholder="e.g., DM2024-2041", key=f"dm_{court['court_id']}")
                        with c2:
                            phone_num = st.text_input("Mobile Number", placeholder="e.g., 9876543210", key=f"ph_{court['court_id']}")
                            room_num = st.text_input("Hostel Room", placeholder="e.g., MG Block - 104", key=f"rm_{court['court_id']}")
                            
                        duration = st.selectbox("Play Duration", options=USAGE_DURATIONS, index=2, key=f"dur_{court['court_id']}")
                        
                        checkin_btn = st.form_submit_button(f"Confirm Check-In to {court['court_name']}", type="primary", use_container_width=True)
                        
                        if checkin_btn:
                            if not player_name.strip():
                                st.error("Lead Player Name is required.")
                            elif not dm_num.strip():
                                st.error("DM Number is required.")
                            elif not phone_num.strip():
                                st.error("Mobile Number is required.")
                            elif not room_num.strip():
                                st.error("Hostel Room is required.")
                            else:
                                clean_p = re.sub(r"[^\d]", "", phone_num.strip())
                                with st.spinner("Checking in..."):
                                    ok_occ, msg_occ = occupy_court(
                                        court_id=court['court_id'],
                                        student_name=player_name,
                                        dm_number=dm_num,
                                        contact_number=clean_p,
                                        hostel_room=room_num,
                                        intended_duration=duration,
                                        notes=""
                                    )
                                    if ok_occ:
                                        st.success(msg_occ)
                                        st.rerun()
                                    else:
                                        st.error(msg_occ)
