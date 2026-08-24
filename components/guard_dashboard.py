import streamlit as st
from datetime import datetime
from db import (
    get_pending_requests, approve_allocation_request,
    get_active_checkouts, return_equipment, get_all_equipment
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
            help="Your name will be stamped on all authorized checkout and return audit logs."
        )
        
    tab_queue, tab_active, tab_returns = st.tabs([
        "Pending Verifications & Queue",
        "Active Checkouts Monitor",
        "Return Logs & Equipment Inspection"
    ])
    
    # -------------------------------------------------------------
    # TAB 1: Pending Queue & ID Verification
    # -------------------------------------------------------------
    with tab_queue:
        pending_list = get_pending_requests()
        st.markdown(f"#### Pending ID Verification Queue ({len(pending_list)} requests waiting)")
        
        if not pending_list:
            st.info("No students are currently waiting in the verification queue. All submitted requests have been processed or expired.")
        else:
            for req in pending_list:
                time_str, mins_left, is_expired, is_urgent = calculate_time_remaining(req['expires_at'])
                timer_class = "timer-pill urgent" if is_urgent else "timer-pill"
                
                with st.container(border=True):
                    h1, h2 = st.columns([2.5, 1.5])
                    with h1:
                        st.markdown(f"### {req['equipment_name']}")
                        st.caption(f"Category: {req['category']} | Request ID: `{req['request_id']}`")
                    with h2:
                        st.markdown(f"""
                        <div style="text-align: right;">
                            <span class="{timer_class}">Validity: {time_str}</span>
                        </div>
                        """, unsafe_allow_html=True)
                        
                    st.divider()
                    
                    b1, b2, b3, b4 = st.columns(4)
                    b1.markdown(f"**Student Name**<br>`{req['student_name']}`", unsafe_allow_html=True)
                    b2.markdown(f"**DM Number**<br>`{req['dm_number']}`", unsafe_allow_html=True)
                    b3.markdown(f"**Phone**<br>`{req['mobile_number']}`", unsafe_allow_html=True)
                    b4.markdown(f"**Hostel Room**<br>`{req['room_number']}`", unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div style="background: #EFF6FF; border-left: 4px solid #1D4ED8; padding: 0.85rem; border-radius: 8px; margin: 0.75rem 0;">
                        <strong style="color: #1E3A8A;">Mandatory Guard Verification Checklist:</strong>
                        <ol style="margin: 0.25rem 0 0 1.25rem; font-size: 0.85rem; color: #1E293B;">
                            <li>Inspect physical Student Identity Card presented by the student.</li>
                            <li>Confirm student face matches the photo and DM number reads <strong>{req['dm_number']}</strong>.</li>
                            <li>Confirm physical sports equipment unit is available and handed over.</li>
                        </ol>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    verify_checkbox = st.checkbox(
                        f"I have inspected the physical ID card for {req['student_name']} ({req['dm_number']})",
                        key=f"chk_verify_{req['request_id']}"
                    )
                    
                    btn_col1, btn_col2 = st.columns([2, 1])
                    with btn_col1:
                        if st.button(
                            "Approve & Issue Equipment",
                            key=f"approve_{req['request_id']}",
                            type="primary",
                            use_container_width=True,
                            disabled=not verify_checkbox,
                            help="Check the verification box above after reviewing the physical ID card to enable this button."
                        ):
                            with st.spinner("Authorizing checkout..."):
                                ok, msg = approve_allocation_request(req['request_id'], guard_name=guard_on_duty)
                                if ok:
                                    st.success(msg)
                                    st.rerun()
                                else:
                                    st.error(msg)
                                    
                    with btn_col2:
                        st.caption(f"Requested: {format_iso_time(req['requested_at'])}")

    # -------------------------------------------------------------
    # TAB 2: Active Checkouts Monitor
    # -------------------------------------------------------------
    with tab_active:
        active_checkouts = get_active_checkouts()
        st.markdown(f"#### Active Borrow Sessions ({len(active_checkouts)} items currently in use)")
        
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
                with st.container(border=True):
                    st.markdown(f"### {d_item['item_name']} ({d_item['category']})")
                    st.markdown(f"""
                    **Damaged Units:** `{d_item['damaged_quantity']}` / `{d_item['total_quantity']}` | 
                    **Rack:** `{d_item['location_rack']}` | 
                    **Reported State:** `{d_item['condition']}`
                    """)
                    if d_item.get('notes'):
                        st.caption(d_item['notes'])
