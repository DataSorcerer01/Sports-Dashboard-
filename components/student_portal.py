import re
import streamlit as st
import pandas as pd
from datetime import datetime
from db import (
    get_all_equipment, create_allocation_request,
    get_pending_requests, get_active_checkouts,
    get_student_active_requests, cancel_request
)
from models import USAGE_DURATIONS
from components.ui_helpers import (
    render_status_badge, calculate_time_remaining,
    format_iso_time
)


def render_student_portal():
    st.markdown("### Student Equipment Allocation & Tracking")
    st.caption("Submit equipment requests, monitor your 30-minute verification countdown, and view active borrowers.")
    
    all_equipment = get_all_equipment()
    available_items = [eq for eq in all_equipment if eq['available_quantity'] > 0]
    
    # -------------------------------------------------------------
    # TOP BALANCED 2-COLUMN SECTION: ALLOCATION FORM + TIMER & INVENTORY
    # -------------------------------------------------------------
    col_form, col_right = st.columns([1.1, 0.9], gap="large")
    
    with col_form:
        with st.container(border=True):
            st.markdown("#### Borrower Allocation Form")
            st.caption("Select sports gear and fill in your details to reserve equipment.")
            
            if not available_items:
                st.warning("All equipment is currently in use. Check the Peer Directory below to coordinate handovers.")
            else:
                with st.form(key="student_request_form", clear_on_submit=False):
                    eq_options = {
                        f"{eq['item_name']} ({eq['available_quantity']} Available)": eq['equipment_id']
                        for eq in available_items
                    }
                    
                    selected_label = st.selectbox(
                        "Select Sports Equipment",
                        options=list(eq_options.keys()),
                        index=0,
                        help="Choose equipment item to borrow."
                    )
                    selected_eq_id = eq_options[selected_label]
                    
                    # Student Details
                    c1, c2 = st.columns(2)
                    with c1:
                        student_name = st.text_input(
                            "Student Full Name",
                            placeholder="e.g., Rahul Sharma",
                            help="Name printed on student ID."
                        )
                    with c2:
                        dm_number = st.text_input(
                            "DM Number (Student ID)",
                            placeholder="e.g., DM2024-1052",
                            help="Your unique DM roll number."
                        )
                        
                    c3, c4 = st.columns(2)
                    with c3:
                        mobile_number = st.text_input(
                            "Mobile Phone Number",
                            placeholder="e.g., 9876543210",
                            help="10-digit mobile number."
                        )
                    with c4:
                        room_number = st.text_input(
                            "Hostel Room Number",
                            placeholder="e.g., Block B - 204",
                            help="Hostel block & room number."
                        )
                        
                    intended_duration = st.selectbox(
                        "Intended Play Duration",
                        options=USAGE_DURATIONS,
                        index=1
                    )
                    
                    st.info("Submitting starts a strict 30-minute validity timer. Present your physical ID card to the guard before expiry.")
                    
                    submit_btn = st.form_submit_button("Submit Allocation Request", use_container_width=True, type="primary")
                    
                    if submit_btn:
                        val_errors = []
                        if not student_name.strip():
                            val_errors.append("Student Full Name is required.")
                        if not dm_number.strip():
                            val_errors.append("DM Number is required.")
                        elif len(dm_number.strip()) < 4:
                            val_errors.append("DM Number must be at least 4 characters long.")
                            
                        clean_phone = re.sub(r"[^\d]", "", mobile_number.strip())
                        if not clean_phone:
                            val_errors.append("Mobile Phone Number is required.")
                        elif len(clean_phone) != 10:
                            val_errors.append(f"Mobile Phone Number must be 10 digits (found {len(clean_phone)}).")
                            
                        if not room_number.strip():
                            val_errors.append("Hostel Room Number is required.")
                            
                        if val_errors:
                            for err in val_errors:
                                st.error(err)
                        else:
                            with st.spinner("Reserving equipment..."):
                                ok, msg, req_data = create_allocation_request(
                                    equipment_id=selected_eq_id,
                                    student_name=student_name,
                                    dm_number=dm_number,
                                    mobile_number=clean_phone,
                                    room_number=room_number,
                                    intended_duration=intended_duration
                                )
                                if ok:
                                    st.success(msg)
                                    st.session_action_req = req_data
                                    st.rerun()
                                else:
                                    st.error(msg)
                                    
    with col_right:
        # 1. Active Request Status Lookup (Right at the top beside the form!)
        with st.container(border=True):
            st.markdown("#### My Active Request Status & Timer")
            my_dm = st.text_input("Lookup by DM Number:", placeholder="e.g., DM2024-1052").strip().upper()
            
            if my_dm:
                active_reqs = get_student_active_requests(my_dm)
                if not active_reqs:
                    st.info(f"No active requests found for {my_dm}")
                else:
                    for req in active_reqs:
                        h1, h2 = st.columns([2, 1])
                        with h1:
                            st.markdown(f"**{req['equipment_name']}**")
                            st.caption(f"ID: `{req['request_id']}`")
                        with h2:
                            st.markdown(render_status_badge(req['status']), unsafe_allow_html=True)
                            
                        if req['status'] == 'Pending Verification':
                            time_str, mins_left, is_expired, is_urgent = calculate_time_remaining(req['expires_at'])
                            timer_class = "timer-pill urgent" if is_urgent else "timer-pill"
                            
                            st.markdown(f"""
                            <div style="margin: 0.5rem 0;">
                                <span class="{timer_class}">Timer: {time_str}</span>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            if st.button("Cancel Request", key=f"cancel_{req['request_id']}", use_container_width=True):
                                ok_c, msg_c = cancel_request(req['request_id'], reason="Cancelled by Student")
                                if ok_c:
                                    st.success(msg_c)
                                    st.rerun()
                                else:
                                    st.error(msg_c)
                        elif req['status'] == 'In Use':
                            st.markdown(f"""
                            <div style="background: #EFF6FF; border-left: 3px solid #2563EB; padding: 0.5rem 0.75rem; border-radius: 6px; font-size: 0.85rem; color: #1E40AF; margin-top: 0.25rem;">
                                Authorized by {req.get('guard_name', 'Guard')} at {format_iso_time(req.get('authorized_at'))}.
                            </div>
                            """, unsafe_allow_html=True)
            else:
                st.caption("Enter your DM number above to view active requests and countdown timers.")

        # 2. Live Inventory Stock Table
        with st.container(border=True):
            st.markdown("#### Live Equipment Stock")
            inv_data = [
                {
                    "Equipment": eq['item_name'],
                    "Category": eq['category'],
                    "Available": f"{eq['available_quantity']} / {eq['total_quantity']}",
                    "Rack": eq['location_rack']
                }
                for eq in all_equipment
            ]
            st.dataframe(pd.DataFrame(inv_data), use_container_width=True, hide_index=True)

    # -------------------------------------------------------------
    # BOTTOM SECTION: PEER TRANSPARENCY DIRECTORY
    # -------------------------------------------------------------
    st.divider()
    st.markdown("#### Peer Transparency Directory (Currently In-Use Equipment)")
    st.caption("Contact peers who currently have equipment checked out to coordinate handovers.")
    
    in_use_checkouts = get_active_checkouts()
    if not in_use_checkouts:
        st.info("No equipment is currently in use. All items are available in the sports room.")
    else:
        peer_data = [
            {
                "Equipment": item['equipment_name'],
                "Borrower Name": item['student_name'],
                "DM Number": item['dm_number'],
                "Phone": item['mobile_number'],
                "Hostel Room": item['room_number'],
                "Issued At": format_iso_time(item.get('authorized_at')),
                "Duration": item['intended_duration']
            }
            for item in in_use_checkouts
        ]
        st.dataframe(pd.DataFrame(peer_data), use_container_width=True, hide_index=True)
