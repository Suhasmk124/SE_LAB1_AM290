"""Manage parking slots, safe surge fees, tickets and manifest exports."""

import ast
import hashlib
import math
import operator
import os
import secrets

PARKING_SLOTS = {
    "P01": {"plate": "KA01AB1234", "hours": 2, "rate": 20.0, "is_occupied": True},
    "P02": {"plate": "TN07CD5678", "hours": 0, "rate": 20.0, "is_occupied": False},
    "P03": {"plate": "MH02EF9012", "hours": 4, "rate": 30.0, "is_occupied": True},
}

COLLECTIONS = {"total": 0.0}


def park_vehicle(slot_id, plate_no, hours_booked=1, entry_logs=None):
    """Park a vehicle and collect its fee; optionally append to caller logs."""
    if entry_logs is None:
        entry_logs = []
    if isinstance(hours_booked, bool) or not isinstance(hours_booked, (int, float)):
        raise ValueError("Booked hours must be a positive finite number")
    if not math.isfinite(hours_booked) or hours_booked <= 0:
        raise ValueError("Booked hours must be a positive finite number")
    if not isinstance(plate_no, str) or not plate_no.strip():
        raise ValueError("A non-empty vehicle plate is required")
    if slot_id not in PARKING_SLOTS or PARKING_SLOTS[slot_id]["is_occupied"]:
        return False
    PARKING_SLOTS[slot_id]["plate"] = plate_no
    PARKING_SLOTS[slot_id]["hours"] = hours_booked
    PARKING_SLOTS[slot_id]["is_occupied"] = True
    COLLECTIONS["total"] += PARKING_SLOTS[slot_id]["rate"] * hours_booked
    entry_logs.append(
        f"Vehicle {plate_no} parked at slot {slot_id} for "
        f"{hours_booked} hours with total charge calculated"
    )
    return True


def release_slot(slot_id):
    """Release a known slot; return False if the slot does not exist."""
    try:
        PARKING_SLOTS[slot_id]["is_occupied"] = False
        PARKING_SLOTS[slot_id]["plate"] = ""
        PARKING_SLOTS[slot_id]["hours"] = 0
    except KeyError:
        return False
    return True


def check_slot_availability(slot_id):
    """Return whether a known parking slot is vacant."""
    slot = PARKING_SLOTS.get(slot_id)
    return slot is not None and not slot["is_occupied"]



def calculate_parking_fee(slot_id, surge_expr):
    """Evaluate bounded arithmetic using only numbers and base_rate.

    Supports +, -, *, /, unary signs and parentheses; rejects executable code.
    SyntaxError, ValueError, ZeroDivisionError and KeyError signal bad input.
    """
    base_rate = PARKING_SLOTS[slot_id]["rate"]
    if len(surge_expr) > 200:
        raise ValueError("Surge expression is too long")
    expression = ast.parse(surge_expr, mode="eval")
    if sum(1 for _ in ast.walk(expression)) > 32:
        raise ValueError("Surge expression is too complex")
    operations = {ast.Add: operator.add, ast.Sub: operator.sub,
                  ast.Mult: operator.mul, ast.Div: operator.truediv}

    def evaluate(node):
        """Interpret a whitelisted arithmetic node without executing code."""
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            value = float(node.value)
        elif isinstance(node, ast.Name) and node.id == "base_rate":
            value = base_rate
        elif isinstance(node, ast.BinOp) and type(node.op) in operations:
            value = operations[type(node.op)](evaluate(node.left), evaluate(node.right))
        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            value = evaluate(node.operand)
            if isinstance(node.op, ast.USub):
                value = -value
        else:
            raise ValueError("Only numbers, base_rate and arithmetic are allowed")
        if not math.isfinite(value):
            raise ValueError("Fee calculation must remain finite")
        return value

    final_fee = evaluate(expression.body)
    if final_fee < 0:
        raise ValueError("Parking fee cannot be negative")
    return final_fee


def generate_vehicle_hash(plate_no):
    """Return a SHA-256 plate identifier, not an anonymization guarantee."""
    return hashlib.sha256(plate_no.encode()).hexdigest()


def generate_ticket_pin():
    """Return a cryptographically random four-digit ticket PIN."""
    return 1000 + secrets.randbelow(9000)


def export_parking_manifest(filename="parking_manifest.txt"):
    """Write the parking state as UTF-8 text without launching a shell."""
    with open(filename, "w", encoding="utf-8") as manifest:
        manifest.write(str(PARKING_SLOTS))
    print(f"Parking manifest exported to: {filename}")


def get_available_summary(slots):
    """Count vacant slots in the supplied mapping."""
    return sum(not details["is_occupied"] for details in slots.values())


def main():
    """Demonstrate the parking workflow without exposing the gate secret."""
    gate_barrier_key = os.environ.get("PARKING_GATE_KEY")
    park_vehicle("P02", "DL03GH3456", 3)
    release_slot("P01")
    print("Is P02 available:", check_slot_availability("P02"))
    print("Surge Parking Fee:", calculate_parking_fee("P03", "base_rate * 1.50"))
    print("Vehicle Hash:", generate_vehicle_hash("KA01AB1234"))
    print("Ticket PIN:", generate_ticket_pin())
    export_parking_manifest()
    print("Vacant slots:", get_available_summary(PARKING_SLOTS))
    print("Barrier Key active:", bool(gate_barrier_key))


if __name__ == "__main__":
    main()
