"""
sample_data.py - Campus sports equipment inventory seed data.
"""
from datetime import datetime
from db import get_connection, init_db

SEED_EQUIPMENT = [
    {
        "equipment_id": "EQ-BDM-001",
        "category": "Badminton",
        "item_name": "Yonex Nanoray Carbon Badminton Racquet",
        "total_quantity": 6,
        "available_quantity": 6,
        "location_rack": "Rack A-1 (Badminton Locker)",
        "condition": "Good Condition",
        "notes": "Graphite shaft with padded head cover."
    },
    {
        "equipment_id": "EQ-BDM-002",
        "category": "Badminton",
        "item_name": "Yonex Mavis 350 Nylon Shuttlecock (Tube of 6)",
        "total_quantity": 8,
        "available_quantity": 8,
        "location_rack": "Shelf B-2",
        "condition": "Good Condition",
        "notes": "Yellow nylon shuttles for outdoor/indoor court."
    },
    {
        "equipment_id": "EQ-FTB-001",
        "category": "Football",
        "item_name": "Nivia Pro Match Football (Size 5)",
        "total_quantity": 5,
        "available_quantity": 5,
        "location_rack": "Ball Bin 1",
        "condition": "Good Condition",
        "notes": "FIFA-standard match ball, 32-panel stitched."
    },
    {
        "equipment_id": "EQ-BSK-001",
        "category": "Basketball",
        "item_name": "Spalding NBA Game Official Basketball (Size 7)",
        "total_quantity": 4,
        "available_quantity": 4,
        "location_rack": "Ball Bin 2",
        "condition": "Good Condition",
        "notes": "Composite leather with premium grip for wooden/concrete court."
    },
    {
        "equipment_id": "EQ-TT-001",
        "category": "Table Tennis",
        "item_name": "Stag Professional TT Paddle Set (Pair)",
        "total_quantity": 6,
        "available_quantity": 6,
        "location_rack": "Cabinet C-1",
        "condition": "Good Condition",
        "notes": "Includes 2 high-spin rubber racquets."
    },
    {
        "equipment_id": "EQ-TT-002",
        "category": "Table Tennis",
        "item_name": "Stag 3-Star Seamless 40mm TT Balls (Pack of 3)",
        "total_quantity": 10,
        "available_quantity": 10,
        "location_rack": "Cabinet C-1",
        "condition": "Good Condition",
        "notes": "White ITTF approved celluloid-free balls."
    },
    {
        "equipment_id": "EQ-CRK-001",
        "category": "Cricket",
        "item_name": "SS Ton English Willow Cricket Bat",
        "total_quantity": 4,
        "available_quantity": 4,
        "location_rack": "Locker D-1 (Cricket Kit)",
        "condition": "Good Condition",
        "notes": "Full size with toe guard and grip wrap."
    },
    {
        "equipment_id": "EQ-CRK-002",
        "category": "Cricket",
        "item_name": "SG Heavy Tennis Cricket Ball (Pack of 2)",
        "total_quantity": 6,
        "available_quantity": 6,
        "location_rack": "Locker D-1",
        "condition": "Good Condition",
        "notes": "Heavy tournament grade felt ball."
    },
    {
        "equipment_id": "EQ-VOL-001",
        "category": "Volleyball",
        "item_name": "Mikasa V200W Official Match Volleyball",
        "total_quantity": 3,
        "available_quantity": 3,
        "location_rack": "Ball Bin 3",
        "condition": "Good Condition",
        "notes": "Aerodynamic 18-panel design."
    },
    {
        "equipment_id": "EQ-LTN-001",
        "category": "Lawn Tennis",
        "item_name": "Wilson Pro Staff Tennis Racquet",
        "total_quantity": 3,
        "available_quantity": 3,
        "location_rack": "Rack A-3",
        "condition": "Good Condition",
        "notes": "Strung at 55 lbs tension."
    },
    {
        "equipment_id": "EQ-BRD-001",
        "category": "Board Games",
        "item_name": "Tournament Chess Set with Weighted Pieces",
        "total_quantity": 4,
        "available_quantity": 4,
        "location_rack": "Shelf E-1",
        "condition": "Good Condition",
        "notes": "Roll-up vinyl board with Staunton weighted pieces."
    }
]


def seed_database(force_reseed: bool = False):
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) as cnt FROM equipment")
    count = cursor.fetchone()['cnt']
    
    if count == 0 or force_reseed:
        if force_reseed:
            cursor.execute("DELETE FROM allocation_requests")
            cursor.execute("DELETE FROM inventory_logs")
            cursor.execute("DELETE FROM equipment")
            
        now_iso = datetime.now().isoformat()
        for item in SEED_EQUIPMENT:
            cursor.execute("""
                INSERT INTO equipment (
                    equipment_id, category, item_name, total_quantity,
                    available_quantity, in_use_quantity, pending_quantity,
                    damaged_quantity, location_rack, condition, notes,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, 0, 0, 0, ?, ?, ?, ?, ?)
            """, (
                item['equipment_id'], item['category'], item['item_name'],
                item['total_quantity'], item['available_quantity'],
                item['location_rack'], item['condition'], item.get('notes', ''),
                now_iso, now_iso
            ))
            
        conn.commit()
        print(f"Seeded {len(SEED_EQUIPMENT)} equipment items successfully.")
    else:
        print(f"Database already has {count} equipment items.")
        
    conn.close()

if __name__ == '__main__':
    seed_database(force_reseed=True)
