import io
import pandas as pd
import streamlit as st
from db import (
    get_all_equipment, add_or_update_equipment,
    get_recent_history, get_connection
)
from models import SPORTS_CATEGORIES, ReturnCondition
from data_io import (
    generate_csv_template, generate_excel_template,
    parse_and_validate_file, commit_inventory_import
)
from components.ui_helpers import format_iso_time


def render_inventory_admin():
    st.markdown("### Inventory & Offline Data Management Hub")
    st.caption("Add new sports gear, manage catalogue items, download/upload CSV & Excel batch files, and view audit trails.")
    
    tab_overview, tab_add, tab_bulk, tab_audit = st.tabs([
        "Equipment Catalogue",
        "Add / Edit Equipment",
        "Offline Batch Import/Export",
        "System Audit Trail"
    ])
    
    # -------------------------------------------------------------
    # TAB 1: Equipment Catalogue
    # -------------------------------------------------------------
    with tab_overview:
        equipment = get_all_equipment()
        st.markdown(f"#### Active Campus Inventory ({len(equipment)} item models)")
        
        if equipment:
            df = pd.DataFrame(equipment)[[
                'equipment_id', 'category', 'item_name', 'total_quantity',
                'available_quantity', 'in_use_quantity', 'pending_quantity',
                'damaged_quantity', 'location_rack', 'condition'
            ]]
            df.columns = [
                'ID', 'Category', 'Item Name', 'Total', 'Available',
                'In Use', 'Pending', 'Damaged', 'Location Rack', 'Condition'
            ]
            st.dataframe(df, use_container_width=True, hide_index=True)
            
    # -------------------------------------------------------------
    # TAB 2: Add New Equipment
    # -------------------------------------------------------------
    with tab_add:
        st.markdown("#### Add New Sports Equipment to Catalogue")
        
        with st.form(key="add_equipment_form"):
            c1, c2 = st.columns(2)
            with c1:
                eq_id = st.text_input(
                    "Equipment Asset ID (Unique)",
                    placeholder="e.g., EQ-VB-001",
                    help="Unique campus asset code for the equipment model."
                )
                category = st.selectbox("Sport / Equipment Category", options=SPORTS_CATEGORIES, index=0)
                item_name = st.text_input(
                    "Item Name & Model",
                    placeholder="e.g., Mikasa MVA200 Competition Volleyball",
                    help="Full descriptive name of the sports gear."
                )
                
            with c2:
                total_qty = st.number_input("Total Quantity Units", min_value=1, value=5, step=1)
                location_rack = st.text_input(
                    "Storage Rack / Cabinet Location",
                    placeholder="e.g., Rack B-2 (Indoor Arena)",
                    help="Exact physical location in the sports room."
                )
                condition = st.selectbox(
                    "Initial Physical Condition",
                    options=[
                        ReturnCondition.GOOD.value,
                        ReturnCondition.MINOR_WEAR.value,
                        ReturnCondition.DAMAGED.value
                    ],
                    index=0
                )
                
            notes = st.text_input(
                "Additional Item Notes (Optional)",
                placeholder="e.g., Includes ball pump needle and mesh carrier bag",
                help="Any special maintenance instructions or included accessories."
            )
            
            submit_add = st.form_submit_button("Save Equipment to Inventory", type="primary", use_container_width=True)
            if submit_add:
                if not eq_id.strip():
                    st.error("Equipment Asset ID is required.")
                elif not item_name.strip():
                    st.error("Item Name & Model is required.")
                elif not location_rack.strip():
                    st.error("Storage Rack / Cabinet is required.")
                else:
                    item_dict = {
                        "equipment_id": eq_id.strip().upper(),
                        "category": category,
                        "item_name": item_name.strip(),
                        "total_quantity": int(total_qty),
                        "available_quantity": int(total_qty),
                        "location_rack": location_rack.strip(),
                        "condition": condition,
                        "notes": notes.strip()
                    }
                    with st.spinner("Saving equipment..."):
                        ok, msg = add_or_update_equipment(item_dict)
                        if ok:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)

    # -------------------------------------------------------------
    # TAB 3: Batch Offline Import / Export
    # -------------------------------------------------------------
    with tab_bulk:
        st.markdown("#### Offline Data Management (Download & Upload)")
        st.caption("Work with sports inventory offline via CSV or Excel spreadsheets with strict row-by-row error diagnostics.")
        
        down_col1, down_col2 = st.columns(2)
        with down_col1:
            with st.container(border=True):
                st.markdown("##### Download Inventory Template")
                st.markdown("Get a pre-formatted spreadsheet template with the exact column headers and a ready-to-run example row.")
                
                csv_data = generate_csv_template()
                st.download_button(
                    label="Download Template (CSV)",
                    data=csv_data,
                    file_name="sports_equipment_template.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                
                excel_data = generate_excel_template()
                st.download_button(
                    label="Download Template (Excel .xlsx)",
                    data=excel_data,
                    file_name="sports_equipment_template.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            
        with down_col2:
            with st.container(border=True):
                st.markdown("##### Upload Filled Inventory File")
                st.markdown("Upload your completed CSV or Excel inventory file. Our system checks every cell and row before saving.")
                
                uploaded_file = st.file_uploader(
                    "Select CSV or Excel file to upload",
                    type=["csv", "xlsx", "xls"],
                    help="Upload a valid CSV or Excel inventory spreadsheet adhering to the downloaded template."
                )
                
                if uploaded_file is not None:
                    with st.spinner("Validating uploaded file structure and cell contents..."):
                        res = parse_and_validate_file(uploaded_file, uploaded_file.name)
                        
                    if not res['is_valid']:
                        st.error(f"Validation Failed ({len(res['errors'])} issue(s) detected):")
                        for err in res['errors']:
                            st.markdown(f"- **Row {err['row']}** (Column: `{err['column']}`): {err['message']}")
                    else:
                        st.success(f"File validation passed! Found **{res['valid_count']}** valid equipment record(s).")
                        if st.button("Commit and Import Records into Inventory", type="primary", use_container_width=True):
                            with st.spinner("Importing validated inventory into database..."):
                                ins, errs, err_list = commit_inventory_import(res['clean_data'])
                                if errs == 0:
                                    st.success(f"Successfully imported {ins} equipment items into the campus database!")
                                    st.rerun()
                                else:
                                    st.warning(f"Imported {ins} items, but encountered {errs} issues:")
                                    for e in err_list:
                                        st.error(e)

    # -------------------------------------------------------------
    # TAB 4: System Audit Trail
    # -------------------------------------------------------------
    with tab_audit:
        st.markdown("#### System Activity & Allocation Audit Logs")
        st.caption("Full historical record of requests, checkout approvals, return condition checks, and auto-expirations.")
        
        conn = get_connection()
        logs_df = pd.read_sql_query("""
            SELECT log_id, timestamp, equipment_id, action_type, actor, details
            FROM inventory_logs
            ORDER BY log_id DESC
            LIMIT 100
        """, conn)
        conn.close()
        
        if not logs_df.empty:
            logs_df['timestamp'] = logs_df['timestamp'].apply(format_iso_time)
            logs_df.columns = ['Log #', 'Timestamp', 'Equipment / Court ID', 'Action', 'Actor', 'Details']
            st.dataframe(logs_df, use_container_width=True, hide_index=True)
        else:
            st.info("No audit logs recorded yet. System activities will automatically appear here.")
