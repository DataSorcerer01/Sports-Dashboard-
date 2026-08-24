import streamlit as st
import os
from db import init_db, expire_stale_requests, get_inventory_stats
from sample_data import seed_database
from components.ui_helpers import (
    load_custom_css, render_header, render_kpi_bar,
    render_how_to_use_guide
)
from components.student_portal import render_student_portal
from components.guard_dashboard import render_guard_dashboard
from components.inventory_admin import render_inventory_admin

# Page Configuration
st.set_page_config(
    page_title="Sports Equipment Digital Management System",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Database & seed if needed
seed_database(force_reseed=False)

# Enforce 30-minute auto-expiry on every interaction
expired_count = expire_stale_requests()

# Load SaaS CSS Theme
load_custom_css()

# Sidebar Navigation
st.sidebar.markdown("""
<div style="text-align: center; padding: 1rem 0; border-bottom: 1px solid #E2E8F0; margin-bottom: 1rem;">
    <div style="font-size: 2.2rem;"></div>
    <div style="font-weight: 700; font-size: 1.1rem; color: #0F172A;">Sports Allocation Hub</div>
    <div style="font-size: 0.8rem; color: #64748B;">Campus Equipment Portal</div>
</div>
""", unsafe_allow_html=True)

role_view = st.sidebar.radio(
    "Select System View / Role:",
    options=[
        "Student Portal",
        "Security Guard Dashboard",
        "Inventory & Bulk Data Hub",
        "System Rules & Guide"
    ],
    index=0,
    help="Switch between student self-service allocation, security desk verification, and inventory management."
)

st.sidebar.divider()
st.sidebar.markdown("### Quick System Actions")
if st.sidebar.button("Refresh Data & Timers", use_container_width=True):
    expire_stale_requests()
    st.rerun()

if st.sidebar.button("Reset to Sample Inventory", use_container_width=True, help="Re-seeds the database with default campus sports equipment"):
    seed_database(force_reseed=True)
    st.sidebar.success("Database re-seeded with fresh campus equipment!")
    st.rerun()

st.sidebar.markdown("""
<div style="margin-top: 2rem; padding: 0.75rem; background: #1E293B; border-radius: 8px; border: 1px solid #334155; font-size: 0.8rem; color: #94A3B8;">
    <strong style="color: #F8FAFC;">Campus Policy Rule:</strong><br>
    All allocation requests have a 30-minute physical verification window at the sports desk.
</div>
""", unsafe_allow_html=True)

# Main Screen Header & KPIs
render_header(current_role=role_view)

stats = get_inventory_stats()
render_kpi_bar(stats)

# Built-in Guidance accessible from every screen
render_how_to_use_guide()

# View Routing
if role_view == "Student Portal":
    render_student_portal()
elif role_view == "Security Guard Dashboard":
    render_guard_dashboard()
elif role_view == "Inventory & Bulk Data Hub":
    render_inventory_admin()
elif role_view == "System Rules & Guide":
    st.markdown("""
    ### System Business Rules & Workflow Specifications
    
    The **Sports Equipment Digital Management System** strictly enforces four foundational business rules:
    
    ---
    #### 1. 30-Minute Request Validity Rule
    * Every request submitted by a student carries an active 30-minute reservation countdown.
    * The equipment unit is blocked from other students during this window (`Pending Verification`).
    * If the student fails to complete physical ID card verification at the security desk within 30 minutes, the server-side auto-expiry engine resets the request to `Expired` and restores the item to `Available`.
    
    ---
    #### 2. Mandatory Physical ID Verification
    * Students cannot self-authorize checkouts.
    * The security guard must physically inspect the student's ID card, confirm that the DM Number and photo match, and check the equipment condition before clicking **Approve & Issue Equipment**.
    
    ---
    #### 3. Explicit Lifecycle State Transitions
    * Equipment strictly follows the deterministic workflow:
      $$\\text{Available} \\longrightarrow \\text{Pending Verification} \\longrightarrow \\text{In Use} \\longrightarrow \\text{Returned} \\longrightarrow \\text{Available}$$
    * If gear is returned broken or damaged, it moves to `Damaged / Maintenance` with condition logs.
    
    ---
    #### 4. Peer Transparency & Active Borrower Visibility
    * Whenever equipment is `In Use`, the borrower's **Student Name**, **DM Number**, **Hostel Room**, and **Phone Number** are displayed on the Student Portal directory.
    * This enables direct student-to-student coordination and prevents gear hoarding on campus.
    """)

# Footer
st.markdown("""
<div style="text-align: center; margin-top: 3rem; padding-top: 1.5rem; border-top: 1px solid #E2E8F0; color: #94A3B8; font-size: 0.8rem;">
    Sports Equipment Digital Management System &bull; Campus Recreation & Security Department &bull; Version 2.0
</div>
""", unsafe_allow_html=True)
