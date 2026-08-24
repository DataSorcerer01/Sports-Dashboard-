import os
import streamlit as st
from datetime import datetime


def load_custom_css():
    css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "style.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def render_header(current_role: str = "Student Portal"):
    now_str = datetime.now().strftime("%A, %d %b %Y | %I:%M %p")
    st.markdown(f"""
    <div class="app-header">
        <div>
            <h1>Sports Equipment Digital Management System</h1>
            <p>Automated Campus Sports Inventory & Allocation Workflow &bull; Role: <strong>{current_role}</strong></p>
        </div>
        <div style="text-align: right;">
            <div style="font-size: 0.82rem; color: #94A3B8; font-weight: 500;">Live Campus Time</div>
            <div style="font-size: 1rem; font-weight: 700; color: #F8FAFC;">{now_str}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_kpi_bar(stats: dict):
    st.markdown(f"""
    <div class="stat-grid">
        <div class="stat-card">
            <div class="label">Total Equipment</div>
            <div class="value" style="color: #1E293B;">{stats.get('total', 0)}</div>
        </div>
        <div class="stat-card" style="border-left: 4px solid #10B981;">
            <div class="label">Available Now</div>
            <div class="value" style="color: #059669;">{stats.get('available', 0)}</div>
        </div>
        <div class="stat-card" style="border-left: 4px solid #F59E0B;">
            <div class="label">Pending Verification</div>
            <div class="value" style="color: #D97706;">{stats.get('pending', 0)}</div>
        </div>
        <div class="stat-card" style="border-left: 4px solid #4F46E5;">
            <div class="label">Currently In Use</div>
            <div class="value" style="color: #4F46E5;">{stats.get('in_use', 0)}</div>
        </div>
        <div class="stat-card" style="border-left: 4px solid #EF4444;">
            <div class="label">Damaged / Maint.</div>
            <div class="value" style="color: #DC2626;">{stats.get('damaged', 0)}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_status_badge(status: str) -> str:
    s = str(status).strip()
    if s == "Available":
        return '<span class="badge badge-available">Available</span>'
    elif s == "Pending Verification":
        return '<span class="badge badge-pending">Pending Verification</span>'
    elif s == "In Use":
        return '<span class="badge badge-in-use">In Use</span>'
    elif s == "Returned":
        return '<span class="badge badge-returned">Returned</span>'
    elif s == "Damaged" or "Broken" in s or "Missing" in s:
        return '<span class="badge badge-damaged">Damaged</span>'
    elif s == "Expired":
        return '<span class="badge badge-expired">Expired</span>'
    else:
        return f'<span class="badge">{s}</span>'


def calculate_time_remaining(expires_at_iso: str):
    """
    Returns (formatted_string, minutes_remaining, is_expired, is_urgent)
    """
    try:
        expires_at = datetime.fromisoformat(expires_at_iso)
        now = datetime.now()
        diff = expires_at - now
        total_seconds = int(diff.total_seconds())
        
        if total_seconds <= 0:
            return "Expired (0m 00s)", 0, True, False
            
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        is_urgent = minutes < 5
        formatted = f"{minutes}m {seconds:02d}s left"
        return formatted, minutes, False, is_urgent
    except Exception:
        return "N/A", 0, False, False


def format_iso_time(iso_str: str) -> str:
    if not iso_str:
        return "N/A"
    try:
        dt = datetime.fromisoformat(iso_str)
        return dt.strftime("%d %b, %I:%M %p")
    except Exception:
        return str(iso_str)


def render_how_to_use_guide():
    with st.expander("How to Use the Sports Equipment System (Step-by-Step Guide)", expanded=False):
        st.markdown("""
        ### Welcome to the Sports Equipment Digital Management System!
        This system automates and digitizes the sports equipment allocation process on campus. Follow these simple steps based on your role:

        ---
        #### For Students (Borrowing Equipment):
        1. **Check Availability**: Go to the **Student Portal** tab to see real-time inventory counts and available gear across all sports categories.
        2. **Submit Allocation Request**: Select your desired equipment, fill in your Name, DM Number, Mobile Number, Hostel Room Number, and Intended Duration, then click **Submit Request**.
        3. **30-Minute Timer Starts**: Once submitted, a strict **30-minute validity timer** begins counting down.
        4. **Physical Verification at Security Desk**: Walk over to the campus sports security desk, present your physical Student ID card to the duty guard.
        5. **Checkout Authorized**: The guard confirms your ID card and DM number match, and officially marks the item as **In Use**.
        6. **Peer Visibility**: While you have the gear, your contact info is visible on the student directory so peers can coordinate handovers.
        7. **Return on Time**: Once finished, return the gear to the security guard desk so the guard can inspect the condition and check it in.

        ---
        #### For Security Personnel (Desk Authorization & Returns):
        1. **View Pending Queue**: Check the **Pending Verification** table on the Guard Dashboard for new student requests.
        2. **Verify Physical ID**: Ask the student for their physical ID card. Check that their DM number matches the request.
        3. **Approve Checkout**: Click **Approve & Issue Equipment** to authorize checkout.
        4. **Monitor Active Checkouts**: Track all gear currently in use and review intended durations.
        5. **Check In Returns**: When the student returns the gear, click **Mark Returned**, select the physical condition (*Good*, *Minor Wear*, *Damaged*, *Missing Parts*), add any notes, and confirm return.

        ---
        #### For Inventory & Sports Management:
        1. **Manage Equipment**: Add new sports gear or update existing stock levels in the **Inventory & Bulk Data Hub**.
        2. **Offline Data**: Use **Download Template** to generate standardized CSV/Excel sheets and **Upload Template** to batch-import inventory with instant row-by-row validation.
        """)
