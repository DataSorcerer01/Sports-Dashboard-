import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="Campus Sports Management System",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

from db import init_db, expire_stale_requests, seed_database, get_inventory_stats, get_court_stats
from components.ui_helpers import load_custom_css, render_header, render_kpi_bar
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

# Session State for Authentication / Role Selection
if "user_role" not in st.session_state:
    st.session_state.user_role = None  # None, "Student", "Security Guard"

# Sidebar
st.sidebar.markdown("""
<div style="padding: 0.5rem 0 1rem 0;">
    <div style="font-size: 1.3rem; font-weight: 700; color: #0F2942;">Campus Sports Hub</div>
    <div style="font-size: 0.82rem; color: #1E3A8A;">Equipment & Facility Management</div>
</div>
""", unsafe_allow_html=True)

if st.session_state.user_role is not None:
    st.sidebar.markdown(f"""
    <div style="background: #FFFFFF; border: 1px solid #BFDBFE; border-radius: 8px; padding: 0.75rem; margin-bottom: 1rem;">
        <div style="font-size: 0.75rem; color: #64748B; font-weight: 700; text-transform: uppercase;">Active Session</div>
        <div style="font-size: 1rem; font-weight: 700; color: #0F2942; margin-top: 0.2rem;">{st.session_state.user_role}</div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.sidebar.button("Log Out / Switch Role", use_container_width=True, type="secondary"):
        st.session_state.user_role = None
        st.rerun()

st.sidebar.divider()
st.sidebar.markdown("### System Actions")
if st.sidebar.button("Refresh Data & Timers", use_container_width=True):
    expire_stale_requests()
    st.rerun()

if st.sidebar.button("Reset Default Campus Inventory", use_container_width=True, help="Re-seeds the database with default campus sports equipment and 14 courts"):
    seed_database(force_reseed=True)
    st.sidebar.success("Database re-seeded with fresh campus equipment and courts!")
    st.rerun()

st.sidebar.markdown("""
<div style="margin-top: 1.5rem; padding: 0.85rem; background: #FFFFFF; border-radius: 8px; border: 1px solid #BFDBFE; font-size: 0.8rem; color: #334155; box-shadow: 0 1px 2px rgba(0,0,0,0.04);">
    <strong style="color: #0F2942;">Campus Policy:</strong><br>
    All equipment allocation requests have a 30-minute physical verification window at the sports desk.
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# VIEW ROUTING BASED ON AUTHENTICATION
# -------------------------------------------------------------

if st.session_state.user_role is None:
    # ---------------------------------------------------------
    # LOGIN GATE: SELECT ROLE
    # ---------------------------------------------------------
    render_header(current_role="Select Portal Role")
    
    stats = get_inventory_stats()
    render_kpi_bar(stats)
    
    st.markdown("## Welcome to Campus Sports Management")
    st.markdown("Please choose your portal access role below:")
    
    col_stud, col_guard = st.columns(2, gap="large")
    
    with col_stud:
        with st.container(border=True):
            st.markdown("""
            <div style="text-align: center; padding: 1rem 0;">
                <h3 style="color: #0F2942; font-size: 1.5rem; margin-bottom: 0.5rem;">Student Portal</h3>
                <p style="color: #475569; font-size: 0.95rem; line-height: 1.5;">
                    View live equipment inventory, submit a 30-minute gear allocation request, check active request timers, and track court availability.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Enter as Student", type="primary", use_container_width=True, key="btn_student_login"):
                st.session_state.user_role = "Student"
                st.rerun()
                
    with col_guard:
        with st.container(border=True):
            st.markdown("""
            <div style="text-align: center; padding: 1rem 0;">
                <h3 style="color: #0F2942; font-size: 1.5rem; margin-bottom: 0.5rem;">Security Guard & Staff Desk</h3>
                <p style="color: #475569; font-size: 0.95rem; line-height: 1.5;">
                    Verify student physical ID cards, approve checkouts, monitor active borrow sessions, inspect return conditions, and manage inventory.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander("Security Desk Login (Staff Only)", expanded=False):
                with st.form(key="guard_login_form"):
                    pass_code = st.text_input("Security Desk Passcode", type="password", placeholder="Enter staff passcode")
                    st.caption("Hint: Default staff passcode is `guard123`")
                    submit_guard = st.form_submit_button("Log In to Security Dashboard", type="primary", use_container_width=True)
                    if submit_guard:
                        if pass_code.strip() in ["guard123", "sportsdesk", "admin", "1234"]:
                            st.session_state.user_role = "Security Guard"
                            st.rerun()
                        else:
                            st.error("Invalid passcode. Please use `guard123` to enter.")

elif st.session_state.user_role == "Student":
    # ---------------------------------------------------------
    # STUDENT PORTAL: ONLY STUDENT TABS
    # ---------------------------------------------------------
    render_header(current_role="Student Portal")
    
    stats = get_inventory_stats()
    render_kpi_bar(stats)
    
    tab_equipment, tab_facilities = st.tabs([
        "Equipment Allocation & Inventory",
        "Court & Facility Availability Tracker"
    ])
    
    with tab_equipment:
        render_student_portal()
        
    with tab_facilities:
        render_court_tracker()

elif st.session_state.user_role == "Security Guard":
    # ---------------------------------------------------------
    # SECURITY GUARD PORTAL: GUARD & MANAGEMENT TABS
    # ---------------------------------------------------------
    render_header(current_role="Security Desk Control Panel")
    
    stats = get_inventory_stats()
    render_kpi_bar(stats)
    
    tab_guard, tab_courts, tab_inv, tab_rules = st.tabs([
        "Security Guard Desk & Verifications",
        "Court Occupancy Manager",
        "Inventory & Offline Data Hub",
        "System Policy & Guide"
    ])
    
    with tab_guard:
        render_guard_dashboard()
        
    with tab_courts:
        render_court_tracker()
        
    with tab_inv:
        render_inventory_admin()
        
    with tab_rules:
        st.markdown("""
        ### System Policy & Business Rules
        
        1. **Mandatory Physical ID Verification**:
           - Security guards must inspect the physical student ID card and verify the DM registration number before clicking Approve.
           
        2. **30-Minute Validity Window**:
           - If a student does not present physical ID within 30 minutes of request creation, the item automatically expires and returns to available inventory.
           
        3. **Return Inspection**:
           - Inspect equipment condition upon check-in (*Good Condition*, *Minor Wear*, *Damaged*, *Missing Parts*).
        """)
