"""
FILE: ml_engine/pipelines/explainability.py
ROLE: Role 2 — ML/AI Engineer
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 WHAT IS THIS FILE?
    This file converts ML model scores and feature values into plain-English
    explanation strings for each predicted ATM candidate. These strings appear
    on Role 4's frontend as the human-readable "reason" cards on the Top-5
    ATM list, and are included in the Police Dispatch PDF export.

    Project Drishti MUST be explainable. Police officers, IPS officers, and
    SIH judges will NOT trust a black-box system that just says "Go to ATM X".
    They need to understand WHY. This is the feature that separates Drishti
    from a simple ML demo into a real law enforcement intelligence tool.

📌 WHY IS THIS FILE NEEDED?
    SHAP (SHapley Additive exPlanations) is the gold standard for ML
    explainability. For tree models like LightGBM, SHAP computes the exact
    contribution of each input feature to the final prediction score.
    We translate those SHAP values into cop-friendly English.

📌 WHAT TO IMPLEMENT HERE:

    1. SHAP-BASED EXPLANATION (for when LambdaMART model is used):
       def generate_shap_explanations(
           model,              # The trained LightGBM model object
           feature_matrix,     # numpy array of features for top 5 candidates
           candidate_atms,     # list of candidate dicts from spatial_filter.py
           feature_names       # list of feature column names
       ) -> list[str]:
           """
           Uses the `shap` library to compute feature contributions for each
           of the top 5 ranked ATMs, then translates the top 2 contributing
           features into a natural language explanation string.

           STEPS:
           1. Create a TreeExplainer: explainer = shap.TreeExplainer(model)
           2. Compute SHAP values: shap_values = explainer.shap_values(feature_matrix)
              shap_values shape: (num_candidates, num_features)
           3. For each candidate (row in shap_values):
               a. Find the top 2 features with the highest absolute SHAP value.
               b. Map those feature names to human-readable phrases using a
                  lookup dictionary (see FEATURE_DESCRIPTIONS below).
               c. Format the explanation string.

           FEATURE_DESCRIPTIONS lookup dict (map feature name → readable phrase):
           {
               "travel_time_mins": "estimated road travel time of {val:.0f} mins",
               "historical_fraud_count": "high ATM fraud history ({val:.0f} past incidents)",
               "mule_atm_affinity": "previously used by this mule network",
               "distance_km": "nearest reachable location at {val:.1f} km",
               "h3_fraud_density": "high crime density in surrounding area",
           }

           EXAMPLE OUTPUT STRING:
           "Primary driver: 7-min road travel. Secondary: 4 prior mule incidents at this ATM."

           Return a list of explanation strings, one per candidate, in same order.
           """

    2. TEMPLATE-BASED EXPLANATION (fallback when heuristic model is used):
       def generate_template_explanation(candidate: dict) -> str:
           """
           When the Fallback Heuristic is used (no SHAP available),
           generate a simpler template-based explanation using the feature values.

           Use if/elif rules to compose the string:
           - If historical_fraud_count >= 5: mention "high historical fraud density"
           - If travel_time_mins < 10: mention "very close travel distance"
           - If mule_atm_affinity > 0 (from historical data): mention "prior mule usage"

           EXAMPLE:
           "Close proximity (8 min travel) + historical fraud activity (3 incidents) at this ATM."
           """

    3. MASTER DISPATCH FUNCTION (called by inference_pipeline.py):
       def generate_explanations(
           top_5_candidates: list[dict],
           model=None,
           feature_matrix=None,
           feature_names=None,
           model_used: str = "FallbackHeuristic"
       ) -> list[str]:
           """
           Routes to the correct explanation method based on which model was used.
           If model_used == "LambdaMART": call generate_shap_explanations().
           If model_used == "FallbackHeuristic": call generate_template_explanation() for each.
           Returns a list of explanation strings in the same order as top_5_candidates.
           """

📌 HOW IT CONNECTS TO OTHER FILES:
    - Called BY: ml_engine/pipelines/inference_pipeline.py (STEP 5).
    - Uses: The trained LightGBM model from ml_engine/models/ltr_ranker.py.
    - The explanation strings become the `explanation` field in each ATMCandidate
      object in the PredictionAlert payload.
    - Frontend (Role 4) displays these strings on the ATM ranking cards.

📌 LIBRARIES TO USE:
    - shap (pip install shap)
    - numpy (for feature matrix operations)
"""
