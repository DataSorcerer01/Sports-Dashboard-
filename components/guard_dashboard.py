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
                qty = req.get('quantity', 1)
                
                with st.container(border=True):
                    h1, h2 = st.columns([2.5, 1.5])
                    with h1:
                        st.markdown(f"### {qty}x {req['equipment_name']}")
                        st.caption(f"Category: {req['category']} | Request ID: `{req['request_id']}` | Quantity: {qty}")
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
                            <li>Confirm <strong>{qty} unit(s)</strong> of <strong>{req['equipment_name']}</strong> are inspected and handed over.</li>
                        </ol>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    verify_checkbox = st.checkbox(
                        f"I have inspected the physical ID card for {req['student_name']} ({req['dm_number']}) and verified {qty}x {req['equipment_name']}",
                        key=f"chk_verify_{req['request_id']}"
                    )
                    
                    btn_col1, btn_col2 = st.columns([2, 1])
                    with btn_col1:
                        if st.button(
                            f"Approve & Issue {qty}x {req['equipment_name']}",
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
                qty = item.get('quantity', 1)
                with st.container(border=True):
                    h1, h2 = st.columns([2.5, 1.5])
                    with h1:
                        st.markdown(f"### {qty}x {item['equipment_name']}")
                        st.caption(f"Category: {item['category']} | Request ID: `{item['request_id']}` | Quantity: {qty}")
                    with h2:
                        st.markdown(render_status_badge("In Use"), unsafe_allow_html=True)
                        
                    st.divider()
                    
                    c1, c2, c3, c4 = st.columns(4)
                    c1.markdown(f"**Borrower**<br>`{item['student_name']}` ({item['dm_number']})", unsafe_allow_html=True)
                    c2.markdown(f"**Contact**<br>`{item['mobile_number']}`", unsafe_allow_html=True)
                    c3.markdown(f"**Room**<br>`{item['room_number']}`", unsafe_allow_html=True)
                    c4.markdown(f"**Issued At**<br>`{format_iso_time(item.get('authorized_at'))}`", unsafe_allow_html=True)
                    
                    # Return Section
                    with st.expander(f"Check-In / Return {qty}x {item['equipment_name']}", expanded=False):
                        with st.form(key=f"return_form_{item['request_id']}"):
                            ret_cond = st.selectbox(
                                "Return Physical Condition",
                                options=[c.value for c in ReturnCondition],
                                index=0
                            )
                            guard_notes = st.text_input("Return Notes / Inspection Comments", placeholder="e.g., Returned intact on time")
                            return_btn = st.form_submit_button("Confirm Return & Check-In", type="primary", use_container_width=True)
                            
                            if return_btn:
                                with st.spinner("Processing return..."):
                                    ok_ret, msg_ret = return_equipment(
                                        request_id=item['request_id'],
                                        return_condition=ret_cond,
                                        guard_notes=guard_notes,
                                        guard_name=guard_on_duty
                                    )
                                    if ok_ret:
                                        st.success(msg_ret)
                                        st.rerun()
                                    else:
                                        st.error(msg_ret)

    # -------------------------------------------------------------
    # TAB 3: Return History & Logs
    # -------------------------------------------------------------
    with tab_returns:
        from db import get_recent_history
        import pandas as pd
        
        st.markdown("#### Return & Checkout History Audit Trail")
        history = get_recent_history(limit=50)
        
        if not history:
            st.info("No transaction history recorded yet.")
        else:
            df = pd.DataFrame([
                {
                    "Req ID": h['request_id'],
                    "Equipment": f"{h.get('quantity', 1)}x {h['equipment_name']}",
                    "Student": f"{h['student_name']} ({h['dm_number']})",
                    "Status": h['status'],
                    "Requested": format_iso_time(h['requested_at']),
                    "Authorized": format_iso_time(h.get('authorized_at')),
                    "Returned": format_iso_time(h.get('returned_at')),
                    "Condition": h.get('return_condition') or 'N/A'
                }
                for h in history
            ])
            st.dataframe(df, use_container_width=True, hide_index=True)
