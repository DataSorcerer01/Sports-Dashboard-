from db import init_db, seed_database, get_all_courts, occupy_court, release_court, get_court_stats

init_db()
seed_database(force_reseed=True)

# 1. Verify 14 courts
courts = get_all_courts()
assert len(courts) == 14, f"Expected 14 courts, got {len(courts)}"
stats_init = get_court_stats()
assert stats_init['total'] == 14
assert stats_init['available'] == 14
assert stats_init['occupied'] == 0

# 2. Test Check-in / Occupy Court
ok, msg = occupy_court(
    court_id="CRT-BDM-01",
    student_name="Ananya Roy",
    dm_number="DM2024-2041",
    contact_number="9876543210",
    hostel_room="MG Block 104",
    intended_duration="1 Hour",
    notes="Doubles match"
)
assert ok is True, f"Failed to occupy court: {msg}"
stats_occ = get_court_stats()
assert stats_occ['occupied'] == 1
assert stats_occ['available'] == 13

# 3. Test double occupation prevention
ok_double, msg_double = occupy_court(
    court_id="CRT-BDM-01",
    student_name="Vikramaditya",
    dm_number="DM2024-1052",
    contact_number="9988776655",
    hostel_room="Elango Block 202",
    intended_duration="30 Minutes"
)
assert ok_double is False, "Allowed double occupation on occupied court!"

# 4. Test Court Release / Check-out
ok_rel, msg_rel = release_court("CRT-BDM-01", released_by="Duty Guard")
assert ok_rel is True, f"Failed to release court: {msg_rel}"
stats_rel = get_court_stats()
assert stats_rel['occupied'] == 0
assert stats_rel['available'] == 14

print("ALL COURT & FACILITY LOGIC TESTS PASSED SUCCESSFULLY (100% SUCCESS)!")
