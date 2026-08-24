"""
sample_data.py - Campus sports equipment inventory & courts seed data.
"""
from datetime import datetime

SEED_EQUIPMENT = [
    {
        "equipment_id": "EQ-BDM-001",
        "category": "Badminton",
        "item_name": "Yonex Carbon Badminton Racquet",
        "total_quantity": 10,
        "available_quantity": 10,
        "location_rack": "Rack A-1 (Badminton Locker)",
        "condition": "Good Condition",
        "notes": "10 rackets available for match and practice."
    },
    {
        "equipment_id": "EQ-TT-001",
        "category": "Table Tennis",
        "item_name": "Stag Professional TT Racquet",
        "total_quantity": 10,
        "available_quantity": 10,
        "location_rack": "Cabinet C-1 (TT Arena)",
        "condition": "Good Condition",
        "notes": "10 TT rackets available for indoor play."
    },
    {
        "equipment_id": "EQ-TT-002",
        "category": "Table Tennis",
        "item_name": "Stag 3-Star 40mm TT Balls",
        "total_quantity": 5,
        "available_quantity": 5,
        "location_rack": "Cabinet C-1 (TT Arena)",
        "condition": "Good Condition",
        "notes": "5 official match TT balls."
    },
    {
        "equipment_id": "EQ-POOL-001",
        "category": "Pool & Billiards",
        "item_name": "Full Pool & Billiards Kit (Cues, Chalk, Triangle, Ball Set)",
        "total_quantity": 1,
        "available_quantity": 1,
        "location_rack": "Billiards Room Locker",
        "condition": "Good Condition",
        "notes": "1 full pool kit with cues, triangle, cue balls, and chalk."
    },
    {
        "equipment_id": "EQ-CRM-001",
        "category": "Carrom",
        "item_name": "Carrom Board Coins & Striker Set",
        "total_quantity": 2,
        "available_quantity": 2,
        "location_rack": "Shelf E-1 (Recreation Room)",
        "condition": "Good Condition",
        "notes": "2 complete sets of wooden coins, queen, and weighted tournament strikers."
    },
    {
        "equipment_id": "EQ-CRK-001",
        "category": "Cricket",
        "item_name": "SS Willow Cricket Bat",
        "total_quantity": 2,
        "available_quantity": 2,
        "location_rack": "Locker D-1 (Cricket Kit)",
        "condition": "Good Condition",
        "notes": "2 full-size bats with grip wrap and protective toe guard."
    },
    {
        "equipment_id": "EQ-CRK-002",
        "category": "Cricket",
        "item_name": "Tournament Match Cricket Ball",
        "total_quantity": 1,
        "available_quantity": 1,
        "location_rack": "Locker D-1 (Cricket Kit)",
        "condition": "Good Condition",
        "notes": "1 leather match cricket ball."
    },
    {
        "equipment_id": "EQ-FTB-001",
        "category": "Football",
        "item_name": "Nivia Match Football (Size 5)",
        "total_quantity": 1,
        "available_quantity": 1,
        "location_rack": "Ball Bin 1 (Stadium)",
        "condition": "Good Condition",
        "notes": "1 FIFA standard match ball, 32-panel stitched."
    },
    {
        "equipment_id": "EQ-PB-001",
        "category": "Pickleball",
        "item_name": "Pro Graphite Pickleball Paddle",
        "total_quantity": 10,
        "available_quantity": 10,
        "location_rack": "Rack P-1 (Pickleball Locker)",
        "condition": "Good Condition",
        "notes": "10 pickleball rackets available with ergonomic grip."
    },
    {
        "equipment_id": "EQ-PB-002",
        "category": "Pickleball",
        "item_name": "USAPA Outdoor Pickleball Balls",
        "total_quantity": 2,
        "available_quantity": 2,
        "location_rack": "Rack P-1 (Pickleball Locker)",
        "condition": "Good Condition",
        "notes": "2 high-durability perforated pickleball balls."
    },
    {
        "equipment_id": "EQ-TN-001",
        "category": "Tennis",
        "item_name": "Wilson Pro Staff Tennis Racquet",
        "total_quantity": 4,
        "available_quantity": 4,
        "location_rack": "Rack A-3 (Tennis Locker)",
        "condition": "Good Condition",
        "notes": "4 tennis rackets pre-strung."
    },
    {
        "equipment_id": "EQ-TN-002",
        "category": "Tennis",
        "item_name": "Wilson Championship Tennis Balls",
        "total_quantity": 4,
        "available_quantity": 4,
        "location_rack": "Rack A-3 (Tennis Locker)",
        "condition": "Good Condition",
        "notes": "4 pressurized championship tennis balls."
    }
]

SEED_COURTS = [
    {
        "court_id": "CRT-BDM-01",
        "court_name": "Badminton Court 1",
        "sport_type": "Badminton",
        "location_venue": "Elango Complex",
        "status": "Available",
        "notes": "Indoor wooden court - Court 1"
    },
    {
        "court_id": "CRT-BDM-02",
        "court_name": "Badminton Court 2",
        "sport_type": "Badminton",
        "location_venue": "Elango Complex",
        "status": "Available",
        "notes": "Indoor wooden court - Court 2"
    },
    {
        "court_id": "CRT-BDM-03",
        "court_name": "Badminton Court 3",
        "sport_type": "Badminton",
        "location_venue": "MG Complex",
        "status": "Available",
        "notes": "Synthetic mat indoor court - Court 3"
    },
    {
        "court_id": "CRT-BDM-04",
        "court_name": "Badminton Court 4",
        "sport_type": "Badminton",
        "location_venue": "MG Complex",
        "status": "Available",
        "notes": "Synthetic mat indoor court - Court 4"
    },
    {
        "court_id": "CRT-PB-01",
        "court_name": "Pickleball Court 1",
        "sport_type": "Pickleball",
        "location_venue": "Outdoor Arena",
        "status": "Available",
        "notes": "Official size pickleball court with regulation net"
    },
    {
        "court_id": "CRT-PB-02",
        "court_name": "Pickleball Court 2",
        "sport_type": "Pickleball",
        "location_venue": "Outdoor Arena",
        "status": "Available",
        "notes": "Official size pickleball court with regulation net"
    },
    {
        "court_id": "CRT-TN-01",
        "court_name": "Lawn Tennis Court 1",
        "sport_type": "Tennis",
        "location_venue": "Tennis Complex",
        "status": "Available",
        "notes": "Hard synthetic tennis court with floodlight support"
    },
    {
        "court_id": "CRT-TT-01",
        "court_name": "Table Tennis Table 1",
        "sport_type": "Table Tennis",
        "location_venue": "Indoor TT Arena",
        "status": "Available",
        "notes": "Stag International ITTF Table 1"
    },
    {
        "court_id": "CRT-TT-02",
        "court_name": "Table Tennis Table 2",
        "sport_type": "Table Tennis",
        "location_venue": "Indoor TT Arena",
        "status": "Available",
        "notes": "Stag International ITTF Table 2"
    },
    {
        "court_id": "CRT-POOL-01",
        "court_name": "Pool Table 1",
        "sport_type": "Pool & Billiards",
        "location_venue": "Billiards Lounge",
        "status": "Available",
        "notes": "8-ft Slate pool & billiards table"
    },
    {
        "court_id": "CRT-CRM-01",
        "court_name": "Carrom Station 1",
        "sport_type": "Carrom",
        "location_venue": "Recreation Hall",
        "status": "Available",
        "notes": "Synco tournament carrom board station 1"
    },
    {
        "court_id": "CRT-CRM-02",
        "court_name": "Carrom Station 2",
        "sport_type": "Carrom",
        "location_venue": "Recreation Hall",
        "status": "Available",
        "notes": "Synco tournament carrom board station 2"
    },
    {
        "court_id": "CRT-CRK-01",
        "court_name": "Main Cricket Ground",
        "sport_type": "Cricket",
        "location_venue": "Campus Sports Grounds",
        "status": "Available",
        "notes": "Full cricket oval with turf pitch and practice nets"
    },
    {
        "court_id": "CRT-FTB-01",
        "court_name": "Football Turf Ground",
        "sport_type": "Football",
        "location_venue": "Campus Stadium",
        "status": "Available",
        "notes": "Regulation size football field with natural turf"
    }
]
