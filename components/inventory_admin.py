import streamlit as st
import pandas as pd
from db import (
    get_all_equipment, add_or_update_equipment,
    get_recent_history, get_inventory_stats
)
from data_io import (
    generate_csv_template, generate_excel_template,
    parse_and_validate_file, commit_inventory_import
)
from models import SPORTS_CATEGORIES
from components.ui_helpers import render_status_badge, format_iso_time


def render_inventory_admin():
    st.markdown("### Sports Inventory & Offline Data Hub")
    st.caption("Manage campus gear stock counts, download standardized templates, bulk-import inventory spreadsheets, and inspect the chronological audit trail.")
    
    tab_catalog, tab_add, tab_bulk, tab_logs = st.tabs([
        "Equipment Catalogue",
        "Add New Equipment",
        "Offline Batch Import/Export",
        "System Audit Trail"
    ])
    
    # -------------------------------------------------------------
    # TAB 1: Catalogue Overview
    # -------------------------------------------------------------
    with tab_catalog:
        st.markdown("#### Campus Sports Inventory Catalogue")
        equipment_list = get_all_equipment()
        
        if equipment_list:
            df_display = pd.DataFrame(equipment_list)[[
                'equipment_id', 'category', 'item_name', 'total_quantity',
                'available_quantity', 'in_use_quantity', 'pending_quantity',
                'damaged_quantity', 'location_rack', 'condition'
            ]]
            df_display.columns = [
                'ID', 'Category', 'Item Name', 'Total', 'Available',
                'In Use', 'Pending', 'Damaged', 'Location Rack', 'Condition'
            ]
            st.dataframe(df_display, use_container_width=True, hide_index=True)
        else:
            st.warning("No equipment in inventory.")

    # -------------------------------------------------------------
    # TAB 2: Add New Equipment Form
    # -------------------------------------------------------------
    with tab_add:
        st.markdown("#### Register New Sports Equipment Item")
        with st.form(key="add_equipment_form"):
            col1, col2 = st.columns(2)
            with col1:
                eq_id = st.text_input(
                    "Equipment Asset ID",
                    placeholder="e.g., EQ-VB-002",
                    help="Unique identifier for the gear item or set. Example: EQ-VB-002"
                )
                category = st.selectbox(
                    "Sports Category",
                    options=SPORTS_CATEGORIES,
                    help="Sports discipline for this equipment."
                )
                item_name = st.text_input(
                    "Item Name & Model",
                    placeholder="e.g., Cosco Super Volley Match Ball",
                    help="Detailed item brand and model name. Example: Cosco Super Volley Match Ball"
                )
            with col2:
                total_qty = st.number_input(
                    "Total Quantity",
                    min_value=1,
                    value=5,
                    step=1,
                    help="Total number of units being added to inventory. Example: 5"
                )
                location_rack = st.text_input(
                    "Storage Rack / Cabinet",
                    placeholder="e.g., Ball Bin 3 (Court Locker)",
                    help="Exact physical storage location in sports room. Example: Ball Bin 3"
                )
                condition = st.selectbox(
                    "Initial Condition",
                    options=["New", "Good Condition", "Minor Normal Wear"],
                    help="Physical quality of the item when adding."
                )
                
            notes = st.text_area(
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
                            st.success(f"{msg}")
                            st.rerun()
                        else:
                            st.error(f"{msg}")

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
    with tab_logs:
        st.markdown("#### Chronological Allocation & Activity Logs")
        history = get_recent_history(limit=50)
        if not history:
            st.info("No allocation activity recorded yet.")
        else:
            for item in history:
                status_color = "#10B981" if item['status'] == "Returned" else "#4F46E5" if item['status'] == "In Use" else "#F59E0B"
                st.markdown(f"""
                <div style="border-left: 3px solid {status_color}; background: #F8FAFC; padding: 0.85rem 1rem; border-radius: 6px; margin-bottom: 0.75rem; border-top: 1px solid #E2E8F0; border-right: 1px solid #E2E8F0; border-bottom: 1px solid #E2E8F0;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: 600; color: #1E293B; font-size: 0.95rem;">
                            {item['equipment_name']} &bull; Borrower: {item['student_name']} ({item['dm_number']})
                        </span>
                        <span>{render_status_badge(item['status'])}</span>
                    </div>
                    <div style="font-size: 0.82rem; color: #64748B; margin-top: 0.35rem;">
                        <strong>Requested:</strong> {format_iso_time(item['requested_at'])} &bull; 
                        <strong>Authorized:</strong> {format_iso_time(item.get('authorized_at'))} &bull; 
                        <strong>Returned:</strong> {format_iso_time(item.get('returned_at'))} &bull; 
                        <strong>Condition:</strong> {item.get('return_condition', 'N/A')}
                    </div>
                    {f"<div style='font-size: 0.8rem; color: #475569; margin-top: 0.25rem; font-style: italic;'>Notes: {item['guard_notes']}</div>" if item.get('guard_notes') else ""}
                </div>
                """, unsafe_allow_html=True)
