# 🏸 Sports Equipment Digital Management System

An automated, trackable, and peer-transparent web application built with **Python & Streamlit** to replace manual register-based sports equipment allocations on campus.

---

## 🌟 Key Features

* **🎓 Student Portal**:
  * Real-time sports inventory status and availability tracking.
  * Borrower request form with full field validation (Student Name, DM Number, 10-digit Phone, Hostel Room, Duration).
  * **Strict 30-Minute Validity Rule**: Live countdown timer; requests automatically expire and unblock inventory if not verified in time.
  * **👥 Peer Transparency Directory**: Active checkouts display borrower details and issue timestamps for student-to-student handover coordination.

* **🛡️ Security Guard Dashboard**:
  * Mobile-friendly queue with live request validity timers.
  * **Mandatory Physical ID Verification Checklist** before one-click approval.
  * Active checkouts monitoring with return condition inspection logging (*Good Condition*, *Minor Wear*, *Damaged*, *Missing Parts*).

* **📦 Inventory & Bulk Data Hub**:
  * Catalogue overview and individual equipment editor.
  * **Download Template**: Standardized CSV and Excel (.xlsx) templates with prefilled example row.
  * **Upload Template with Strict Validator**: Comprehensive cell-by-cell validation reporting exact row and column errors.
  * **System Audit Trail**: Complete chronological activity log.

---

## 🚀 Quick Start & Installation

### 1. Clone the repository
`ash
git clone https://github.com/<your-username>/sports-equipment-system.git
cd sports-equipment-system
`

### 2. Install dependencies
`ash
pip install -r requirements.txt
`

### 3. Run the Streamlit application
`ash
streamlit run app.py
`
Open your browser and navigate to http://localhost:8501.

---

## 🏗️ Project Architecture

`
sports-equipment-system/
├── app.py                      # Main entry point & role view navigation
├── db.py                       # SQLite database engine, state transitions, & auto-expiry timer
├── models.py                   # Data classes, enums, & business constants
├── data_io.py                  # CSV/Excel template generator & cell-by-cell validator
├── sample_data.py              # Campus sports equipment seed catalogue
├── components/
│   ├── ui_helpers.py           # Header, KPI cards, badges, & step-by-step user guide
│   ├── student_portal.py       # Student allocation request workflow & peer directory
│   ├── guard_dashboard.py      # Guard ID verification, approval, & return condition logger
│   └── inventory_admin.py      # Inventory manager, batch CSV/Excel import/export, & audit trail
├── static/
│   └── style.css               # SaaS styling, responsive grid, & status badges
└── requirements.txt            # Python package dependencies
`

---

## 🛡️ Campus Business Rules

1. **30-Minute Request Validity**: Requests not authorized at the security desk within 30 minutes automatically expire and release reserved equipment.
2. **Mandatory Guard ID Verification**: Equipment cannot be checked out without physical ID card inspection.
3. **Explicit Lifecycle States**: Available $\rightarrow$ Pending Verification $\rightarrow$ In Use $\rightarrow$ Returned $\rightarrow$ Available (or Damaged).
4. **Peer Visibility**: Active borrowers' contact info is visible on the student directory to prevent equipment hoarding.

---

## 📄 License
MIT License. Built for Campus Recreation & Security Management.
