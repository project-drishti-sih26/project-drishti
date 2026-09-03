"""
FILE: ml_engine/models/fallback_heuristic.py
ROLE: Role 2 — ML/AI Engineer
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 WHAT IS THIS FILE?
    This file implements the Cold-Start Fallback Heuristic for the WHERE prediction.
    It is the FIRST thing to implement because it requires NO training data and
    NO machine learning library. It guarantees that even on Day 1, before any
    ML model is trained, Project Drishti can produce a working prediction.

    This IS the "Phase 1" of the WHERE engine.

📌 WHY IS THIS FILE NEEDED?
    The LightGBM LambdaMART model (ltr_ranker.py) requires historical transaction
    data to train. If we encounter a mule account with NO prior transaction history
    (a "cold start" problem), the ML model simply cannot make an informed prediction
    — it has never seen this account before.

    The fallback heuristic bypasses this by using pure domain knowledge:
    - Fraudsters prefer ATMs with low surveillance / high cash flow.
    - Fraudsters prefer ATMs that are historically associated with fraud.
    - Fraudsters choose ATMs that minimize travel time (reduce exposure time).

    This formula is directly from the Project Blueprint:
    Score = (Fraud_History × 0.7) + (1/Distance × 0.3)

📌 WHAT TO IMPLEMENT HERE:

    CONSTANTS:
    FRAUD_HISTORY_WEIGHT = 0.7
    DISTANCE_WEIGHT = 0.3

    MAIN FUNCTION:
    def score_candidates_heuristic(
        candidate_atms: list[dict],
        mule_latitude: float,
        mule_longitude: float
    ) -> list[dict]:
        """
        Scores and sorts ATM candidates using the domain-knowledge heuristic.
        Returns the candidates sorted by score (highest first).

        SCORING FORMULA (from PROJECT_BLUEPRINT.md):
        Score = (normalized_fraud_history × 0.7) + (normalized_inverse_distance × 0.3)

        STEPS:
        Step 1: Normalize historical_fraud_count across all candidates.
            - Find max_fraud = max(c['historical_fraud_count'] for c in candidates)
            - If max_fraud == 0 (all ATMs have 0 fraud history): set all fraud_scores = 0
            - Else: fraud_score_i = candidate_i['historical_fraud_count'] / max_fraud
            - This gives a value between 0 and 1 for each candidate.

        Step 2: Compute and normalize the inverse distance score.
            - distance_score_i = 1.0 / (candidate_i['travel_time_mins'] + 1.0)
              (Add 1 to avoid division by zero for ATMs at 0 minutes distance)
            - Normalize: max_dist_score = max(all distance_scores)
              normalized_dist_score_i = distance_score_i / max_dist_score

        Step 3: Compute the final weighted score for each candidate:
            score_i = (fraud_score_i × FRAUD_HISTORY_WEIGHT)
                    + (normalized_dist_score_i × DISTANCE_WEIGHT)

        Step 4: Add the score to each candidate dict:
            candidate['score'] = round(score_i, 4)
            candidate['confidence_score'] = round(score_i, 4)  # alias for frontend

        Step 5: Sort candidates descending by score.
            candidates.sort(key=lambda x: x['score'], reverse=True)

        Step 6: Return the sorted list.

        EXAMPLE OUTPUT (top-ranked candidate):
        {
            "location_id": "ATM_SBI_001",
            "bank_name": "SBI",
            "latitude": 28.63,
            "longitude": 77.21,
            "address": "...",
            "distance_km": 2.4,
            "travel_time_mins": 7,
            "historical_fraud_count": 6,
            "score": 0.842,
            "confidence_score": 0.842
        }
        """

    HELPER FUNCTION (optional, for testing the heuristic):
    def demo_score(fraud_count: int, travel_mins: float) -> float:
        """
        Simple demo to show how the formula works for a single ATM.
        Useful for testing and explaining to judges:
        demo_score(6, 7)  → 0.84 (high score: high fraud history + close)
        demo_score(0, 30) → 0.01 (low score: no fraud history + far away)
        """

📌 HOW IT CONNECTS TO OTHER FILES:
    - Called BY: ml_engine/pipelines/inference_pipeline.py when mule has no history.
    - Input comes FROM: ml_engine/pipelines/spatial_filter.py (candidate ATMs).
    - Output goes TO: inference_pipeline.py (top 5 candidates for final payload).

📌 LIBRARIES TO USE:
    - Only Python standard library! (math is optional)
    - No pandas, no sklearn, no ML libraries needed here.
    - This intentional simplicity means it ALWAYS works, even if other
      dependencies fail to install on the presentation laptop.
"""
