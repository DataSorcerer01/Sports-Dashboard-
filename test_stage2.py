import io
import pandas as pd
from data_io import (
    generate_csv_template, generate_excel_template,
    validate_inventory_dataframe, parse_and_validate_file,
    commit_inventory_import, REQUIRED_COLUMNS
)
from db import get_all_equipment, init_db

def run_stage2_tests():
    print("=== Starting Stage 2 Automated Unit Tests (Data I/O & Template Validator) ===")
    init_db()
    
    # 1. Test CSV Template Generation
    csv_text = generate_csv_template()
    assert all(col in csv_text for col in REQUIRED_COLUMNS), "CSV template missing required columns!"
    assert "EQ-BDM-003" in csv_text, "CSV template missing example row!"
    print("PASS [1/6]: CSV template correctly generated with required headers and example row.")
    
    # 2. Test Excel Template Generation
    excel_bytes = generate_excel_template()
    assert len(excel_bytes) > 100, "Excel template output was empty!"
    df_excel = pd.read_excel(io.BytesIO(excel_bytes))
    assert list(df_excel.columns) == REQUIRED_COLUMNS, "Excel template columns mismatch!"
    print("PASS [2/6]: Excel (.xlsx) template successfully generated with proper formatting.")
    
    # 3. Test Valid Data Validation & Import
    res_valid = validate_inventory_dataframe(df_excel)
    assert res_valid['is_valid'] is True, f"Valid template failed validation: {res_valid['errors']}"
    assert len(res_valid['clean_data']) == 2, "Expected 2 clean items"
    ins, errs, _ = commit_inventory_import(res_valid['clean_data'])
    assert ins == 2 and errs == 0, "Failed to commit valid items to database"
    print("PASS [3/6]: Valid template parsed, validated, and imported into database without errors.")
    
    # 4. Test Missing Header Detection
    df_bad_header = pd.DataFrame([{"Equipment_ID": "EQ-01", "Category": "Football"}])
    res_bad_header = validate_inventory_dataframe(df_bad_header)
    assert res_bad_header['is_valid'] is False, "Did not catch missing headers!"
    assert "Total_Quantity" in res_bad_header['errors'][0]['message'], "Did not name missing Total_Quantity column!"
    print(f"PASS [4/6]: Missing header detected with exact missing columns: {res_bad_header['errors'][0]['message']}")
    
    # 5. Test Cell-Level Value Errors (Bad integer, negative quantity, blank fields)
    bad_rows = [
        # Row 2: bad quantity "five"
        {
            "Equipment_ID": "EQ-ERR-1",
            "Category": "Football",
            "Item_Name": "Match Ball",
            "Total_Quantity": "five",
            "Condition": "Good Condition",
            "Location_Rack": "Bin 1",
            "Notes": ""
        },
        # Row 3: negative quantity -2
        {
            "Equipment_ID": "EQ-ERR-2",
            "Category": "Basketball",
            "Item_Name": "Game Ball",
            "Total_Quantity": -2,
            "Condition": "Good Condition",
            "Location_Rack": "Bin 2",
            "Notes": ""
        },
        # Row 4: blank Item_Name
        {
            "Equipment_ID": "EQ-ERR-3",
            "Category": "Badminton",
            "Item_Name": "",
            "Total_Quantity": 4,
            "Condition": "Good Condition",
            "Location_Rack": "Rack A",
            "Notes": ""
        },
        # Row 5: blank Location_Rack
        {
            "Equipment_ID": "EQ-ERR-4",
            "Category": "Cricket",
            "Item_Name": "SS Bat",
            "Total_Quantity": 2,
            "Condition": "Good Condition",
            "Location_Rack": "",
            "Notes": ""
        }
    ]
    df_bad_cells = pd.DataFrame(bad_rows)
    res_bad_cells = validate_inventory_dataframe(df_bad_cells)
    assert res_bad_cells['is_valid'] is False, "Did not catch cell-level errors!"
    assert len(res_bad_cells['errors']) >= 4, f"Expected at least 4 errors, got {len(res_bad_cells['errors'])}"
    
    # Verify row numbers and column names are accurately reported
    rows_reported = [e['row'] for e in res_bad_cells['errors']]
    cols_reported = [e['column'] for e in res_bad_cells['errors']]
    assert 2 in rows_reported and 3 in rows_reported and 4 in rows_reported and 5 in rows_reported, "Row numbers mismatch!"
    assert "Total_Quantity" in cols_reported and "Item_Name" in cols_reported and "Location_Rack" in cols_reported, "Column names mismatch!"
    print("PASS [5/6]: Cell-level validations correctly reported exact row numbers (Rows 2, 3, 4, 5) and column names.")
    
    # 6. Test Duplicate Equipment_ID Detection
    dup_rows = [
        {"Equipment_ID": "EQ-DUP-1", "Category": "Football", "Item_Name": "Ball A", "Total_Quantity": 2, "Condition": "Good", "Location_Rack": "B1", "Notes": ""},
        {"Equipment_ID": "EQ-DUP-1", "Category": "Football", "Item_Name": "Ball B", "Total_Quantity": 2, "Condition": "Good", "Location_Rack": "B1", "Notes": ""}
    ]
    df_dup = pd.DataFrame(dup_rows)
    res_dup = validate_inventory_dataframe(df_dup)
    assert res_dup['is_valid'] is False, "Did not catch duplicate Equipment_ID!"
    assert "Duplicate Equipment_ID 'EQ-DUP-1'" in res_dup['errors'][0]['message'], "Duplicate error message mismatch!"
    print(f"PASS [6/6]: Duplicate Equipment_ID detected: {res_dup['errors'][0]['message']}")
    
    print("\n>>> ALL STAGE 2 TESTS PASSED WITH 100% SUCCESS <<<")

if __name__ == '__main__':
    run_stage2_tests()
