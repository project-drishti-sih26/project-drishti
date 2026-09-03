"""
Project Drishti — ML Engine
File: ml_engine/pipelines/explainability.py
Role: Role 2 — ML/AI Engineer

Converts ML scores and feature values into plain-English explanation
strings for police dispatch. No black boxes — every prediction comes
with a human-readable reason.

Phase 1: Template-based explanations (immediate, no SHAP needed).
Phase 2: Real SHAP values when LightGBM model is trained.
"""

from typing import List, Dict, Any, Optional


# ─── Feature → Human-readable phrase lookup ───────────────────────────────────
FEATURE_PHRASES = {
    "travel_time_mins": "~{val:.0f}-min road travel time",
    "distance_km": "{val:.1f} km road distance",
    "historical_fraud_count": "{val:.0f} prior fraud incident(s) recorded at this ATM",
    "mule_atm_affinity": "previously used by this mule in {val:.0f} prior fraud(s)",
    "mule_network_affinity": "used by {val:.0f} linked mule account(s) in this network",
    "h3_fraud_density": "high crime concentration in surrounding area",
    "is_weekend": "weekend timing pattern (higher mule activity)",
}

# Fraud count thresholds for natural language
def _fraud_label(count: int) -> str:
    if count == 0:
        return "no prior fraud history"
    elif count <= 2:
        return f"{count} prior fraud incident(s)"
    elif count <= 5:
        return f"{count} confirmed fraud incidents (high-risk)"
    else:
        return f"{count} confirmed fraud incidents (VERY HIGH risk)"


def _travel_label(mins: float) -> str:
    if mins <= 5:
        return f"extremely close (~{mins:.0f} min travel)"
    elif mins <= 15:
        return f"close proximity (~{mins:.0f} min travel)"
    elif mins <= 30:
        return f"moderate distance (~{mins:.0f} min travel)"
    else:
        return f"distant location (~{mins:.0f} min travel)"


# ─── Template-based explanation (Phase 1 — immediate) ─────────────────────────
def generate_template_explanation(candidate: Dict[str, Any], rank: int) -> str:
    """
    Generates a readable explanation string from candidate feature values.
    Works without any ML model or SHAP — pure template logic.

    Args:
        candidate: ATM candidate dict with travel_time_mins, historical_fraud_count, etc.
        rank:      The ATM's rank in the Top-5 list (1 = most likely).

    Returns:
        Human-readable explanation string for police dispatch display.
    """
    travel_mins = candidate.get("travel_time_mins", 0)
    fraud_count = candidate.get("historical_fraud_count", 0)
    mule_affinity = candidate.get("mule_atm_affinity", 0)
    network_affinity = candidate.get("mule_network_affinity", 0)
    score = candidate.get("confidence_score", 0)

    # ── Build explanation components ─────────────────────────────────────
    reasons = []

    # Primary: Travel distance (always the clearest factor)
    reasons.append(_travel_label(travel_mins))

    # Secondary: Fraud history
    reasons.append(_fraud_label(fraud_count))

    # Tertiary: Mule-specific affinity (if available)
    if mule_affinity and mule_affinity > 0:
        reasons.append(f"this mule has used this ATM before ({int(mule_affinity)} time(s))")
    elif network_affinity and network_affinity > 0:
        reasons.append(f"linked mule accounts have used this ATM ({int(network_affinity)} time(s))")

    # ── Compose final string ──────────────────────────────────────────────
    if len(reasons) == 1:
        explanation = f"Rank #{rank}: {reasons[0]}."
    elif len(reasons) == 2:
        explanation = f"Rank #{rank}: {reasons[0]} + {reasons[1]}."
    else:
        explanation = f"Rank #{rank}: {reasons[0]} + {reasons[1]} + {reasons[2]}."

    # Confidence suffix
    if score >= 0.8:
        explanation += " [HIGH CONFIDENCE]"
    elif score >= 0.5:
        explanation += " [MODERATE CONFIDENCE]"

    return explanation


# ─── SHAP-based explanation (Phase 2 — after LightGBM is trained) ─────────────
def generate_shap_explanations(
    model,
    feature_matrix,
    candidate_atms: List[Dict],
    feature_names: List[str],
) -> List[str]:
    """
    Uses SHAP TreeExplainer to compute feature contributions for each
    ranked ATM, then translates the top 2 contributing features into
    natural language explanations.

    Args:
        model:          Trained LightGBM model object.
        feature_matrix: numpy array of shape (n_candidates, n_features).
        candidate_atms: List of candidate dicts (same order as feature_matrix rows).
        feature_names:  List of feature column names matching feature_matrix columns.

    Returns:
        List of explanation strings, one per candidate.
    """
    try:
        import shap
        import numpy as np
    except ImportError:
        print("[Explainability] SHAP not installed. Falling back to template explanations.")
        return [
            generate_template_explanation(c, i + 1)
            for i, c in enumerate(candidate_atms)
        ]

    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(feature_matrix)

    explanations = []
    for i, (atm, shap_row) in enumerate(zip(candidate_atms, shap_values)):
        # Find top 2 features by absolute SHAP value
        abs_shap = [(abs(sv), fname, sv) for sv, fname in zip(shap_row, feature_names)]
        abs_shap.sort(reverse=True)
        top_features = abs_shap[:2]

        parts = []
        for _, fname, sv in top_features:
            phrase_template = FEATURE_PHRASES.get(fname)
            if phrase_template:
                val = atm.get(fname, 0)
                phrase = phrase_template.replace("{val:.0f}", f"{val:.0f}")
                phrase = phrase.replace("{val:.1f}", f"{val:.1f}")
                parts.append(phrase)

        base = f"Rank #{i + 1}: "
        if parts:
            explanation = base + " + ".join(parts) + "."
        else:
            explanation = base + f"ML score = {atm.get('score', 0):.3f}."

        explanations.append(explanation)

    return explanations


# ─── Master dispatch function ─────────────────────────────────────────────────
def generate_explanations(
    top_candidates: List[Dict[str, Any]],
    model=None,
    feature_matrix=None,
    feature_names: Optional[List[str]] = None,
    model_used: str = "FallbackHeuristic",
) -> List[str]:
    """
    Routes to the correct explanation method based on which model was used.

    Called by inference_pipeline.py after ranking is complete.

    Args:
        top_candidates: The final Top-5 ATM candidates (sorted by rank).
        model:          LightGBM model (or None if heuristic was used).
        feature_matrix: numpy feature array (or None).
        feature_names:  Feature column names (or None).
        model_used:     "LambdaMART" or "FallbackHeuristic".

    Returns:
        List of explanation strings, one per candidate.
    """
    if model_used == "LambdaMART" and model is not None and feature_matrix is not None:
        print("[Explainability] Using SHAP explanations (LambdaMART model).")
        return generate_shap_explanations(model, feature_matrix, top_candidates, feature_names or [])
    else:
        print("[Explainability] Using template explanations (Fallback/Heuristic mode).")
        return [
            generate_template_explanation(c, i + 1)
            for i, c in enumerate(top_candidates)
        ]


# ─── Self-test ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    test_candidates = [
        {"bank_name": "HDFC", "address": "Rajiv Chowk",      "travel_time_mins": 7,  "historical_fraud_count": 8, "mule_atm_affinity": 2, "confidence_score": 0.91},
        {"bank_name": "SBI",  "address": "Connaught Place",   "travel_time_mins": 0,  "historical_fraud_count": 6, "mule_atm_affinity": 0, "confidence_score": 0.84},
        {"bank_name": "UBI",  "address": "Nangloi",           "travel_time_mins": 40, "historical_fraud_count": 7, "mule_atm_affinity": 1, "confidence_score": 0.72},
        {"bank_name": "BOB",  "address": "Mayur Vihar",       "travel_time_mins": 38, "historical_fraud_count": 5, "mule_atm_affinity": 0, "confidence_score": 0.60},
        {"bank_name": "PNB",  "address": "Lajpat Nagar",      "travel_time_mins": 21, "historical_fraud_count": 4, "mule_atm_affinity": 0, "confidence_score": 0.45},
    ]

    explanations = generate_explanations(test_candidates, model_used="FallbackHeuristic")

    print("\n[TEST] Generated Explanations for Police Dispatch:\n")
    for i, (atm, expl) in enumerate(zip(test_candidates, explanations), 1):
        print(f"  {expl}")
