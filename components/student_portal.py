import re
import streamlit as st
from datetime import datetime
from db import (
    get_all_equipment, create_allocation_request,
    get_active_checkouts, get_student_active_requests,
    cancel_request
)
from models import SPORTS_CATEGORIES, USAGE_DURATIONS
from components.ui_helpers import (
    render_status_badge, calculate_time_remaining,
    format_iso_time
)


def render_student_portal():
    st.markdown("### Student Sports Equipment Portal")
    st.caption("Browse available sports inventory, submit checkout requests with a 30-minute verification window, and track peer checkouts.")
    
    tab1, tab2, tab3 = st.tabs([
        "Request Equipment",
        "My Active Requests & Timer",
        "Peer Equipment Directory (In Use)"
    ])
    
    # -------------------------------------------------------------
    # TAB 1: Request Equipment Form & Catalog
    # -------------------------------------------------------------
    with tab1:
        st.markdown("#### 1. Select Equipment & Fill Borrower Details")
        
        all_equipment = get_all_equipment()
        available_items = [eq for eq in all_equipment if eq['available_quantity'] > 0]
        
        if not available_items:
            st.warning("All sports equipment is currently checked out or reserved. Please check back shortly or view the Peer Directory to see who has items.")
            return

        col_form, col_summary = st.columns([1.2, 0.8], gap="large")
        
        with col_form:
            with st.container(border=True):
                st.subheader("Borrower Allocation Form")
                
                with st.form(key="student_request_form", clear_on_submit=False):
                    # Category & Item Selection
                    categories_available = sorted(list(set(eq['category'] for eq in available_items)))
                    selected_cat = st.selectbox(
                        "Sport / Equipment Category",
                        options=categories_available,
                        index=0,
                        help="Select the sports discipline you want equipment for. Example: Badminton, Football"
                    )
                    
                    cat_items = [eq for eq in available_items if eq['category'] == selected_cat]
                    item_options = {
                        f"{eq['item_name']} (Available: {eq['available_quantity']}/{eq['total_quantity']} | {eq['location_rack']})": eq['equipment_id']
                        for eq in cat_items
                    }
                    
                    selected_item_label = st.selectbox(
                        "Specific Equipment Item",
                        options=list(item_options.keys()),
                        help="Choose the specific equipment model and unit from available stock. Example: Yonex Nanoray Carbon Badminton Racquet"
                    )
                    selected_eq_id = item_options[selected_item_label]
                    
                    # Student Details
                    col1, col2 = st.columns(2)
                    with col1:
                        student_name = st.text_input(
                            "Student Full Name",
                            placeholder="e.g., Rahul Sharma",
                            help="Enter your official name as shown on your university student ID card. Example: Rahul Sharma"
                        )
                    with col2:
                        dm_number = st.text_input(
                            "DM Number (Student ID)",
                            placeholder="e.g., DM2024-1052",
                            help="Your unique DM roll/registration number for identity verification at the security desk. Example: DM2024-1052"
                        )
                        
                    col3, col4 = st.columns(2)
                    with col3:
                        mobile_number = st.text_input(
                            "Mobile Phone Number",
                            placeholder="e.g., 9876543210",
                            help="10-digit active phone number for peer coordination and return alerts. Example: 9876543210"
                        )
                    with col4:
                        room_number = st.text_input(
                            "Hostel Room Number",
                            placeholder="e.g., Block B - 204",
                            help="Your campus hostel block and room number. Example: Block B - 204"
                        )
                        
                    intended_duration = st.selectbox(
                        "Intended Usage Duration",
                        options=USAGE_DURATIONS,
                        index=1,
                        help="Estimated duration of your play session. Equipment should be returned promptly once finished. Example: 1 Hour"
                    )
                    
                    st.info("**Important Rule**: Submitting this form temporarily reserves 1 unit and starts a **strict 30-minute timer**. You must visit the security guard desk and show your physical ID card before the timer expires.")
                    
                    submit_btn = st.form_submit_button("Submit Allocation Request", use_container_width=True, type="primary")
                    
                    if submit_btn:
                        # Field Validations
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
                                st.error(f"{err}")
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
                                    st.success(f"{msg}")
                                    st.session_action_req = req_data
                                    st.balloons()
                                    st.rerun()
                                else:
                                    st.error(f"{msg}")
                                
        with col_summary:
            with st.container(border=True):
                st.subheader("Live Sports Inventory")
                for eq in all_equipment:
                    avail_color = "#34D399" if eq['available_quantity'] > 0 else "#EF4444"
                    st.markdown(f"""
                    <div class="eq-card">
                        <div class="eq-card-header">
                            <div class="eq-title">{eq['item_name']}</div>
                            <span class="badge" style="background-color: {avail_color}25; color: {avail_color}; border: 1px solid {avail_color}80;">
                                {eq['available_quantity']} / {eq['total_quantity']} Available
                            </span>
                        </div>
                        <div class="eq-meta">
                            Category: <strong>{eq['category']}</strong> &bull; Rack: {eq['location_rack']} &bull; Condition: {eq['condition']}
                        </div>
                        <div style="font-size: 0.82rem; color: #94A3B8;">
                            {eq.get('notes', '')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    # -------------------------------------------------------------
    # TAB 2: My Active Requests & 30-Min Countdown Timer
    # -------------------------------------------------------------
    with tab2:
        st.markdown("#### Track Your Allocation Requests & Countdown Timer")
        
        lookup_col1, lookup_col2 = st.columns([1, 1])
        with lookup_col1:
            search_dm = st.text_input(
                "Enter your DM Number to track your requests:",
                placeholder="e.g., DM2024-1052",
                help="Type your DM Number to look up all active pending verification requests or active checkouts. Example: DM2024-1052"
            )
            
        if search_dm.strip():
            student_reqs = get_student_active_requests(search_dm)
            if not student_reqs:
                st.info(f"No active pending or in-use requests found for DM Number **{search_dm.upper()}**.")
            else:
                for req in student_reqs:
                    with st.container(border=True):
                        timer_str, mins_left, is_exp, is_urg = calculate_time_remaining(req['expires_at'])
                        
                        header_col1, header_col2 = st.columns([2, 1])
                        with header_col1:
                            st.markdown(f"### {req['equipment_name']}")
                            st.caption(f"Request ID: `{req['request_id']}` | Requested at: {format_iso_time(req['requested_at'])}")
                        with header_col2:
                            st.markdown(render_status_badge(req['status']), unsafe_allow_html=True)
                            if req['status'] == 'Pending Verification':
                                urg_class = "timer-pill urgent" if is_urg else "timer-pill"
                                st.markdown(f'<div class="{urg_class}">{timer_str}</div>', unsafe_allow_html=True)
                        
                        st.divider()
                        
                        d_col1, d_col2, d_col3, d_col4 = st.columns(4)
                        d_col1.metric("Borrower", req['student_name'])
                        d_col2.metric("DM Number", req['dm_number'])
                        d_col3.metric("Hostel Room", req['room_number'])
                        d_col4.metric("Duration", req['intended_duration'])
                        
                        if req['status'] == 'Pending Verification':
                            st.warning("**Action Required**: Please proceed to the **Security Guard Desk** immediately with your physical Student ID card to authorize checkout before the timer reaches zero.")
                            if st.button("Cancel This Request", key=f"cancel_btn_{req['request_id']}"):
                                ok_c, msg_c = cancel_request(req['request_id'], reason="Cancelled by student")
                                if ok_c:
                                    st.success("Request cancelled and item returned to available inventory.")
                                    st.rerun()
                                else:
                                    st.error(msg_c)
                        elif req['status'] == 'In Use':
                            st.success(f"Authorized by guard: **{req.get('guard_name', 'Duty Guard')}** at {format_iso_time(req.get('authorized_at'))}. Please return equipment in good condition when done!")
        else:
            st.info("Enter your DM number above to view your real-time countdown timer and authorization status.")

    # -------------------------------------------------------------
    # TAB 3: Peer Transparency Directory (Active Checkouts)
    # -------------------------------------------------------------
    with tab3:
        st.markdown("#### Peer Transparency & Active Checkouts Directory")
        st.caption("See which equipment items are currently in use, who borrowed them, their hostel room, and phone number for direct student-to-student coordination.")
        
        active_checkouts = get_active_checkouts()
        if not active_checkouts:
            st.success("All equipment items are currently returned and available in the sports room!")
        else:
            for item in active_checkouts:
                st.markdown(f"""
                <div class="content-card" style="border-left: 4px solid #4F46E5;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
                        <div style="font-size: 1.15rem; font-weight: 700; color: #0F172A;">
                            {item['equipment_name']} <span style="font-size: 0.85rem; font-weight: 500; color: #64748B;">({item['category']})</span>
                        </div>
                        <span class="badge badge-in-use">In Use</span>
                    </div>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; background: #F8FAFC; padding: 1rem; border-radius: 8px; border: 1px solid #E2E8F0;">
                        <div>
                            <div style="font-size: 0.75rem; color: #64748B; font-weight: 600; text-transform: uppercase;">Current Borrower</div>
                            <div style="font-size: 0.95rem; font-weight: 600; color: #1E293B;">{item['student_name']}</div>
                        </div>
                        <div>
                            <div style="font-size: 0.75rem; color: #64748B; font-weight: 600; text-transform: uppercase;">DM Registration No.</div>
                            <div style="font-size: 0.95rem; font-weight: 600; color: #1E293B;">{item['dm_number']}</div>
                        </div>
                        <div>
                            <div style="font-size: 0.75rem; color: #64748B; font-weight: 600; text-transform: uppercase;">Hostel Room</div>
                            <div style="font-size: 0.95rem; font-weight: 600; color: #1E293B;">{item['room_number']}</div>
                        </div>
                        <div>
                            <div style="font-size: 0.75rem; color: #64748B; font-weight: 600; text-transform: uppercase;">Phone Number</div>
                            <div style="font-size: 0.95rem; font-weight: 600; color: #1E293B;">{item['mobile_number']}</div>
                        </div>
                        <div>
                            <div style="font-size: 0.75rem; color: #64748B; font-weight: 600; text-transform: uppercase;">Checked Out At</div>
                            <div style="font-size: 0.95rem; font-weight: 600; color: #1E293B;">{format_iso_time(item['authorized_at'])}</div>
                        </div>
                        <div>
                            <div style="font-size: 0.75rem; color: #64748B; font-weight: 600; text-transform: uppercase;">Intended Duration</div>
                            <div style="font-size: 0.95rem; font-weight: 600; color: #1E293B;">{item['intended_duration']}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
