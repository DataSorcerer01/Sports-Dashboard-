"""
models.py - Core data schemas, enums, and validation constants.
"""
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class EquipmentStatus(str, Enum):
    AVAILABLE = "Available"
    PENDING_VERIFICATION = "Pending Verification"
    IN_USE = "In Use"
    RETURNED = "Returned"
    DAMAGED = "Damaged"
    MAINTENANCE = "Under Maintenance"


class RequestStatus(str, Enum):
    PENDING = "Pending Verification"
    APPROVED = "In Use"
    RETURNED = "Returned"
    EXPIRED = "Expired"
    CANCELLED = "Cancelled"
    REJECTED = "Rejected"


class ReturnCondition(str, Enum):
    GOOD = "Good Condition"
    MINOR_WEAR = "Minor Normal Wear"
    DAMAGED = "Damaged / Broken"
    MISSING_PARTS = "Missing Parts"


class CourtStatus(str, Enum):
    AVAILABLE = "Available"
    OCCUPIED = "Occupied"
    MAINTENANCE = "Under Maintenance"


SPORTS_CATEGORIES = [
    "Badminton",
    "Table Tennis",
    "Pickleball",
    "Tennis",
    "Pool & Billiards",
    "Carrom",
    "Cricket",
    "Football",
    "Volleyball",
    "Board Games"
]

USAGE_DURATIONS = [
    "30 Minutes",
    "45 Minutes",
    "1 Hour",
    "1.5 Hours",
    "2 Hours",
    "3 Hours"
]

REQUEST_EXPIRY_MINUTES = 30


@dataclass
class Equipment:
    equipment_id: str
    category: str
    item_name: str
    total_quantity: int
    available_quantity: int
    in_use_quantity: int
    pending_quantity: int
    damaged_quantity: int
    location_rack: str
    condition: str
    notes: Optional[str] = ""
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@dataclass
class AllocationRequest:
    request_id: str
    equipment_id: str
    equipment_name: str
    category: str
    student_name: str
    dm_number: str
    mobile_number: str
    room_number: str
    intended_duration: str
    status: str
    requested_at: str
    expires_at: str
    authorized_at: Optional[str] = None
    guard_name: Optional[str] = None
    returned_at: Optional[str] = None
    return_condition: Optional[str] = None
    guard_notes: Optional[str] = None


@dataclass
class CourtFacility:
    court_id: str
    court_name: str
    sport_type: str
    location_venue: str
    status: str
    current_occupant: Optional[str] = None
    dm_number: Optional[str] = None
    contact_number: Optional[str] = None
    hostel_room: Optional[str] = None
    occupied_since: Optional[str] = None
    intended_duration: Optional[str] = None
    notes: Optional[str] = None
