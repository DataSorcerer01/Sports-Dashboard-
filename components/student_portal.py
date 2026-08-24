import re
import streamlit as st
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
    st.markdown("### Student Equipment Allocation & Inventory")
    st.caption("Select your desired sports equipment, fill in borrower details, and submit a 30-minute allocation request.")
    
    all_equipment = get_all_equipment()
    available_items = [eq for eq in all_equipment if eq['available_quantity'] > 0]
    
    # -------------------------------------------------------------
    # SECTION 1: Allocation Request Form & Live Inventory
    # -------------------------------------------------------------
    st.markdown("#### 1. Select Equipment & Submit Request")
    
    if not available_items:
        st.warning("All sports equipment is currently checked out or in use. Please check the Peer Directory below to coordinate with active borrowers.")
    else:
        col_form, col_summary = st.columns([1.2, 0.8], gap="large")
        
        with col_form:
            with st.container(border=True):
                st.subheader("Borrower Allocation Form")
                
                with st.form(key="student_request_form", clear_on_submit=False):
                    # Equipment Options (Direct, simple list - no secondary model/brand selection required)
                    eq_options = {
                        f"{eq['item_name']} ({eq['category']}) - {eq['available_quantity']} Available (Rack: {eq['location_rack']})": eq['equipment_id']
                        for eq in available_items
                    }
                    
                    selected_label = st.selectbox(
                        "Select Sports Equipment to Borrow",
                        options=list(eq_options.keys()),
                        index=0,
                        help="Choose the sports equipment item you wish to borrow from the sports room."
                    )
                    selected_eq_id = eq_options[selected_label]
                    
                    # Student Details
                    col1, col2 = st.columns(2)
                    with col1:
                        student_name = st.text_input(
                            "Student Full Name",
                            placeholder="e.g., Rahul Sharma",
                            help="Enter your name as printed on your campus student ID card."
                        )
                    with col2:
                        dm_number = st.text_input(
                            "DM Number (Student ID)",
                            placeholder="e.g., DM2024-1052",
                            help="Your unique DM roll/registration number for verification at the security desk."
                        )
                        
                    col3, col4 = st.columns(2)
                    with col3:
                        mobile_number = st.text_input(
                            "Mobile Phone Number",
                            placeholder="e.g., 9876543210",
                            help="10-digit active phone number."
                        )
                    with col4:
                        room_number = st.text_input(
                            "Hostel Room Number",
                            placeholder="e.g., Block B - 204",
                            help="Your campus hostel block and room number."
                        )
                        
                    intended_duration = st.selectbox(
                        "Intended Usage Duration",
                        options=USAGE_DURATIONS,
                        index=1,
                        help="Estimated play time. Equipment should be returned promptly once finished."
                    )
                    
                    st.info("Submitting this form temporarily reserves 1 unit and starts a strict 30-minute timer. Please visit the sports security desk with your physical ID card before the timer expires.")
                    
                    submit_btn = st.form_submit_button("Submit Allocation Request", use_container_width=True, type="primary")
                    
                    if submit_btn:
                        val_errors = []
                        if not student_name.strip():
                            val_errors.append("Student Full Name is required.")
                        if not dm_number.strip():
                            val_errors.append("DM Number is required.")
                        elif len(dm_number.strip()) < 4:
                            val_errors.append("DM Number must be at least 4 characters long (e.g., DM2024-1052).")
                            
                        clean_phone = re.sub(r"[^\d]", "", mobile_number.strip())
                        if not clean_phone:
                            val_errors.append("Mobile Phone Number is required.")
                        elif len(clean_phone) != 10:
                            val_errors.append(f"Mobile Phone Number must be exactly 10 digits (found {len(clean_phone)} digits).")
                            
                        if not room_number.strip():
                            val_errors.append("Hostel Room Number is required.")
                            
                        if val_errors:
                            for err in val_errors:
                                st.error(err)
                        else:
                            with st.spinner("Processing request and reserving equipment..."):
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
                                    
        with col_summary:
            with st.container(border=True):
                st.subheader("Live Sports Inventory")
                for eq in all_equipment:
                    avail_color = "#059669" if eq['available_quantity'] > 0 else "#DC2626"
                    st.markdown(f"""
                    <div class="eq-card">
                        <div class="eq-card-header">
                            <div class="eq-title">{eq['item_name']}</div>
                            <span style="font-weight: 700; color: {avail_color}; font-size: 0.9rem;">
                                {eq['available_quantity']} / {eq['total_quantity']} Avail
                            </span>
                        </div>
                        <div class="eq-meta">
                            <strong>Category:</strong> {eq['category']} &bull; 
                            <strong>Rack:</strong> {eq['location_rack']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    # -------------------------------------------------------------
    # SECTION 2: Active Request Status & 30-Min Countdown
    # -------------------------------------------------------------
    st.divider()
    st.markdown("#### 2. Check My Active Request Status & Timer")
    
    col_lookup1, col_lookup2 = st.columns([1.5, 1])
    with col_lookup1:
        my_dm = st.text_input("Enter your DM Number to check active requests:", placeholder="e.g., DM2024-1052").strip().upper()
        
    if my_dm:
        active_reqs = get_student_active_requests(my_dm)
        if not active_reqs:
            st.info(f"No active requests found for DM Number: {my_dm}")
        else:
            for req in active_reqs:
                with st.container(border=True):
                    h1, h2 = st.columns([2, 1])
                    with h1:
                        st.markdown(f"### {req['equipment_name']}")
                        st.caption(f"Request ID: `{req['request_id']}` | Requested: {format_iso_time(req['requested_at'])}")
                    with h2:
                        st.markdown(render_status_badge(req['status']), unsafe_allow_html=True)
                        
                    if req['status'] == 'Pending Verification':
                        time_str, mins_left, is_expired, is_urgent = calculate_time_remaining(req['expires_at'])
                        timer_class = "timer-pill urgent" if is_urgent else "timer-pill"
                        
                        st.markdown(f"""
                        <div style="margin: 0.75rem 0;">
                            <strong>Verification Timer:</strong> 
                            <span class="{timer_class}">{time_str}</span>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.markdown("""
                        <div style="background: #FFFBEB; border-left: 4px solid #F59E0B; padding: 0.75rem; border-radius: 6px; font-size: 0.85rem; color: #92400E; margin-bottom: 0.75rem;">
                            <strong>Next Step:</strong> Visit the sports security desk and present your physical student ID card to the guard on duty.
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if st.button("Cancel My Request", key=f"cancel_{req['request_id']}"):
                            ok_c, msg_c = cancel_request(req['request_id'], reason="Cancelled by Student")
                            if ok_c:
                                st.success(msg_c)
                                st.rerun()
                            else:
                                st.error(msg_c)
                    elif req['status'] == 'In Use':
                        st.markdown(f"""
                        <div style="background: #EFF6FF; border-left: 4px solid #2563EB; padding: 0.75rem; border-radius: 6px; font-size: 0.85rem; color: #1E40AF;">
                            <strong>Checkout Authorized:</strong> Issued by {req.get('guard_name', 'Security Guard')} at {format_iso_time(req.get('authorized_at'))}. Return upon session completion.
                        </div>
                        """, unsafe_allow_html=True)

    # -------------------------------------------------------------
    # SECTION 3: Peer Transparency Directory
    # -------------------------------------------------------------
    st.divider()
    st.markdown("#### 3. Peer Transparency Directory (Currently In-Use Equipment)")
    st.caption("Contact peers who currently have equipment checked out to coordinate smooth handovers and play sessions.")
    
    in_use_checkouts = get_active_checkouts()
    if not in_use_checkouts:
        st.info("No equipment is currently in use. All items are available in the sports room.")
    else:
        for item in in_use_checkouts:
            with st.container(border=True):
                c1, c2, c3, c4 = st.columns(4)
                c1.markdown(f"**Equipment**<br>`{item['equipment_name']}`", unsafe_allow_html=True)
                c2.markdown(f"**Borrower**<br>`{item['student_name']}` ({item['dm_number']})", unsafe_allow_html=True)
                c3.markdown(f"**Contact**<br>`{item['mobile_number']}` (Room: {item['room_number']})", unsafe_allow_html=True)
                c4.markdown(f"**Issued At**<br>`{format_iso_time(item.get('authorized_at'))}`", unsafe_allow_html=True)
