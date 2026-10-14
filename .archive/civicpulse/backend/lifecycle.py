"""
lifecycle.py — Phase 4 repair lifecycle state machine.

Defines valid transitions and helper functions.
All business rules for status changes live here so
they can be tested independently of FastAPI.

Valid lifecycle states:
  reported → under_inspection → assigned → in_progress →
  awaiting_verification → resolved
                        ↑
  reopened ─────────────┘  (reopened → assigned → ...)

The old 2-value "status" field (open / in-progress / resolved) is
kept for backward compatibility and derived from lifecycle_status.
"""

from typing import Dict, Set

# ─────────────────────────────────────────────────────────────────
# ALLOWED TRANSITIONS
# key = current state, value = set of states it may move to
# ─────────────────────────────────────────────────────────────────
TRANSITIONS: Dict[str, Set[str]] = {
    "reported":               {"under_inspection", "assigned"},
    "under_inspection":       {"assigned"},
    "assigned":               {"in_progress"},
    "in_progress":            {"awaiting_verification"},
    "awaiting_verification":  {"resolved", "in_progress"},   # resolved=approved, in_progress=rejected
    "resolved":               {"reopened"},
    "reopened":               {"under_inspection", "assigned"},
}

# Human-readable labels
STATE_LABELS: Dict[str, str] = {
    "reported":              "Reported",
    "under_inspection":      "Under Inspection",
    "assigned":              "Assigned",
    "in_progress":           "In Progress",
    "awaiting_verification": "Awaiting Verification",
    "resolved":              "Resolved",
    "reopened":              "Reopened",
}

# Map lifecycle_status → old status field (for backward compat)
LIFECYCLE_TO_STATUS: Dict[str, str] = {
    "reported":              "open",
    "under_inspection":      "open",
    "assigned":              "open",
    "in_progress":           "in-progress",
    "awaiting_verification": "in-progress",
    "resolved":              "resolved",
    "reopened":              "open",
}


def is_valid_transition(current: str, target: str) -> bool:
    """Return True if moving from current → target is permitted."""
    return target in TRANSITIONS.get(current, set())


def validate_transition(current: str, target: str) -> None:
    """
    Raise ValueError with a clear message if the transition is not allowed.
    FastAPI endpoints catch this and return HTTP 422.
    """
    if not is_valid_transition(current, target):
        allowed = sorted(TRANSITIONS.get(current, set()))
        raise ValueError(
            f"Cannot transition from '{STATE_LABELS.get(current, current)}' "
            f"to '{STATE_LABELS.get(target, target)}'. "
            f"Allowed next states: {[STATE_LABELS.get(s, s) for s in allowed]}."
        )


def derive_status(lifecycle_status: str) -> str:
    """Return the legacy 'status' string for a given lifecycle state."""
    return LIFECYCLE_TO_STATUS.get(lifecycle_status, "open")


def all_states() -> list:
    return list(TRANSITIONS.keys())
