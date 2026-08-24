import streamlit as st
import re
from datetime import datetime
from db import get_all_courts, occupy_court, release_court, get_court_stats
from models import USAGE_DURATIONS
from components.ui_helpers import format_iso_time


def render_court_tracker():
    st.markdown("### ??? Live Campus Courts & Facility Availability Tracker")
    st.caption("Real-time occupancy status for campus sports courts, grounds, and recreation tables. Check if a court is currently free or occupied before heading over.")
    
    court_stats = get_court_stats()
    
    # KPI Metric Bar for Courts
    st.markdown(f"""
    <div class="stat-grid">
        <div class="stat-card">
            <div class="label">Total Facilities</div>
            <div class="value" style="color: #0F172A;">{court_stats.get('total', 14)}</div>
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
    
    col_filt, col_search = st.columns([1, 1])
    with col_filt:
        selected_sport = st.selectbox(
            "Filter Courts by Sport:",
            options=sport_types,
            index=0,
            help="Filter campus playing facilities by specific sport or venue (Badminton Elango/MG, Pickleball, Tennis, TT, Pool, Carrom, Cricket, Football)."
        )
        
    filtered_courts = all_courts
    if selected_sport != "All Sports / Venues":
        filtered_courts = [c for c in all_courts if c['sport_type'] == selected_sport]
        
    st.markdown(f"#### Active Facilities ({len(filtered_courts)} Courts & Grounds)")
    
    # 2-column responsive layout for courts
    cols = st.columns(2, gap="medium")
    
    for idx, court in enumerate(filtered_courts):
        col_target = cols[idx % 2]
        is_occupied = court['status'] == 'Occupied'
        status_color = "#DC2626" if is_occupied else "#059669"
        status_bg = "#FEF2F2" if is_occupied else "#ECFDF5"
        status_text = "?? Occupied / In Play" if is_occupied else "?? Available to Play"
        
        with col_target:
            with st.container(border=True):
                # Header with Status
                h1, h2 = st.columns([2, 1])
                with h1:
                    st.markdown(f"### {court['court_name']}")
                    st.markdown(f"?? **Venue**: `{court['location_venue']}` &bull; ?? **Sport**: `{court['sport_type']}`")
                with h2:
                    st.markdown(f"""
                    <div style="text-align: right; margin-top: 0.25rem;">
                        <span style="display: inline-block; padding: 0.35rem 0.75rem; border-radius: 9999px; font-weight: 700; font-size: 0.8rem; background: {status_bg}; color: {status_color}; border: 1px solid {status_color}40;">
                            {status_text}
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
                
                if court.get('notes'):
                    st.caption(f"?? {court['notes']}")
                    
                st.divider()
                
                if is_occupied:
                    # Display Occupant Details
                    st.markdown(f"""
                    <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 0.85rem; margin-bottom: 0.75rem;">
                        <div style="font-size: 0.8rem; color: #64748B; font-weight: 700; text-transform: uppercase;">Current Occupant Info</div>
                        <div style="font-size: 1rem; font-weight: 700; color: #0F172A; margin-top: 0.2rem;">
                            ?? {court['current_occupant']} <span style="font-size: 0.85rem; color: #475569;">({court['dm_number']})</span>
                        </div>
                        <div style="font-size: 0.85rem; color: #334155; margin-top: 0.35rem;">
                            ?? <strong>Phone:</strong> {court['contact_number']} &bull; ?? <strong>Room:</strong> {court['hostel_room']}
                        </div>
                        <div style="font-size: 0.82rem; color: #64748B; margin-top: 0.25rem;">
                            ?? <strong>Playing Since:</strong> {format_iso_time(court['occupied_since'])} &bull; ? <strong>Duration:</strong> {court['intended_duration']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"?? Release / Check Out: {court['court_name']}", key=f"rel_{court['court_id']}", use_container_width=True):
                        with st.spinner("Releasing court..."):
                            ok_rel, msg_rel = release_court(court['court_id'], released_by="Campus User / Guard")
                            if ok_rel:
                                st.success(msg_rel)
                                st.rerun()
                            else:
                                st.error(msg_rel)
                else:
                    # Court is Available -> Check-In Accordion
                    with st.expander(f"? Check-In / Start Session on {court['court_name']}", expanded=False):
                        with st.form(key=f"occupy_form_{court['court_id']}"):
                            c1, c2 = st.columns(2)
                            with c1:
                                player_name = st.text_input("Lead Player Full Name", placeholder="e.g., Ananya Roy", help="Your name as printed on student ID.")
                                dm_num = st.text_input("DM Registration Number", placeholder="e.g., DM2024-2041", help="Your unique DM roll number.")
                            with c2:
                                phone_num = st.text_input("Contact Mobile Number", placeholder="e.g., 9876543210", help="10-digit mobile number.")
                                room_num = st.text_input("Hostel Room Number", placeholder="e.g., MG Block - 104", help="Campus hostel block and room.")
                                
                            duration = st.selectbox("Intended Play Duration", options=USAGE_DURATIONS, index=2, key=f"dur_{court['court_id']}")
                            session_notes = st.text_input("Remarks / Match Type (Optional)", placeholder="e.g., 2v2 Doubles practice match", key=f"rem_{court['court_id']}")
                            
                            checkin_btn = st.form_submit_button("?? Confirm Court Check-In", type="primary", use_container_width=True)
                            
                            if checkin_btn:
                                if not player_name.strip():
                                    st.error("Lead Player Full Name is required.")
                                elif not dm_num.strip():
                                    st.error("DM Number is required.")
                                elif not phone_num.strip():
                                    st.error("Contact Mobile Number is required.")
                                elif not room_num.strip():
                                    st.error("Hostel Room Number is required.")
                                else:
                                    clean_p = re.sub(r"[^\d]", "", phone_num.strip())
                                    with st.spinner("Checking in to court..."):
                                        ok_occ, msg_occ = occupy_court(
                                            court_id=court['court_id'],
                                            student_name=player_name,
                                            dm_number=dm_num,
                                            contact_number=clean_p,
                                            hostel_room=room_num,
                                            intended_duration=duration,
                                            notes=session_notes
                                        )
                                        if ok_occ:
                                            st.success(msg_occ)
                                            st.rerun()
                                        else:
                                            st.error(msg_occ)
