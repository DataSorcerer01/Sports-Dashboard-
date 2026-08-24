# ?? Campus Sports Equipment & Court Facility Digital Management System

An automated, trackable, and peer-transparent web application built with **Python & Streamlit** to manage campus sports equipment allocations and live playing court occupancies.

---

## ?? Key Features

### 1. ??? Live Court & Facility Occupancy Tracker (New!)
* **14 Campus Facilities Tracked in Real-Time**:
  * **Badminton**: 4 Courts (2 in Elango Complex & 2 in MG Complex)
  * **Pickleball**: 2 Outdoor Courts
  * **Tennis**: 1 Lawn Tennis Court
  * **Table Tennis**: 2 Indoor TT Tables
  * **Pool & Billiards**: 1 Tournament Pool Table
  * **Carrom**: 2 Station Boards
  * **Outdoor Grounds**: Main Cricket Ground & Football Stadium Turf
* **Instant Occupancy Badges**: `?? Available to Play` vs `?? Occupied / In Play`.
* **Lead Player Transparency**: Displays who is currently playing, DM number, phone number, hostel room, start time, and play duration.
* **Quick Check-In & Check-Out**: Direct self-service court check-in and checkout button.

---

### 2. ?? Student Equipment Portal
* **Real-time Inventory Tracking**: Live stock numbers across all sports gear.
* **Updated Campus Gear Catalogue**:
  * 10 Badminton Racquets
  * 10 Table Tennis Racquets & 5 TT Balls
  * 1 Full Pool & Billiards Kit (Cues, Chalk, Triangle, Ball Set)
  * 2 Sets of Carrom Coins & Strikers
  * 2 Cricket Bats & 1 Cricket Match Ball
  * 1 Match Football
  * 10 Pickleball Paddles & 2 Pickleball Balls
  * 4 Tennis Racquets & 4 Tennis Balls
* **Strict 30-Minute Validity Rule**: Live countdown timer; requests automatically expire and release equipment if not physically verified at the security desk.
* **?? Peer Transparency Directory**: Active checkouts display borrower details and issue timestamps for student-to-student handover coordination.

---

### 3. ??? Security Guard Dashboard
* Mobile-friendly queue with live request validity timers.
* **Mandatory Physical ID Verification Checklist** before one-click approval.
* Active checkouts monitoring with return condition inspection logging (*Good Condition*, *Minor Wear*, *Damaged*, *Missing Parts*).

---

### 4. ?? Inventory & Bulk Data Hub
* Catalogue overview and individual equipment editor.
* **Download Template**: Standardized CSV and Excel (`.xlsx`) templates with prefilled example rows.
* **Upload Template with Strict Validator**: Comprehensive cell-by-cell validation reporting exact row and column errors.
* **System Audit Trail**: Chronological activity log of all requests, guard approvals, returns, and court bookings.

---

## ?? Design & Theme
* **Modern SaaS Light Theme**: Crisp pure white cards, soft slate canvas (`#F8FAFC`), deep navy typography (`#0F172A`), high-contrast input labels, and clear status pills.

---

## ?? Quick Start

```bash
# Clone the repository
git clone https://github.com/DataSorcerer01/Sports-Dashboard-.git
cd Sports-Dashboard-

# Install dependencies
pip install -r requirements.txt

# Run the Streamlit application
streamlit run app.py
```

---

## ?? License
MIT License. Built for Campus Sports & Recreation Management.
