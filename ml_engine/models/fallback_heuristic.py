"""
Project Drishti — ML Engine
File: ml_engine/models/fallback_heuristic.py
Role: Role 2 — ML/AI Engineer

STEP 1 of WHERE Engine: Cold-Start Fallback Scorer.
No training data needed. Works on Day 1.

Formula (from PROJECT_BLUEPRINT.md):
    Score = (normalized_fraud_history * 0.7) + (normalized_inverse_distance * 0.3)
"""

from typing import List, Dict, Any

# ─── Tunable Weights ─────────────────────────────────────────────────────────
FRAUD_HISTORY_WEIGHT = 0.7
DISTANCE_WEIGHT = 0.3


def score_candidates_heuristic(
    candidate_atms: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Scores and sorts ATM candidates using the domain-knowledge heuristic.
    Works without any ML model or training data.

    Args:
        candidate_atms: List of ATM candidate dicts from spatial_filter.py.
                        Each dict must have: 'historical_fraud_count', 'travel_time_mins'

    Returns:
        The same list, sorted by 'score' descending, with 'score' and
        'confidence_score' fields added to each dict.
    """
    if not candidate_atms:
        return []

    # ── Step 1: Normalize historical_fraud_count ───────────────────────────
    max_fraud = max(c.get("historical_fraud_count", 0) for c in candidate_atms)

    for c in candidate_atms:
        fraud_count = c.get("historical_fraud_count", 0)
        c["_fraud_score"] = (fraud_count / max_fraud) if max_fraud > 0 else 0.0

    # ── Step 2: Compute normalized inverse-distance score ─────────────────
    # Add 1 to avoid division by zero (ATM at 0 mins still gets a finite score)
    raw_dist_scores = [1.0 / (c.get("travel_time_mins", 999) + 1.0) for c in candidate_atms]
    max_dist_score = max(raw_dist_scores) if raw_dist_scores else 1.0

    for c, raw_score in zip(candidate_atms, raw_dist_scores):
        c["_dist_score"] = raw_score / max_dist_score if max_dist_score > 0 else 0.0

    # ── Step 3: Compute final weighted score ──────────────────────────────
    for c in candidate_atms:
        score = (c["_fraud_score"] * FRAUD_HISTORY_WEIGHT) + (c["_dist_score"] * DISTANCE_WEIGHT)
        c["score"] = round(score, 4)
        c["confidence_score"] = round(score, 4)  # Frontend alias

    # ── Step 4: Clean up temp fields & sort ──────────────────────────────
    for c in candidate_atms:
        c.pop("_fraud_score", None)
        c.pop("_dist_score", None)

    candidate_atms.sort(key=lambda x: x["score"], reverse=True)

    return candidate_atms


def demo_score(fraud_count: int, travel_mins: float) -> float:
    """
    Quick demo of the formula for a SINGLE ATM (no normalization).
    Useful for explaining the formula to judges or in notebooks.

    Example:
        >>> demo_score(6, 7)   # High fraud + close → high score
        >>> demo_score(0, 30)  # No fraud + far    → low score
    """
    fraud_component = fraud_count / (fraud_count + 1)   # Simple normalization
    dist_component = 1.0 / (travel_mins + 1.0)          # Inverse distance
    return round(
        (fraud_component * FRAUD_HISTORY_WEIGHT) + (dist_component * DISTANCE_WEIGHT), 4
    )


# ─── Self-test ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    test_candidates = [
        {"location_id": "ATM_SBI_001", "bank_name": "SBI", "latitude": 28.63,
         "longitude": 77.21, "address": "Connaught Place", "distance_km": 2.4,
         "travel_time_mins": 7, "historical_fraud_count": 6},
        {"location_id": "ATM_HDFC_002", "bank_name": "HDFC", "latitude": 28.65,
         "longitude": 77.22, "address": "Karol Bagh", "distance_km": 5.1,
         "travel_time_mins": 14, "historical_fraud_count": 1},
        {"location_id": "ATM_PNB_003", "bank_name": "PNB", "latitude": 28.61,
         "longitude": 77.20, "address": "Lajpat Nagar", "distance_km": 8.2,
         "travel_time_mins": 22, "historical_fraud_count": 4},
    ]

    results = score_candidates_heuristic(test_candidates)
    print("\n[RESULTS] Heuristic Ranking:")
    for i, atm in enumerate(results, 1):
        print(f"  Rank #{i}: {atm['bank_name']} | {atm['address']} | "
              f"Score={atm['score']} | Fraud={atm['historical_fraud_count']} | "
              f"Travel={atm['travel_time_mins']}min")

    print("\n[SCORE] fraud=6, travel=7min  :", demo_score(6, 7))
    print("[SCORE] fraud=0, travel=30min :", demo_score(0, 30))
