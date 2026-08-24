import streamlit as st
from datetime import datetime
from db import (
    get_pending_requests, get_active_checkouts,
    approve_allocation_request, return_equipment,
    cancel_request, get_all_equipment
)
from models import ReturnCondition
from components.ui_helpers import (
    render_status_badge, calculate_time_remaining,
    format_iso_time
)


def render_guard_dashboard():
    st.markdown("### Security Guard Desk & Allocation Control Panel")
    st.caption("Verify student physical ID cards, authorize sports equipment checkouts, monitor active borrow sessions, and inspect return conditions.")
    
    # Guard Identity Input
    guard_col1, guard_col2 = st.columns([1, 2])
    with guard_col1:
        guard_on_duty = st.text_input(
            "Officer on Duty Name",
            value="Officer Rajesh (Main Sports Desk)",
            placeholder="e.g., Officer Rajesh",
            help="Name or badge number of the guard currently operating the verification desk."
        )
        
    tab_pending, tab_active, tab_returns = st.tabs([
        "Pending Verifications & Queue",
        "Active Checkouts Monitor",
        "Return Logs & Equipment Inspection"
    ])
    
    # -------------------------------------------------------------
    # TAB 1: Pending Verifications & ID Check
    # -------------------------------------------------------------
    with tab_pending:
        st.markdown("#### Pending Student Allocation Requests")
        st.caption("Students must present their physical ID card at the desk within 30 minutes of submitting their request.")
        
        pending_requests = get_pending_requests()
        
        if not pending_requests:
            st.info("No pending verification requests right now. The queue is clear.")
        else:
            for req in pending_requests:
                timer_str, mins_left, is_exp, is_urg = calculate_time_remaining(req['expires_at'])
                
                with st.container(border=True):
                    c1, c2 = st.columns([2.5, 1.5])
                    with c1:
                        st.markdown(f"### {req['equipment_name']}")
                        st.markdown(f"**Category**: `{req['category']}` &bull; **Request ID**: `{req['request_id']}`")
                    with c2:
                        st.markdown(render_status_badge(req['status']), unsafe_allow_html=True)
                        urg_class = "timer-pill urgent" if is_urg else "timer-pill"
                        st.markdown(f'<div class="{urg_class}">{timer_str}</div>', unsafe_allow_html=True)
                        
                    st.divider()
                    
                    # Student Details Grid
                    sc1, sc2, sc3, sc4 = st.columns(4)
                    sc1.markdown(f"**Student Name**<br>`{req['student_name']}`", unsafe_allow_html=True)
                    sc2.markdown(f"**DM Number**<br>`{req['dm_number']}`", unsafe_allow_html=True)
                    sc3.markdown(f"**Phone Number**<br>`{req['mobile_number']}`", unsafe_allow_html=True)
                    sc4.markdown(f"**Hostel Room**<br>`{req['room_number']}`", unsafe_allow_html=True)
                    
                    st.markdown('<div class="verification-box">', unsafe_allow_html=True)
                    st.markdown("<strong>Mandatory Guard Authorization Checklist:</strong>", unsafe_allow_html=True)
                    
                    id_verified = st.checkbox(
                        f"Physical ID Card verified: DM '{req['dm_number']}' and photo match student '{req['student_name']}'",
                        key=f"chk_id_{req['request_id']}"
                    )
                    gear_inspected = st.checkbox(
                        f"Equipment condition checked prior to handover",
                        value=True,
                        key=f"chk_gear_{req['request_id']}"
                    )
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    btn_col1, btn_col2 = st.columns([2, 1])
                    with btn_col1:
                        if st.button("Approve & Issue Equipment", key=f"approve_{req['request_id']}", type="primary", use_container_width=True):
                            if not id_verified:
                                st.error("Mandatory Requirement: You must verify the student's physical ID card before approving checkout!")
                            else:
                                with st.spinner("Authorizing checkout..."):
                                    ok, msg = approve_allocation_request(req['request_id'], guard_name=guard_on_duty)
                                    if ok:
                                        st.success(msg)
                                        st.rerun()
                                    else:
                                        st.error(msg)
                                        
                    with btn_col2:
                        if st.button("Reject Request", key=f"reject_{req['request_id']}", use_container_width=True):
                            ok_r, msg_r = cancel_request(req['request_id'], reason=f"Rejected by guard {guard_on_duty}")
                            if ok_r:
                                st.warning("Request rejected and gear returned to inventory.")
                                st.rerun()
                            else:
                                st.error(msg_r)

    # -------------------------------------------------------------
    # TAB 2: Active Checkouts Monitor & Returns
    # -------------------------------------------------------------
    with tab_active:
        st.markdown("#### Currently Checked Out Equipment (In Use)")
        active_checkouts = get_active_checkouts()
        
        if not active_checkouts:
            st.info("No equipment is currently checked out. All inventory is secure in the sports room.")
        else:
            for item in active_checkouts:
                with st.container(border=True):
                    h1, h2 = st.columns([2.5, 1.5])
                    with h1:
                        st.markdown(f"### {item['equipment_name']}")
                        st.caption(f"Category: {item['category']} | Request ID: `{item['request_id']}`")
                    with h2:
                        st.markdown(render_status_badge(item['status']), unsafe_allow_html=True)
                        st.caption(f"Authorized: {format_iso_time(item.get('authorized_at'))}")
                        
                    st.divider()
                    
                    b1, b2, b3, b4 = st.columns(4)
                    b1.markdown(f"**Borrower**<br>`{item['student_name']}`", unsafe_allow_html=True)
                    b2.markdown(f"**DM Number**<br>`{item['dm_number']}`", unsafe_allow_html=True)
                    b3.markdown(f"**Phone**<br>`{item['mobile_number']}`", unsafe_allow_html=True)
                    b4.markdown(f"**Duration**<br>`{item['intended_duration']}`", unsafe_allow_html=True)
                    
                    with st.expander(f"Check In & Mark Returned: {item['equipment_name']}", expanded=False):
                        with st.form(key=f"return_form_{item['request_id']}"):
                            ret_condition = st.selectbox(
                                "Return Condition",
                                options=[
                                    ReturnCondition.GOOD.value,
                                    ReturnCondition.MINOR_WEAR.value,
                                    ReturnCondition.DAMAGED.value,
                                    ReturnCondition.MISSING_PARTS.value
                                ],
                                help="Inspect the physical state of the returned item. If Damaged or Missing Parts, item is moved to Maintenance."
                            )
                            guard_notes = st.text_input(
                                "Guard Return Inspection Notes",
                                placeholder="e.g., Returned in clean working condition, no strings broken",
                                help="Optional remarks regarding physical condition or return timing."
                            )
                            
                            confirm_return = st.form_submit_button("Confirm Equipment Return", type="primary", use_container_width=True)
                            if confirm_return:
                                with st.spinner("Processing equipment check-in..."):
                                    ok_ret, msg_ret = return_equipment(
                                        request_id=item['request_id'],
                                        return_condition=ret_condition,
                                        guard_notes=guard_notes,
                                        guard_name=guard_on_duty
                                    )
                                    if ok_ret:
                                        st.success(msg_ret)
                                        st.rerun()
                                    else:
                                        st.error(msg_ret)

    # -------------------------------------------------------------
    # TAB 3: Equipment Condition & Damaged Inventory
    # -------------------------------------------------------------
    with tab_returns:
        st.markdown("#### Damaged & Under Maintenance Inventory")
        all_eq = get_all_equipment()
        damaged_items = [eq for eq in all_eq if eq['damaged_quantity'] > 0]
        
        if not damaged_items:
            st.success("100% of equipment inventory is in good working order. No damaged items reported.")
        else:
            for d_item in damaged_items:
                st.markdown(f"""
                <div class="content-card" style="border-left: 4px solid #EF4444;">
                    <div style="font-size: 1.1rem; font-weight: 700; color: #991B1B;">
                        {d_item['item_name']} ({d_item['category']})
                    </div>
                    <div style="margin-top: 0.5rem; font-size: 0.9rem; color: #334155;">
                        <strong>Damaged Units:</strong> {d_item['damaged_quantity']} / {d_item['total_quantity']} &bull;
                        <strong>Storage Rack:</strong> {d_item['location_rack']} &bull;
                        <strong>Reported State:</strong> {d_item['condition']}
                    </div>
                    <div style="font-size: 0.85rem; color: #64748B; margin-top: 0.25rem;">
                        {d_item.get('notes', '')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
