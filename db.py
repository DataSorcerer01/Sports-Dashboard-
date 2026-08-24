"""
db.py - SQLite database layer, state transitions, auto-expiration engine, and inventory tracking.
"""
import sqlite3
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sports_equipment.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, timeout=20.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Equipment table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS equipment (
        equipment_id TEXT PRIMARY KEY,
        category TEXT NOT NULL,
        item_name TEXT NOT NULL,
        total_quantity INTEGER NOT NULL CHECK(total_quantity >= 0),
        available_quantity INTEGER NOT NULL CHECK(available_quantity >= 0),
        in_use_quantity INTEGER NOT NULL DEFAULT 0 CHECK(in_use_quantity >= 0),
        pending_quantity INTEGER NOT NULL DEFAULT 0 CHECK(pending_quantity >= 0),
        damaged_quantity INTEGER NOT NULL DEFAULT 0 CHECK(damaged_quantity >= 0),
        location_rack TEXT NOT NULL,
        condition TEXT NOT NULL DEFAULT 'Good Condition',
        notes TEXT DEFAULT '',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );
    """)
    
    # Allocation requests table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS allocation_requests (
        request_id TEXT PRIMARY KEY,
        equipment_id TEXT NOT NULL,
        equipment_name TEXT NOT NULL,
        category TEXT NOT NULL,
        student_name TEXT NOT NULL,
        dm_number TEXT NOT NULL,
        mobile_number TEXT NOT NULL,
        room_number TEXT NOT NULL,
        intended_duration TEXT NOT NULL,
        status TEXT NOT NULL,
        requested_at TEXT NOT NULL,
        expires_at TEXT NOT NULL,
        authorized_at TEXT,
        guard_name TEXT,
        returned_at TEXT,
        return_condition TEXT,
        guard_notes TEXT,
        FOREIGN KEY (equipment_id) REFERENCES equipment (equipment_id)
    );
    """)
    
    # Audit log / Return condition records
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inventory_logs (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        equipment_id TEXT NOT NULL,
        action_type TEXT NOT NULL,
        details TEXT NOT NULL,
        actor TEXT NOT NULL
    );
    """)
    
    conn.commit()
    conn.close()


def expire_stale_requests() -> int:
    """
    Evaluates all 'Pending Verification' requests.
    If current_time > expires_at (30 mins elapsed), automatically marks as 'Expired'
    and unblocks the reserved inventory.
    """
    conn = get_connection()
    cursor = conn.cursor()
    now_iso = datetime.now().isoformat()
    
    cursor.execute("""
        SELECT request_id, equipment_id, student_name, dm_number
        FROM allocation_requests
        WHERE status = 'Pending Verification' AND expires_at <= ?
    """, (now_iso,))
    
    expired_rows = cursor.fetchall()
    expired_count = len(expired_rows)
    
    for row in expired_rows:
        req_id = row['request_id']
        eq_id = row['equipment_id']
        
        # Mark request expired
        cursor.execute("""
            UPDATE allocation_requests
            SET status = 'Expired'
            WHERE request_id = ?
        """, (req_id,))
        
        # Release inventory: decrement pending, increment available
        cursor.execute("""
            UPDATE equipment
            SET pending_quantity = MAX(0, pending_quantity - 1),
                available_quantity = available_quantity + 1,
                updated_at = ?
            WHERE equipment_id = ?
        """, (now_iso, eq_id))
        
        # Audit log
        cursor.execute("""
            INSERT INTO inventory_logs (timestamp, equipment_id, action_type, details, actor)
            VALUES (?, ?, 'AUTO_EXPIRE', ?, 'System Timer')
        """, (now_iso, eq_id, f"Request {req_id} by {row['student_name']} ({row['dm_number']}) auto-expired after 30 mins."))
        
    conn.commit()
    conn.close()
    return expired_count


def create_allocation_request(
    equipment_id: str,
    student_name: str,
    dm_number: str,
    mobile_number: str,
    room_number: str,
    intended_duration: str
) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    Submits a student allocation request.
    Strictly reserves 1 unit (Available -> Pending Verification) and sets a 30-min timer.
    """
    expire_stale_requests()
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Check equipment availability
        cursor.execute("SELECT * FROM equipment WHERE equipment_id = ?", (equipment_id,))
        eq = cursor.fetchone()
        if not eq:
            conn.close()
            return False, f"Equipment ID '{equipment_id}' not found.", None
            
        if eq['available_quantity'] <= 0:
            conn.close()
            return False, f"Equipment '{eq['item_name']}' has no available units at this moment.", None
            
        # Generate Request ID (e.g., REQ-20260824-1234)
        now = datetime.now()
        req_id = f"REQ-{now.strftime('%Y%m%d')}-{now.strftime('%H%M%S%f')[:8]}"
        req_at = now.isoformat()
        expires_at = (now + timedelta(minutes=30)).isoformat()
        
        # Reserve equipment unit
        cursor.execute("""
            UPDATE equipment
            SET available_quantity = available_quantity - 1,
                pending_quantity = pending_quantity + 1,
                updated_at = ?
            WHERE equipment_id = ? AND available_quantity > 0
        """, (req_at, equipment_id))
        
        if cursor.rowcount == 0:
            conn.close()
            return False, "Could not reserve item due to concurrent allocation. Please retry.", None
            
        # Insert allocation request
        cursor.execute("""
            INSERT INTO allocation_requests (
                request_id, equipment_id, equipment_name, category,
                student_name, dm_number, mobile_number, room_number,
                intended_duration, status, requested_at, expires_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Pending Verification', ?, ?)
        """, (
            req_id, equipment_id, eq['item_name'], eq['category'],
            student_name.strip(), dm_number.strip().upper(),
            mobile_number.strip(), room_number.strip().upper(),
            intended_duration, req_at, expires_at
        ))
        
        # Log action
        cursor.execute("""
            INSERT INTO inventory_logs (timestamp, equipment_id, action_type, details, actor)
            VALUES (?, ?, 'REQUEST_CREATED', ?, ?)
        """, (req_at, equipment_id, f"Request {req_id} submitted by {student_name} ({dm_number}). 30-min timer started.", student_name))
        
        conn.commit()
        
        req_data = {
            "request_id": req_id,
            "equipment_id": equipment_id,
            "equipment_name": eq['item_name'],
            "category": eq['category'],
            "student_name": student_name,
            "dm_number": dm_number.upper(),
            "mobile_number": mobile_number,
            "room_number": room_number.upper(),
            "intended_duration": intended_duration,
            "status": "Pending Verification",
            "requested_at": req_at,
            "expires_at": expires_at
        }
        conn.close()
        return True, "Request submitted successfully! Present your physical ID card to the guard within 30 minutes.", req_data
        
    except Exception as e:
        conn.rollback()
        conn.close()
        return False, f"Database error while creating request: {str(e)}", None


def approve_allocation_request(request_id: str, guard_name: str = "Duty Guard") -> Tuple[bool, str]:
    """
    Security guard verifies student ID card and authorizes checkout.
    Moves status: 'Pending Verification' -> 'In Use'.
    """
    expire_stale_requests()
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT * FROM allocation_requests WHERE request_id = ?", (request_id,))
        req = cursor.fetchone()
        if not req:
            conn.close()
            return False, f"Request '{request_id}' not found."
            
        if req['status'] == 'Expired':
            conn.close()
            return False, "This request has expired (30-minute window exceeded). The student must submit a new request."
            
        if req['status'] != 'Pending Verification':
            conn.close()
            return False, f"Cannot approve request with current status '{req['status']}'."
            
        now_iso = datetime.now().isoformat()
        
        # Update request status to 'In Use'
        cursor.execute("""
            UPDATE allocation_requests
            SET status = 'In Use',
                authorized_at = ?,
                guard_name = ?
            WHERE request_id = ? AND status = 'Pending Verification'
        """, (now_iso, guard_name, request_id))
        
        # Update equipment counts: pending -> in_use
        cursor.execute("""
            UPDATE equipment
            SET pending_quantity = MAX(0, pending_quantity - 1),
                in_use_quantity = in_use_quantity + 1,
                updated_at = ?
            WHERE equipment_id = ?
        """, (now_iso, req['equipment_id']))
        
        # Audit log
        cursor.execute("""
            INSERT INTO inventory_logs (timestamp, equipment_id, action_type, details, actor)
            VALUES (?, ?, 'GUARD_APPROVED', ?, ?)
        """, (now_iso, req['equipment_id'], f"Authorized checkout for {req['student_name']} ({req['dm_number']}) by {guard_name}.", guard_name))
        
        conn.commit()
        conn.close()
        return True, f"Checkout approved! {req['equipment_name']} is now marked 'In Use' by {req['student_name']}."
        
    except Exception as e:
        conn.rollback()
        conn.close()
        return False, f"Database error approving checkout: {str(e)}"


def return_equipment(
    request_id: str,
    return_condition: str = "Good Condition",
    guard_notes: str = "",
    guard_name: str = "Duty Guard"
) -> Tuple[bool, str]:
    """
    Security guard marks equipment as returned and logs physical condition.
    Moves status: 'In Use' -> 'Returned'.
    Updates equipment counts: decrements in_use, increments available (or damaged).
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT * FROM allocation_requests WHERE request_id = ?", (request_id,))
        req = cursor.fetchone()
        if not req:
            conn.close()
            return False, f"Request '{request_id}' not found."
            
        if req['status'] != 'In Use':
            conn.close()
            return False, f"Cannot return equipment for request with status '{req['status']}'. Must be 'In Use'."
            
        now_iso = datetime.now().isoformat()
        is_damaged = return_condition in ["Damaged / Broken", "Missing Parts"]
        
        # Update request record
        cursor.execute("""
            UPDATE allocation_requests
            SET status = 'Returned',
                returned_at = ?,
                return_condition = ?,
                guard_notes = ?
            WHERE request_id = ?
        """, (now_iso, return_condition, guard_notes.strip(), request_id))
        
        # Update equipment inventory
        if is_damaged:
            cursor.execute("""
                UPDATE equipment
                SET in_use_quantity = MAX(0, in_use_quantity - 1),
                    damaged_quantity = damaged_quantity + 1,
                    condition = ?,
                    updated_at = ?
                WHERE equipment_id = ?
            """, (return_condition, now_iso, req['equipment_id']))
        else:
            cursor.execute("""
                UPDATE equipment
                SET in_use_quantity = MAX(0, in_use_quantity - 1),
                    available_quantity = available_quantity + 1,
                    updated_at = ?
                WHERE equipment_id = ?
            """, (now_iso, req['equipment_id']))
            
        # Log return
        cursor.execute("""
            INSERT INTO inventory_logs (timestamp, equipment_id, action_type, details, actor)
            VALUES (?, ?, 'RETURNED', ?, ?)
        """, (now_iso, req['equipment_id'], f"Returned by {req['student_name']} ({req['dm_number']}). Condition: {return_condition}. Notes: {guard_notes}", guard_name))
        
        conn.commit()
        conn.close()
        return True, f"Equipment '{req['equipment_name']}' successfully checked in. Status reset to Available."
        
    except Exception as e:
        conn.rollback()
        conn.close()
        return False, f"Database error processing return: {str(e)}"


def cancel_request(request_id: str, reason: str = "Cancelled by User") -> Tuple[bool, str]:
    """
    Cancels a pending request and unblocks the item.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT * FROM allocation_requests WHERE request_id = ?", (request_id,))
        req = cursor.fetchone()
        if not req:
            conn.close()
            return False, "Request not found."
            
        if req['status'] != 'Pending Verification':
            conn.close()
            return False, f"Cannot cancel request with status '{req['status']}'."
            
        now_iso = datetime.now().isoformat()
        
        cursor.execute("""
            UPDATE allocation_requests
            SET status = 'Cancelled', guard_notes = ?
            WHERE request_id = ?
        """, (reason, request_id))
        
        cursor.execute("""
            UPDATE equipment
            SET pending_quantity = MAX(0, pending_quantity - 1),
                available_quantity = available_quantity + 1,
                updated_at = ?
            WHERE equipment_id = ?
        """, (now_iso, req['equipment_id']))
        
        conn.commit()
        conn.close()
        return True, "Request cancelled and inventory unblocked."
    except Exception as e:
        conn.rollback()
        conn.close()
        return False, str(e)


def get_all_equipment() -> List[Dict[str, Any]]:
    expire_stale_requests()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM equipment ORDER BY category ASC, item_name ASC")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def get_pending_requests() -> List[Dict[str, Any]]:
    expire_stale_requests()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM allocation_requests
        WHERE status = 'Pending Verification'
        ORDER BY requested_at ASC
    """)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def get_active_checkouts() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM allocation_requests
        WHERE status = 'In Use'
        ORDER BY authorized_at DESC
    """)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def get_student_active_requests(dm_number: str) -> List[Dict[str, Any]]:
    expire_stale_requests()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM allocation_requests
        WHERE dm_number = ? AND status IN ('Pending Verification', 'In Use')
        ORDER BY requested_at DESC
    """, (dm_number.strip().upper(),))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def get_recent_history(limit: int = 50) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM allocation_requests
        ORDER BY requested_at DESC
        LIMIT ?
    """, (limit,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def get_inventory_stats() -> Dict[str, int]:
    expire_stale_requests()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            SUM(total_quantity) as total,
            SUM(available_quantity) as available,
            SUM(in_use_quantity) as in_use,
            SUM(pending_quantity) as pending,
            SUM(damaged_quantity) as damaged
        FROM equipment
    """)
    row = cursor.fetchone()
    conn.close()
    
    return {
        "total": row['total'] or 0,
        "available": row['available'] or 0,
        "in_use": row['in_use'] or 0,
        "pending": row['pending'] or 0,
        "damaged": row['damaged'] or 0,
    }


def add_or_update_equipment(item_dict: Dict[str, Any]) -> Tuple[bool, str]:
    conn = get_connection()
    cursor = conn.cursor()
    now_iso = datetime.now().isoformat()
    
    try:
        cursor.execute("SELECT * FROM equipment WHERE equipment_id = ?", (item_dict['equipment_id'],))
        existing = cursor.fetchone()
        
        if existing:
            # Update existing
            cursor.execute("""
                UPDATE equipment
                SET category = ?,
                    item_name = ?,
                    total_quantity = ?,
                    available_quantity = ?,
                    location_rack = ?,
                    condition = ?,
                    notes = ?,
                    updated_at = ?
                WHERE equipment_id = ?
            """, (
                item_dict['category'],
                item_dict['item_name'],
                item_dict['total_quantity'],
                item_dict['available_quantity'],
                item_dict['location_rack'],
                item_dict.get('condition', 'Good Condition'),
                item_dict.get('notes', ''),
                now_iso,
                item_dict['equipment_id']
            ))
            action = "updated"
        else:
            # Insert new
            cursor.execute("""
                INSERT INTO equipment (
                    equipment_id, category, item_name, total_quantity,
                    available_quantity, in_use_quantity, pending_quantity,
                    damaged_quantity, location_rack, condition, notes,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, 0, 0, 0, ?, ?, ?, ?, ?)
            """, (
                item_dict['equipment_id'],
                item_dict['category'],
                item_dict['item_name'],
                item_dict['total_quantity'],
                item_dict['available_quantity'],
                item_dict['location_rack'],
                item_dict.get('condition', 'Good Condition'),
                item_dict.get('notes', ''),
                now_iso,
                now_iso
            ))
            action = "created"
            
        conn.commit()
        conn.close()
        return True, f"Equipment item {item_dict['equipment_id']} {action} successfully."
    except Exception as e:
        conn.rollback()
        conn.close()
        return False, f"Failed to save equipment: {str(e)}"
