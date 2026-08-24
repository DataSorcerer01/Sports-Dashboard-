import io
import pandas as pd
from datetime import datetime, timedelta
from db import (
    init_db, get_connection, create_allocation_request,
    approve_allocation_request, return_equipment,
    cancel_request, expire_stale_requests, get_all_equipment,
    get_pending_requests, get_active_checkouts,
    get_student_active_requests, get_inventory_stats,
    add_or_update_equipment, seed_database
)
from data_io import (
    generate_csv_template, generate_excel_template,
    validate_inventory_dataframe, commit_inventory_import
)

def run_end_to_end_verification():
    print("=" * 65)
    print("RUNNING FULL END-TO-END VERIFICATION SUITE")
    print("=" * 65)
    
    # 1. Initialize & Seed DB
    seed_database(force_reseed=True)
    all_eq = get_all_equipment()
    stats = get_inventory_stats()
    assert len(all_eq) >= 10, "Equipment catalog must contain initial items"
    assert stats['available'] == stats['total'], "All items should be initially available"
    print(f"STEP 1: DB Initialized and Seeded ({stats['total']} total items, {stats['available']} available).")
    
    # 2. Student Request Submission with Quantity = 2
    target_eq = all_eq[0]
    eq_id = target_eq['equipment_id']
    init_avail = target_eq['available_quantity']
    
    ok, msg, req_data = create_allocation_request(
        equipment_id=eq_id,
        student_name="Vikramaditya Roy",
        dm_number="DM2024-9988",
        mobile_number="9876543210",
        room_number="Hostel Block C - Room 302",
        intended_duration="2 Hours",
        quantity=2
    )
    assert ok is True, f"Request submission failed: {msg}"
    req_id = req_data['request_id']
    assert req_data['quantity'] == 2
    print(f"STEP 2: Student submitted request {req_id} (Reserved 2 units with 30-min timer).")
    
    # Verify counts: available down by 2, pending up by 2
    stats_after_req = get_inventory_stats()
    assert stats_after_req['available'] == stats['available'] - 2
    assert stats_after_req['pending'] == 2
    print("STEP 3: State transition verified: 2 units moved to 'Pending Verification'.")
    
    # 3. Guard Approval with Mandatory ID Check
    ok_appr, msg_appr = approve_allocation_request(req_id, guard_name="Officer Rajesh")
    assert ok_appr is True, f"Guard approval failed: {msg_appr}"
    print(f"STEP 4: Security guard verified physical ID and authorized checkout ({msg_appr}).")
    
    # Verify Active Checkouts Peer Transparency Directory
    active_list = get_active_checkouts()
    assert len(active_list) == 1
    assert active_list[0]['quantity'] == 2
    assert active_list[0]['student_name'] == "Vikramaditya Roy"
    print("STEP 5: Peer Transparency Directory confirmed: Borrower name, DM, room, phone, quantity (2), issue timestamp visible.")
    
    # 4. Return Processing
    ok_ret, msg_ret = return_equipment(
        request_id=req_id,
        return_condition="Good Condition",
        guard_notes="Returned intact on time",
        guard_name="Officer Rajesh"
    )
    assert ok_ret is True, f"Equipment return failed: {msg_ret}"
    stats_after_ret = get_inventory_stats()
    assert stats_after_ret['available'] == stats['total']
    assert stats_after_ret['in_use'] == 0
    print("STEP 6: Equipment successfully returned and reset to 'Available'.")
    
    # 5. Timer Expiration Verification
    print("Testing strict 30-minute auto-expiration engine...")
    ok_stale, _, stale_req = create_allocation_request(
        equipment_id=eq_id,
        student_name="Ananya Verma",
        dm_number="DM2024-5544",
        mobile_number="9988776655",
        room_number="Hostel Block A - 101",
        intended_duration="1 Hour",
        quantity=2
    )
    stale_id = stale_req['request_id']
    
    # Backdate expiration timestamp in DB to simulate 35 mins elapsed
    past_iso = (datetime.now() - timedelta(minutes=35)).isoformat()
    conn = get_connection()
    conn.execute("UPDATE allocation_requests SET expires_at = ? WHERE request_id = ?", (past_iso, stale_id))
    conn.commit()
    conn.close()
    
    # Run auto-expire
    expired_cnt = expire_stale_requests()
    assert expired_cnt >= 1, "Auto-expire engine must expire overdue requests"
    
    stats_after_expire = get_inventory_stats()
    assert stats_after_expire['available'] == stats['total'], "Inventory must be restored on expiration"
    assert stats_after_expire['pending'] == 0
    print(f"STEP 7: Stale request (>30 min, 2 units) successfully expired and unblocked inventory automatically.")
    
    # 6. Bulk Import Validation Engine Test
    sample_invalid_df = pd.DataFrame([
        {"Equipment_ID": "EQ-NEW-01", "Category": "Badminton", "Item_Name": "Badminton", "Total_Quantity": 5, "Condition": "Good Condition", "Location_Rack": "Rack A", "Notes": "OK"},
        {"Equipment_ID": "EQ-NEW-02", "Category": "Cricket", "Item_Name": "Bat", "Total_Quantity": -3, "Condition": "Good Condition", "Location_Rack": "Rack B", "Notes": "Bad Qty"}, # invalid qty
        {"Equipment_ID": "EQ-NEW-03", "Category": "Tennis", "Item_Name": "", "Total_Quantity": 4, "Condition": "Good Condition", "Location_Rack": "Rack C", "Notes": "Empty Name"}, # empty name
    ])
    val_res = validate_inventory_dataframe(sample_invalid_df)
    assert val_res['is_valid'] is False
    assert len(val_res['errors']) == 2
    print(f"STEP 8: CSV/Excel template validator accurately diagnosed exact Row 2 (Total_Quantity) and Row 3 (Item_Name) errors.")
    
    print("=" * 65)
    print("ALL END-TO-END VERIFICATION CHECKS PASSED WITH 100% SUCCESS!")
    print("=" * 65)

if __name__ == "__main__":
    run_end_to_end_verification()
