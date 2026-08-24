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
    
    # 2. Student Request Submission
    target_eq = all_eq[0]
    eq_id = target_eq['equipment_id']
    init_avail = target_eq['available_quantity']
    
    ok, msg, req_data = create_allocation_request(
        equipment_id=eq_id,
        student_name="Vikramaditya Roy",
        dm_number="DM2024-9988",
        mobile_number="9876543210",
        room_number="Hostel Block C - Room 302",
        intended_duration="2 Hours"
    )
    assert ok is True, f"Request submission failed: {msg}"
    req_id = req_data['request_id']
    print(f"STEP 2: Student submitted request {req_id} (Reserved 1 unit with 30-min timer).")
    
    # Verify counts: available down by 1, pending up by 1
    stats_after_req = get_inventory_stats()
    assert stats_after_req['available'] == stats['available'] - 1
    assert stats_after_req['pending'] == 1
    print("STEP 3: State transition verified: 1 unit moved to 'Pending Verification'.")
    
    # 3. Guard Approval with Mandatory ID Check
    ok_appr, msg_appr = approve_allocation_request(req_id, guard_name="Officer Rajesh")
    assert ok_appr is True, f"Guard approval failed: {msg_appr}"
    print(f"STEP 4: Security guard verified physical ID and authorized checkout ({msg_appr}).")
    
    # Verify Active Checkouts Peer Transparency Directory
    active_list = get_active_checkouts()
    assert len(active_list) == 1
    borrower_item = active_list[0]
    assert borrower_item['student_name'] == "Vikramaditya Roy"
    assert borrower_item['dm_number'] == "DM2024-9988"
    assert borrower_item['room_number'] == "HOSTEL BLOCK C - ROOM 302"
    assert borrower_item['mobile_number'] == "9876543210"
    assert borrower_item['authorized_at'] is not None
    print("STEP 5: Peer Transparency Directory confirmed: Borrower name, DM, room, phone, issue timestamp visible.")
    
    # 4. Equipment Return & Condition Logging
    ok_ret, msg_ret = return_equipment(
        request_id=req_id,
        return_condition="Good Condition",
        guard_notes="Returned in spotless condition, strings intact",
        guard_name="Officer Rajesh"
    )
    assert ok_ret is True, f"Return failed: {msg_ret}"
    stats_after_ret = get_inventory_stats()
    assert stats_after_ret['in_use'] == 0
    assert stats_after_ret['available'] == stats['available']
    print("STEP 6: Equipment successfully returned and reset to 'Available'.")
    
    # 5. 30-Minute Expiration Engine
    print("Testing strict 30-minute auto-expiration engine...")
    ok_exp, _, req_data_exp = create_allocation_request(
        equipment_id=eq_id,
        student_name="Test Expiry Student",
        dm_number="DM2024-EXPIRE",
        mobile_number="9112233445",
        room_number="Hostel Block A - 101",
        intended_duration="30 Minutes"
    )
    req_exp_id = req_data_exp['request_id']
    
    # Force expiration timestamp into past (>30 min)
    conn = get_connection()
    past_time = (datetime.now() - timedelta(minutes=35)).isoformat()
    conn.execute("UPDATE allocation_requests SET expires_at = ? WHERE request_id = ?", (past_time, req_exp_id))
    conn.commit()
    conn.close()
    
    count_expired = expire_stale_requests()
    assert count_expired >= 1, "Expiry engine failed to identify stale request!"
    
    stats_after_exp = get_inventory_stats()
    assert stats_after_exp['available'] == stats['total']
    assert stats_after_exp['pending'] == 0
    print("STEP 7: Stale request (>30 min) successfully expired and unblocked inventory automatically.")
    
    # 6. CSV/Excel Offline Bulk Operations & Error Diagnostics
    csv_temp = generate_csv_template()
    assert "Equipment_ID" in csv_temp and "Total_Quantity" in csv_temp
    
    # Test error diagnostic precision
    err_df = pd.DataFrame([
        {"Equipment_ID": "EQ-NEW-01", "Category": "Football", "Item_Name": "Pro Ball", "Total_Quantity": "invalid_num", "Condition": "Good", "Location_Rack": "Bin 1", "Notes": ""},
        {"Equipment_ID": "EQ-NEW-02", "Category": "Tennis", "Item_Name": "", "Total_Quantity": 3, "Condition": "Good", "Location_Rack": "Rack T", "Notes": ""}
    ])
    res_err = validate_inventory_dataframe(err_df)
    assert res_err['is_valid'] is False
    assert len(res_err['errors']) == 2
    assert res_err['errors'][0]['row'] == 2 and res_err['errors'][0]['column'] == "Total_Quantity"
    assert res_err['errors'][1]['row'] == 3 and res_err['errors'][1]['column'] == "Item_Name"
    print("STEP 8: CSV/Excel template validator accurately diagnosed exact Row 2 (Total_Quantity) and Row 3 (Item_Name) errors.")
    
    print("=" * 65)
    print("ALL END-TO-END VERIFICATION CHECKS PASSED WITH 100% SUCCESS!")
    print("=" * 65)

if __name__ == '__main__':
    run_end_to_end_verification()
