"""
models.py - Core data schemas, enums, and validation constants for Sports Equipment System.
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


SPORTS_CATEGORIES = [
    "Badminton",
    "Football",
    "Basketball",
    "Table Tennis",
    "Cricket",
    "Volleyball",
    "Lawn Tennis",
    "Squash",
    "Board Games"
]

USAGE_DURATIONS = [
    "30 Minutes",
    "1 Hour",
    "1.5 Hours",
    "2 Hours",
    "3 Hours",
    "Full Afternoon (4 Hours)"
]

# Strict 30-Minute validity rule for student pending requests
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
