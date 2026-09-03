"""
FILE: ml_engine/pipelines/inference_pipeline.py
ROLE: Role 2 — ML/AI Engineer
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 WHAT IS THIS FILE?
    This is the MASTER ENTRYPOINT of the entire ML Engine. It exposes ONE
    clean function: `predict_fraud_cashout()` that the Backend's trigger_service.py
    calls. Internally, it orchestrates all four steps of the prediction pipeline:
    Spatial Filtering → LTR Ranking → Survival Time → SHAP Explainability.

    This file is the "glue" of the ML module. It should stay thin —
    actual ML logic lives in the models/ and pipelines/ sub-files.
    This file only calls them in the right sequence.

📌 WHY IS THIS FILE NEEDED?
    The Backend (Role 1) should NOT need to know HOW the ML works internally.
    It just calls `predict_fraud_cashout(input_data)` and gets back a
    structured prediction dict. This separation is called the "Facade Pattern":
    - It hides ML complexity from the backend.
    - If the ML team wants to swap LightGBM for a different model, they only
      change files in ml_engine/. The backend doesn't need any changes.
    - Easier to unit-test each pipeline step independently.

📌 WHAT TO IMPLEMENT HERE:

    THE MAIN FUNCTION (called by backend's trigger_service.py):
    def predict_fraud_cashout(input_data: dict) -> dict:
        """
        Master inference pipeline orchestrator.

        ARGS:
            input_data (dict): Contains these keys (sent by trigger_service.py):
            {
                "mule_account_id": str,
                "last_latitude": float or None,   # Mule's last known GPS location
                "last_longitude": float or None,
                "transaction_amount": float,       # ₹ amount transferred
                "transaction_timestamp": str,      # ISO format timestamp
                "case_id": str,
                "victim_account_id": str,
            }

        RETURNS:
            dict: A prediction payload matching the PredictionAlert schema
                  defined in backend/app/schemas/prediction.py. Structure:
            {
                "alert_id": str,
                "case_id": str,
                "mule_account_id": str,
                "victim_account_id": str,
                "compromised_amount": float,
                "detected_at": str,
                "time_window": {
                    "start": str,
                    "end": str,
                    "minutes_from_now": int,
                    "confidence": float
                },
                "top_5_atms": [ ... list of 5 ATMCandidate dicts ... ],
                "model_used": str,
                "total_candidates_evaluated": int
            }

        PIPELINE STEPS:

        STEP 1 — LOAD ATM CANDIDATES:
            Import and call `get_candidate_atms()` from spatial_filter.py.
            Pass: last_latitude, last_longitude, transaction_timestamp.
            Receives: a list of ~100-200 ATM dicts within reachable distance.

            If last_latitude/last_longitude is None (location unknown):
            Fall back to using city-center coordinates (e.g., Delhi: 28.6139, 77.2090).

        STEP 2 — CHECK IF MULE HAS HISTORY (decides which model to use):
            Check if this mule_account_id appears in historical_transactions.csv.
            If mule has at least 5 prior events → use LambdaMART model (WHERE).
            If mule is brand new (cold start) → use fallback heuristic (WHERE).
            Set `model_used = "LambdaMART"` or `"FallbackHeuristic"` accordingly.

        STEP 3 — WHERE PREDICTION (rank the candidates):
            If mule has history:
                Import `rank_atm_candidates()` from ltr_ranker.py.
            Else:
                Import `score_candidates_heuristic()` from fallback_heuristic.py.
            
            Both functions accept the candidate list and return them sorted by score.
            Take the top 5 candidates as `top_5_candidates`.

        STEP 4 — WHEN PREDICTION (time window):
            Import `predict_time_window()` from survival_time.py.
            Pass: transaction_timestamp, mule_account_id.
            Receives: {"start": datetime, "end": datetime, "minutes_from_now": int, "confidence": float}

        STEP 5 — GENERATE SHAP EXPLANATIONS:
            Import `generate_explanations()` from explainability.py.
            For each of the top_5_candidates, generate a human-readable
            explanation string based on which features drove the ranking score.

        STEP 6 — ASSEMBLE AND RETURN THE PAYLOAD:
            Build the final dict matching PredictionAlert schema.
            Include all top_5 ATMs with their rank, coordinates, explanation, etc.
        """

    IMPORTANT — HACKATHON PHASE 1 APPROACH:
    Start by implementing a SIMPLE version:
    - Skip STEP 2 (always use fallback heuristic initially)
    - Skip STEP 4 (hardcode a time window of "now + 25 mins to now + 45 mins")
    - Skip STEP 5 (hardcode explanation strings)
    Then add real ML models one by one as they become ready.
    The Backend team can use this simplified version immediately.

📌 HOW IT CONNECTS TO OTHER FILES:
    - Called BY: backend/app/services/trigger_service.py
    - Calls: ml_engine/pipelines/spatial_filter.py (get_candidate_atms)
    - Calls: ml_engine/models/ltr_ranker.py OR fallback_heuristic.py (ranking)
    - Calls: ml_engine/models/survival_time.py (time window)
    - Calls: ml_engine/pipelines/explainability.py (SHAP strings)

📌 LIBRARIES TO USE:
    - json (standard library)
    - datetime (standard library)
    - uuid (for alert_id generation)
    - All ml_engine sub-modules (see above)
"""
