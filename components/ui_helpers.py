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
            <div class="app-title">Campus Sports Management System</div>
            <div class="app-subtitle">
                Equipment Allocation & Facility Availability Portal &bull; Logged in as: <strong>{current_role}</strong>
            </div>
        </div>
        <div style="text-align: right;">
            <div class="clock-label">Campus Clock</div>
            <div class="clock-time">{now_str}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_kpi_bar(stats: dict):
    st.markdown(f"""
    <div class="stat-grid">
        <div class="stat-card">
            <div class="label">Total Gear Units</div>
            <div class="value" style="color: #0F2942;">{stats.get('total', 0)}</div>
        </div>
        <div class="stat-card" style="border-left: 4px solid #10B981 !important;">
            <div class="label">Available Now</div>
            <div class="value" style="color: #059669;">{stats.get('available', 0)}</div>
        </div>
        <div class="stat-card" style="border-left: 4px solid #F59E0B !important;">
            <div class="label">Pending Verification</div>
            <div class="value" style="color: #D97706;">{stats.get('pending', 0)}</div>
        </div>
        <div class="stat-card" style="border-left: 4px solid #2563EB !important;">
            <div class="label">Currently In Use</div>
            <div class="value" style="color: #1D4ED8;">{stats.get('in_use', 0)}</div>
        </div>
        <div class="stat-card" style="border-left: 4px solid #EF4444 !important;">
            <div class="label">Damaged / Maint.</div>
            <div class="value" style="color: #DC2626;">{stats.get('damaged', 0)}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_status_badge(status: str) -> str:
    s = str(status).strip()
    if s == "Available":
        return '<span class="badge badge-available">Available</span>'
    elif s == "Occupied":
        return '<span class="badge badge-occupied">Occupied</span>'
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
