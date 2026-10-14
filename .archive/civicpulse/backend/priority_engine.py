"""
priority_engine.py — CivicPulse AI Phase 3

Rule-based priority scoring engine.

DISCLAIMER:
  This is a decision-support prototype. The scoring formula and thresholds
  have NOT been validated against real municipal failure data. Final repair
  decisions must be made by authorized maintenance personnel.

Scoring formula:
  Priority Score = (0.40 × Severity)
                 + (0.25 × Recurrence)
                 + (0.20 × PendingTime)
                 + (0.15 × PublicImpact)

Each factor is normalised to 0–100 before weighting.

Priority categories (prototype thresholds):
  High   : 70 – 100
  Medium : 40 – 69.99
  Low    :  0 – 39.99
"""

from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURABLE WEIGHTS AND THRESHOLDS
# These can be overridden at runtime via POST /api/priority/recalculate
# ─────────────────────────────────────────────────────────────────────────────

DEFAULT_WEIGHTS = {
    "severity":      0.40,
    "recurrence":    0.25,
    "pending_time":  0.20,
    "public_impact": 0.15,
}

DEFAULT_THRESHOLDS = {
    "high":   70.0,
    "medium": 40.0,
    # anything below medium is "low"
}

# Severity word → raw score (0–100)
SEVERITY_SCORES: Dict[str, float] = {
    "high":   100.0,
    "medium":  60.0,
    "low":     20.0,
}

# Asset condition → public-impact multiplier
CONDITION_IMPACT: Dict[str, float] = {
    "poor": 100.0,
    "fair":  60.0,
    "good":  20.0,
}

# Max days pending before the time factor is saturated at 100
MAX_PENDING_DAYS = 30.0

# Max recurrence count before the recurrence factor is saturated at 100
MAX_RECURRENCE = 5


# ─────────────────────────────────────────────────────────────────────────────
# FACTOR CALCULATION HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def calc_severity_score(severity: str) -> float:
    """Map severity label to a 0–100 score."""
    return SEVERITY_SCORES.get(severity.lower(), 50.0)


def calc_recurrence_score(recurrence_count: int) -> float:
    """
    Normalise complaint recurrence count to 0–100.
    A single complaint = 0; MAX_RECURRENCE or more = 100.
    """
    if recurrence_count <= 1:
        return 0.0
    # Each additional complaint beyond the first adds proportional weight
    score = min((recurrence_count - 1) / (MAX_RECURRENCE - 1), 1.0) * 100.0
    return round(score, 2)


def calc_pending_time_score(reported_at: datetime) -> float:
    """
    Normalise days since complaint was reported to 0–100.
    0 days = 0;  MAX_PENDING_DAYS or more = 100.
    """
    now = datetime.now(timezone.utc)
    # Make reported_at timezone-aware if it isn't
    if reported_at.tzinfo is None:
        reported_at = reported_at.replace(tzinfo=timezone.utc)

    days = (now - reported_at).total_seconds() / 86400.0
    score = min(days / MAX_PENDING_DAYS, 1.0) * 100.0
    return round(score, 2)


def calc_public_impact_score(asset_condition: str, asset_type: str) -> float:
    """
    Estimate public impact from asset condition and type.
    Street-facing assets get a higher baseline.
    """
    base = CONDITION_IMPACT.get(asset_condition.lower(), 50.0)
    # Streetlights on public roads carry higher impact
    type_multiplier = 1.0 if "streetlight" in asset_type.lower() else 0.8
    return round(min(base * type_multiplier, 100.0), 2)


# ─────────────────────────────────────────────────────────────────────────────
# SCORE AGGREGATION
# ─────────────────────────────────────────────────────────────────────────────

def calculate_priority(
    severity: str,
    recurrence_count: int,
    reported_at: datetime,
    asset_condition: str,
    asset_type: str,
    weights: Optional[Dict[str, float]] = None,
    thresholds: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    """
    Compute the composite priority score and category for a complaint.

    Returns a dict with:
      score           : float 0–100
      priority_level  : "high" | "medium" | "low"
      factors         : breakdown of each component
      explanation     : plain-English rationale
      suggested_action: recommended next step
    """
    w = weights   or DEFAULT_WEIGHTS
    t = thresholds or DEFAULT_THRESHOLDS

    # --- Individual factors (0–100 each) ---
    f_severity     = calc_severity_score(severity)
    f_recurrence   = calc_recurrence_score(recurrence_count)
    f_pending      = calc_pending_time_score(reported_at)
    f_impact       = calc_public_impact_score(asset_condition, asset_type)

    days_pending = max(0.0, (datetime.now(timezone.utc) -
                             (reported_at if reported_at.tzinfo
                              else reported_at.replace(tzinfo=timezone.utc))
                             ).total_seconds() / 86400.0)

    # --- Weighted composite score ---
    raw_score = (
        w["severity"]      * f_severity  +
        w["recurrence"]    * f_recurrence +
        w["pending_time"]  * f_pending   +
        w["public_impact"] * f_impact
    )
    score = round(min(max(raw_score, 0.0), 100.0), 1)

    # --- Category ---
    if score >= t["high"]:
        priority_level = "high"
    elif score >= t["medium"]:
        priority_level = "medium"
    else:
        priority_level = "low"

    # --- Factor breakdown (for transparency) ---
    factors = {
        "severity": {
            "label":       "Issue Severity",
            "raw_score":   f_severity,
            "weight":      w["severity"],
            "contribution": round(w["severity"] * f_severity, 1),
            "input":        severity,
        },
        "recurrence": {
            "label":       "Recurrence Count",
            "raw_score":   f_recurrence,
            "weight":      w["recurrence"],
            "contribution": round(w["recurrence"] * f_recurrence, 1),
            "input":        recurrence_count,
        },
        "pending_time": {
            "label":       "Days Pending",
            "raw_score":   f_pending,
            "weight":      w["pending_time"],
            "contribution": round(w["pending_time"] * f_pending, 1),
            "input":        round(days_pending, 1),
        },
        "public_impact": {
            "label":       "Public Service Impact",
            "raw_score":   f_impact,
            "weight":      w["public_impact"],
            "contribution": round(w["public_impact"] * f_impact, 1),
            "input":        asset_condition,
        },
    }

    # --- Explainable text ---
    explanation = _build_explanation(
        priority_level, severity, recurrence_count, days_pending, asset_condition
    )
    suggested_action = _suggest_action(priority_level, recurrence_count, days_pending)

    return {
        "score":           score,
        "priority_level":  priority_level,
        "factors":         factors,
        "explanation":     explanation,
        "suggested_action": suggested_action,
        "days_pending":    round(days_pending, 1),
        "recurrence_count": recurrence_count,
    }


# ─────────────────────────────────────────────────────────────────────────────
# EXPLANATION GENERATION
# ─────────────────────────────────────────────────────────────────────────────

def _build_explanation(
    priority_level: str,
    severity: str,
    recurrence_count: int,
    days_pending: float,
    condition: str,
) -> str:
    """
    Construct a plain-English explanation derived entirely from scoring factors.
    No LLM is used — all reasons are traceable to input values.
    """
    parts: List[str] = []

    # Severity contribution
    if severity == "high":
        parts.append("the issue is rated high severity")
    elif severity == "medium":
        parts.append("the issue is rated medium severity")
    else:
        parts.append("the issue is rated low severity")

    # Recurrence contribution
    if recurrence_count > 3:
        parts.append(f"this asset has {recurrence_count} repeated fault reports indicating a persistent problem")
    elif recurrence_count > 1:
        parts.append(f"there are {recurrence_count} complaints on this asset suggesting recurrence")

    # Pending time contribution
    if days_pending >= 20:
        parts.append(f"the complaint has been unresolved for {days_pending:.0f} days")
    elif days_pending >= 7:
        parts.append(f"it has been pending for {days_pending:.0f} days")

    # Condition contribution
    if condition == "poor":
        parts.append("the asset is in poor condition amplifying public impact")
    elif condition == "fair":
        parts.append("the asset condition is fair")

    if not parts:
        parts.append("standard scoring factors were applied")

    reason = "; ".join(parts).capitalize() + "."
    return f"{priority_level.capitalize()} priority because {reason}"


def _suggest_action(
    priority_level: str,
    recurrence_count: int,
    days_pending: float,
) -> str:
    """Return a suggested next action based on scoring outcomes."""
    if priority_level == "high":
        if recurrence_count > 2:
            return "Schedule immediate inspection and consider root-cause analysis for recurring failure."
        return "Assign to repair team within 24 hours."
    elif priority_level == "medium":
        if days_pending > 14:
            return "Schedule repair within 3 days; complaint is ageing."
        return "Schedule repair within 1 week."
    else:
        return "Add to routine maintenance queue."


# ─────────────────────────────────────────────────────────────────────────────
# RECURRENCE DETECTION
# ─────────────────────────────────────────────────────────────────────────────

def detect_recurrence(complaints: List[Any]) -> Dict[str, int]:
    """
    Given a list of Complaint ORM objects (or dicts with asset_id),
    return a mapping of asset_id → complaint count.

    Only counts non-resolved complaints as active recurrences.
    Resolved complaints are included in the history count separately.
    """
    counts: Dict[str, int] = {}
    for c in complaints:
        aid = c.asset_id if hasattr(c, "asset_id") else c["asset_id"]
        counts[aid] = counts.get(aid, 0) + 1
    return counts
