import io
import csv
import pandas as pd
from typing import Tuple, List, Dict, Any, Optional
from db import add_or_update_equipment, get_connection
from models import SPORTS_CATEGORIES

REQUIRED_COLUMNS = [
    "Equipment_ID",
    "Category",
    "Item_Name",
    "Total_Quantity",
    "Condition",
    "Location_Rack",
    "Notes"
]

EXAMPLE_ROWS = [
    {
        "Equipment_ID": "EQ-BDM-003",
        "Category": "Badminton",
        "Item_Name": "Li-Ning G-Force Superlite Badminton Racquet",
        "Total_Quantity": 4,
        "Condition": "Good Condition",
        "Location_Rack": "Rack A-2",
        "Notes": "Pre-strung high tension carbon fiber"
    },
    {
        "Equipment_ID": "EQ-FTB-002",
        "Category": "Football",
        "Item_Name": "Adidas Tango Training Football (Size 5)",
        "Total_Quantity": 6,
        "Condition": "Good Condition",
        "Location_Rack": "Ball Bin 1",
        "Notes": "Outdoor synthetic turf match ball"
    }
]

VALID_CONDITIONS = [
    "Good Condition",
    "Minor Normal Wear",
    "New",
    "Damaged / Broken",
    "Under Maintenance"
]


def generate_csv_template() -> str:
    """
    Generates a CSV template with standard column headers and example rows.
    """
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=REQUIRED_COLUMNS, lineterminator="\n")
    writer.writeheader()
    for row in EXAMPLE_ROWS:
        writer.writerow(row)
    return output.getvalue()


def generate_excel_template() -> bytes:
    """
    Generates an Excel (.xlsx) template with standard column headers and example rows.
    """
    output = io.BytesIO()
    df = pd.DataFrame(EXAMPLE_ROWS, columns=REQUIRED_COLUMNS)
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Inventory Template")
    return output.getvalue()


def validate_inventory_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Performs comprehensive cell-by-cell and row-by-row validation on uploaded data.
    Never fails silently: returns exact row index, column name, and explanation.
    """
    errors: List[Dict[str, Any]] = []
    
    # 1. Header Validation
    df_cols = [str(col).strip() for col in df.columns]
    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df_cols]
    
    if missing_cols:
        return {
            "is_valid": False,
            "error_type": "HEADER_ERROR",
            "errors": [{
                "row": "Header",
                "column": ", ".join(missing_cols),
                "message": f"Missing required column header(s): {', '.join(missing_cols)}. Expected headers: {', '.join(REQUIRED_COLUMNS)}"
            }],
            "clean_data": [],
            "row_count": len(df)
        }
        
    if len(df) == 0:
        return {
            "is_valid": False,
            "error_type": "EMPTY_FILE",
            "errors": [{
                "row": 0,
                "column": "All",
                "message": "The uploaded file contains column headers but has zero data rows."
            }],
            "clean_data": [],
            "row_count": 0
        }
        
    seen_ids = set()
    clean_data: List[Dict[str, Any]] = []
    
    # 2. Row and Cell Level Validation
    for idx, raw_row in df.iterrows():
        # Human-friendly row number (1-based header is row 1, data rows start at row 2)
        row_num = idx + 2
        row_has_error = False
        
        # Equipment_ID
        eq_id_raw = raw_row.get("Equipment_ID")
        if pd.isna(eq_id_raw) or str(eq_id_raw).strip() == "":
            errors.append({
                "row": row_num,
                "column": "Equipment_ID",
                "value": str(eq_id_raw),
                "message": f"Row {row_num}: 'Equipment_ID' cannot be empty."
            })
            row_has_error = True
        else:
            eq_id = str(eq_id_raw).strip()
            if eq_id in seen_ids:
                errors.append({
                    "row": row_num,
                    "column": "Equipment_ID",
                    "value": eq_id,
                    "message": f"Row {row_num}: Duplicate Equipment_ID '{eq_id}' found. Each item must have a unique ID."
                })
                row_has_error = True
            seen_ids.add(eq_id)
            
        # Category
        cat_raw = raw_row.get("Category")
        if pd.isna(cat_raw) or str(cat_raw).strip() == "":
            errors.append({
                "row": row_num,
                "column": "Category",
                "value": str(cat_raw),
                "message": f"Row {row_num}: 'Category' is required and cannot be empty."
            })
            row_has_error = True
            cat = ""
        else:
            cat = str(cat_raw).strip()
            
        # Item_Name
        name_raw = raw_row.get("Item_Name")
        if pd.isna(name_raw) or str(name_raw).strip() == "":
            errors.append({
                "row": row_num,
                "column": "Item_Name",
                "value": str(name_raw),
                "message": f"Row {row_num}: 'Item_Name' is required and cannot be empty."
            })
            row_has_error = True
            item_name = ""
        else:
            item_name = str(name_raw).strip()
            
        # Total_Quantity
        qty_raw = raw_row.get("Total_Quantity")
        total_qty = 0
        if pd.isna(qty_raw) or str(qty_raw).strip() == "":
            errors.append({
                "row": row_num,
                "column": "Total_Quantity",
                "value": "empty",
                "message": f"Row {row_num}: 'Total_Quantity' is missing. Must be a positive integer."
            })
            row_has_error = True
        else:
            try:
                total_qty = int(float(qty_raw))
                if total_qty <= 0:
                    errors.append({
                        "row": row_num,
                        "column": "Total_Quantity",
                        "value": str(qty_raw),
                        "message": f"Row {row_num}: 'Total_Quantity' must be greater than 0, but found '{qty_raw}'."
                    })
                    row_has_error = True
            except (ValueError, TypeError):
                errors.append({
                    "row": row_num,
                    "column": "Total_Quantity",
                    "value": str(qty_raw),
                    "message": f"Row {row_num}: 'Total_Quantity' must be a valid integer number, but found '{qty_raw}'."
                })
                row_has_error = True
                
        # Condition
        cond_raw = raw_row.get("Condition")
        if pd.isna(cond_raw) or str(cond_raw).strip() == "":
            condition = "Good Condition"
        else:
            condition = str(cond_raw).strip()
            
        # Location_Rack
        loc_raw = raw_row.get("Location_Rack")
        if pd.isna(loc_raw) or str(loc_raw).strip() == "":
            errors.append({
                "row": row_num,
                "column": "Location_Rack",
                "value": "empty",
                "message": f"Row {row_num}: 'Location_Rack' is required (e.g., 'Rack A-1', 'Locker 2')."
            })
            row_has_error = True
            location_rack = ""
        else:
            location_rack = str(loc_raw).strip()
            
        # Notes
        notes_raw = raw_row.get("Notes")
        notes = "" if pd.isna(notes_raw) else str(notes_raw).strip()
        
        if not row_has_error:
            clean_data.append({
                "equipment_id": str(eq_id_raw).strip(),
                "category": cat,
                "item_name": item_name,
                "total_quantity": total_qty,
                "available_quantity": total_qty,
                "location_rack": location_rack,
                "condition": condition,
                "notes": notes
            })
            
    is_valid = len(errors) == 0
    return {
        "is_valid": is_valid,
        "error_type": None if is_valid else "CELL_VALIDATION_ERROR",
        "errors": errors,
        "clean_data": clean_data,
        "row_count": len(df),
        "valid_count": len(clean_data)
    }


def parse_and_validate_file(file_obj, filename: str) -> Dict[str, Any]:
    """
    Reads uploaded CSV or Excel file object and validates contents.
    """
    try:
        if filename.endswith(".csv"):
            df = pd.read_csv(file_obj)
        elif filename.endswith((".xlsx", ".xls")):
            df = pd.read_excel(file_obj)
        else:
            return {
                "is_valid": False,
                "error_type": "FILE_FORMAT_ERROR",
                "errors": [{
                    "row": "N/A",
                    "column": "File Type",
                    "message": f"Unsupported file extension for '{filename}'. Please upload a .csv or .xlsx file."
                }],
                "clean_data": [],
                "row_count": 0
            }
        return validate_inventory_dataframe(df)
    except Exception as e:
        return {
            "is_valid": False,
            "error_type": "PARSING_ERROR",
            "errors": [{
                "row": "N/A",
                "column": "File Content",
                "message": f"Could not parse file '{filename}'. Details: {str(e)}"
            }],
            "clean_data": [],
            "row_count": 0
        }


def commit_inventory_import(clean_data: List[Dict[str, Any]]) -> Tuple[int, int, List[str]]:
    """
    Saves validated inventory items to database.
    """
    inserted = 0
    errors = []
    for item in clean_data:
        ok, msg = add_or_update_equipment(item)
        if ok:
            inserted += 1
        else:
            errors.append(f"Item {item['equipment_id']}: {msg}")
    return inserted, len(errors), errors
